const http = require('http');

const hostname = '0.0.0.0';
const port = 3000;

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  // Указываем UTF-8
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end('<h1>Привет, мир!</h1>');
});

server.listen(port, hostname, () => {
  console.log(`Сервер запущен на http://${hostname}:${port}/`);
});
