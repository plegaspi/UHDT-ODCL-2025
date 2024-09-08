from sklearn.cluster import KMeans
import cv2 as cv
import numpy as np
from rembg import remove, new_session
import os


def identify_color(cluster_center):
    # Convert BGR cluster to HSV
    bgr = np.uint8([[cluster_center]])
    h, s, v = cv.cvtColor(bgr, cv.COLOR_BGR2HSV)[0][0]
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



def quantize_image(img, k):
    x = img.reshape((-1, 3))
    total_pixels = x.shape[0]

    kmeans = KMeans(n_clusters=k, init="k-means++").fit(x)

    centers = np.uint8(kmeans.cluster_centers_)
    labels = np.uint8(kmeans.labels_)

    unique_labels, counts = np.unique(labels, return_counts=True)

    color_data = []
    for label, count in zip(unique_labels, counts):
        percentage = (count/total_pixels) * 100
        color_values = np.array(centers[label])
        color_data.append((color_values, count, percentage, label))

    color_data.sort(key=lambda x: x[1], reverse=True)    


    quantized_data = centers[labels.flatten()]
    quantized_image = quantized_data.reshape(img.shape)
    return quantized_image, color_data


def process_color_data(color_data, debug=False):
    colors = []

    for color_values, count, percentage, label in color_data:
        color_name = identify_color(color_values)
        colors.append((color_name, label, color_values))
    return colors

def apply_erosion(image, kernel_size=(5, 5), iterations=2):
    kernel = np.ones(kernel_size, np.uint8)
    return cv.erode(image, kernel, iterations=iterations)

def apply_dilation(image, kernel_size=(5, 5), iterations=2):
    kernel = np.ones(kernel_size, np.uint8)
    return cv.dilate(image, kernel, iterations=iterations)

def fillBackground(img, color, erosion_applied = True):
    model_name = "isnet-general-use"
    session = new_session(model_name)
    height, width, _ = img.shape
    mask = remove(img, alpha_matting=True, alpha_matting_foreground_threshold=300,
                  alpha_matting_background_threshold=300, alpha_matting_erode_size=70, session=session, masks=True,
                  post_process_mask=True, only_mask=True)
    yellow_background = np.full((height, width, 3), color, dtype=np.uint8)
    if (erosion_applied):
        mask = apply_erosion(mask, (3, 3), 1)

    _, binary_mask = cv.threshold(mask, 127, 255, cv.THRESH_BINARY)
    alpha_channel = np.where(binary_mask == 255, 255, 0).astype(np.uint8)
    bool_mask = mask.astype(bool)
    img[~bool_mask] = yellow_background[~bool_mask]

    return img

def create_masks(image, color_value):
    mask = 0
    mask += cv.inRange(image, color_value, color_value)
    return mask

def classify_color(img, initial_k=30):
    quantized_img = quantize_image(img,initial_k)[0]
    filtered_img = cv.bilateralFilter(quantized_img, 10, 50, 25)
    bg_removed_img = fillBackground(filtered_img, (0, 255, 255))
    final_img, color_data = quantize_image(bg_removed_img, 3)
    colors = process_color_data(color_data, color_count)
    bg_color_values = colors[1][2]
    alphanum_color_values = colors[2][2]
    print(bg_color_values)
    bg_mask = create_masks(final_img, bg_color_values)
    bg_mask_result = cv.bitwise_and(final_img, final_img, mask=bg_mask)
    alphanum_mask = create_masks(final_img, alphanum_color_values)
    alphanum_mask_result = cv.bitwise_and(final_img, final_img, mask=alphanum_mask)
    return final_img, colors, bg_mask_result, alphanum_mask_result

if __name__ == "__main__":
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

    folder_path = os.path.join('cropped_images', 'datasets','processed', '3-8-24 DJI Images-10')
    for img_file_path in os.listdir(folder_path):
        img = cv.imread(os.path.join(folder_path, img_file_path))
        orig_img = img
        img, colors, bg_masked, alphanum_masked = classify_color(img)
        print(colors)
        for i in range(len(colors)):
            print(colors[i][0])
            color_count[colors[i][0]] += 1
        #print(color_count)
        img_arr = np.hstack([orig_img, img, bg_masked, alphanum_masked])
        cv.imshow("Test", img_arr)
        cv.waitKey(0)
        cv.destroyAllWindows()
