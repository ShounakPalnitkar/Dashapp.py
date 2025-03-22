require('dotenv').config();  // To load environment variables from the .env file
const express = require('express');
const { Pool } = require('pg');  // PostgreSQL client for Node.js
const cors = require('cors');    // CORS for cross-origin requests

const app = express();
const port = process.env.PORT || 3000;  // Use Render's assigned port or default to 3000

// Set up PostgreSQL connection using pg library
const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

// Test database connection
pool.connect()
  .then(() => console.log('Connected to the database'))
  .catch((err) => console.error('Error connecting to the database', err.stack));

// Middleware to handle JSON data
app.use(express.json());
app.use(cors());  // Enable CORS

// API endpoint to fetch data from the database
app.get('/api/data', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM your_table_name');  // Replace with your table name
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send('Database query error');
  }
});

// Additional endpoint to handle POST requests (example)
app.post('/api/data', async (req, res) => {
  try {
    const { name, age } = req.body;  // Example data to insert
    const result = await pool.query('INSERT INTO your_table_name (name, age) VALUES ($1, $2) RETURNING *', [name, age]);
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).send('Error inserting data');
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});