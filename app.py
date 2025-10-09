from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    """Initialize SQLite database."""
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

@app.route('/')
def index():
    """Render the main page with customer list."""
    try:
        with sqlite3.connect('crm.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM customers')
            customers = c.fetchall()
        return render_template('index.html', customers=customers)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/add', methods=['POST'])
def add_customer():
    """Add a new customer."""
    name = request.form.get('name').strip()
    email = request.form.get('email').strip()
    phone = request.form.get('phone').strip()
    company = request.form.get('company').strip()
    created_at = datetime.utcnow().isoformat()

    if not name or not email:
        return jsonify({'status': 'error', 'message': 'Name and email are required'})

    try:
        with sqlite3.connect('crm.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO customers (name, email, phone, company, created_at) VALUES (?, ?, ?, ?, ?)',
                      (name, email, phone, company, created_at))
            conn.commit()
        return jsonify({'status': 'success', 'message': 'Customer added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'Email already exists'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to add customer: {str(e)}'})

@app.route('/update/<int:id>', methods=['POST'])
def update_customer(id):
    """Update an existing customer."""
    name = request.form.get('name').strip()
    email = request.form.get('email').strip()
    phone = request.form.get('phone').strip()
    company = request.form.get('company').strip()

    if not name and not email and not phone and not company:
        return jsonify({'status': 'error', 'message': 'At least one field must be provided'})

    try:
        with sqlite3.connect('crm.db') as conn:
            c = conn.cursor()
            updates = []
            params = []
            if name:
                updates.append("name = ?")
                params.append(name)
            if email:
                updates.append("email = ?")
                params.append(email)
            if phone:
                updates.append("phone = ?")
                params.append(phone)
            if company:
                updates.append("company = ?")
                params.append(company)
            if not updates:
                return jsonify({'status': 'error', 'message': 'No fields to update'})

            params.append(id)
            c.execute(f"UPDATE customers SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
        return jsonify({'status': 'success', 'message': 'Customer updated successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'Email already exists'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to update customer: {str(e)}'})

@app.route('/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    """Delete a customer."""
    try:
        with sqlite3.connect('crm.db') as conn:
            c = conn.cursor()
            c.execute('DELETE FROM customers WHERE id = ?', (id,))
            conn.commit()
        return jsonify({'status': 'success', 'message': 'Customer deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to delete customer: {str(e)}'})

@app.route('/get/<int:id>')
def get_customer(id):
    """Get customer details by ID."""
    try:
        with sqlite3.connect('crm.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM customers WHERE id = ?', (id,))
            customer = c.fetchone()
            if customer:
                return jsonify({
                    'id': customer['id'],
                    'name': customer['name'],
                    'email': customer['email'],
                    'phone': customer['phone'],
                    'company': customer['company'],
                    'created_at': customer['created_at']
                })
            return jsonify({'status': 'error', 'message': 'Customer not found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to fetch customer: {str(e)}'})

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    app.run(debug=True)
