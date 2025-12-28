const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = 3000;

app.use(express.static(path.join(__dirname, 'public')));

// Массив для хранения всех линий
let drawingHistory = [];

io.on('connection', (socket) => {
  console.log('Новый пользователь подключился');

  // Отправляем историю новому клиенту
  socket.emit('drawingHistory', drawingHistory);

  socket.on('drawing', (data) => {
    drawingHistory.push(data); // Сохраняем линию
    socket.broadcast.emit('drawing', data); // Шлем всем остальным
  });

  socket.on('disconnect', () => {
    console.log('Пользователь отключился');
  });
});

server.listen(PORT, () => {
  console.log(`Сервер запущен на http://0.0.0.0:${PORT}`);
});
