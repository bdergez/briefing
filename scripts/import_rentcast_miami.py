#!/usr/bin/env python3
"""
Import Miami-area listings from RentCast into Supabase.

Recommended usage:
  1. Keep RENTCAST_API_KEY in .env.local
  2. Add SUPABASE_SERVICE_ROLE_KEY to .env.local when you're ready to write
  3. Run in preview mode first:
       python3 scripts/import_rentcast_miami.py --dry-run
  4. Then write to Supabase:
       python3 scripts/import_rentcast_miami.py

This script is intentionally scoped to Miami only to protect a low monthly
RentCast quota. It fetches a small batch of sale listings plus a small batch of
rental listings, normalizes them into the app's schema, and upserts them into
Supabase.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env.local"

RENTCAST_BASE = "https://api.rentcast.io/v1"
DEFAULT_SUPABASE_URL = "https://buxitxwnqhezszwqbqwh.supabase.co"
SUPABASE_REST_PATH = "/rest/v1"

MARKET_SLUG = "miami"
MARKET_NAME = "Miami Area"
MARKET_CITY = "Miami"
MARKET_STATE = "FL"

SALE_LIMIT = 12
RENTAL_LIMIT = 8
DEFAULT_DAYS_OLD = 30
PROVIDER_NAME = "RentCast"
MOCK_PROVIDER_NAME = "Mock Listing Feed"


def load_env_file(path: Path) -> None:
    if not path.exists():
      return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def require_env(name: str, *, allow_missing: bool = False) -> str | None:
    value = os.environ.get(name, "").strip()
    if value or allow_missing:
        return value or None
    raise SystemExit(f"Missing required environment variable: {name}")


def http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: Any = None,
) -> Any:
    payload = None
    final_headers = dict(headers or {})
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        final_headers.setdefault("Content-Type", "application/json")
    req = Request(url, data=payload, headers=final_headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            if not raw:
                return None
            return json.loads(raw)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error for {url}: {exc}") from exc


def rentcast_get(path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    api_key = require_env("RENTCAST_API_KEY")
    url = f"{RENTCAST_BASE}{path}?{urlencode(params)}"
    data = http_json(url, headers={"X-Api-Key": api_key, "Accept": "application/json"})
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("items"), list):
            return data["items"]
        if isinstance(data.get("results"), list):
            return data["results"]
    raise RuntimeError(f"Unexpected RentCast response shape from {path}")


def first_non_empty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def extract_photo_url(item: dict[str, Any]) -> str | None:
    candidates = [
        item.get("primaryPhotoUrl"),
        item.get("photoUrl"),
        item.get("listingPhotoUrl"),
    ]

    for container in (item.get("photos"), item.get("images"), item.get("media")):
        for entry in as_list(container):
            if isinstance(entry, str) and entry:
                candidates.append(entry)
            elif isinstance(entry, dict):
                candidates.extend([
                    entry.get("url"),
                    entry.get("href"),
                    entry.get("sourceUrl"),
                    entry.get("large"),
                    entry.get("medium"),
                    entry.get("small"),
                ])

    return first_non_empty(*candidates)


def extract_address(item: dict[str, Any]) -> tuple[str | None, str | None, str | None, str | None]:
    address = item.get("address") or {}
    street = first_non_empty(
        item.get("addressLine1"),
        item.get("streetAddress"),
        address.get("line1") if isinstance(address, dict) else None,
        address.get("addressLine1") if isinstance(address, dict) else None,
    )
    city = first_non_empty(item.get("city"), address.get("city") if isinstance(address, dict) else None, MARKET_CITY)
    state = first_non_empty(item.get("state"), address.get("state") if isinstance(address, dict) else None, MARKET_STATE)
    postal = first_non_empty(
        item.get("zipCode"),
        item.get("postalCode"),
        address.get("zipCode") if isinstance(address, dict) else None,
        address.get("postalCode") if isinstance(address, dict) else None,
    )
    return street, city, state, postal


def extract_coordinates(item: dict[str, Any]) -> tuple[float | None, float | None]:
    address = item.get("address") or {}
    latitude = first_non_empty(item.get("latitude"), address.get("latitude") if isinstance(address, dict) else None)
    longitude = first_non_empty(item.get("longitude"), address.get("longitude") if isinstance(address, dict) else None)
    return latitude, longitude


def normalize_property_type(raw_type: str | None, feed_kind: str) -> str:
    value = (raw_type or "").lower()
    if "condo" in value:
        return "condo"
    if "town" in value:
        return "townhome"
    if "multi" in value or "duplex" in value or "triplex" in value:
        return "multi-family"
    if "land" in value or "lot" in value:
        return "land"
    if "commercial" in value:
        return "commercial"
    if feed_kind == "rental":
        return "rental"
    return "house"


def build_title(item: dict[str, Any], property_type: str, city: str | None, feed_kind: str) -> str:
    explicit = first_non_empty(item.get("formattedAddress"), item.get("address"), item.get("title"))
    if isinstance(explicit, str) and explicit.strip():
        if property_type == "rental":
            return f"Rental Listing in {city or MARKET_CITY}"
        if property_type == "condo":
            return f"Condo Listing in {city or MARKET_CITY}"
        return explicit

    bedrooms = first_non_empty(item.get("bedrooms"), item.get("beds"))
    if bedrooms:
        label = f"{bedrooms}BR"
    else:
        label = "Listing"

    if property_type == "rental":
        kind = "Rental"
    elif property_type == "condo":
        kind = "Condo"
    elif property_type == "townhome":
        kind = "Townhome"
    else:
        kind = "Home"
    return f"{label} {kind} in {city or MARKET_CITY}"


def normalize_listing(item: dict[str, Any], feed_kind: str) -> dict[str, Any]:
    provider_listing_id = str(first_non_empty(item.get("id"), item.get("listingId"), item.get("propertyId")))
    if not provider_listing_id or provider_listing_id == "None":
        raise RuntimeError(f"Missing listing id in RentCast item: {json.dumps(item)[:250]}")

    street, city, state, postal = extract_address(item)
    latitude, longitude = extract_coordinates(item)
    property_type = normalize_property_type(first_non_empty(item.get("propertyType"), item.get("type")), feed_kind)
    status = "rental-active" if feed_kind == "rental" else "active"
    price = first_non_empty(item.get("price"), item.get("listPrice"), item.get("rent"))
    beds = first_non_empty(item.get("bedrooms"), item.get("beds"))
    baths = first_non_empty(item.get("bathrooms"), item.get("baths"))
    sqft = first_non_empty(item.get("squareFootage"), item.get("sqft"))
    photo_url = extract_photo_url(item)
    listing_url = first_non_empty(
        item.get("listingUrl"),
        item.get("url"),
        item.get("propertyUrl"),
        item.get("mlsUrl"),
        f"https://www.rentcast.io/",
    )
    updated_at = first_non_empty(item.get("lastSeenDate"), item.get("updatedDate"), item.get("dateUpdated"))
    listed_at = first_non_empty(item.get("listedDate"), item.get("dateListed"), updated_at)

    return {
        "provider_name": PROVIDER_NAME,
        "provider_listing_id": provider_listing_id,
        "source_mls": first_non_empty(item.get("mlsName"), item.get("mlsNumber"), item.get("source")),
        "status": status,
        "property_type": property_type,
        "title": build_title(item, property_type, city, feed_kind),
        "street_address": street,
        "city": city or MARKET_CITY,
        "state": state or MARKET_STATE,
        "postal_code": postal,
        "latitude": latitude,
        "longitude": longitude,
        "price": price,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "description": item.get("description"),
        "primary_photo_url": photo_url,
        "photo_urls": [photo_url] if photo_url else [],
        "listing_url": listing_url,
        "broker_name": first_non_empty(item.get("brokerName"), item.get("officeName")),
        "agent_name": first_non_empty(item.get("agentName"), item.get("listingAgent")),
        "listed_at": listed_at,
        "updated_at": updated_at,
        "raw_payload": item,
    }


class SupabaseClient:
    def __init__(self, project_url: str, service_role_key: str) -> None:
        self.base = f"{project_url.rstrip('/')}{SUPABASE_REST_PATH}"
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Accept": "application/json",
        }

    def select(self, path: str, query: dict[str, str]) -> Any:
        return http_json(f"{self.base}/{path}?{urlencode(query)}", headers=self.headers)

    def insert_or_upsert(
        self,
        path: str,
        rows: list[dict[str, Any]],
        *,
        on_conflict: str | None = None,
    ) -> Any:
        query = ""
        if on_conflict:
            query = f"?{urlencode({'on_conflict': on_conflict})}"
        headers = {
            **self.headers,
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        return http_json(f"{self.base}/{path}{query}", method="POST", headers=headers, body=rows)

    def delete(self, path: str, query: dict[str, str]) -> Any:
        headers = {
            **self.headers,
            "Prefer": "return=representation",
        }
        return http_json(f"{self.base}/{path}?{urlencode(query)}", method="DELETE", headers=headers)


def fetch_miami_listings(days_old: int) -> list[dict[str, Any]]:
    common = {
        "city": MARKET_CITY,
        "state": MARKET_STATE,
        "status": "Active",
        "daysOld": str(days_old),
        "suppressLogging": "true",
    }
    sale_raw = rentcast_get("/listings/sale", {**common, "limit": str(SALE_LIMIT)})
    rental_raw = rentcast_get("/listings/rental/long-term", {**common, "limit": str(RENTAL_LIMIT)})

    normalized = [normalize_listing(item, "sale") for item in sale_raw]
    normalized.extend(normalize_listing(item, "rental") for item in rental_raw)

    deduped: dict[str, dict[str, Any]] = {}
    for listing in normalized:
        deduped[listing["provider_listing_id"]] = listing
    return list(deduped.values())


def ensure_market_id(client: SupabaseClient) -> str:
    rows = client.select("markets", {"select": "id", "slug": f"eq.{MARKET_SLUG}", "limit": "1"})
    if not rows:
        raise RuntimeError(f"Supabase market '{MARKET_SLUG}' not found")
    return rows[0]["id"]


def remove_market_links_for_provider(client: SupabaseClient, market_id: str, provider_name: str) -> None:
    rows = client.select(
        "listing_cards",
        {
            "select": "id,provider_name",
            "market_slug": f"eq.{MARKET_SLUG}",
            "provider_name": f"eq.{provider_name}",
        },
    )
    listing_ids = [row["id"] for row in rows if row.get("id")]
    if not listing_ids:
        return
    id_filter = "in.(" + ",".join(listing_ids) + ")"
    client.delete("listing_markets", {"market_id": f"eq.{market_id}", "listing_id": id_filter})
    if provider_name == MOCK_PROVIDER_NAME:
        client.delete("listings", {"id": id_filter, "provider_name": f"eq.{provider_name}"})


def write_to_supabase(listings: list[dict[str, Any]]) -> None:
    project_url = os.environ.get("SUPABASE_PROJECT_URL", DEFAULT_SUPABASE_URL)
    service_role_key = require_env("SUPABASE_SERVICE_ROLE_KEY")
    client = SupabaseClient(project_url, service_role_key)
    market_id = ensure_market_id(client)

    remove_market_links_for_provider(client, market_id, MOCK_PROVIDER_NAME)
    remove_market_links_for_provider(client, market_id, PROVIDER_NAME)

    upserted = client.insert_or_upsert("listings", listings, on_conflict="provider_name,provider_listing_id")
    listing_rows = [{"listing_id": row["id"], "market_id": market_id} for row in upserted if row.get("id")]
    if listing_rows:
        client.insert_or_upsert("listing_markets", listing_rows)


def print_summary(listings: list[dict[str, Any]], *, dry_run: bool) -> None:
    sale_count = sum(1 for item in listings if item["status"] == "active")
    rental_count = sum(1 for item in listings if item["status"] == "rental-active")
    print(f"Miami import prepared {len(listings)} listings ({sale_count} sale, {rental_count} rental).")
    print("Mode:", "dry-run only" if dry_run else "write to Supabase")
    for item in listings[:5]:
        print(f"- {item['title']} | {item.get('price') or 'n/a'} | {item.get('city')}, {item.get('state')}")


def maybe_write_preview(path: str | None, listings: list[dict[str, Any]]) -> None:
    if not path:
        return
    output = Path(path)
    output.write_text(json.dumps(listings, indent=2))
    print(f"Wrote preview JSON to {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Miami Area listings from RentCast into Supabase.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and normalize listings without writing to Supabase.")
    parser.add_argument("--days-old", type=int, default=DEFAULT_DAYS_OLD, help="Limit to listings no older than this many days.")
    parser.add_argument("--preview-json", help="Optional path to write normalized JSON for inspection.")
    return parser.parse_args()


def main() -> int:
    load_env_file(ENV_FILE)
    args = parse_args()

    listings = fetch_miami_listings(args.days_old)
    print_summary(listings, dry_run=args.dry_run)
    maybe_write_preview(args.preview_json, listings)

    if args.dry_run:
        return 0

    if not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        raise SystemExit(
            "SUPABASE_SERVICE_ROLE_KEY is not set. Add it to .env.local before writing to Supabase, "
            "or rerun with --dry-run."
        )

    write_to_supabase(listings)
    print("Supabase update complete for Miami Area.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise
