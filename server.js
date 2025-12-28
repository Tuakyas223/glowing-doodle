const https = require('https');
const fs = require('fs');
const path = require('path');

const hostname = '0.0.0.0';
const port = 3001;

// Читаем сертификаты
const options = {
  key: fs.readFileSync(path.join(__dirname, 'server.key')),
  cert: fs.readFileSync(path.join(__dirname, 'server.cert'))
};

// Читаем HTML файл
const htmlFilePath = path.join(__dirname, 'index.html');
const htmlContent = fs.readFileSync(htmlFilePath, 'utf-8');

const server = https.createServer(options, (req, res) => {
  res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
  res.end(htmlContent);
});

server.listen(port, hostname, () => {
  console.log(`HTTPS сервер запущен на https://${hostname}:${port}/`);
});

