const ALLOWED_FEED_HOSTS = new Set([
  '10xtravel.com',
  'awardwallet.com',
  'boardingarea.com',
  'doctorofcredit.com',
  'frequentmiler.com',
  'loyaltylobby.com',
  'milestomemories.com',
  'newsroom.hyatt.com',
  'onemileatatime.com',
  'thepointsguy.com',
  'thriftytraveler.com',
  'upgradedpoints.com',
  'viewfromthewing.com',
  'nextcard.com',
]);

function isAllowedFeedHost(hostname) {
  const normalized = hostname.toLowerCase();
  const bareHostname = normalized.startsWith('www.') ? normalized.slice(4) : normalized;
  return ALLOWED_FEED_HOSTS.has(normalized) || ALLOWED_FEED_HOSTS.has(bareHostname);
}

function jsonError(message, status, details = {}) {
  return Response.json(
    { error: message, ...details },
    {
      status,
      headers: {
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
      },
    },
  );
}

function getAllowedTarget(request) {
  const requestUrl = new URL(request.url);
  const rawTarget = requestUrl.searchParams.get('url');
  if (!rawTarget) return { error: jsonError('Missing url parameter', 400) };

  let target;
  try {
    target = new URL(rawTarget);
  } catch {
    return { error: jsonError('Invalid target URL', 400) };
  }

  const hasUnsafeAuthority = target.username || target.password || (target.port && target.port !== '443');
  if (target.protocol !== 'https:' || hasUnsafeAuthority) {
    return { error: jsonError('Only standard HTTPS feed URLs are allowed', 400) };
  }
  if (!isAllowedFeedHost(target.hostname)) {
    return { error: jsonError('Feed host is not allowed', 403) };
  }

  return { target };
}

async function fetchAllowedFeed(request) {
  if (request.method !== 'GET') {
    return new Response('Method not allowed', { status: 405, headers: { Allow: 'GET' } });
  }

  const { target, error } = getAllowedTarget(request);
  if (error) return error;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  try {
    const upstream = await fetch(target.toString(), {
      headers: {
        Accept: 'application/rss+xml, application/xml, text/xml, text/html;q=0.9, */*;q=0.8',
      },
      redirect: 'follow',
      signal: controller.signal,
      cf: {
        cacheEverything: true,
        cacheTtl: 300,
      },
    });

    const finalHost = new URL(upstream.url).hostname.toLowerCase();
    if (!isAllowedFeedHost(finalHost)) {
      return jsonError('Feed redirected to a host that is not allowed', 502);
    }
    if (!upstream.ok) {
      return jsonError('Feed source returned an error', 502, { upstreamStatus: upstream.status });
    }

    const headers = new Headers({
      'Cache-Control': 'public, max-age=120, s-maxage=300',
      'X-Content-Type-Options': 'nosniff',
      'X-PMDash-Feed-Host': finalHost,
    });
    headers.set('Content-Type', upstream.headers.get('Content-Type') || 'text/plain; charset=utf-8');

    return new Response(upstream.body, { status: 200, headers });
  } catch (fetchError) {
    const timedOut = fetchError?.name === 'AbortError';
    return jsonError(timedOut ? 'Feed source timed out' : 'Feed source could not be reached', timedOut ? 504 : 502);
  } finally {
    clearTimeout(timeout);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/api/health') {
      return Response.json(
        { status: 'ok', service: 'pmdash-feed-relay' },
        { headers: { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } },
      );
    }
    if (url.pathname === '/api/fetch') return fetchAllowedFeed(request);
    if (url.pathname.startsWith('/api/')) return jsonError('API route not found', 404);

    return env.ASSETS.fetch(request);
  },
};
