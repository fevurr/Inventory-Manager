import os
import sys
import requests
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import firebase_admin 
from firebase_admin import credentials, db
from packaging import version 
import webbrowser 
import random

# Application version
CURRENT_VERSION = "v1.5.0"

if getattr(sys, 'frozen', False): 
    cred_path = os.path.join(sys._MEIPASS, 'firebase_keys/inventory-database-c81ac-firebase-adminsdk-7tm75-bb1d275ac8.json')
else:
    cred_path = 'firebase_keys/inventory-database-c81ac-firebase-adminsdk-7tm75-bb1d275ac8.json'

cred = credentials.Certificate(cred_path)
# Initialize app with service account, granting admin privileges 
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://inventory-database-c81ac-default-rtdb.firebaseio.com/'
})
# THIS ALLOWS USE OF "firebase_admin.db" MODULE TO INTERACT WITH THE DATABASE

# Constants
BG_COLOR = '#bd4f4f'
button_width = 120
button_height = 30
GRID_COLUMNS = ("ID", "Type", "Name", "Quantity")
ENTRY_WIDTH = 50
FONT_SANS_12 = ("Sans Serif", 12)

inventory_data = []  # Temporary storage for input data

#=========================  INITIALIZE FUNCTIONS =================
def check_for_updates():
    print("Checking for updates...")
    api_url = "https://api.github.com/repos/fevurr/Inventory-Manager/releases/latest"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release['tag_name']
        print(f"Latest version on GitHub: {latest_version}")
        print(f"Current version: {CURRENT_VERSION}")
        if version.parse(latest_version) > version.parse(CURRENT_VERSION):
            print("An update is available.")
            return latest_release['html_url']
        else:
            print("Your application is up to date.")
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None

def prompt_for_update(update_url):
    print("Prompting for update...")
    if messagebox.askyesno("Update Available", "A new version of Inventory Manager is available. Would you like to download it now?"):
        webbrowser.open(update_url)
        print("User chose to update. Opening web browser...")
    else:
        root.focus_force()

def fetch_inventory():
    # Clear Treeview
    inventory_grid.delete(*inventory_grid.get_children())
    
    # Fetch Firebase data 
    firebase_ref = firebase_admin.db.reference('inventory')
    try:
        items = firebase_ref.get()
        if items:
            for item_id, item_info in items.items():
                inventory_grid.insert("", "end", values=(
                    item_id,
                    item_info['type'],
                    item_info['name'],
                    item_info['quantity']
                ))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        
        sort_inventory()

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def confirm_exit():
    response = messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?")
    if response:
        root.destroy()

def is_numeric(input_str):
    """Check if the input string is numeric."""
    return input_str.isdigit()

def generate_random_id():
    # Generate a random 10-character ID using uppercase letters and digits
    characters = "0123456789"
    random_id = ''.join(random.choice(characters) for _ in range(10))
    return random_id

def add_item(type_entry, name_entry, quantity_entry):
    global inventory_grid

    # Generate a random ID
    item_id = generate_random_id()

    item_type = type_entry.get()
    item_name = name_entry.get()
    quantity = quantity_entry.get()

    # Check if any of the fields are empty
    if not all([item_type, item_name, quantity]):
        messagebox.showerror("Error", "Please fill out all input fields.")
    else:
        # Add an item to the inventory in Firebase with the generated random ID
        firebase_ref = firebase_admin.db.reference('inventory')
        firebase_ref.child(item_id).set({
            'type': item_type,
            'name': item_name,
            'quantity': quantity
        })

        inventory_grid.insert("", "end", values=(item_id, item_type, item_name, quantity))

        # Clear the input fields after adding the item
        type_entry.delete(0, "end")
        name_entry.delete(0, "end")
        quantity_entry.delete(0, "end")

        sort_inventory()

def update_item(item_id_entry, type_entry, name_entry, quantity_entry):
    # Get the selected item
    global inventory_grid 
    selected_item = inventory_grid.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an item to update.")
        return

    # Assuming the first value in the values tuple is the item ID
    selected_item_id = inventory_grid.item(selected_item[0], 'values')[0]
    
    # Firebase reference
    firebase_ref = firebase_admin.db.reference(f'inventory/{selected_item_id}')

    # Get the current data from Firebase
    current_data = firebase_ref.get()
    if not current_data:
        messagebox.showerror("Error", "Selected item not found in the database.")
        return

    # Get the updated values from the entry fields
    new_item_id = item_id_entry.get()
    new_item_type = type_entry.get()
    new_item_name = name_entry.get()
    new_quantity = quantity_entry.get()

    # Prepare the updated data dictionary
    updated_data = {}
    if new_item_id and new_item_id != selected_item_id:
        messagebox.showerror("Error", "You cannot change the item ID.")
        return
    if new_item_type:
        updated_data['type'] = new_item_type
    if new_item_name:
        updated_data['name'] = new_item_name
    if new_quantity:
        updated_data['quantity'] = new_quantity

    # Update Firebase with the new data
    firebase_ref.update(updated_data)

    # Update the Treeview item
    updated_values = (
        selected_item_id,
        updated_data.get('type', current_data['type']),
        updated_data.get('name', current_data['name']),
        updated_data.get('quantity', current_data['quantity'])
    )
    inventory_grid.item(selected_item, values=updated_values)

    # Clear the input fields after updating
    item_id_entry.delete(0, "end")
    type_entry.delete(0, "end")
    name_entry.delete(0, "end")
    quantity_entry.delete(0, "end")

    # Sort the inventory again if necessary
    sort_inventory()

def delete_item(item_id_entry, type_entry, name_entry, quantity_entry):
    selected_items = inventory_grid.selection()

    item_type = type_entry.get()
    item_name = name_entry.get()
    item_quantity = quantity_entry.get()

    if selected_items:
        for item in selected_items:
            # Get the item ID from the selected row in the Treeview
            item_id = inventory_grid.item(item, 'values')[0]

            # Delete the item from Firebase
            firebase_ref = firebase_admin.db.reference('inventory')
            firebase_ref.child(item_id).delete()

            # Remove the item from the GUI
            inventory_grid.delete(item)
    else:
        messagebox.showerror("Error", "Please select an item to delete.")
        
    item_id_entry.delete(0, tk.END)
    type_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

def sort_inventory():
    items = [(inventory_grid.item(item, 'values')[1], item) for item in inventory_grid.get_children('')]
    items.sort()
    for index, item in enumerate(items):
        inventory_grid.move(item[1], '', index)

def filter_inventory(filter_entry):
    keyword = filter_entry.get().lower()  # Convert the keyword to lowercase for a case-insensitive search

    # Get all items from the grid
    all_items = inventory_grid.get_children()

    for item in all_items:
        item_values = inventory_grid.item(item, 'values')

        # Convert item values to lowercase for a case-insensitive search
        item_values_lower = [str(val).lower() for val in item_values]

        # If the keyword is not present in any of the item values, remove the item from the grid
        if not any(keyword in value for value in item_values_lower):
            inventory_grid.delete(item)

def clear_filter(filter_entry):
    # Clear the filter input field
    filter_entry.delete(0, "end")

    # Clear the grid
    inventory_grid.delete(*inventory_grid.get_children())

    # Repopulate the grid with items from Firebase
    firebase_ref = firebase_admin.db.reference('inventory')
    try:
        items = firebase_ref.get()
        if items:
            for item_id, item_info in items.items():
                inventory_grid.insert("", "end", values=(
                    item_id,
                    item_info['type'],
                    item_info['name'],
                    item_info['quantity']
                ))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching data: {e}")

def select_item(event, type_entry, name_entry, quantity_entry, item_id_entry):
    # Get the selected item
    selected_item = inventory_grid.selection()
    if not selected_item:
        return  # No item selected, do nothing

    # Assuming the first value in the values tuple is the item ID
    selected_item_id = inventory_grid.item(selected_item[0], 'values')[0]

    # Fetch the item's data from the Treeview
    item_type = inventory_grid.item(selected_item[0], 'values')[1]
    item_name = inventory_grid.item(selected_item[0], 'values')[2]
    item_quantity = inventory_grid.item(selected_item[0], 'values')[3]

    # Update the entry fields with the selected item's data
    item_id_entry.delete(0, "end")
    item_id_entry.insert(0, selected_item_id)
    type_entry.delete(0, "end")
    type_entry.insert(0, item_type)
    name_entry.delete(0, "end")
    name_entry.insert(0, item_name)
    quantity_entry.delete(0, "end")
    quantity_entry.insert(0, item_quantity)

def populate_entries(event, type_entry, name_entry, quantity_entry, item_id_entry):
    # Get the selected item
    selected_item = inventory_grid.selection()
    if not selected_item:
        return  # No item selected, do nothing

    # Assuming the first value in the values tuple is the item ID
    selected_item_id = inventory_grid.item(selected_item[0], 'values')[0]

    # Fetch the item's data from the Treeview
    item_type = inventory_grid.item(selected_item[0], 'values')[1]
    item_name = inventory_grid.item(selected_item[0], 'values')[2]
    item_quantity = inventory_grid.item(selected_item[0], 'values')[3]

    # Update the entry fields with the selected item's data
    item_id_entry.delete(0, "end")
    item_id_entry.insert(0, selected_item_id)
    type_entry.delete(0, "end")
    type_entry.insert(0, item_type)
    name_entry.delete(0, "end")
    name_entry.insert(0, item_name)
    quantity_entry.delete(0, "end")
    quantity_entry.insert(0, item_quantity)

def on_treeview_select(event, item_id_entry):
    # Get the selected item
    selected_item = inventory_grid.selection()
    if not selected_item:
        return  # No item selected, do nothing

    # Assuming the first value in the values tuple is the item ID
    selected_item_id = inventory_grid.item(selected_item[0], 'values')[0]

    # Enable the ID entry temporarily, populate it, and then disable it again
    item_id_entry.configure(state="normal")
    item_id_entry.delete(0, "end")
    item_id_entry.insert(0, selected_item_id)
    item_id_entry.configure(state="disabled")

def start_inventory_application():
    global root, inventory_grid
    root = tk.Tk()
    root.title("Inventory Manager")
    root.attributes("-fullscreen", True)
    root.configure(bg=BG_COLOR)

    style = ttk.Style(root)
    style.configure("Treeview", background="lightgray", fieldbackground="white", rowheight=25)

    #==================== GUI INITIALIZATION =============================

    # Frame for input fields
    input_frame = ttk.Frame(root)
    input_frame.grid(row=0, column=0, sticky="nsew")

    # Add input fields/labels  
    item_id_label = ttk.Label(input_frame, text="Item ID:", font=("Sans Serif", 12))
    item_id_label.grid(row=0, column=0, sticky="w")
    item_id_entry = ttk.Entry(input_frame, width=50, state="disabled")
    item_id_entry.grid(row=0, column=1, sticky="w")

    type_label = ttk.Label(input_frame, text="Item Type:", font=("Sans Serif", 12))
    type_label.grid(row=1, column=0, sticky="w")
    type_entry = ttk.Entry(input_frame, width=50)
    type_entry.grid(row=1, column=1, sticky="w")

    name_label = ttk.Label(input_frame, text="Item Name:", font=("Sans Serif", 12))
    name_label.grid(row=2, column=0, sticky="w")
    name_entry = ttk.Entry(input_frame, width=50)
    name_entry.grid(row=2, column=1, sticky="w")

    quantity_label = ttk.Label(input_frame, text="Quantity:", font=("Sans Serif", 12))
    quantity_label.grid(row=3, column=0, sticky="w")
    quantity_entry = ttk.Entry(input_frame, width=50)
    quantity_entry.grid(row=3, column=1, sticky="w")

    filter_label = ttk.Label(root, text="Filter:", font=("Sans Serif", 12))
    filter_label.place(relx=0, rely=0.122)
    filter_entry = ttk.Entry(root, width=30)
    filter_entry.place(relx=0.03, rely=0.122)

    esc_tip_label = ttk.Label(root, text="Use Esc to exit the application", font=("Sans Serif", 12))
    esc_tip_label.place(relx=0, rely=0.97)

    title_label = ttk.Label(root, text="CRUD Inventory Log", font=("Sans Serif", 20))
    title_label.place(relx=0.5, rely=0.05, anchor="center")

    scrollbar = ttk.Scrollbar(root, orient="vertical")
    scrollbar.place(relx=0.975, rely=0.2, relheight=0.75)

    inventory_grid = ttk.Treeview(root, columns=("ID", "Type", "Name", "Quantity"), show="headings")

    inventory_grid.bind("<<TreeviewSelect>>", lambda event, item_id_entry=item_id_entry: on_treeview_select(event, item_id_entry))
    root.bind("<Escape>", lambda event: confirm_exit())
    inventory_grid.bind("<ButtonRelease-1>", lambda event, type_entry=type_entry, name_entry=name_entry, quantity_entry=quantity_entry: populate_entries(event, type_entry, name_entry, quantity_entry, item_id_entry))
    root.bind("<Up>", lambda event, item_id_entry=item_id_entry, type_entry=type_entry, name_entry=name_entry, quantity_entry=quantity_entry: select_item(event, type_entry, name_entry, quantity_entry, item_id_entry))
    root.bind("<Down>", lambda event, item_id_entry=item_id_entry, type_entry=type_entry, name_entry=name_entry, quantity_entry=quantity_entry: select_item(event, type_entry, name_entry, quantity_entry, item_id_entry))

    # Define column headings
    inventory_grid.heading("ID", text="ID")
    inventory_grid.heading("Type", text="Type")
    inventory_grid.heading("Name", text="Name")
    inventory_grid.heading("Quantity", text="Qty")

    # Define column widths
    inventory_grid.column("ID", width=50, anchor=tk.CENTER)
    inventory_grid.column("Type", width=100, anchor=tk.CENTER)
    inventory_grid.column("Name", width=150, anchor=tk.CENTER)
    inventory_grid.column("Quantity", width=50, anchor=tk.CENTER)

    # Place the Treeview grid and make it fill both horizontally and vertically
    inventory_grid.place(relx=0, rely=0.2, relwidth=1, relheight=0.75)

    # Buttons
    button_style = ttk.Style()
    button_style.configure("Custom.TButton", font=("Sans Serif", 10), foreground="black", background="white")

    # Calculate the x-position for centering
    x_center = (1 - button_width / root.winfo_screenwidth()) / 2  # Centered

    add_button = ttk.Button(root, text="Add Item", style="Custom.TButton", command=lambda: add_item(type_entry, name_entry, quantity_entry))
    add_button.place(relx=x_center - 0.468, rely=0.165, width=button_width, height=button_height)

    update_button = ttk.Button(root, text="Update Item", style="Custom.TButton", command=lambda: update_item(item_id_entry, type_entry, name_entry, quantity_entry))
    update_button.place(relx=x_center - 0.4, rely=0.165, width=button_width, height=button_height)  # Adjust the x-position

    delete_button = ttk.Button(root, text="Delete Item", style="Custom.TButton", command=lambda: delete_item(item_id_entry, type_entry, name_entry, quantity_entry))
    delete_button.place(relx=x_center - 0.332, rely=0.165, width=button_width, height=button_height)  # Adjust the x-position

    filter_button = ttk.Button(root, text="Filter", style="Custom.TButton", command=lambda: filter_inventory(filter_entry))
    filter_button.place(relx=0.135, rely=0.122, height=20)

    clear_filter_button = ttk.Button(root, text="Clear Filter", style="Custom.TButton", command=lambda: clear_filter(filter_entry))
    clear_filter_button.place(relx=0, rely=0.1, height=20)

    scrollbar.config(command=inventory_grid.yview)

    update_url = check_for_updates()
    if update_url:
        prompt_for_update(update_url)

    fetch_inventory()

    # START MAIN LOOP
    root.mainloop()

if __name__ == "__main__":
    start_inventory_application()