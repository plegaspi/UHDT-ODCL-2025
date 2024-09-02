import cv2
import numpy as np
from rembg import remove, new_session


##########
# Usage
#
# Function of interest: color_classification
# Return Values: detected_bg_color, detected_alphanum_color, bg_hsv, alphanum_hsv, bg_mask, alphanum_mask, segmented_info
# Notes: LapSRN is used for upscaling the images. opencv-contrib must be installed for upscaling support.
#
###########



#####################
# Core Functions
#####################
def identify_color(cluster_center):
    # Convert BGR cluster to HSV
    bgr = np.uint8([[cluster_center]])
    h, s, v = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[0][0]
    if 28.5 < h < 33 and s > 250 and v > 250:
        return 'BACKGROUND'

    if v <= 50:
        return 'BLACK'
    elif v >= 248 and s <= 71:
        return 'WHITE'

    if h <= 10 or h >= 160:
        if 0 <= h < 5:
            if v < 200:
                if 129 < s < 135:
                    return "BLACK"
                else:
                    return "BROWN"
            else:
                if s < 40:
                    return "WHITE"
                else:
                    return "RED"
        if 5 <= h <= 10:
            if s < 120:
                if v >= 232:
                    if 22 < s < 31:
                        return "WHITE"
                    else:
                        return "ORANGE"
                else:
                    if s < 113:
                        return "ORANGE"
                    return "BROWN"
            elif s < 220:
                if v < 220:
                    if v > 217:
                        if 125 < s < 220:
                            return "PURPLE"
                        else:
                            return "BROWN"
                    else:
                        return "BROWN"
                    return "BROWN"
                else:
                    if s < 200:
                        return "ORANGE"
                    else:
                        return "RED"
            else:
                if s > 240:
                    return "WHITE"
                else:
                    return 'RED'
        if 160 <= h:
            if v < 210:
                if 138 < s < 146:
                    return "RED"
                elif 165 < s < 178:
                    return "RED"
                elif 123 < s < 132:
                    if h < 170:
                        return "ORANGE"
                    else:
                        return "BROWN"
                elif 153 < s < 160:
                    return "BLACK"
                elif 48 < s < 59:
                    return "ORANGE"
                else:
                    return "BROWN"
            else:
                print('B')
                if (h < 170) and (163 < s < 178):
                    return "PURPLE"
                elif 40 < s < 58:
                    return "ORANGE"
                else:
                    return "RED"
        else:
            return "RED"
    elif 10 < h <= 33:
        if 10 < h <= 12:
            if v > 200:
                return "ORANGE"
            else:
                return "BROWN"
        else:
            if v >= 235:
                return "ORANGE"
            else:
                if 157 < s < 165:
                    return "BLACK"
                return "BROWN"

    elif 33 < h <= 75:
        if v > 200:
            return "ORANGE"
        else:
            if v < 120:
                if 135 < s < 141:
                    return "BROWN"
                return "GREEN"
            else:
                return "BROWN"
    elif 75 < h <= 100:
        print("TEST5")
        if s < 50:
            if s < 6:
                if v > 245:
                    return "WHITE"
                else:
                    return "ORANGE"
            else:
                return "BROWN"
        elif 158 < s < 202:
            if 159 < v < 192:
                return "BLACK"
            if 210 < v < 214:
                return "BLACK"
            else:
                return "GREEN"
        elif s > 248:
            if 75 < h < 96:
                if 148 < v < 154:
                    if s > 254:
                        return "GREEN"
                    else:
                        return "BLACK"
                elif 125 < v < 135:
                    return "BLACK"
                else:
                    return "GREEN"
            else:

                return "BLUE"
        else:
            if s > 242:
                if 213 < v < 223:
                    return "GREEN"
                else:
                    return "BLACK"
            else:
                if v > 249:
                    return "WHITE"
                elif 213 < v < 225:
                    return "GREEN"
                elif 133 < v < 137:
                    return "BLACK"
                elif 174 < s < 178:
                    return "GREEN"
                else:
                    if h > 98 and s > 226:
                        return "BLUE"
                    return "GREEN"
    elif 100 < h <= 120:
        if s < 4:
            return "BROWN"
        elif s < 23:
            if v > 210:
                return "WHITE"
            return "BLACK"
        elif 40 < s < 50:
            if v > 243:
                return "WHITE"
            elif 200 < v < 212:
                return "ORANGE"
            else:
                return "BLACK"
        elif (73 < s < 83) and (v > 240):
            return "WHITE"
        elif 112 < s < 120:
            return "GREEN"
        elif 121 < s < 129:
            return "BLACK"
        elif 120 < s < 128:
            return "BLACK"
        elif 158 < s < 165:
            if v > 219:
                return "BLUE"
            else:
                return "BROWN"
        elif 165 <= s <= 169:
            return "GREEN"
        elif 169 < s < 180:
            return "BROWN"
        elif 185 < s < 195:
            if 127 < v < 135:
                return "BLACK"
            else:
                return "BLUE"
        elif 163 < v < 180:
            return "BLACK"
        else:
            return "BLUE"
    elif 120 < h <= 130:
        if v < 200:
            if 180 < v < 210:
                return "PURPLE"
            else:
                return "BROWN"
        else:
            if v > 237:
                return "WHITE"
            elif 200 < v < 213:
                return "PURPLE"
            else:
                return "BLUE"
    elif 130 < h <= 159:
        print('H')
        if v < 223:
            if 103 < s < 111:
                return "BLUE"
            elif 138 < s < 144:
                return "RED"
            elif 189 < s < 195:
                if v < 160:
                    return "PURPLE"
                else:
                    return "RED"
            elif 17 < s < 23:
                return "RED"
            elif 50 < s < 60:
                return "BLUE"
            elif 84 < s < 91:
                return "ORANGE"
            else:
                return "PURPLE"
        else:
            if v > 226:
                if s < 24:
                    return "RED"
                else:
                    return "BLUE"
            else:
                return "PURPLE"
    return 'UNKNOWN'


def create_masks(image, color):
    mask = 0
    hsv = color
    mask += cv2.inRange(image, np.array(hsv), np.array(hsv))
    return mask

def segment_image(img, k):
    color_count = {
        'BLACK': 0,
        'WHITE': 0,
        'RED': 0,
        'BROWN': 0,
        'ORANGE': 0,
        'GREEN': 0,
        'BLUE': 0,
        'PURPLE': 0,
        'BACKGROUND': 0,
        'UNKNOWN': 0
    }

    # Reshape the image to a 2D array of pixels
    pixels = img.reshape((-1, 3))
    pixels = np.float32(pixels)
    total_pixels = pixels.shape[0]

    # Define criteria and apply kmeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.85)
    retval, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

    # Convert back to 8-bit values
    centers = np.uint8(centers)
    segmented_data = centers[labels.flatten()]
    segmented_image = segmented_data.reshape(img.shape)

    return segmented_image, color_count, centers, labels, total_pixels

def extract_colors(color_count, centers, labels, total_pixels, debug = False):
    unique_labels, counts = np.unique(labels, return_counts=True)

    # Identify and count the colors, and calculate their percentages
    color_data = []

    for label, count in zip(unique_labels, counts):
        color_name = identify_color(centers[label])
        percentage = (count / total_pixels) * 100
        hsv = np.array(centers[label]).tolist()
        color_data.append((color_name, count, percentage, label, hsv))
        if debug:
            print("Color Debug")
            print(label, ':', centers[label], hsv)

    # Sort by percentage in descending order
    color_data.sort(key=lambda x: x[2], reverse=True)

    # Unique colors identified
    colors = []

    for color_name, count, percentage, label, hsv in color_data:
        if debug:
            print(f"Label: {label}, Color: {color_name} ({hsv}), Count: {count}, Percentage: {percentage:.2f}")
        if color_name == 'BACKGROUND' and color_count['BACKGROUND'] < 1:
            color_count['BACKGROUND'] += 1
            continue
        else:
            colors.append((color_name, label, hsv, percentage))
            color_count[color_name] += 1
    return colors, color_data

def color_classification(img):
    # Image processing steps
    #img = enhance_image(img, 8, True)
    img = fillBackground(img, (0, 255, 255))
    results = segment_image(img, 3)
    segmented_img, color_count, centers, labels, total_pixels = results
    colors, color_data = extract_colors(color_count, centers, labels, total_pixels, False)
    detected_bg_color= colors[0][0]
    detected_alphanum_color = colors[1][0]
    bg_hsv = colors[0][2]
    alphanum_hsv = colors[1][2]
    bg_mask = create_masks(segmented_img, bg_hsv)
    bg_mask_result = cv2.bitwise_and(segmented_img, segmented_img, mask=bg_mask)
    alphanum_mask = create_masks(segmented_img, alphanum_hsv)
    alphanum_mask_result = cv2.bitwise_and(segmented_img, segmented_img, mask=alphanum_mask)
    segmented_info =  (segmented_img, color_count, centers, labels, total_pixels)
    return detected_bg_color, detected_alphanum_color, cv2.cvtColor(np.uint8([[bg_hsv]]), cv2.COLOR_BGR2HSV), cv2.cvtColor(np.uint8([[alphanum_hsv]]), cv2.COLOR_BGR2HSV), bg_mask, alphanum_mask, segmented_info

######################################
# Masking and Morphological Operations
######################################

def fillBackground(img, color, erosion_applied = True):
    model_name = "u2net"
    session = new_session(model_name)
    height, width, _ = img.shape
    mask = remove(img, alpha_matting=True, alpha_matting_foreground_threshold=300,
                  alpha_matting_background_threshold=300, alpha_matting_erode_size=70, session=session, masks=True,
                  post_process_mask=True, only_mask=True)
    yellow_background = np.full((height, width, 3), color, dtype=np.uint8)
    if (erosion_applied):
        mask = apply_erosion(mask, (6, 6), 1)
        mask = apply_erosion(mask, (5, 5), 1)
        mask = apply_erosion(mask, (2, 2), 1)
    _, binary_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    alpha_channel = np.where(binary_mask == 255, 255, 0).astype(np.uint8)
    bool_mask = mask.astype(bool)

    img[~bool_mask] = yellow_background[~bool_mask]

    return img
def apply_erosion(image, kernel_size=(5, 5), iterations=1):
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.erode(image, kernel, iterations=iterations)

######################################
# Image Pre-processing Functions
######################################
def upscale_image(img, iterations=4):
    model = cv2.dnn_superres.DnnSuperResImpl_create()
    model_path = 'LapSRN_x2.pb'
    model.readModel(model_path)
    model.setModel('lapsrn', 2)

    height, width, _ = img.shape

    for i in range(iterations):
        img = model.upsample(img)
        img = cv2.resize(img, (width, height), cv2.INTER_AREA)
    return img

def enhance_image(img, upscale_iterations, boostSaturation=True):
    img = upscale_image(img, upscale_iterations)
    if boostSaturation:
        img = increase_saturation(img)
    return img


def increase_saturation(image, saturation_scale=1.5):
    # Convert the image from BGR to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Convert to float32 to prevent clipping during scaling
    hsv_image = hsv_image.astype(np.float32)

    # Scale the saturation by the specified factor
    hsv_image[:, :, 1] *= saturation_scale

    # Clip values to stay within valid range [0, 255]
    hsv_image[:, :, 1] = np.clip(hsv_image[:, :, 1], 0, 255)

    # Convert back to uint8
    hsv_image = np.uint8(hsv_image)

    # Convert the HSV image back to BGR color space
    bgr_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    return bgr_image





