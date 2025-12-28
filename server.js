const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = 3000;

// Раздаем статические файлы из папки public
app.use(express.static(path.join(__dirname, 'public')));

io.on('connection', (socket) => {
  console.log('Новый пользователь подключился');

  // Получаем рисование от одного клиента и шлем всем остальным
  socket.on('drawing', (data) => {
    socket.broadcast.emit('drawing', data);
  });

  socket.on('disconnect', () => {
    console.log('Пользователь отключился');
  });
});

server.listen(PORT, () => {
  console.log(`Сервер запущен на http://0.0.0.0:${PORT}`);
});
