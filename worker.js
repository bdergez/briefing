export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith('/api/reddit/')) {
      return handleRedditApi(request, url);
    }

    return env.ASSETS.fetch(request);
  },
};

async function handleRedditApi(request, url) {
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: corsHeaders(request.headers.get('Origin')),
    });
  }

  let upstreamUrl = null;

  if (url.pathname === '/api/reddit/churning-hot') {
    upstreamUrl = new URL('https://www.reddit.com/r/churning/hot.json');
    upstreamUrl.searchParams.set('limit', '50');
    upstreamUrl.searchParams.set('raw_json', '1');
  } else if (url.pathname.startsWith('/api/reddit/comments/')) {
    const postId = url.pathname.split('/').pop();
    if (!postId) return jsonError('Missing post id', 400);
    upstreamUrl = new URL(`https://www.reddit.com/r/churning/comments/${encodeURIComponent(postId)}.json`);
    upstreamUrl.searchParams.set('limit', url.searchParams.get('limit') || '25');
    upstreamUrl.searchParams.set('sort', url.searchParams.get('sort') || 'top');
    upstreamUrl.searchParams.set('raw_json', '1');
    upstreamUrl.searchParams.set('depth', url.searchParams.get('depth') || '1');
  } else if (url.pathname.startsWith('/api/reddit/sub/')) {
    const subId = url.pathname.split('/').pop();
    if (!subId) return jsonError('Missing subreddit id', 400);
    upstreamUrl = new URL(`https://www.reddit.com/r/${encodeURIComponent(subId)}/hot.json`);
    upstreamUrl.searchParams.set('limit', url.searchParams.get('limit') || '50');
    upstreamUrl.searchParams.set('raw_json', '1');
  } else {
    return jsonError('Unknown endpoint', 404);
  }

  const headers = {
    Accept: 'application/json',
    'User-Agent': 'PMDash/1.0 (+https://pmdash.evrolab.net)',
  };
  const body = await fetchRedditJson(upstreamUrl.toString(), headers);
  if (!body) return jsonError('Upstream fetch failed', 502, request.headers.get('Origin'));

  return new Response(body, {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=UTF-8',
      'cache-control': 'no-store',
      ...corsHeaders(request.headers.get('Origin')),
    },
  });
}

async function fetchRedditJson(url, headers) {
  const strategies = [
    async () => {
      const response = await fetch(url, { headers });
      if (!response.ok) throw new Error(`Direct failed: ${response.status}`);
      return response.text();
    },
    async () => {
      const response = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`);
      if (!response.ok) throw new Error(`AllOrigins failed: ${response.status}`);
      const wrapper = await response.json();
      return wrapper.contents;
    },
    async () => {
      const response = await fetch(`https://corsproxy.io/?${encodeURIComponent(url)}`);
      if (!response.ok) throw new Error(`Corsproxy failed: ${response.status}`);
      return response.text();
    },
    async () => {
      const response = await fetch(`https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`);
      if (!response.ok) throw new Error(`Codetabs failed: ${response.status}`);
      return response.text();
    },
  ];

  for (const strategy of strategies) {
    try {
      return await strategy();
    } catch (error) {
      // try the next fallback
    }
  }

  return null;
}

function jsonError(message, status, origin) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: {
      'content-type': 'application/json; charset=UTF-8',
      'cache-control': 'no-store',
      ...corsHeaders(origin),
    },
  });
}

function corsHeaders(origin = '*') {
  return {
    'access-control-allow-origin': origin || '*',
    'access-control-allow-methods': 'GET, OPTIONS',
    'access-control-allow-headers': 'Content-Type',
    vary: 'Origin',
  };
}
