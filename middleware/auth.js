require('dotenv').config();

function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.trim();

  if (!token || token !== process.env.FUR_PAT) {
    return res.status(401).json({ message: 'Unauthorized: Invalid PAT' });
  }

  next();
}

module.exports = authMiddleware;
