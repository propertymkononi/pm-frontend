const express = require('express');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Database setup
const db = new sqlite3.Database(':memory:'); // Using an in-memory database for simplicity

// Create the tenants table
db.run(`
    CREATE TABLE tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenantName TEXT,
        houseNumber TEXT,
        phoneNumber TEXT,
        apartment TEXT,
        rentStatus TEXT,
        tenancyDuration TEXT,
        houseCondition TEXT,
        leaseDate TEXT
    )
`);

// Add a new tenant
app.post('/tenants', (req, res) => {
    const {
        tenantName, houseNumber, phoneNumber, apartment, 
        rentStatus, tenancyDuration, houseCondition, leaseDate
    } = req.body;

    const query = `
        INSERT INTO tenants (tenantName, houseNumber, phoneNumber, apartment, rentStatus, tenancyDuration, houseCondition, leaseDate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `;
    const values = [tenantName, houseNumber, phoneNumber, apartment, rentStatus, tenancyDuration, houseCondition, leaseDate];

    db.run(query, values, function (err) {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.status(201).json({ id: this.lastID });
    });
});

// Get all tenants
app.get('/tenants', (_req, res) => {
    db.all('SELECT * FROM tenants', [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

// Update a tenant
app.put('/tenants/:id', (req, res) => {
    const { id } = req.params;
    const {
        tenantName, houseNumber, phoneNumber, apartment, 
        rentStatus, tenancyDuration, houseCondition, leaseDate
    } = req.body;

    const query = `
        UPDATE tenants
        SET tenantName = ?, houseNumber = ?, phoneNumber = ?, apartment = ?, rentStatus = ?, tenancyDuration = ?, houseCondition = ?, leaseDate = ?
        WHERE id = ?
    `;
    const values = [tenantName, houseNumber, phoneNumber, apartment, rentStatus, tenancyDuration, houseCondition, leaseDate, id];

    db.run(query, values, function (err) {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ updated: this.changes });
    });
});

// Delete a tenant
app.delete('/tenants/:id', (req, res) => {
    const { id } = req.params;
    const query = 'DELETE FROM tenants WHERE id = ?';

    db.run(query, id, function (err) {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ deleted: this.changes });
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
