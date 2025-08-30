import pickle
import os
import requests
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import shutil

# File paths
PICKLE_FILE = "chains.pkl"
IMAGES_FOLDER = "Local Images"
PROGRESS_FILE = "progress.txt"
ACTION_LOG_FILE = "action_log.txt"
ID_URL = "https://raw.githubusercontent.com/LJEN94/MasterDuelDB/main/ID.csv"
CARD_IMAGE_URL_TEMPLATE = "https://images.ygoprodeck.com/images/cards/{}.jpg"

# Global variables
chains = []
current_chain = None
current_step = 1
zoom_level = 1.0
labels = {
    "next": "Next Step", "prev": "Previous Step", "reset": "Reset",
    "save": "Save Progress", "load": "Load Progress", "end": "End of Steps", "help": "Help"
}
card_id_map = {}

# Create the images folder if it doesn't exist
if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)

def load_card_id_map():
    """Load card ID mappings from the provided URL."""
    global card_id_map
    try:
        print("Fetching card ID map...")
        df = pd.read_csv(ID_URL, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()  # Clean header names
        print("Columns in CSV:", df.columns.tolist())
        for index, row in df.iterrows():
            card_name = row['Name'].strip()
            card_id = str(row['ID']).strip()
            card_id_map[card_name] = card_id
            print(f"Processed card: {card_name} with ID: {card_id}")
        print("Card IDs loaded successfully")
    except Exception as e:
        print(f"Failed to fetch card ID data: {e}")
        messagebox.showerror("Error", f"Failed to fetch card ID data: {e}")

def download_card_image(card_name):
    """Download and save the card image locally if not already downloaded."""
    if card_name in card_id_map:
        card_id = card_id_map[card_name]
        image_path = os.path.join(IMAGES_FOLDER, f"{card_id}.jpg")
        
        if not os.path.exists(image_path):
            image_url = CARD_IMAGE_URL_TEMPLATE.format(card_id)
            try:
                print(f"Downloading image for {card_name} from {image_url}")
                response = requests.get(image_url)
                response.raise_for_status()
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                print(f"Image downloaded and saved: {image_path}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download image for {card_name}: {e}")
        else:
            print(f"Image already exists for {card_name}: {image_path}")
        return image_path
    else:
        print(f"Card name {card_name} not found in card ID map")
    return None

def load_chains():
    """Load chains from the pickle file and create a backup."""
    global chains
    try:
        print("Loading chains from pickle file...")
        if os.path.exists(PICKLE_FILE):
            with open(PICKLE_FILE, 'rb') as file:
                chains = pickle.load(file)
                if not isinstance(chains, list):
                    raise ValueError("Loaded chains data is not a list")
            print("Chains loaded successfully")

            backup_path = os.path.join(IMAGES_FOLDER, "chains_backup.pkl")
            shutil.copy2(PICKLE_FILE, backup_path)
            print(f"Backup of chains.pkl created at {backup_path}")
        else:
            print("No saved chains found.")
    except Exception as e:
        print(f"Failed to load chains: {e}")
        messagebox.showerror("Error", f"Failed to load chains: {e}")

def log_action(action):
    """Log actions to a file."""
    with open(ACTION_LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {action}\n")

def save_progress():
    """Save the current progress to a file."""
    try:
        with open(PROGRESS_FILE, "w") as f:
            f.write(str(current_step))
        log_action("Progress saved.")
    except Exception as e:
        log_action(f"Failed to save progress: {e}")

def load_progress():
    """Load progress from a file."""
    global current_step
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, "r") as f:
                current_step = int(f.read().strip())
            log_action("Progress loaded.")
    except Exception as e:
        log_action(f"Failed to load progress: {e}")

def switch_theme(theme):
    """Switch between light and dark themes."""
    print(f"Switching theme to {theme}")
    status_bar.config(text=f"Switched to {theme} theme")
    if theme == "Light":
        root.style.theme_use('default')
    elif theme == "Dark":
        root.style.theme_use('clam')

def show_help():
    """Display help information."""
    messagebox.showinfo(labels["help"], "Navigate through steps using Next and Previous. Use the Reset button to restart. Save progress to continue later.")

def show_images(step):
    """Display card images and effect text."""
    try:
        image_frame = ttk.Frame(root, padding="10")
        image_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

        canvas = tk.Canvas(image_frame, bg="#ffffff", width=800, height=250)
        scrollbar = ttk.Scrollbar(image_frame, orient="horizontal", command=canvas.xview)
        inner_frame = ttk.Frame(canvas)

        inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")

        opening_card_name = step['opening_card']
        if opening_card_name:
            print(f"Processing opening card: {opening_card_name}")
            opening_image_path = download_card_image(opening_card_name)
            if opening_image_path and os.path.exists(opening_image_path):
                img = Image.open(opening_image_path)
                img = img.resize((int(150 * zoom_level), int(200 * zoom_level)))
                img = ImageTk.PhotoImage(img)

                label_frame = ttk.Label(inner_frame, text=opening_card_name, font=("Arial", 10, "bold"))
                label_frame.grid(row=0, column=0, padx=10, pady=5)

                label = ttk.Label(inner_frame, image=img)
                label.image = img
                label.grid(row=1, column=0, padx=10)
            else:
                print(f"Image path not found for opening card: {opening_card_name}")

        if 'effects' in step and step['effects']:
            effect_text = step['effects'][0]
            effect_label = ttk.Label(inner_frame, text=effect_text, font=("Arial", 12, "italic"))
            effect_label.grid(row=1, column=1, padx=10, pady=5)

        for i, card_name in enumerate(step['next_cards']):
            if card_name:
                print(f"Processing next card: {card_name}")
                image_path = download_card_image(card_name)
                if image_path and os.path.exists(image_path):
                    img = Image.open(image_path)
                    img = img.resize((int(150 * zoom_level), int(200 * zoom_level)))
                    img = ImageTk.PhotoImage(img)

                    label_frame = ttk.Label(inner_frame, text=card_name, font=("Arial", 10, "bold"))
                    label_frame.grid(row=0, column=i + 2, padx=10, pady=5)

                    label = ttk.Label(inner_frame, image=img)
                    label.image = img
                    label.grid(row=1, column=i + 2, padx=10)
                else:
                    print(f"Image path not found for next card: {card_name}")
    except Exception as e:
        print(f"Error in show_images function: {e}")

def display_step():
    """Display the current step."""
    global current_step, current_chain

    for widget in root.winfo_children():
        widget.destroy()

    if current_chain and current_step <= len(current_chain["steps"]):
        step = current_chain["steps"][current_step - 1]

        header_frame = ttk.Frame(root, padding="10")
        header_frame.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

        step_label = ttk.Label(
            header_frame, text=f"Step {current_step}: {step['opening_card']} -> {step['effects'][0]} -> {', '.join([card for card in step['next_cards'] if card])}", font=("Arial", 14)
        )
        step_label.pack()

        global progress_label
        progress_label = ttk.Label(root, font=("Arial", 12))
        progress_label.grid(row=1, column=0, columnspan=3)
        progress_label.config(text=f"Step {current_step} of {len(current_chain['steps'])}")

        show_images(step)

        nav_frame = ttk.Frame(root, padding="10")
        nav_frame.grid(row=3, column=0, columnspan=3, pady=20, sticky="ew")

        prev_button = ttk.Button(nav_frame, text=labels["prev"], command=previous_step)
        prev_button.pack(side="left", padx=10)

        reset_button = ttk.Button(nav_frame, text=labels["reset"], command=reset_app)
        reset_button.pack(side="left", padx=10)

        save_button = ttk.Button(nav_frame, text=labels["save"], command=save_progress)
        save_button.pack(side="left", padx=10)

        load_button = ttk.Button(nav_frame, text=labels["load"], command=load_progress)
        load_button.pack(side="left", padx=10)

        next_button = ttk.Button(nav_frame, text=labels["next"], command=next_step)
        next_button.pack(side="left", padx=10)

        # Progress bar
        progress = (current_step / len(current_chain["steps"])) * 100
        progress_bar['value'] = progress
        status_bar.config(text=f"Step {current_step} of {len(current_chain['steps'])} ({int(progress)}%)")
    else:
        messagebox.showinfo(labels["end"], "You have reached the end of this chain.")
        log_action("Reached end of steps.")

def previous_step():
    """Go to the previous step."""
    global current_step
    if current_step > 1:
        current_step -= 1
        display_step()
        log_action("Moved to previous step.")

def next_step():
    """Go to the next step."""
    global current_step
    if current_step < len(current_chain["steps"]):
        current_step += 1
        display_step()
        log_action("Moved to next step.")

def reset_app():
    """Reset the application to the initial state."""
    global current_step, current_chain
    for widget in root.winfo_children():
        widget.destroy()

    current_step = 1
    current_chain = None
    log_action("Application reset.")

    dropdown_frame = ttk.Frame(root, padding="10")
    dropdown_frame.grid(row=0, column=0, pady=20, sticky="ew")

    chain_dropdown = ttk.Combobox(dropdown_frame, values=[chain['chain_name'] for chain in chains], state="readonly")
    chain_dropdown.pack(side="left", padx=10)

    load_button = ttk.Button(dropdown_frame, text="Load Chain", command=lambda: load_chain(chain_dropdown.get()))
    load_button.pack(side="left", padx=10)

def load_chain(chain_name):
    """Load a chain and display the first step."""
    global current_chain, current_step
    current_chain = next((chain for chain in chains if chain["chain_name"] == chain_name), None)
    current_step = 1
    if current_chain:
        log_action(f"Loaded chain: {chain_name}")
        display_step()
    else:
        messagebox.showerror("Error", "Chain not found!")

# Initialize the Tkinter window
root = tk.Tk()
root.title("Yu-Gi-Oh Chain Manager")
root.geometry("900x700")
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)

# Apply styles
root.style = ttk.Style()
root.style.configure('TButton', font=('Arial', 10), padding=5)
root.style.configure('TLabel', font=('Arial', 10))

# Status bar
status_bar = ttk.Label(root, text="Welcome to Yu-Gi-Oh Chain Manager", relief=tk.SUNKEN, anchor=tk.W)
status_bar.grid(row=4, column=0, columnspan=3, sticky="ew")

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=100, mode="determinate")
progress_bar.grid(row=5, column=0, columnspan=3, sticky="ew")

# Load card ID mappings
load_card_id_map()

# Load chains initially
load_chains()

# Default theme
switch_theme("Light")

# Main menu bar
menu = tk.Menu(root)
root.config(menu=menu)

# Themes menu
theme_menu = tk.Menu(menu, tearoff=0)
theme_menu.add_command(label="Light Theme", command=lambda: switch_theme("Light"))
theme_menu.add_command(label="Dark Theme", command=lambda: switch_theme("Dark"))
menu.add_cascade(label="Themes", menu=theme_menu)

# File menu
file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Save Progress", command=save_progress)
file_menu.add_command(label="Load Progress", command=load_progress)
menu.add_cascade(label="File", menu=file_menu)

# Navigation menu
nav_menu = tk.Menu(menu, tearoff=0)
nav_menu.add_command(label="Next Step", command=next_step)
nav_menu.add_command(label="Previous Step", command=previous_step)
nav_menu.add_command(label="Reset", command=reset_app)
menu.add_cascade(label="Navigation", menu=nav_menu)

# Help menu
menu.add_command(label="Help", command=show_help)

# Reset the app to show the initial dropdown menu
reset_app()

# Run the main event loop
root.mainloop()