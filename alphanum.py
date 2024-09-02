import os
import cv2
import re
import pytesseract
from pytesseract import Output
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import time

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Custom configuration for Tesseract
custom_config = ("-c tessedit"
                  "_char_whitelist=37FTX"
                  " --psm 6"
                  )

#Helper function for rotation
def zoom_at(img, zoom=1, angle=0, coord=None):
    
    cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
    
    rot_mat = cv2.getRotationMatrix2D((cx,cy), angle, zoom)
    result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
    
    return result


# Function to perform OCR on an image and return the result with confidence
def image2textConf(img):
    text = []
    results = pytesseract.image_to_data(img, config=custom_config, output_type=Output.DICT)
    text.append(results["text"][len(results["text"]) - 1])
    text.append(results["conf"][len(results["text"]) - 1])
    return text

# Function to process a single image with a whitelist
def image2text(image, whitelist=None):
    custom_config = f"-c tessedit_char_whitelist={whitelist} --psm 6" if whitelist else "-c tessedit""_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"" --psm 6"
    # Read image using OpenCV
    image = cv2.imread(image)
                    
    # Invert colors
    #inverted_image = cv2.bitwise_not(image)
    #inverted_image_pil = Image.fromarray(inverted_image)

    non_invert = Image.fromarray(image)
                    
    # Apply 1.5x resize
    width, height = non_invert.size
    new_size = (int(width * 1), int(height * 1))
    zoomed_image_pil = non_invert.resize(new_size)
                    
    # Display the zoomed image
    plt.imshow(zoomed_image_pil)
    plt.title("Zoomed Image")
    plt.axis('off')
    plt.show()
    
    text = []
    results = pytesseract.image_to_data(zoomed_image_pil, config=custom_config, output_type=Output.DICT)
    text.append(results["text"][len(results["text"]) - 1])
    text.append(results["conf"][len(results["text"]) - 1])
    print(text)


#Use this code if the original function does not work. It rotates the image until it is recognized or until 360 degree rotation is achieved
def image2textRotate(image, whitelist=None):
    start_time = time.time()
    custom_config = f"-c tessedit_char_whitelist={whitelist} --psm 6" if whitelist else "-c tessedit""_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"" --psm 6"
    print(custom_config)
    non_invert = Image.fromarray(image)
                    
    # Apply 1.5x resize
    width, height = non_invert.size
    new_size = (int(width * 1.5), int(height * 1.5))
    zoomed_image_pil = non_invert.resize(new_size)

    best_text = ""
    best_confidence = 0

    #This rotates the character until the model outputs something, change the 3rd number to change how much the image rotates by
    for angle in range(0, 360, 30):
        #print(f"Trying angle {angle}...")
        rotated_image = zoom_at(np.array(zoomed_image_pil), angle=angle % 360)
        results = pytesseract.image_to_data(rotated_image, config=custom_config, output_type=Output.DICT)
        confidences = [int(conf) for conf in results["conf"]]
        if confidences and max(confidences) > -1:
            max_index = confidences.index(max(confidences))
            best_text = results["text"][max_index]
            best_confidence = max(confidences)
            break

    #print("Process finished --- %s seconds ---" % (time.time() - start_time))
    return best_text, best_confidence

