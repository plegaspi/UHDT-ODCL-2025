from PIL import Image
import os
import math

Image.MAX_IMAGE_PIXELS = None  


#################
# Configuration #
#################
SOURCE_IMAGE = "home.jpg"
OUTPUT_DIR = "flight-tests/output"
TARGET_WIDTH_IN = 118  
TARGET_HEIGHT_IN = 80 
DPI = 300  #

A0_WIDTH_MM = 841
A0_HEIGHT_MM = 1189

MARGIN_INCHES = 1  
MARGIN_PX = int(DPI * MARGIN_INCHES)


A0_WIDTH_PX = int(A0_WIDTH_MM * DPI / 25.4)
A0_HEIGHT_PX = int(A0_HEIGHT_MM * DPI / 25.4)


EFFECTIVE_WIDTH_PX = A0_WIDTH_PX - 2 * MARGIN_PX
EFFECTIVE_HEIGHT_PX = A0_HEIGHT_PX - 2 * MARGIN_PX


TARGET_WIDTH_PX = int(TARGET_WIDTH_IN * DPI)
TARGET_HEIGHT_PX = int(TARGET_HEIGHT_IN * DPI)

def determine_grid_size():
    cols = math.ceil(TARGET_WIDTH_PX / EFFECTIVE_WIDTH_PX)
    rows = math.ceil(TARGET_HEIGHT_PX / EFFECTIVE_HEIGHT_PX)
    return rows, cols

def resize_image(image):
    original_width, original_height = image.size
    aspect_ratio = original_width / original_height


    target_aspect_ratio = TARGET_WIDTH_PX / TARGET_HEIGHT_PX

    if aspect_ratio > target_aspect_ratio:
        new_width = TARGET_WIDTH_PX
        new_height = int(TARGET_WIDTH_PX / aspect_ratio)
    else:
        new_height = TARGET_HEIGHT_PX
        new_width = int(TARGET_HEIGHT_PX * aspect_ratio)

    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    background = Image.new("RGB", (TARGET_WIDTH_PX, TARGET_HEIGHT_PX), "white")
    x_offset = (TARGET_WIDTH_PX - new_width) // 2
    y_offset = (TARGET_HEIGHT_PX - new_height) // 2
    background.paste(resized_image, (x_offset, y_offset))

    return background

def chop_and_save(image, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    rows, cols = determine_grid_size()

    for row in range(rows):
        for col in range(cols):
            left = col * EFFECTIVE_WIDTH_PX
            upper = row * EFFECTIVE_HEIGHT_PX
            right = min(left + EFFECTIVE_WIDTH_PX, TARGET_WIDTH_PX)
            lower = min(upper + EFFECTIVE_HEIGHT_PX, TARGET_HEIGHT_PX)

            cropped = image.crop((left, upper, right, lower))

            background = Image.new("RGB", (A0_WIDTH_PX, A0_HEIGHT_PX), "white")
            background.paste(cropped, (MARGIN_PX, MARGIN_PX))

            output_path = os.path.join(output_folder, f"part_{row+1}_{col+1}.jpg")
            background.save(output_path, dpi=(DPI, DPI))
            print(f"Saved {output_path}")

def main(input_image_path, output_folder="output_images"):
    image = Image.open(input_image_path)
    resized_image = resize_image(image)
    chop_and_save(resized_image, output_folder)

if __name__ == "__main__":
    main(SOURCE_IMAGE, OUTPUT_DIR)