const express = require("express");
const app = express();

app.use(express.json());

const clients = new Map();
const HEARTBEAT_TIMEOUT = 10_000;

// heartbeat
app.post("/heartbeat", (req, res) => {
  const { id } = req.body;
  if (!id) return res.sendStatus(400);

  clients.set(id, Date.now());
  res.sendStatus(200);
});

// сайт
app.get("/", (req, res) => {
  const now = Date.now();

  let online = 0;
  for (const [_, last] of clients) {
    if (now - last < HEARTBEAT_TIMEOUT) online++;
  }

  res.send(`
    <html>
      <body style="
        margin:0;
        background:black;
        color:white;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:64px;
        font-family:Arial;
      ">
        Online: ${online}
      </body>
    </html>
  `);
});

app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});
