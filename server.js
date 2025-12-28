const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = 3000;

app.use(express.static(path.join(__dirname, 'public')));

let drawingHistory = [];

io.on('connection', (socket) => {
  console.log('Новый пользователь подключился');

  // История линий
  socket.emit('drawingHistory', drawingHistory);

  // Линии рисования
  socket.on('drawing', (data) => {
    drawingHistory.push(data);
    socket.broadcast.emit('drawing', data);
  });

  // Чат
  socket.on('chatMessage', (msg) => {
    io.emit('chatMessage', msg); // рассылаем всем
  });

  socket.on('disconnect', () => console.log('Пользователь отключился'));
});

server.listen(PORT, () => {
  console.log(`Сервер запущен на http://0.0.0.0:${PORT}`);
});
