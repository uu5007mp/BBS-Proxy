const http = require('http');
const url = require('url');
const bun = require('bun');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const PORT = 3000;

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB

const server = http.createServer(async (req, res) => {
  const { pathname, query } = url.parse(req.url, true);

  if (pathname === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <html>
      <head>
        <title>Proxy Server</title>
        <style>
          body { font-family: Arial, sans-serif; }
          input { padding: 5px; margin-right: 10px; }
          button { padding: 5px 10px; }
        </style>
      </head>
      <body>
        <h1>Enter URL to Proxy:</h1>
        <form action="/proxy" method="get">
          <input type="text" name="requesturl" placeholder="Enter URL" style="width: 400px;">
          <button type="submit">Proxy</button>
        </form>
      </body>
      </html>
    `);
    return;
  }

  if (pathname === '/proxy') {
    const targetUrl = query.requesturl;

    if (!targetUrl) {
      res.statusCode = 400;
      res.end('URL parameter is required');
      return;
    }

    try {
      const response = await bun.fetch(targetUrl);
      const contentType = response.headers.get('content-type');
      res.writeHead(response.status, {
        'Content-Type': contentType + '; charset=utf-8',
        'Access-Control-Allow-Origin': '*', // CORSをすべて許可
      });

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

        html = html.replace(/<link[^>]+href="([^">]+)"/g, (match, group1) => {
          const cssUrl = new URL(group1, targetUrl);
          return match.replace(group1, `/proxy?requesturl=${encodeURIComponent(cssUrl)}`);
        });

        html = html.replace(/<script[^>]+src="([^">]+)"/g, (match, group1) => {
          const scriptUrl = new URL(group1, targetUrl);
          return match.replace(group1, `/proxy?requesturl=${encodeURIComponent(scriptUrl)}`);
        });

        res.end(html);
      } else {
        if (response.headers.get('content-length') <= MAX_FILE_SIZE_BYTES) {
          const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), '/log/'));
          const filePath = path.join(tempDir, 'file');
          const fileStream = fs.createWriteStream(filePath);

          response.body.pipe(fileStream);

          response.body.on('end', () => {
            res.end('File downloaded successfully');
          });

          response.body.on('error', (err) => {
            console.error('Error downloading file:', err);
            res.statusCode = 500;
            res.end('Error downloading file');
          });
        } else {
          res.statusCode = 400;
          res.end('File size exceeds maximum limit');
        }
      }
    } catch (err) {
      res.statusCode = 500;
      res.end(`Error fetching URL: ${err.message}`);
    }
  }
});

server.listen(PORT, () => {
  console.log(`Proxy server running at http://localhost:${PORT}`);
});
