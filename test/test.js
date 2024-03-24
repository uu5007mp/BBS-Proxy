//bun test.jsで実行できるはず...

const http = require('http');
const url = require('url');
const bun = require('bun');
const fs = require('fs').promises;

const PORT = 3000;

const server = http.createServer(async (req, res) => {
  const { pathname, query } = url.parse(req.url, true);
  const targetUrl = query.requesturl;

  if (!targetUrl) {
    res.statusCode = 400;
    res.end('URL parameter is required');
    return;
  }

  try {
    const response = await bun.fetch(targetUrl);
    const contentType = response.headers.get('content-type');
    res.writeHead(response.status, { 'Content-Type': contentType + '; charset=utf-8' });

    if (contentType && contentType.includes('text/html')) {
      let html = await response.text();
      html = html.replace(/<img[^>]+src="([^">]+)"/g, (match, group1) => {
        const imageUrl = new URL(group1, targetUrl);
        return match.replace(group1, `/proxy?requesturl=${encodeURIComponent(imageUrl)}`);
      });
      html = html.replace(/<a[^>]+href="([^">]+)"/g, (match, group1) => {
        const linkUrl = new URL(group1, targetUrl);
        return match.replace(group1, `/proxy?requesturl=${encodeURIComponent(linkUrl)}`);
      });

      res.end(html);
    } else {
      response.body.pipe(res);
    }
  } catch (err) {
    res.statusCode = 500;
    res.end(`Error fetching URL: ${err.message}`);
  }
});

server.listen(PORT, () => {
  console.log(`Proxy server running at http://localhost:${PORT}`);
});
