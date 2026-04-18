const express = require('express');
const cors = require('cors');
require('dotenv').config();
const db = require('./db');

const app = express();

app.use(cors()); // Permite que Vue (puerto 5173) hable con Node (puerto 3000)
app.use(express.json()); // Permite que el servidor entienda datos en formato JSON

// Ruta de prueba: http://localhost:3000/
app.get('/', (req, res) => {
    res.send('Servidor de Mercadillos en Casa (MEC) funcionando 🚀');
});

// Obtener eventos
app.get('/api/eventos', async (req, res) => {
    try {
        const query = `
            SELECT e.*, c.nombre as categoria_nombre, c.color_hex 
            FROM eventos e 
            JOIN categorias c ON e.id_categoria = c.id_categoria
        `;
        const [rows] = await db.query(query);
        res.json(rows);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Crear un evento
app.post('/api/eventos', async (req, res) => {
    const { id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin } = req.body;
    
    try {
        const query = `INSERT INTO eventos (id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`;
        
        const [result] = await db.query(query, [id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin]);
        
        res.status(201).json({ message: 'Evento creado con éxito', id: result.insertId });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Borrar evento por id 
app.delete('/api/eventos/:id', async (req, res) => {
    const { id } = req.params;
    try {
        await db.query('DELETE FROM eventos WHERE id_evento = ?', [id]);
        res.json({ message: 'Evento eliminado correctamente' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});
// Obtener categorias 
app.get('/api/categorias', async (req, res) => {
    try {
        const [rows] = await db.query('SELECT * FROM categorias');
        res.json(rows);
    } catch (error) {
        res.status(500).json({ error: 'Error al obtener categorías: ' + error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Servidor MEC corriendo en http://localhost:${PORT}`);
});