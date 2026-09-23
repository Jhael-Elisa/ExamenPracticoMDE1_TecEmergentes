const express = require('express');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

const PORT = process.env.API_PORT || 3000;

// Conexión a PostgreSQL usando el nombre del servicio "postgres" (no localhost)
const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'postgres',
  port: parseInt(process.env.POSTGRES_PORT) || 5432,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB,
});

// Crear la tabla users si no existe (con reintentos por si Postgres aún no está listo)
async function initDB() {
  const createTable = `
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      email VARCHAR(100) NOT NULL UNIQUE
    );
  `;
  let retries = 10;
  while (retries > 0) {
    try {
      await pool.query(createTable);
      console.log('✅ Tabla users lista');
      return;
    } catch (err) {
      console.log(`⏳ Esperando a PostgreSQL... (${retries} intentos restantes)`);
      retries--;
      await new Promise(r => setTimeout(r, 3000));
    }
  }
  console.error('❌ No se pudo conectar a PostgreSQL');
}

// Endpoint /health
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Endpoint GET /users
app.get('/users', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM users ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

// Endpoint POST /users
app.post('/users', async (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'name y email son requeridos' });
  }
  try {
    const result = await pool.query(
      'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
      [name, email]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, async () => {
  console.log(`🚀 API escuchando en puerto ${PORT}`);
  await initDB();
});