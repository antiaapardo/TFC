const mysql = require('mysql2');
require('dotenv').config();

const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

const promisePool = pool.promise();

async function testConnection() {
    try {
        const [rows] = await promisePool.query('SELECT "Conexión exitosa" as mensaje');
        console.log('✅ Base de Datos conectada:', rows[0].mensaje);
    } catch (error) {
        console.error('❌ Error conectando a la base de datos:', error.message);
    }
}

testConnection();

module.exports = promisePool;