import os
import cv2
import argparse
import numpy as np
from glob import glob

# Default Configurations
GRID_SIZE = (2, 2)  # Grid rows and columns
WINDOW_NAME = "Detections"

def get_images(folder):
    """Fetch all image file paths in the folder."""
    return sorted(glob(os.path.join(folder, "*.jpg")) + 
                  glob(os.path.join(folder, "*.jpeg")) + 
                  glob(os.path.join(folder, "*.png")))

def create_image_grid(image_paths, grid_size):
    """Creates an OpenCV image grid from a list of images."""
    if not image_paths:
        return np.zeros((500, 500, 3), dtype=np.uint8)  # Return a blank image if no images exist
    
    images = [cv2.imread(img) for img in image_paths]

    # Resize images to fit the grid
    min_width = min(img.shape[1] for img in images)
    min_height = min(img.shape[0] for img in images)
    images = [cv2.resize(img, (min_width, min_height)) for img in images]

    # Calculate grid shape
    rows, cols = grid_size
    total_slots = rows * cols

    # Fill the grid with images (or black placeholders)
    while len(images) < total_slots:
        images.append(np.zeros((min_height, min_width, 3), dtype=np.uint8))

    # Stack images into a grid
    image_rows = [np.hstack(images[i * cols:(i + 1) * cols]) for i in range(rows)]
    grid = np.vstack(image_rows)
    
    return grid

def main(watch_dir):
    """Displays the image grid once and exits when the user closes the window."""
    if not os.path.exists(watch_dir):
        print(f"Error: Directory '{watch_dir}' does not exist.")
        return

    image_paths = get_images(watch_dir)
    if not image_paths:
        print("No images found in the directory.")
        return

    grid_image = create_image_grid(image_paths[:GRID_SIZE[0] * GRID_SIZE[1]], GRID_SIZE)
    cv2.imshow(WINDOW_NAME, grid_image)

    # Wait until user closes the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display images from a folder in a grid.")
    parser.add_argument("watch_dir", type=str, help="Path to the directory containing images")
    args = parser.parse_args()

    main(args.watch_dir)