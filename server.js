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
let chatHistory = [];
let users = {}; // socket.id -> nickname

io.on('connection', (socket) => {

  socket.on('join', (nickname) => {
    users[socket.id] = nickname;

    socket.emit('drawingHistory', drawingHistory);
    socket.emit('chatHistory', chatHistory);

    io.emit('systemMessage', `${nickname} вошёл`);
  });

  socket.on('drawing', (data) => {
    drawingHistory.push(data);
    socket.broadcast.emit('drawing', data);
  });

  socket.on('cursor', (data) => {
    socket.broadcast.emit('cursor', {
      id: socket.id,
      nick: users[socket.id],
      x: data.x,
      y: data.y
    });
  });

  socket.on('chatMessage', (text) => {
    const msg = {
      nick: users[socket.id],
      text,
      time: Date.now()
    };
    chatHistory.push(msg);
    io.emit('chatMessage', msg);
  });

  socket.on('disconnect', () => {
    const nick = users[socket.id];
    delete users[socket.id];
    if (nick) io.emit('systemMessage', `${nick} вышел`);
  });
});

server.listen(PORT, () => {
  console.log(`http://0.0.0.0:${PORT}`);
});
