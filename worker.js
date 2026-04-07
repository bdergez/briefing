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

  const response = await fetch(upstreamUrl.toString(), { headers });
  const body = await response.text();

  return new Response(body, {
    status: response.status,
    headers: {
      'content-type': 'application/json; charset=UTF-8',
      'cache-control': 'no-store',
      ...corsHeaders(request.headers.get('Origin')),
    },
  });
}

function jsonError(message, status) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: {
      'content-type': 'application/json; charset=UTF-8',
      'cache-control': 'no-store',
      ...corsHeaders(),
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
