
import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import os
import requests
from datetime import datetime  # For timestamp

# Global variables
chains = []
available_cards = []
available_effects = ["Summon", "Search", "Activate", "Attack", "Synchro", "Link", "Poly", "Destroy"]  # Add actual effects here
current_chain = []  # List to store the current chain's steps
chain_name = ""  # To store the name of the current chain
PICKLE_FILE = "chains.pkl"  # File to store chains
step_history = []  # List to store the history of the steps added

# Function to save all chains using pickle
def save_all_chains():
    try:
        with open(PICKLE_FILE, 'wb') as file:
            pickle.dump(chains, file)
            print("Chains saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save chains: {e}")

# Function to load all chains using pickle
def load_all_chains():
    global chains
    try:
        if os.path.exists(PICKLE_FILE):
            with open(PICKLE_FILE, 'rb') as file:
                chains = pickle.load(file)
                print(f"Chains loaded: {chains}")  # Print loaded chains to check their structure
                if not isinstance(chains, list):
                    raise ValueError("Loaded chains data is not a list")
        else:
            print("No saved chains found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load chains: {e}")

# Fetch card names from the GitHub URL
def fetch_available_cards():
    global available_cards
    try:
        response = requests.get("https://raw.githubusercontent.com/LJEN94/MasterDuelDB/main/Card%20Ref.txt")
        response.raise_for_status()  # Check if the request was successful
        # Process the text file line by line and extract card names
        available_cards = [line.strip() for line in response.text.splitlines() if line.strip()]
        print(f"Fetched {len(available_cards)} cards.")  # Debugging line
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch card data: {e}")

# Function to start a new chain
def start_chain():
    global chain_name, chain_name_entry, step_history
    chain_name = chain_name_entry.get().strip()  # Get the name from the entry widget
    if not chain_name:
        messagebox.showerror("Error", "Please enter a name for the chain!")
        return
    
    current_chain.clear()  # Clear any previous chain data
    step_history.clear()  # Clear the history of steps
    messagebox.showinfo("Chain Started", f"Starting chain creation: {chain_name}")
    show_step_form()

# Function to create a step in the chain
def create_step():
    opening_card = opening_card_dropdown.get()
    effect = effect_dropdown.get()  # Use the effect dropdown
    next_card_1 = next_card_dropdown_1.get()
    next_card_2 = next_card_dropdown_2.get()
    next_card_3 = next_card_dropdown_3.get()
    
    if not opening_card or not effect or not (next_card_1 or next_card_2 or next_card_3):
        messagebox.showerror("Error", "All fields must be filled!")
        return

    # Add the step to the current chain
    step = {
        "opening_card": opening_card,
        "effects": [effect],
        "next_cards": [next_card_1, next_card_2, next_card_3]
    }
    current_chain.append(step)
    
    # Add the step to the history with timestamp
    history_entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "opening_card": opening_card,
        "effect": effect,
        "next_cards": [next_card_1, next_card_2, next_card_3]
    }
    step_history.append(history_entry)
    print(f"Step added: {step}")

    # Clear fields after adding the step
    effect_dropdown.set('')  # Reset the effect dropdown

    # Prompt to move to the next step
    messagebox.showinfo("Step Added", f"Step added to {chain_name}. Add another step or finish the chain.")
    show_step_form()

# Function to save the chain
def save_chain():
    if not current_chain:
        messagebox.showerror("Error", "No steps in the chain to save!")
        return

    # Prepare the chain data to be saved
    chain_data = {
        "chain_name": chain_name,
        "steps": current_chain
    }

    # Print the structure of chain_data before saving to verify it
    print("Chain data to be saved:", chain_data)

    chains.append(chain_data)
    print(f"Chain saved: {chain_data}")

    # Save all chains to file using pickle
    save_all_chains()

    # Clear current chain and history
    current_chain.clear()
    step_history.clear()
    messagebox.showinfo("Chain Saved", f"Chain '{chain_name}' saved successfully!")
    show_main_menu()

# Function to show the history of steps
def show_step_history():
    # Clear the previous widgets
    for widget in root.winfo_children():
        widget.grid_forget()

    # Step history display
    ttk.Label(root, text="Step History").grid(row=0, column=0, padx=10, pady=5)
    
    history_text = "\n".join([f"{entry['timestamp']}: {entry['opening_card']} -> {entry['effect']} -> {entry['next_cards']}"
                             for entry in step_history])
    history_label = ttk.Label(root, text=history_text, anchor="w", justify="left")
    history_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    # Buttons for this step
    ttk.Button(root, text="Add Step", command=create_step).grid(row=3, column=0, padx=10, pady=10)
    ttk.Button(root, text="Finish Chain", command=save_chain).grid(row=3, column=1, padx=10, pady=10)

# Function to show the chain creation step form
def show_step_form():
    # Clear the previous widgets
    for widget in root.winfo_children():
        widget.grid_forget()

    # Step form: Opening card dropdown
    ttk.Label(root, text="Opening Card").grid(row=0, column=0, padx=10, pady=5)
    global opening_card_dropdown
    opening_card_dropdown = create_searchable_combobox(root, available_cards)
    opening_card_dropdown.grid(row=0, column=1, padx=10, pady=5)

    # Effect dropdown
    ttk.Label(root, text="Effect").grid(row=1, column=0, padx=10, pady=5)
    global effect_dropdown
    effect_dropdown = create_searchable_combobox(root, available_effects)
    effect_dropdown.grid(row=1, column=1, padx=10, pady=5)

    # Next card dropdowns
    ttk.Label(root, text="Next Card 1").grid(row=2, column=0, padx=10, pady=5)
    global next_card_dropdown_1
    next_card_dropdown_1 = create_searchable_combobox(root, available_cards)
    next_card_dropdown_1.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(root, text="Next Card 2").grid(row=3, column=0, padx=10, pady=5)
    global next_card_dropdown_2
    next_card_dropdown_2 = create_searchable_combobox(root, available_cards)
    next_card_dropdown_2.grid(row=3, column=1, padx=10, pady=5)

    ttk.Label(root, text="Next Card 3").grid(row=4, column=0, padx=10, pady=5)
    global next_card_dropdown_3
    next_card_dropdown_3 = create_searchable_combobox(root, available_cards)
    next_card_dropdown_3.grid(row=4, column=1, padx=10, pady=5)

    # Buttons for this step
    ttk.Button(root, text="Add Step", command=create_step).grid(row=5, column=0, padx=10, pady=10)
    ttk.Button(root, text="Finish Chain", command=save_chain).grid(row=5, column=1, padx=10, pady=10)

# Function to create a searchable combobox
def create_searchable_combobox(parent, values):
    combobox = ttk.Combobox(parent, values=values, state="normal", width=30)
    combobox.set_completion_list = lambda completion_list: combobox.configure(values=completion_list)

    # Bind the key release event to dynamically filter the combobox values
    def on_key_release(event):
        value = event.widget.get().strip().lower()
        filtered_values = [item for item in values if value in item.lower()]
        combobox.set_completion_list(filtered_values)

    combobox.bind('<KeyRelease>', on_key_release)
    return combobox

# Function to show the main menu with an option to select an existing chain
def show_main_menu():
    # Clear all widgets
    for widget in root.winfo_children():
        widget.grid_forget()

    # Dropdown for selecting an existing chain
    ttk.Label(root, text="Select an Existing Chain").grid(row=0, column=0, padx=10, pady=5)
    global chain_dropdown, chain_name_entry
    chain_dropdown = create_searchable_combobox(root, [chain['chain_name'] for chain in chains])
    chain_dropdown.grid(row=0, column=1, padx=10, pady=5)

    # Entry field to input the chain name for new chain creation
    ttk.Label(root, text="Enter Chain Name").grid(row=1, column=0, padx=10, pady=5)
    chain_name_entry = ttk.Entry(root)
    chain_name_entry.grid(row=1, column=1, padx=10, pady=5)

    # Buttons to select an existing chain or start a new one
    ttk.Button(root, text="Edit Chain", command=edit_chain).grid(row=2, column=0, padx=10, pady=10)
    ttk.Button(root, text="Start New Chain", command=start_chain).grid(row=2, column=1, padx=10, pady=10)
    ttk.Button(root, text="Delete Chain", command=delete_chain).grid(row=3, column=0, padx=10, pady=10)

# Function to edit an existing chain
def edit_chain():
    selected_chain_name = chain_dropdown.get()
    if not selected_chain_name:
        messagebox.showerror("Error", "Please select a chain to edit!")
        return

    # Find the selected chain from the list
    selected_chain = next((chain for chain in chains if chain['chain_name'] == selected_chain_name), None)
    if selected_chain:
        global current_chain
        current_chain = selected_chain['steps']
        global chain_name
        chain_name = selected_chain_name
        messagebox.showinfo("Chain Editing", f"Editing existing chain: {chain_name}")
        show_chain_steps()
    else:
        messagebox.showerror("Error", "Selected chain not found!")

# Function to show the steps in the chain and allow editing
def show_chain_steps():
    # Clear previous widgets
    for widget in root.winfo_children():
        widget.grid_forget()

    ttk.Label(root, text="Steps in the Chain").grid(row=0, column=0, padx=10, pady=5)

    # List the steps in the current chain and add edit buttons
    for index, step in enumerate(current_chain):
        step_text = f"Step {index + 1}: {step['opening_card']} -> {step['effects'][0]} -> {step['next_cards']}"
        ttk.Label(root, text=step_text).grid(row=index + 1, column=0, padx=10, pady=5)
        ttk.Button(root, text=f"Edit Step {index + 1}", command=lambda i=index: edit_step(i)).grid(row=index + 1, column=1, padx=10, pady=5)

    # Button to finish editing and save the chain
    ttk.Button(root, text="Save Chain", command=save_chain).grid(row=len(current_chain) + 1, column=0, padx=10, pady=10)
    ttk.Button(root, text="Back to Main Menu", command=show_main_menu).grid(row=len(current_chain) + 1, column=1, padx=10, pady=10)

# Function to edit a specific step
def edit_step(index):
    step = current_chain[index]
    
    # Recreate the dropdowns for editing the step
    opening_card_dropdown = create_searchable_combobox(root, available_cards)
    opening_card_dropdown.set(step['opening_card'])  # Set the current opening card
    opening_card_dropdown.grid(row=3, column=0, padx=10, pady=5)

    effect_dropdown = create_searchable_combobox(root, available_effects)
    effect_dropdown.set(step['effects'][0])  # Set the current effect
    effect_dropdown.grid(row=3, column=1, padx=10, pady=5)

    next_card_dropdown_1 = create_searchable_combobox(root, available_cards)
    next_card_dropdown_1.set(step['next_cards'][0])  # Set the current next card 1
    next_card_dropdown_1.grid(row=4, column=0, padx=10, pady=5)

    next_card_dropdown_2 = create_searchable_combobox(root, available_cards)
    next_card_dropdown_2.set(step['next_cards'][1])  # Set the current next card 2
    next_card_dropdown_2.grid(row=4, column=1, padx=10, pady=5)

    next_card_dropdown_3 = create_searchable_combobox(root, available_cards)
    next_card_dropdown_3.set(step['next_cards'][2])  # Set the current next card 3
    next_card_dropdown_3.grid(row=4, column=2, padx=10, pady=5)

    # Change the "Add Step" button to "Update Step"
    ttk.Button(root, text="Update Step", command=lambda: update_step(index, opening_card_dropdown, effect_dropdown, next_card_dropdown_1, next_card_dropdown_2, next_card_dropdown_3)).grid(row=5, column=0, padx=10, pady=10)

# Function to update a step
def update_step(index, opening_card_dropdown, effect_dropdown, next_card_dropdown_1, next_card_dropdown_2, next_card_dropdown_3):
    opening_card = opening_card_dropdown.get()
    effect = effect_dropdown.get()
    next_card_1 = next_card_dropdown_1.get()
    next_card_2 = next_card_dropdown_2.get()
    next_card_3 = next_card_dropdown_3.get()

    if not opening_card or not effect or not (next_card_1 or next_card_2 or next_card_3):
        messagebox.showerror("Error", "All fields must be filled!")
        return

    # Update the step
    current_chain[index] = {
        "opening_card": opening_card,
        "effects": [effect],
        "next_cards": [next_card_1, next_card_2, next_card_3]
    }

    messagebox.showinfo("Step Updated", "Step updated successfully!")
    show_chain_steps()

# Function to delete an existing chain with a confirmation prompt
def delete_chain():
    selected_chain_name = chain_dropdown.get()
    if not selected_chain_name:
        messagebox.showerror("Error", "Please select a chain to delete!")
        return
    
    # Confirm the deletion
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the chain '{selected_chain_name}'?")
    if confirm:
        # Find and delete the selected chain
        global chains
        chains = [chain for chain in chains if chain['chain_name'] != selected_chain_name]
        save_all_chains()  # Save changes after deletion
        messagebox.showinfo("Chain Deleted", f"Chain '{selected_chain_name}' has been deleted.")
        show_main_menu()

# Initialize the root window
root = tk.Tk()
root.title("Yu-Gi-Oh Chain Manager")

# Load the chains and available cards initially
load_all_chains()
fetch_available_cards()

# Show the main menu initially
show_main_menu()

# Run the main event loop
root.mainloop()