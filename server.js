const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, 'public')));

let drawHistory = [];
let chatHistory = [];
let users = {};

io.on('connection', socket => {

  socket.on('join', nick => {
    users[socket.id] = nick;
    socket.emit('drawHistory', drawHistory);
    socket.emit('chatHistory', chatHistory);
    io.emit('system', `${nick} вошёл`);
  });

  socket.on('draw', data => {
    drawHistory.push(data);
    socket.broadcast.emit('draw', data);
  });

  socket.on('cursor', data => {
    socket.broadcast.emit('cursor', {
      id: socket.id,
      nick: users[socket.id],
      ...data
    });
  });

  socket.on('chat', text => {
    const msg = { nick: users[socket.id], text };
    chatHistory.push(msg);
    io.emit('chat', msg);
  });

  socket.on('disconnect', () => {
    io.emit('removeCursor', socket.id);
    if (users[socket.id]) {
      io.emit('system', `${users[socket.id]} вышел`);
      delete users[socket.id];
    }
  });
});

server.listen(3000, () => {
  console.log('http://0.0.0.0:3000');
});
