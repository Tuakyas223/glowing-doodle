const https = require('https');
const fs = require('fs');

const hostname = '0.0.0.0';
const port = 3001;

// Читаем сертификаты
const options = {
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.cert')
};

const server = https.createServer(options, (req, res) => {
  res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
  res.end('<h1>Привет, мир через HTTPS!</h1>');
});

server.listen(port, hostname, () => {
  console.log(`HTTPS сервер запущен на https://${hostname}:${port}/`);
});
