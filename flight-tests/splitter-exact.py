from PIL import Image
import os
import math

Image.MAX_IMAGE_PIXELS = None  # Prevent decompression bomb errors

# User-defined settings
TARGET_WIDTH_IN = 118  # Target width in inches
TARGET_HEIGHT_IN = 80  # Target height in inches
DPI = 300  # Desired print resolution

A0_WIDTH_MM = 841
A0_HEIGHT_MM = 1189

MARGIN_INCHES = 1  # White margin on all sides
MARGIN_PX = int(DPI * MARGIN_INCHES)

# Convert A0 paper size to pixels at the given DPI
A0_WIDTH_PX = int(A0_WIDTH_MM * DPI / 25.4)
A0_HEIGHT_PX = int(A0_HEIGHT_MM * DPI / 25.4)

# Effective area within margins
EFFECTIVE_WIDTH_PX = A0_WIDTH_PX - 2 * MARGIN_PX
EFFECTIVE_HEIGHT_PX = A0_HEIGHT_PX - 2 * MARGIN_PX

# Convert target image size to pixels
TARGET_WIDTH_PX = int(TARGET_WIDTH_IN * DPI)
TARGET_HEIGHT_PX = int(TARGET_HEIGHT_IN * DPI)

def determine_grid_size():
    """Determine the best rows × columns for A0-sized prints."""
    cols = math.ceil(TARGET_WIDTH_PX / EFFECTIVE_WIDTH_PX)
    rows = math.ceil(TARGET_HEIGHT_PX / EFFECTIVE_HEIGHT_PX)
    return rows, cols

def resize_image_exact(image):
    """Resize the image exactly to the target dimensions (stretched if necessary)."""
    return image.resize((TARGET_WIDTH_PX, TARGET_HEIGHT_PX), Image.LANCZOS)

def chop_and_save(image, output_folder):
    """Chop the image into variable-sized grid sections and save each with margins."""
    os.makedirs(output_folder, exist_ok=True)
    rows, cols = determine_grid_size()

    for row in range(rows):
        for col in range(cols):
            left = col * EFFECTIVE_WIDTH_PX
            upper = row * EFFECTIVE_HEIGHT_PX
            right = min(left + EFFECTIVE_WIDTH_PX, TARGET_WIDTH_PX)
            lower = min(upper + EFFECTIVE_HEIGHT_PX, TARGET_HEIGHT_PX)

            cropped = image.crop((left, upper, right, lower))

            # Create a white background canvas
            background = Image.new("RGB", (A0_WIDTH_PX, A0_HEIGHT_PX), "white")
            background.paste(cropped, (MARGIN_PX, MARGIN_PX))

            output_path = os.path.join(output_folder, f"part_{row+1}_{col+1}.jpg")
            background.save(output_path, dpi=(DPI, DPI))
            print(f"Saved {output_path}")

def main(input_image_path, output_folder="output_images"):
    image = Image.open(input_image_path)

    # Resize to exact dimensions (stretched if needed)
    resized_exact = resize_image_exact(image)
    resized_exact.save(os.path.join(output_folder, "resized_exact.jpg"), dpi=(DPI, DPI))
    print("Saved resized image with exact dimensions.")

    # Chop the exact-resized image into A0 sections
    chop_and_save(resized_exact, output_folder)

if __name__ == "__main__":
    input_image = "/Users/plegaspi/Desktop/Untitled 6.png"  # Replace with your image path
    main(input_image, "test_exact_dir")