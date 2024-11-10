from PIL import Image
import random
import string
import math

def generate_random_string(length):
    characters = string.ascii_letters + string.digits  
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def select_random_target():
    class_list = ['person', 'car', 'motorcycle', 'airplane', 'bus', 'boat', 'stop_sign', 'snowboard', 'umbrella', 'sports_ball', 'baseball_bat', 'bed', 'tennis_racket', 'suitcase', 'skis']
    return class_list[random.randint(0, len(class_list) - 1)]

def translate_class_to_id(class_name):
    object_class_list = ['person', 'car', 'motorcycle', 'airplane', 'bus', 'boat', 'stop_sign', 'snowboard', 'umbrella', 'sports_ball', 'baseball_bat', 'bed', 'tennis_racket', 'suitcase', 'skis']
    for object_class_id, object_class in enumerate(object_class_list):
        if class_name == object_class:
            return object_class_id
    raise ValueError(f"{class_name} is not a valid class")

def scale_target(img, scale_factor):
    width, height = img.size
    width = int(width * scale_factor)
    height = int(height * scale_factor)
    img.thumbnail((width, height), Image.Resampling.LANCZOS)
    return img

def rotate_target(img, angle):
    rotated_img = img.rotate(angle, expand=True)

    bbox = rotated_img.getbbox()
    
    tight_img = rotated_img.crop(bbox)

    return tight_img


def calculate_normalized_coords(bg_img_width, bg_img_height, x1, y1, x2, y2):
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    normalized_center_x = center_x / bg_img_width
    normalized_center_y = center_y / bg_img_height
    normalized_width = (x2 - x1) / bg_img_width
    normalized_height = (y2 - y1) / bg_img_height
    return normalized_center_x, normalized_center_y, normalized_width, normalized_height

def is_overlapping(new_placement, existing_placements):
    for x1, y1, x2, y2 in existing_placements:
        if not (new_placement[2] <= x1 or new_placement[0] >= x2 or 
                new_placement[3] <= y1 or new_placement[1] >= y2):
            return True  
    return False

def is_within_visible_threshold(x1, y1, x2, y2, bg_img_width, bg_img_height):
    visible_width = min(x2, bg_img_width) - max(x1, 0)
    visible_height = min(y2, bg_img_height) - max(y1, 0)
    visible_area = max(visible_width, 0) * max(visible_height, 0)
    img_area = (x2 - x1) * (y2 - y1)
    return visible_area >= 0.5 * img_area

def generate_translations(bg_img, imgs, class_ids):
    bg_img_width, bg_img_height = bg_img.size
    max_img_width, max_img_height = int(bg_img_width * 0.2), int(bg_img_height * 0.2)
    existing_placements = []
    annotations = []

    for img_index, img in enumerate(imgs):
        img_width, img_height = img.size
        if img_width > max_img_width or img_height > max_img_height:
            img.thumbnail((max_img_width, max_img_height), Image.Resampling.LANCZOS)
            img_width, img_height = img.size

        for _ in range(100): 
            x1 = random.randint(-img_width // 2, bg_img_width - img_width // 2)
            y1 = random.randint(-img_height // 2, bg_img_height - img_height // 2)
            x2 = x1 + img_width
            y2 = y1 + img_height
            new_placement = (x1, y1, x2, y2)

            if not is_overlapping(new_placement, existing_placements) and is_within_visible_threshold(x1, y1, x2, y2, bg_img_width, bg_img_height):
                bg_img.paste(img, (x1, y1), img if img.mode == 'RGBA' else None)
                existing_placements.append(new_placement)
                normalized_center_x, normalized_center_y, normalized_width, normalized_height = calculate_normalized_coords(bg_img_width, bg_img_height, x1, y1, x2, y2)
                annotation = f"{class_ids[img_index]} {normalized_center_x} {normalized_center_y} {normalized_width} {normalized_height}"
                annotations.append(annotation)
                break
        else:
            print("Could not place an image without overlap after 100 attempts.")

    return bg_img, annotations

def write_annotations(obj_label_file_path, annotations):
    with open(obj_label_file_path, '+a') as label_file:
        for annotation in annotations:
            label_file.write(f"{annotation}\n")
