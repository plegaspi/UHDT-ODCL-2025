import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2 as cv
import pandas as pd
import os
from Color import *

# List of valid class names (color names)
valid_class_names = ["RED", "ORANGE", "BROWN", "GREEN", "BLUE", "PURPLE", "BLACK", "WHITE"]

# Function to convert a cv2 (OpenCV) image to a PhotoImage for tkinter
def cv2_to_tkinter_image(cv2_image, index):
    if cv2_image is None:
        print(f"Error: OpenCV image at index {index} is None!")
        return None
    try:
        cv2_image_rgb = cv.cvtColor(cv2_image, cv.COLOR_BGR2RGB)  # Convert to RGB format
        pil_image = Image.fromarray(cv2_image_rgb)  # Convert to PIL format
        pil_image = pil_image.resize((150, 150))  # Resize image
        tk_image = ImageTk.PhotoImage(pil_image)  # Convert to Tkinter format
        print(f"Image at index {index} successfully converted to Tkinter format")
        return tk_image
    except Exception as e:
        print(f"Error converting OpenCV image at index {index}: {e}")
        return None

# Function to check if the entered class is valid
def validate_class_name(class_value):
    if not class_value:
        return True  # Empty values are valid
    return class_value.upper() in valid_class_names

# Function to display multiple images (cv2 images) and class entry fields using Tkinter
def create_gui(cv_images, rgb_values, csv_df, csv_file_path):
    root = tk.Tk()
    root.title("Image Display with Class Entry")

    # Ensure the window is always on top
    root.attributes("-topmost", True)

    image_labels = []  # To store image label references
    class_entries = []  # To store class entry references
    existing_class_labels = []  # To store existing class labels

    for idx, cv_image in enumerate(cv_images):
        # Convert OpenCV image to Tkinter-compatible format
        tk_image = cv2_to_tkinter_image(cv_image, idx)
        
        if tk_image is None:
            print(f"Failed to convert image at index {idx}. Skipping.")
            continue

        # Create a label to display the image
        label = tk.Label(root, image=tk_image)
        label.image = tk_image  # Keep a reference to avoid garbage collection
        label.grid(row=idx // 2, column=idx % 2, padx=10, pady=10)  # Display in a 2x2 grid
        image_labels.append(label)  # Store the label reference

        # Only add class entry fields for the last two images
        if idx >= 2:
            # Create entry for class name
            class_entry = tk.Entry(root, width=20)
            class_entry.grid(row=idx//2+1, column=idx%2, padx=10, pady=5)
            class_entries.append(class_entry)

            # Check if this RGB value already has a class in the CSV
            r, g, b = rgb_values[idx-2]
            existing_class = get_class_for_rgb((r, g, b), csv_df)

            if existing_class:
                existing_class_label = tk.Label(root, text=f"Existing Class: {existing_class}")
            else:
                existing_class_label = tk.Label(root, text="No existing class")
            
            existing_class_label.grid(row=idx//2+2, column=idx%2, padx=10, pady=5)
            existing_class_labels.append(existing_class_label)

    # Function to handle the submit action
    def process_input():
        global csv_df  # Declare csv_df as global to allow modification
        data_to_add = []

        # Validate and process class entries
        for idx in range(2, 4):  # Only process bottom two images
            class_value = class_entries[idx-2].get().strip().upper()
            r, g, b = rgb_values[idx-2]

            if not validate_class_name(class_value):
                messagebox.showerror("Invalid Class Name", f"The class '{class_value}' is not valid.")
                return

            # If a valid class was entered, add or update the CSV
            if class_value:
                existing_class = get_class_for_rgb((r, g, b), csv_df)

                # If the RGB value exists in the CSV, update it
                if existing_class:
                    csv_df.loc[(csv_df['r'] == r) & (csv_df['g'] == g) & (csv_df['b'] == b), 'class'] = class_value
                    print(f"Updated class for RGB ({r}, {g}, {b}) to '{class_value}'")
                else:
                    data_to_add.append({"class": class_value, "r": r, "g": g, "b": b})

        # Add new entries to the CSV if any
        if data_to_add:
            new_df = pd.DataFrame(data_to_add)
            csv_df = pd.concat([csv_df, new_df], ignore_index=True)
            print("New entries added to CSV")

        # Save the updated CSV file
        csv_df.to_csv(csv_file_path, index=False)
        print(f"CSV file '{csv_file_path}' updated.")

        root.destroy()

    # Submit button to process the input
    submit_button = tk.Button(root, text="Submit", command=process_input)
    submit_button.grid(row=4, columnspan=2, pady=20)

    root.mainloop()

# Helper function to check if RGB values exist in the CSV and retrieve their class
def get_class_for_rgb(rgb, csv_df):
    row = csv_df[(csv_df['r'] == rgb[0]) & (csv_df['g'] == rgb[1]) & (csv_df['b'] == rgb[2])]
    if not row.empty:
        return row['class'].values[0]  # Return the class name
    return None

# Function to load or create a CSV (only once)
def load_or_create_csv():
    # Create a temporary Tkinter window to keep dialogs on top
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    choice = messagebox.askyesno("CSV File", "Do you want to load an existing CSV file?", parent=root)
    
    if choice:
        csv_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], parent=root)
        if csv_file:
            root.destroy()  # Close the root window after the file dialog
            return pd.read_csv(csv_file), csv_file
    else:
        csv_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], parent=root)
        if csv_file:
            df = pd.DataFrame(columns=['class', 'r', 'g', 'b', 'last_file_processed'])
            df.to_csv(csv_file, index=False)  # Save the empty DataFrame to the file
            root.destroy()  # Close the root window after the file dialog
            return df, csv_file
    root.destroy()

# Function to remember where we left off by saving the last processed file
def get_last_processed_file(csv_df):
    if 'last_file_processed' in csv_df.columns and not csv_df['last_file_processed'].isnull().all():
        return csv_df['last_file_processed'].iloc[-1]
    return None

# Function to update the last processed file in the CSV
def update_last_processed_file(csv_df, csv_file_path, last_file):
    csv_df['last_file_processed'] = last_file
    csv_df.to_csv(csv_file_path, index=False)

# Test with multiple images and RGB values
if __name__ == "__main__":
    folder_path = os.path.join('cropped_images', 'datasets', 'processed', '3-8-24 DJI Images-10')

    # Load or create the CSV file
    csv_df, csv_file_path = load_or_create_csv()

    # Get the last processed file
    last_processed_file = get_last_processed_file(csv_df)

    # Get the sorted list of files
    img_files = sorted(os.listdir(folder_path))

    # If there was a last processed file, start from the next file
    if last_processed_file and last_processed_file in img_files:
        start_index = img_files.index(last_processed_file) + 1
    else:
        start_index = 0

    for img_file_path in img_files[start_index:]:
        img = cv.imread(os.path.join(folder_path, img_file_path))

        if img is None:
            print(f"Error: Image file {img_file_path} could not be loaded.")
            continue

        orig_img = img
        img, colors, bg_masked, alphanum_masked, bg_mask, alphanum_mask = classify_color(img)
        print(colors)

        cv_images = [orig_img, img, bg_masked, alphanum_masked]

        rgb_values = [
            colors[1][2].tolist(),
            colors[2][2].tolist()
        ]

        # Pass the list of cv2 images, RGB values, and the CSV data
        create_gui(cv_images, rgb_values, csv_df, csv_file_path)

        # Update the last processed file in the CSV
        update_last_processed_file(csv_df, csv_file_path, img_file_path)
