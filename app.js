const express = require('express');
const app = express();
const authMiddleware = require('./middleware/auth');
require('dotenv').config();

app.use(express.json());

app.get('/', (req, res) => {
  res.send('Willkommen bei MATRIX GPT API');
});

app.get('/matrix-gpt', authMiddleware, (req, res) => {
  res.json({ message: 'Zugriff erfolgreich: MATRIX GPT ist authentifiziert' });
});

const PORT = process.env.PORT2 || 3000;
app.listen(PORT, () => console.log(`Server läuft auf Port ${PORT}`));
