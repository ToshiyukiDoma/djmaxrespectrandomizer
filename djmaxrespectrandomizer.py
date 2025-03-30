import csv
import tkinter as tk
from tkinter import ttk  # For Combobox and Notebook
import random
from typing import List, Dict, Tuple  # Import Tuple
from tkinter.font import Font  # Import the Font class
import os

def get_songs_by_categories(csv_file, selected_categories: List[str], key_mode_filter: str,
                           include_nm_hd_mx: bool, include_sc: bool,
                           nm_hd_mx_min_level: int, nm_hd_mx_max_level: int,
                           sc_min_level: int, sc_max_level: int) -> List[Tuple[str, str, str, str]]:
    """
    Reads a CSV file and returns a list of song titles with their corresponding difficulty and level,
    filtered by multiple categories, key mode, and separate level ranges for NM/HD/MX and SC.

    Args:
        csv_file (str): The path to the CSV file.
        selected_categories (List[str]): A list of categories to filter by.
                                         If "All" is in the list, no filter is applied.
        key_mode_filter (str): The key mode to filter by (e.g., "4B", "5B", "6B", "8B").
                               If "All" or "" no filter applied.
        include_nm_hd_mx (bool): Include NM, HD, and MX difficulties.
        include_sc (bool): Include SC difficulty.
        nm_hd_mx_min_level (int): The minimum level for NM, HD, and MX difficulties.
        nm_hd_mx_max_level (int): The maximum level for NM, HD, and MX difficulties.
        sc_min_level (int): The minimum level for SC difficulty.
        sc_max_level (int): The maximum level for SC difficulty.

    Returns:
        List[Tuple[str, str, str, str]]: A list of tuples, where each tuple contains the song title,
                                     the difficulty (e.g., "4B - NM"), the level, and the category.
    """

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header row
            song_data = []
            for row in reader:
                title = row[0]
                category = row[1]
                if "All" in selected_categories or category in selected_categories:
                    # Apply key mode and difficulty filters
                    if key_mode_filter and key_mode_filter != "All" and key_mode_filter:
                        if include_nm_hd_mx:
                            for diff in ["NM", "HD", "MX"]:
                                level_str = row[header.index(f"{key_mode_filter} {diff}")]
                                if level_str != '0' and level_str.isdigit():  # Ensure level is a number
                                    level = int(level_str)
                                    if nm_hd_mx_min_level <= level <= nm_hd_mx_max_level:
                                        song_data.append((title, f"{key_mode_filter} {diff}", level_str, category)) # added category
                        if include_sc:
                            level_str = row[header.index(f"{key_mode_filter} SC")]
                            if level_str != '0' and level_str.isdigit():
                                level = int(level_str)
                                if sc_min_level <= level <= sc_max_level:
                                    song_data.append((title, f"{key_mode_filter} SC", level_str, category)) # added category

                    elif not key_mode_filter or key_mode_filter == "All" or not key_mode_filter:
                         if include_nm_hd_mx:
                            for diff in ["NM", "HD", "MX"]:
                                key = f"{row[2][:2]} {diff}"
                                if key in header:
                                    level_str = row[header.index(key)]
                                    if level_str != '0' and level_str.isdigit():
                                        level = int(level_str)
                                        if nm_hd_mx_min_level <= level <= nm_hd_mx_max_level:
                                            song_data.append((title, f"{row[2][:2]} {diff}", level_str, category)) # added category
                         if include_sc:
                            key = f"{row[2][:2]} SC"
                            if key in header:
                                level_str = row[header.index(key)]
                                if level_str != '0' and level_str.isdigit():
                                    level = int(level_str)
                                    if sc_min_level <= level <= sc_max_level:
                                        song_data.append((title, f"{row[2][:2]} SC", level_str, category)) # added category
            return song_data
    except FileNotFoundError:
        return [("Error: CSV file not found.", "", "", "")]
    except Exception as e:
        return [(f"An error occurred: {e}", "", "", "")]



def load_full_category_names(category_file):
    """
    Loads the mapping of short category names to full category names from a CSV.

    Args:
        category_file (str): Path to the CSV file containing category mappings.

    Returns:
        Dict[str, str]: A dictionary where keys are short names and values are full names.
    """

    full_category_names = {}
    try:
        with open(category_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                full_category_names[row[0]] = {
                    'full_name': row[1],
                    'source': row[2]
                }
        full_category_names["All"] = {'full_name': "All Categories", 'source': "All"}  # added this line
    except FileNotFoundError:
        print(f"Error: Category file '{category_file}' not found.")
    except Exception as e:
        print(f"An error occurred while loading categories: {e}")
    return full_category_names

def save_to_history(song_data: Tuple[str, str, str, str]):
    """
    Saves the selected song to the history file.

    Args:
        song_data (Tuple[str, str, str, str]): A tuple containing the song title, difficulty, level, and category.
    """
    try:
        with open("history.txt", "a", encoding="utf-8") as file:
            file.write(f"{song_data[0]},{song_data[1]},{song_data[2]}, {song_data[3]}\n") # added category to history
    except Exception as e:
        print(f"An error occurred while saving to history: {e}")

def load_history():
    """
    Loads the song history from the history file.

    Returns:
        List[Tuple[str, str, str, str]]: A list of tuples, where each tuple contains the song title,
                                     difficulty, and level.
    """
    history_data = []
    try:
        with open("history.txt", "r", encoding="utf-8") as file:
            for line in file:
                song_data = line.strip().split(",")
                if len(song_data) == 4:
                    history_data.append(tuple(song_data))
    except FileNotFoundError:
        print("History file not found.  Creating a new one.")
    except Exception as e:
        print(f"An error occurred while loading history: {e}")
    return history_data

# Define difficulty colors
difficulty_colors = {
    "SC": "#ff00ff",
    "MX": "#ff0000",
    "HD": "#ff8200",
    "NM": "#ffd966"
}

def display_song():
    """
    Gets a random song title with difficulty and level based on the selected criteria and displays it.
    Also saves the selected song to the history file.
    """
    # Correct way to get selected categories:
    selected_categories = [category['short_name'] for category in category_buttons if category['variable'].get() == 1]
    selected_key_mode = key_mode_var.get()
    include_nm_hd_mx_value = nm_hd_mx_toggle_var.get()  # Get the state of the NM/HD/MX toggle
    include_sc_value = sc_toggle_var.get()  # Get the state of the SC toggle

    nm_hd_mx_min_level_value = nm_hd_mx_min_level_var.get()
    nm_hd_mx_max_level_value = nm_hd_mx_max_level_var.get()
    sc_min_level_value = sc_min_level_var.get()
    sc_max_level_value = sc_max_level_var.get()

    songs = get_songs_by_categories('SongList.csv', selected_categories, selected_key_mode,
                                     include_nm_hd_mx_value, include_sc_value,
                                     nm_hd_mx_min_level_value, nm_hd_mx_max_level_value,
                                     sc_min_level_value, sc_max_level_value)  # Replace with your CSV file name
    if songs:
        song, difficulty, level, category = random.choice(songs) # added category
        # Get the full category name
        full_category_name = full_category_names.get(category, {'full_name': category}).get('full_name')
        display_text = f"{full_category_name}\n{song} ({difficulty})\n"  # Include full category name

        color = "white"  # Default color
        if selected_key_mode != "All" and selected_key_mode and difficulty and level:
            diff_short = difficulty.split()[-1]  # Get "NM", "HD", "MX", or "SC"
            color = difficulty_colors.get(diff_short, "white")  # Get color, default to white if not found.
            if "NM" in difficulty or "HD" in difficulty or "MX" in difficulty:
                stars = "☆" * int(level)
            elif "SC" in difficulty:
                stars = "★" * int(level)
            else:
                stars = "N/A"
            # Add spaces every 5 stars
            stars = " ".join([stars[i:i+5] for i in range(0, len(stars), 5)])
            display_text += stars
        else:
            display_text = f"{full_category_name}\n{song}\n" # show category even if not detailed.

        song_label.config(text=display_text, font=title_font, fg=color,  # Apply the title font
                         bg="black", highlightthickness=1, highlightcolor="white", justify=tk.CENTER)  # Set black background and center text
        save_to_history((song, difficulty, level, category))  # Save to history # added category
        update_history_display() # Update the history tab

    else:
        song_label.config(text="No songs found with the selected criteria.", font=default_font, width=600,
                         height=150)  # Apply the default font

def clear_history():
    """
    Clears the song history file and updates the history display.
    """
    try:
        with open("history.txt", "w", encoding="utf-8") as file:
            file.write("")  # Clear the file
        history_listbox.delete(0, tk.END)  # Clear the listbox
    except Exception as e:
        print(f"An error occurred while clearing history: {e}")

def update_history_display():
    """
    Updates the history tab with the contents of the history file.
    """
    history_data = load_history()
    history_listbox.delete(0, tk.END)  # Clear the listbox
    for song_data in reversed(history_data): # reversed the history data.
        # Get the full category name
        # full_category_name = full_category_names.get(song_data[3], {'full_name': song_data[3]}).get('full_name')
        # display_text = f"{full_category_name}\n{song_data[0]} ({song_data[1]})\n"

        display_text = f"[{song_data[3].strip()}] {song_data[0]} ({song_data[1]}) " # removed space
        if "NM" in song_data[1] or "HD" in song_data[1] or "MX" in song_data[1]:
            stars = "☆" * int(song_data[2])
        elif "SC" in song_data[1]:
            stars = "★" * int(song_data[2])
        else:
            stars = "N/A"
        stars = " ".join([stars[i:i+5] for i in range(0, len(stars), 5)])
        display_text += stars
        history_listbox.insert(tk.END, display_text)

# Create the main window
window = tk.Tk()
window.title("DJMAX RESPECT SONG RANDOMIZER")  # changed title
window.geometry("1000x1000")  # Adjusted size
window.resizable(False, False)  # Make the window fixed size

# Use a default font
default_font = ("Helvetica", 12)
title_font = ("Helvetica", 20, "bold")  # Font for song title
history_font = ("Helvetica", 12, "bold")

# Create a notebook to hold the tabs
notebook = ttk.Notebook(window)
notebook.pack(fill=tk.BOTH, expand=True)

# Main tab
main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text="Main")

# History tab
history_tab = ttk.Frame(notebook)
notebook.add(history_tab, text="History")

# Category Selection Frame (Main Tab)
category_frame = tk.Frame(main_tab)
category_frame.pack(padx=10, fill=tk.BOTH, anchor='center')  # Center the frame

# Load full category names
full_category_names = load_full_category_names('CategoryNames.csv')  # Replace with your category CSV file name

# Get all unique categories from the CSV
all_songs = get_songs_by_categories('SongList.csv', ["All"], "", True, True, 1, 15, 1, 15)  # Initialize min and max to default values
if "Error" not in all_songs:
    try:
        with open('SongList.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header row
            unique_categories = ["All"]  # Default option
            for row in reader:
                category = row[1]
                if category not in unique_categories:
                    unique_categories.append(category)
            unique_categories.sort()  # Sort the categories
    except FileNotFoundError:
        unique_categories = ["Error: CSV not found"]
    except Exception as e:
        unique_categories = ["Error: " + str(e)]
else:
    unique_categories = ["Error reading CSV"]

# Variables and Toggle Buttons for Categories
num_columns = 5
category_buttons = []
button_width = 20  # Width in characters (adjust as needed)
button_height = 1.25  # Height in lines.  Can now be a float.
separator_color = "gray"  # Color for the separator lines

def on_toggle(category_name):
    """Toggles the state of a category button and handles 'All' logic."""
    for cat_button in category_buttons:
        if cat_button['short_name'] == category_name:
            if category_name == "All":
                if cat_button['variable'].get() == 0:  # If "All" is being selected
                    cat_button['variable'].set(1)
                    cat_button['button'].config(relief=tk.SUNKEN)
                    for other_button in category_buttons:
                        if other_button['short_name'] != "All":
                            other_button['variable'].set(0)
                            other_button['button'].config(relief=tk.RAISED)
                else:  # If "All" is being deselected
                    cat_button['variable'].set(0)
                    cat_button['button'].config(relief=tk.RAISED)
            else:  # For other categories
                if cat_button['variable'].get() == 0:
                    cat_button['variable'].set(1)
                    cat_button['button'].config(relief=tk.SUNKEN)
                    # Deselect "All" if it's selected
                    for all_button in category_buttons:
                        if all_button['short_name'] == "All" and all_button['variable'].get() == 1:
                            all_button['variable'].set(0)
                            all_button['button'].config(relief=tk.RAISED)
                else:
                    cat_button['variable'].set(0)
                    cat_button['button'].config(relief=tk.RAISED)
            break  # Exit the loop after finding the matching button

# Create a dictionary to store categories based on their source
categories_by_source = {}
for short_name, category_data in full_category_names.items():
    source = category_data['source']
    if source not in categories_by_source:
        categories_by_source[source] = []
    categories_by_source[source].append(short_name) # changed from categories_by_source.append(short_name)

# Iterate through the sources and create buttons, adding separators
row_counter = 0
# Ensure "All" is always the first category
if "All" in unique_categories:
    # Add "All" to the beginning of the first source's category list if it's not already there
    first_source = list(categories_by_source.keys())[0]
    if "All" not in categories_by_source[first_source]:
        categories_by_source[first_source].insert(0, "All")
    unique_categories.remove("All")  # Remove "All" from its original position
    unique_categories.insert(0, "All")  # Add "All" to the beginning

for source, category_list in categories_by_source.items():
    # Skip the "All" category source, as we only want it displayed once
    if source == "All":
        continue

    # Add a label for the source
    source_label = tk.Label(category_frame, text=source, font=default_font,
                            fg=separator_color)  # Apply the default font
    source_label.grid(row=row_counter, column=0, columnspan=num_columns, sticky='w', padx=5, pady=5)
    row_counter += 1

    # Add buttons for the categories in the source
    for i, category in enumerate(category_list):
        var = tk.IntVar(value=0 if category != "All" else 1)  # "All" is initially selected
        col = i % num_columns
        row = row_counter + i // num_columns
        display_text = full_category_names[category]['full_name']
        btn = tk.Button(category_frame, text=display_text, relief=tk.RAISED, bd=2, width=button_width,
                        height=int(button_height),  # Changed here
                        command=lambda cat_name=category: on_toggle(cat_name), font=default_font)  # Apply the default font
        category_buttons.append({
            'variable': var,
            'short_name': category,
            'button': btn
        })
        btn.grid(row=row, column=col, sticky='nsew', padx=5, pady=2)
    row_counter = row + 1

    # Add a separator line
    separator = tk.Frame(category_frame, height=2, bg=separator_color)
    separator.grid(row=row_counter, column=0, columnspan=num_columns, sticky='ew', padx=5, pady=5)
    row_counter += 1

#  Add the "All Categories" button separately, at the bottom
all_category_button = tk.Button(category_frame, text="All Categories", relief=tk.RAISED, bd=2,
                                 width=button_width, height=int(button_height),
                                 command=lambda cat_name="All": on_toggle(cat_name),
                                 font=default_font)
category_buttons.insert(0, {
    'variable': tk.IntVar(value=1),
    'short_name': "All",
    'button': all_category_button
})
all_category_button.grid(row=row_counter, column=0, columnspan=num_columns, sticky='nsew', padx=5, pady=2)
row_counter += 1

# Configure grid weights to center content
for i in range(num_columns):
    category_frame.columnconfigure(i, weight=1)
for i in range(row_counter):
    category_frame.rowconfigure(i, weight=1)

# Key Mode Selection (Main Tab)
key_mode_frame = tk.Frame(main_tab)  # Create a frame for label and dropdown
key_mode_frame.pack(pady=5)

key_mode_label = tk.Label(key_mode_frame, text="Select Key Mode:", font=default_font)  # Apply the default font
key_mode_label.pack(side=tk.LEFT, padx=(0, 5))  # Pack label to the left with some right padding
key_mode_var = tk.StringVar(window)
key_mode_choices = ["All", "4B", "5B", "6B", "8B"]
key_mode_dropdown = ttk.Combobox(key_mode_frame, textvariable=key_mode_var, values=key_mode_choices,
                                  font=default_font)  # Apply the default font
key_mode_dropdown.pack(side=tk.LEFT, padx=(0, 10))  # Pack dropdown to the left

key_mode_dropdown.set("All")  # Default selection

# Level Selection Frame (Main Tab)
level_frame = tk.Frame(main_tab)
level_frame.pack(pady=10)

# NM/HD/MX and SC Frames (Main Tab)
nm_hd_mx_frame = tk.Frame(level_frame)
nm_hd_mx_frame.pack(side=tk.LEFT, padx=10)

sc_frame = tk.Frame(level_frame)
sc_frame.pack(side=tk.LEFT, padx=10)

# NM/HD/MX Toggle and Level Selection (Main Tab)
nm_hd_mx_toggle_var = tk.IntVar(value=1)
nm_hd_mx_toggle = tk.Checkbutton(nm_hd_mx_frame, text="Include NM/HD/MX", variable=nm_hd_mx_toggle_var,
                                  font=default_font)  # Apply the default font
nm_hd_mx_toggle.grid(row=0, column=0, sticky='w')  # Use grid for layout

nm_hd_mx_level_label = tk.Label(nm_hd_mx_frame, text="Level:", font=default_font)  # Apply the default font
nm_hd_mx_level_label.grid(row=0, column=1, sticky='w')  # Label on the right

nm_hd_mx_min_level_var = tk.IntVar(value=1)
nm_hd_mx_min_level_spinbox = tk.Spinbox(nm_hd_mx_frame, from_=1, to=15, textvariable=nm_hd_mx_min_level_var,
                                         width=5, font=default_font)  # Apply the default font
nm_hd_mx_min_level_spinbox.grid(row=0, column=2, sticky='w')
nm_hd_mx_max_level_var = tk.IntVar(value=15)
nm_hd_mx_max_level_spinbox = tk.Spinbox(nm_hd_mx_frame, from_=1, to=15, textvariable=nm_hd_mx_max_level_var,
                                         width=5, font=default_font)  # Apply the default font
nm_hd_mx_max_level_spinbox.grid(row=0, column=3, sticky='w')

# SC Toggle and Level Selection (Main Tab)
sc_toggle_var = tk.IntVar(value=1)
sc_toggle = tk.Checkbutton(sc_frame, text="Include SC", variable=sc_toggle_var,
                            font=default_font)  # Apply the default font
sc_toggle.grid(row=0, column=0, sticky='w')  # Use grid for layout

sc_level_label = tk.Label(sc_frame, text="Level:", font=default_font)  # Apply the default font
sc_level_label.grid(row=0, column=1, sticky='w')# Label on the right

sc_min_level_var = tk.IntVar(value=1)
sc_min_level_spinbox = tk.Spinbox(sc_frame, from_=1, to=15, textvariable=sc_min_level_var, width=5,
                                   font=default_font)  # Apply the default font
sc_min_level_spinbox.grid(row=0, column=2, sticky='w')
sc_max_level_var = tk.IntVar(value=15)
sc_max_level_spinbox = tk.Spinbox(sc_frame, from_=1, to=15, textvariable=sc_max_level_var, width=5,
                                   font=default_font)  # Apply the default font
sc_max_level_spinbox.grid(row=0, column=3, sticky='w')

# Button to get a random song (Main Tab)
get_song_button = tk.Button(main_tab, text="Get Random Song", command=display_song,
                            font=default_font)  # Apply the default font
get_song_button.pack(pady=10)

# Label to display the song title (Main Tab)
song_label = tk.Label(main_tab, text="Click 'Get Random Song' to choose a song.", bg="black", fg="white",
                       width=600, height=150, font=default_font)  # set default bg to black and fixed size # Apply the default font
song_label.pack(pady=10)

# History Tab Content
history_label = tk.Label(history_tab, text="Song History", font=title_font)
history_label.pack(pady=10)

history_listbox = tk.Listbox(history_tab, width=80, height=20, bg="gray", font=history_font)
history_listbox.pack(pady=10, padx=10)

clear_history_button = tk.Button(history_tab, text="Clear History", command=clear_history, font=default_font)
clear_history_button.pack(pady=10)

# Credits Label
credits_label = tk.Label(history_tab,
                        text="DJMAX Song Randomizer ver. 2.1.2\nCreated with Google Gemini by Toshiyuki Doma\nLast Update: 2025/03/31",
                        font=("Helvetica", 10),  # Smaller font size
                        fg="gray")
credits_label.place(relx=1.0, rely=1.0, anchor=tk.SE, x=-10, y=-10)  # Position at bottom right

# Initial population of history
update_history_display()

# Run the GUI loop
window.mainloop()
