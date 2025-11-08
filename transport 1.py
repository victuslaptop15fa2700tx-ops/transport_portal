import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector as sql
import pandas as pd

# ---------- DATABASE CONNECTION ----------
mydb = sql.connect(
    host="localhost",
    user="root",
    password="Ayesha@2786",   
    database="transport"
)
mycursor = mydb.cursor()
print(" Database Connected Successfully!")


# ---------- MAIN APP ----------
clients = {}
class TransportApp(tk.Tk):
    def __init__(self):
        
        super().__init__()
        self.title("Transportation Management Portal")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")
        self.current_client = None
        self.show_home_page()

    # ---------- UTILITY ----------
    def clear(self):
        
        for w in self.winfo_children():
            w.destroy()

    # ---------- HOME PAGE ----------
    def show_home_page(self):
        
        self.clear()
        tk.Label(self, text=" Transportation Management Portal",
                 font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=20)
        tk.Button(self, text="Admin Login", width=25, command=self.show_admin_menu,
                  bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self, text="Client Login", width=25, command=self.client_login,
                  bg="#2196F3", fg="white").pack(pady=10)
        tk.Button(self, text="Exit", width=25, command=self.destroy,
                  bg="#f44336", fg="white").pack(pady=10)

    # ---------- ADMIN MENU ----------
    def show_admin_menu(self):
        
        self.clear()
        tk.Label(self, text="🛠 Admin Dashboard", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Button(self, text="Add Vehicle", width=25, command=self.add_vehicle).pack(pady=5)
        tk.Button(self, text="View Vehicles", width=25, command=self.view_vehicles).pack(pady=5)
        tk.Button(self, text="Add Client", width=25, command=self.add_client).pack(pady=5)
        tk.Button(self, text="View Clients", width=25, command=self.view_clients).pack(pady=5)
        tk.Button(self, text="Assign Vehicle", width=25, command=self.assign_vehicle).pack(pady=5)
        tk.Button(self, text="View All Bookings", width=25, command=self.view_bookings).pack(pady=5)
        tk.Button(self, text="Logout", width=25, command=self.show_home_page,
                  bg="#f44336", fg="white").pack(pady=10)

    # ---------- CLIENT LOGIN ----------
    def client_login(self):
        
        cid = simpledialog.askstring("Client Login", "Enter Client ID:")
        if not cid:
            return
        if cid in clients:
            self.current_client = cid
            self.show_client_menu(clients[cid]['name'])
        else:
            messagebox.showerror("Error", "Client not found. Contact Admin.")
    # ---------- CLIENT MENU ----------
    def show_client_menu(self, client_name):
        
        self.clear()
        tk.Label(self, text=f"👤 Welcome {client_name}", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Button(self, text="View Available Vehicles", width=25, command=self.view_vehicles).pack(pady=5)
        tk.Button(self, text="Request Transport", width=25, command=self.request_transport).pack(pady=5)
        tk.Button(self, text="My Bookings", width=25, command=self.my_bookings).pack(pady=5)
        tk.Button(self, text="Logout", width=25, command=self.show_home_page,
                  bg="#f44336", fg="white").pack(pady=10)

    # ---------- ADD CLIENT ----------
    def add_client(self):
        
        cid = simpledialog.askstring("Add Client", "Enter Client ID:")
        name = simpledialog.askstring("Add Client", "Enter Name:")
        contact = simpledialog.askstring("Add Client", "Enter Contact Number:")
        if cid and name:
            clients[cid] = {"name": name, "contact": contact}
            messagebox.showinfo("Success", "Client added successfully (stored in Python only).")
        else:
            messagebox.showwarning("Warning", "Client ID and Name required.")
    # ---------- VIEW CLIENTS ----------
    def view_clients(self):
        
        if not clients:
            messagebox.showinfo("Clients", "No clients found.")
            return
        info = "\n".join([f"ID: {cid}, Name: {data['name']}, Contact: {data['contact']}" 
                      for cid, data in clients.items()])
        messagebox.showinfo("All Clients", info)

    # ---------- ADD VEHICLE ----------
    def add_vehicle(self):
        
        vid = simpledialog.askstring("Add Vehicle", "Enter Vehicle ID:")
        vtype = simpledialog.askstring("Add Vehicle", "Vehicle Type (Bus/Truck/Car):")
        if vid and vtype:
            mycursor.execute(
                "INSERT INTO vehicles (vehicle_id, type, status) VALUES (%s, %s, %s)",
                (vid, vtype, "Available")
            )
            mydb.commit()
            messagebox.showinfo("Success", "Vehicle added successfully.")
        else:
            messagebox.showwarning("Warning", "Vehicle ID and Type required.")

    # ---------- VIEW VEHICLES ----------
    def view_vehicles(self):
        
        mycursor.execute("SELECT * FROM vehicles")
        rows = mycursor.fetchall()
        if rows:
            # Use pandas to construct the SAME output as before
            try:
                df = pd.DataFrame(rows, columns=["vehicle_id", "type", "status"])
                lines = df.apply(
                    lambda r: f"ID: {r['vehicle_id']}, Type: {r['type']}, Status: {r['status']}",
                    axis=1,
                ).tolist()
                info = "\n".join(lines)
            except Exception:
                info = "\n".join([f"ID: {r[0]}, Type: {r[1]}, Status: {r[2]}" for r in rows])
            messagebox.showinfo("All Vehicles", info)
        else:
            messagebox.showinfo("All Vehicles", "No vehicles found.")

    # ---------- ASSIGN VEHICLE ----------
    def assign_vehicle(self):
        cid = simpledialog.askstring("Assign Vehicle", "Client ID:")
        vid = simpledialog.askstring("Assign Vehicle", "Vehicle ID:")
        if not cid or not vid:
            return

        if cid not in clients:
            messagebox.showerror("Error", "Client not found in Python data.")
            return
        mycursor.execute("SELECT * FROM vehicles WHERE vehicle_id=%s", (vid,))
        if not mycursor.fetchone():
            messagebox.showerror("Error", "Vehicle not found.")
            return

        mycursor.execute("UPDATE vehicles SET status='Booked' WHERE vehicle_id=%s", (vid,))
        mycursor.execute("INSERT INTO bookings (client_id, vehicle_id) VALUES (%s, %s)", (cid, vid))
        mydb.commit()
        messagebox.showinfo("Success", "Vehicle assigned to client.")

    # ---------- VIEW BOOKINGS ----------
    def view_bookings(self):
        mycursor.execute("SELECT client_id, vehicle_id FROM bookings")
        rows = mycursor.fetchall()
        info = ""

        for r in rows:
            cid, vid = r
            name = clients[cid]["name"] if cid in clients else "Unknown (not in Python)"
            info += f"Client: {name} ({cid}) | Vehicle: {vid}\n"

        if info:
            messagebox.showinfo("All Bookings", info)
        else:
            messagebox.showinfo("All Bookings", "No bookings found.")

    # ---------- CLIENT: REQUEST TRANSPORT ----------
    def request_transport(self):
        
        mycursor.execute("SELECT vehicle_id FROM vehicles WHERE status='Available'")
        available = [r[0] for r in mycursor.fetchall()]
        if not available:
            messagebox.showinfo("Info", "No available vehicles right now.")
            return

        vid = simpledialog.askstring("Request Transport",
                                     f"Enter Vehicle ID from available: {available}")
        if vid in available:
            mycursor.execute("UPDATE vehicles SET status='Booked' WHERE vehicle_id=%s", (vid,))
            mycursor.execute("INSERT INTO bookings (client_id, vehicle_id) VALUES (%s, %s)",
                             (self.current_client, vid))
            mydb.commit()
            messagebox.showinfo("Success", "Vehicle booked successfully!")
        else:
            messagebox.showerror("Error", "Invalid Vehicle ID.")

    # ---------- CLIENT: MY BOOKINGS ----------
    def my_bookings(self):
        
        cid = self.current_client
        mycursor.execute("""
            SELECT vehicle_id FROM bookings WHERE client_id=%s
        """, (cid,))
        rows = mycursor.fetchall()
        info = "\n".join([f"Vehicle: {r[0]}" for r in rows])
        messagebox.showinfo("My Bookings", info if info else "No bookings yet.")


# ---------- RUN ----------
if __name__ == "__main__":
    try:
        app = TransportApp()
        app.mainloop()
    except Exception as e:
        print("Error:", e)
    finally:
        mycursor.close()
        mydb.close()
    
