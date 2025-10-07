from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    with sqlite3.connect('crm.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS customers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      email TEXT UNIQUE NOT NULL,
                      phone TEXT,
                      company TEXT,
                      created_at TEXT)''')
        conn.commit()

# Helper function to convert database rows to dictionaries
def row_to_dict(row):
    return {
        'id': row[0],
        'name': row[1],
        'email': row[2],
        'phone': row[3],
        'company': row[4],
        'created_at': row[5]
    }

# Create a new customer
@app.route('/api/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'email']):
            return jsonify({'error': 'Name and email are required'}), 400

        name = data['name']
        email = data['email']
        phone = data.get('phone', '')
        company = data.get('company', '')
        created_at = datetime.utcnow().isoformat()

        with sqlite3.connect('crm.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO customers (name, email, phone, company, created_at) VALUES (?, ?, ?, ?, ?)',
                      (name, email, phone, company, created_at))
            conn.commit()
            customer_id = c.lastrowid

        return jsonify({
            'id': customer_id,
            'name': name,
            'email': email,
            'phone': phone,
            'company': company,
            'created_at': created_at
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all customers or a specific customer by ID
@app.route('/api/customers', methods=['GET'])
@app.route('/api/customers/<int:id>', methods=['GET'])
def get_customers(id=None):
    try:
        with sqlite3.connect('crm.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            if id:
                c.execute('SELECT * FROM customers WHERE id = ?', (id,))
                row = c.fetchone()
                if not row:
                    return jsonify({'error': 'Customer not found'}), 404
                return jsonify(row_to_dict(row)), 200
            else:
                c.execute('SELECT * FROM customers')
                rows = c.fetchall()
                return jsonify([row_to_dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a customer
@app.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        with sqlite3.connect('crm.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM customers WHERE id = ?', (id,))
            if not c.fetchone():
                return jsonify({'error': 'Customer not found'}), 404

            updates = []
            params = []
            for key in ['name', 'email', 'phone', 'company']:
                if key in data:
                    updates.append(f"{key} = ?")
                    params.append(data[key])
            if not updates:
                return jsonify({'error': 'No valid fields to update'}), 400

            params.append(id)
            c.execute(f"UPDATE customers SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

            c.execute('SELECT * FROM customers WHERE id = ?', (id,))
            row = c.fetchone()
            return jsonify(row_to_dict(row)), 200
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a customer
@app.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    try:
        with sqlite3.connect('crm.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM customers WHERE id = ?', (id,))
            if not c.fetchone():
                return jsonify({'error': 'Customer not found'}), 404

            c.execute('DELETE FROM customers WHERE id = ?', (id,))
            conn.commit()
            return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
