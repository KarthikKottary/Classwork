import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class CRMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Relationship Management")
        self.root.geometry("800x600")

        # Initialize database
        self.init_db()

        # GUI Components
        self.create_widgets()

    def init_db(self):
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

    def create_widgets(self):
        """Create GUI widgets."""
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Customer Details", padding=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Input Fields
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = ttk.Entry(input_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.phone_entry = ttk.Entry(input_frame)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Company:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.company_entry = ttk.Entry(input_frame)
        self.company_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Customer", command=self.add_customer).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Update Customer", command=self.update_customer).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Customer", command=self.delete_customer).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).grid(row=0, column=3, padx=5)

        # Customer List
        tree_frame = ttk.LabelFrame(self.root, text="Customers", padding=10)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Email", "Phone", "Company", "Created At"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Company", text="Company")
        self.tree.heading("Created At", text="Created At")
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Phone", width=100)
        self.tree.column("Company", width=150)
        self.tree.column("Created At", width=150)
        self.tree.pack(fill="both", expand=True)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Load customers
        self.load_customers()

    def load_customers(self):
        """Load customers into Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            with sqlite3.connect('crm.db') as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('SELECT * FROM customers')
                for row in c.fetchall():
                    self.tree.insert("", "end", values=(row['id'], row['name'], row['email'], row['phone'], row['company'], row['created_at']))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")

    def add_customer(self):
        """Add a new customer."""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        company = self.company_entry.get().strip()
        created_at = datetime.utcnow().isoformat()

        if not name or not email:
            messagebox.showerror("Error", "Name and email are required")
            return

        try:
            with sqlite3.connect('crm.db') as conn:
                c = conn.cursor()
                c.execute('INSERT INTO customers (name, email, phone, company, created_at) VALUES (?, ?, ?, ?, ?)',
                          (name, email, phone, company, created_at))
                conn.commit()
            self.load_customers()
            self.clear_fields()
            messagebox.showinfo("Success", "Customer added successfully")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add customer: {str(e)}")

    def update_customer(self):
        """Update selected customer."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a customer to update")
            return

        customer_id = self.tree.item(selected[0])['values'][0]
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        company = self.company_entry.get().strip()

        if not name and not email and not phone and not company:
            messagebox.showerror("Error", "At least one field must be provided")
            return

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
                    return

                params.append(customer_id)
                c.execute(f"UPDATE customers SET {', '.join(updates)} WHERE id = ?", params)
                conn.commit()
            self.load_customers()
            self.clear_fields()
            messagebox.showinfo("Success", "Customer updated successfully")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update customer: {str(e)}")

    def delete_customer(self):
        """Delete selected customer."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a customer to delete")
            return

        customer_id = self.tree.item(selected[0])['values'][0]
        try:
            with sqlite3.connect('crm.db') as conn:
                c = conn.cursor()
                c.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
                conn.commit()
            self.load_customers()
            self.clear_fields()
            messagebox.showinfo("Success", "Customer deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")

    def clear_fields(self):
        """Clear input fields."""
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.company_entry.delete(0, tk.END)

    def on_select(self, event):
        """Populate fields when a customer is selected."""
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.clear_fields()
            self.name_entry.insert(0, values[1])
            self.email_entry.insert(0, values[2])
            self.phone_entry.insert(0, values[3])
            self.company_entry.insert(0, values[4])

if __name__ == "__main__":
    root = tk.Tk()
    app = CRMApp(root)
    root.mainloop()
