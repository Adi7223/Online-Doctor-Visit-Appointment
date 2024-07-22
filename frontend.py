import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests
from tkcalendar import DateEntry
from datetime import datetime
import logging

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Appointment Booking System")
        self.root.geometry("1600x800")
        self.root.resizable(True, True)
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Fjalla One", 20))
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("TEntry", font=("Arial", 22))
        self.history = []  # Stack to keep track of navigation history

        self.image = Image.open('doctor.jpg')
        self.image_resized = self.image.resize((1600, 800))
        self.photo = ImageTk.PhotoImage(self.image_resized)

        self.background_label = tk.Label(self.root, image=self.photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.back_button = ttk.Button(self.root, text="⏪", command=self.go_back, width=5, style="TButton")
        self.back_button.place(relx=0.01, rely=0.01, anchor='nw')
        self.back_button.lower()

        self.create_initial_ui()

        # Configure logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def go_back(self):
        if self.history:
            self.clear_frame()
            previous_frame = self.history.pop()
            previous_frame()

            if self.history:
                self.back_button.lift()
            else:
                self.back_button.lower()

    def create_initial_ui(self):
        self.clear_frame()
        self.initial_frame = ttk.Frame(self.root, padding=10)
        self.initial_frame.place(relx=0.5, rely=0.5, anchor='center')
        welcome_label = ttk.Label(self.initial_frame, text="🩺 Welcome to the Appointment Booking System 🩺")
        welcome_label.config(font=("Fjalla One", 24))
        welcome_label.pack(pady=30)
        self.style.configure("TButton.Font.TButton", font=("Arial Narrow", 16,))
        ttk.Button(self.initial_frame, text="Login", command=self.create_login_ui, style="TButton.Font.TButton").pack(pady=30)
        ttk.Button(self.initial_frame, text="Sign Up", command=self.create_signup_ui, style="TButton.Font.TButton").pack(pady=30)

        self.back_button.lower()

    def create_login_ui(self):
        self.history.append(self.create_initial_ui)
        self.clear_frame()

        welcome_label = ttk.Label(self.root, text="Login Page")
        welcome_label.config(font=("Fjalla One", 25))
        welcome_label.pack(pady=50)

        ttk.Label(self.root, text="Username:", font=('Calibri 19 bold')).pack()
        self.username_entry = ttk.Entry(self.root, width=40)
        self.username_entry.pack(padx=10, pady=30)

        ttk.Label(self.root, text="Password:", font=('Calibri 19 bold')).pack()
        self.password_entry = ttk.Entry(self.root, show='*', width=40)
        self.password_entry.pack(padx=10, pady=30)

        ttk.Button(self.root, text="Login", command=self.login, style="TButton.Font.TButton").pack(pady=10)

        self.back_button.lift()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        logging.info(f"Logging in user: {username}")
        response = requests.post('http://127.0.0.1:5000/login', json={"username": username, "password": password})
        if response.status_code == 200:
            logging.info("Login successful")
            self.history.clear()
            self.create_dashboard()
        else:
            logging.error("Login failed")
            messagebox.showerror("Error", "Invalid credentials")

    def create_signup_ui(self):
        self.history.append(self.create_initial_ui)
        self.clear_frame()

        welcome_label = ttk.Label(self.root, text="Sign Up Page")
        welcome_label.config(font=("Fjalla One", 25))
        welcome_label.pack(pady=50)

        ttk.Label(self.root, text="Username:", font=('Calibri 19 bold')).pack()
        self.signup_username_entry = ttk.Entry(self.root, width=40)
        self.signup_username_entry.pack(padx=10, pady=30)

        ttk.Label(self.root, text="Password:", font=('Calibri 19 bold')).pack()
        self.signup_password_entry = ttk.Entry(self.root, show='*', width=40)
        self.signup_password_entry.pack(padx=10, pady=30)

        ttk.Label(self.root, text="Confirm Password:", font=('Calibri 19 bold')).pack()
        self.signup_confirm_password_entry = ttk.Entry(self.root, show='*', width=40)
        self.signup_confirm_password_entry.pack(padx=10, pady=30)

        ttk.Button(self.root, text="Sign Up", command=self.signup).pack(pady=10)

        self.back_button.lift()

    def signup(self):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()
        confirm_password = self.signup_confirm_password_entry.get()

        if password != confirm_password:
            logging.error("Passwords do not match")
            messagebox.showerror("Error", "Passwords do not match")
            return

        logging.info(f"Signing up user: {username}")
        response = requests.post('http://127.0.0.1:5000/check_password', json={"password": password})
        if response.status_code == 409:
            logging.error("Password already exists")
            messagebox.showerror("Error", "Password already exists")
            return

        response = requests.post('http://127.0.0.1:5000/signup', json={"username": username, "password": password})
        if response.status_code == 200:
            logging.info("Signup successful")
            messagebox.showinfo("Success", "Account created successfully")
            self.history.clear()
            self.create_login_ui()
        else:
            logging.error("Signup failed")
            messagebox.showerror("Error", response.json()["message"])

    def create_dashboard(self):
        self.clear_frame()
        self.dashboard_frame = ttk.Frame(self.root, padding=20)
        self.dashboard_frame.pack(expand=True)

        ttk.Button(self.dashboard_frame, text="Book Appointment", command=self.book_appointment_ui).pack(pady=10)
        ttk.Button(self.dashboard_frame, text="History", command=self.show_history).pack(pady=10)
        ttk.Button(self.dashboard_frame, text="Cancel Latest Appointment", command=self.cancel_latest_appointment).pack(pady=10)
        self.back_button.config(command=self.create_initial_ui)
        self.back_button.lift()

    def cancel_latest_appointment(self):
        response = requests.delete('http://127.0.0.1:5000/cancel_latest_appointment')
        if response.status_code == 200:
            logging.info("Latest appointment canceled successfully")
            messagebox.showinfo("Success", "Latest appointment canceled successfully")
            self.show_history()  # Refresh the history page after cancellation
        # else:
        #     logging.error(response.json()["message"])
        #     messagebox.showerror("Error", response.json()["message"])

    def update_clock(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        logging.debug(f"Updating clock to: {current_time}")

        if hasattr(self, 'clock_label') and self.clock_label.winfo_exists():
            self.clock_label.config(text=current_time)
        else:
            logging.warning("Clock label does not exist or has been destroyed.")

        self.root.after(1000, self.update_clock)

    def book_appointment_ui(self):
        self.history.append(self.create_dashboard)
        self.clear_frame()
        self.book_frame = ttk.Frame(self.root, padding=20)
        self.book_frame.pack(expand=True)

        ttk.Label(self.book_frame, text="Doctor ID:").pack(anchor='w')
        self.doctor_id_entry = ttk.Entry(self.book_frame, width=20)
        self.doctor_id_entry.pack(fill='x', pady=10)

        ttk.Label(self.book_frame, text="Date (YYYY-MM-DD):").pack(anchor='w')
        self.date_entry = DateEntry(self.book_frame, width=20)
        self.date_entry.pack(fill='x', pady=10)

        ttk.Label(self.book_frame, text="Time (HH:MM):").pack(anchor='w')
        self.time_combobox = ttk.Combobox(self.book_frame, width=20, state='readonly')
        self.time_combobox['values'] = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
        self.time_combobox.pack(fill='x', pady=10)

        self.clock_label = ttk.Label(self.book_frame, text="")
        self.clock_label.pack(anchor='w')

        self.update_clock()

        ttk.Button(self.book_frame, text="Book", command=self.book_appointment).pack(pady=10)

        self.back_button.config(command=self.create_dashboard)
        self.back_button.lift()

    def book_appointment(self):
        doctor_id = self.doctor_id_entry.get()
        date = self.date_entry.get()
        time = self.time_combobox.get()
        logging.info(f"Booking appointment for Doctor ID: {doctor_id}, Date: {date}, Time: {time}")
        response = requests.post('http://127.0.0.1:5000/book_appointment', json={"doctor_id": doctor_id, "date": date, "time": time})
        self.back_button.lift()
        if response.status_code == 200:
            logging.info("Appointment booked successfully")
            messagebox.showinfo("Success", "Appointment booked successfully")
            messagebox.showinfo("Important !","If you want to cancel the latest appointment you can do it on the previous page.(After 3 days you won't be able to do that)")
            self.history.clear()
            self.create_dashboard()
        else:
            logging.error("Failed to book appointment")
            messagebox.showerror("Error", response.json()["message"])

    def show_history(self):
        self.history.append(self.book_appointment_ui)  # Add current UI to history
        self.clear_frame()

        self.history_frame = ttk.Frame(self.root, padding=20)
        self.history_frame.pack(expand=True, fill='both')

        self.tree = ttk.Treeview(self.history_frame, columns=('Doctor ID', 'Date', 'Time'), show='headings', style="TLabel")

        self.tree.heading('Doctor ID', text='DOCTOR ID')
        self.tree.heading('Date', text='DATE')
        self.tree.heading('Time', text='TIME')

        self.tree.column('Doctor ID', anchor='center')
        self.tree.column('Date', anchor='center')
        self.tree.column('Time', anchor='center')

        self.tree.pack(expand=True, fill='both')
        self.back_button.config(command=self.create_dashboard)
        self.back_button.lift()  # Show the back button

        self.fetch_appointment_history()  # Fetch the history after setting up the UI

    def fetch_appointment_history(self):
        response = requests.get('http://127.0.0.1:5000/get_appointments')
        if response.status_code == 200:
            appointments = response.json()
            for appointment in appointments:
                app_id = appointment['_id']
                values = (appointment['doctor_id'], appointment['date'], appointment['time'])
                self.tree.insert('', 'end', values=values, iid=app_id)
        else:
            logging.error("Failed to fetch appointment history")
            # messagebox.showerror("Error", response.json()["message"])

    def clear_frame(self):
        for widget in self.root.winfo_children():
            if widget != self.back_button and widget != self.background_label:
                widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
