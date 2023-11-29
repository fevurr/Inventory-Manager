import requests
import tkinter as tk 
from tkinter import messagebox
from config import FIREBASE_API_KEY

def attempt_login(username, password, on_success, login_window):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"email": username, "password": password, "returnSecureToken": True}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        login_window.destroy()
        on_success()
    else: 
        messagebox.showerror("Login failed", "Incorrect credentials")

def on_enter_key(event, email_entry, password_entry, on_success, login_window):
    # Trigger login when Enter key is pressed
    attempt_login(email_entry.get(), password_entry.get(), on_success, login_window)

def show_login_gui(on_success):
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x150")
    
    background_color = "#bd4f4f"  # Example color, change as needed
    login_window.configure(bg=background_color)
    
    tk.Label(login_window, text="Username:").grid(row=0, column=0, padx=10, pady=10)
    email_entry = tk.Entry(login_window, width=30)
    email_entry.grid(row=0, column=1, padx=10, pady=10)
    
    tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=10)
    password_entry = tk.Entry(login_window, show="*", width=30)
    password_entry.grid(row=1, column=1, padx=10)
    
    login_button = tk.Button(login_window, text="Login", command=lambda: attempt_login(
    email_entry.get(), password_entry.get(), on_success, login_window))
    login_button.grid(row=2, column=0, columnspan=2, pady=20)
    
    # Bind the Enter key press event to the login button
    login_window.bind('<Return>', lambda event, email_entry=email_entry, password_entry=password_entry,
                                    on_success=on_success, login_window=login_window: on_enter_key(event, email_entry, password_entry, on_success, login_window))
    
    ws = login_window.winfo_screenwidth()
    hs = login_window.winfo_screenheight()
    x = (ws/2) - (400/2)
    y = (hs/2) - (200/2)
    login_window.geometry('+%d+%d' % (x, y))
    
    email_entry.focus_set()
    
    login_window.attributes('-topmost', True)
    login_window.update()
    login_window.attributes('-topmost', False)
    
    login_window.lift()
    
    login_window.mainloop()
    
# This function could be replaced with the actual logic for successful login 
def on_login_success():
    print("Logged in successfully")
    
if __name__ == "__main__":
    show_login_gui(on_login_success)