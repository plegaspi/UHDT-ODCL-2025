from PIL import Image, ImageDraw, ImageFont
import glob
import numpy as np
import os
import random
import string
from datetime import datetime

def calculate_centroid(points):
    x = points[:, 0]
    y = points[:, 1]

    x = np.append(x, x[0])
    y = np.append(y, y[0])

    A = 0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])
    
    Cx = (1 / (6 * A)) * np.sum((x[:-1] + x[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1]))
    Cy = (1 / (6 * A)) * np.sum((y[:-1] + y[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1]))

    return Cx, Cy

def calculate_bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)
    return [min(x_coordinates), min(y_coordinates), max(x_coordinates), max(y_coordinates)]

def generate_arc_points(center, radius, start_angle, end_angle, num_points=100):
    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), num_points)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return list(zip(x, y))

def apply_scaling_and_translation(points, translation, scale, center):
    points = np.array(points)
    points = (points - center) * scale + center
    points += np.array(translation)
    return points


def apply_rotation(points, rotation, center):
    points = np.array(points)
    theta = np.radians(rotation)
    rotation_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])
    points = np.dot(points - center, rotation_matrix) + center
    return points

def pick_random_color():
    White = (255, 255, 255)
    Black = (0, 0, 0)
    Red = (255, 0, 0)
    Blue = (0, 0, 255)
    Green = (0, 255, 0)
    Purple = (128, 0, 128)
    Brown = (150, 75, 0)
    Orange = (255, 165, 0)
    colors = [White, Black, Red, Blue, Green, Purple, Brown, Orange]
    color = colors[random.randint(0, 7)]
    return color

def pick_random_alphanum():
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
               "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    return letters[random.randint(0, 35)]

def pick_random_shape():
    shapes = ["circle", "cross", "pentagon", "quartercircle", "rectangle", "semicircle", "star", "triangle"]
    shape = shapes[random.randint(0,7)]
    return shape

def generate_random_string(length):
    characters = string.ascii_letters + string.digits  
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def get_shape_class_id(shape):
    shapes = {
        'circle': 0,
        'cross': 1,
        'pentagon': 2,
        'quartercircle': 3,
        'rectangle': 4,
        'semicircle': 5,
        'star': 6,
        'triangle': 7
    }
    return shapes[shape]


def place_font_on_target(image, centroid, char, font_family, font_size, alphanum_color=(0,0,0), angle=0, scale=1):  
    image_base =  image
    draw = ImageDraw.Draw(image_base)
    width, height = image_base.size
    true_font_height = font_size * scale
    font = ImageFont.truetype(font_family, true_font_height)
    font_width = font.getlength(char)
    font_image_canvas = Image.new('RGBA', (int(true_font_height), int(true_font_height)), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(font_image_canvas)
    font_image_width, font_image_height = font_image_canvas.size
    center_x, center_y = (font_image_width // 2, font_image_height // 2)
    draw2.text((center_x, center_y), char, font=font, anchor="mm", fill=alphanum_color)
    font_image_canvas = font_image_canvas.rotate(angle)
    image_base.paste(font_image_canvas, (int(centroid[0] -font_image_height//2), int(centroid[1]-font_image_height//2)), font_image_canvas)
    return image_base


def draw_shape(background_img, shape, translation=(0, 0), rotation=0, scale=1, shape_color=(255, 0, 0), alphanum_color=(0,0,0), text='A', font_path='arial.ttf', padding=20, cross_thickness=32):
    draw = ImageDraw.Draw(background_img)
    center = np.array(background_img.size) // 2
    radius = 160

    if shape == 'triangle':
        points = np.array([[-np.sqrt(3)/2 * 160, 160 / 2], [np.sqrt(3)/2 * 160, 160 / 2], [0, -160]]) + center

    elif shape == 'star':
        padding = 0
        points = np.array([[0, -160], [44, -48], [150, -48], [74, 22], [94, 128], 
                           [0, 80], [-94, 128], [-74, 22], [-150, -48], [-44, -48]]) + center
        inner_points = [points[i] for i in [1, 3, 5, 7, 9]]
    
    elif shape == 'rectangle':
        points = np.array([[-160, -80], [160, -80], [160, 80], [-160, 80]]) + center
    
    elif shape == 'pentagon':
        points = np.array([[0, -160], [150, -48], [94, 128], [-94, 128], [-150, -48]]) + center
    
    elif shape == 'circle':
        points = generate_arc_points(center, radius, 0, 360)
    
    elif shape == 'quartercircle':
        adjusted_center = (center[0] - radius // 2, center[1] + radius // 2)
        p1 = (adjusted_center[0] + radius, adjusted_center[1])
        p2 = (adjusted_center[0], adjusted_center[1] - radius)
        p3 = adjusted_center
        arc_points = generate_arc_points(p3, radius, 0, -90)
        points = [p1] + arc_points + [p2, p3]
    
    elif shape == 'semicircle':
        adjusted_center = (center[0], center[1] + radius // 2)
        arc_points = generate_arc_points(adjusted_center, radius, 180, 360)
        points = [(adjusted_center[0] - radius, adjusted_center[1])] + arc_points + [(adjusted_center[0] + radius, adjusted_center[1])]
    
    elif shape == 'cross':
        cross_thickness = 100
        padding = 0
        half_thickness = cross_thickness // 2
        points = np.array([[-160, -half_thickness], [-half_thickness, -half_thickness], [-half_thickness, -160], 
                           [half_thickness, -160], [half_thickness, -half_thickness], [160, -half_thickness], 
                           [160, half_thickness], [half_thickness, half_thickness], [half_thickness, 160], 
                           [-half_thickness, 160], [-half_thickness, half_thickness], [-160, half_thickness]]) + center
        inner_points = [points[i] for i in [1, 4, 7, 10]]
    
    else:
        raise ValueError("Shape not recognized")


    # Rotate shape
    points = apply_rotation(points, rotation, center)
    if shape in ['star', 'cross']:
        inner_points = apply_rotation(inner_points, rotation, center)

    # Apply scaling and translation
    points = apply_scaling_and_translation(points, translation, scale, center)
    if shape in ['star', 'cross']:
        inner_points = apply_scaling_and_translation(inner_points, translation, scale, center)


    if len(points) >= 3:
        draw.polygon([tuple(p) for p in points], fill=shape_color)

    if shape in ['star', 'cross']:
        shape_bounds = calculate_bounding_box(inner_points)
    else:
        shape_bounds = calculate_bounding_box(points)

    centroid = calculate_centroid(points)
    image = place_font_on_target(background_img, centroid, text, font_path, 100, alphanum_color, rotation, scale)


    return image, points, centroid

def is_valid_translation(new_translation, existing_translations, min_distance):
    if len(existing_translations) == 0:
        return True

    existing_translations = np.array(existing_translations)
    
    distances = np.sqrt(np.sum((existing_translations - new_translation) ** 2, axis=1))
    
    return np.all(distances >= min_distance)

def generate_translations(img, num_targets, padding=160):
    img_width, img_height = img.size
    
    max_x_offset = img_width // 2 - padding
    max_y_offset = img_height // 2 - padding
    
    translations = []
    min_distance = 2 * padding 
    
    while len(translations) < num_targets:

        rand_x_offset = random.randint(-max_x_offset, max_x_offset)
        rand_y_offset = random.randint(-max_y_offset, max_y_offset)
        
        new_translation = np.array([rand_x_offset, rand_y_offset])
        
       
        if is_valid_translation(new_translation, translations, min_distance):
            translations.append(new_translation)
    
    return np.array(translations)


        

    


if __name__ == "__main__":
    num_of_images = 2
    max_targets_per_image = 10
    min_targets_per_image = 5
    backgrounds_dir = os.path.join("yolo", "backgrounds")
    backgrounds = [background_img_path for background_img_path in os.listdir(backgrounds_dir) if background_img_path.lower().endswith(('.png', '.jpg', '.jpeg')) and not background_img_path.startswith('.')]
    current_date = datetime.now()
    dataset_base_path = os.path.join("yolo", "datasets",f"{current_date.year}_{current_date.month}_{current_date.day}_{current_date.hour}_{current_date.minute}_{current_date.second}")
    img_dir_path = os.path.join(dataset_base_path, "images")
    cls_img_dir_path = os.path.join(dataset_base_path, "cls-images")
    obj_label_dir_path = os.path.join(dataset_base_path, "obj_labels")
    seg_label_dir_path = os.path.join(dataset_base_path, "seg_labels")
    cls_label_dir_path = os.path.join(dataset_base_path, "cls_labels")
    for i in range(num_of_images):
        sample_name = generate_random_string(10)

        if not os.path.exists(img_dir_path):
            os.makedirs(img_dir_path)

        # Object Detection Label Folder
        if not os.path.exists(obj_label_dir_path):
            os.makedirs(obj_label_dir_path)

        # Segmentation Label Folder
        if not os.path.exists(seg_label_dir_path):
            os.makedirs(seg_label_dir_path)

        # Classification Folders
        if not os.path.exists(cls_img_dir_path):
            os.makedirs(cls_img_dir_path)
        shapes = ["circle", "cross", "pentagon", "quartercircle", "rectangle", "semicircle", "star", "triangle"]
        for x in shapes:
            shape_dir_path = os.path.join(cls_img_dir_path, x)
            os.mkdir(shape_dir_path)


        img_file_path = os.path.join(img_dir_path, f"{sample_name}.png")
        obj_label_file_path = os.path.join(obj_label_dir_path, f"{sample_name}.txt")
        seg_label_file_path = os.path.join(seg_label_dir_path, f"{sample_name}.txt")

        background_index = random.randint(0, len(backgrounds)-1)
        background_img_path = os.path.join(backgrounds_dir, backgrounds[background_index])
        background_img = Image.open(background_img_path)
        num_targets_in_image = random.randint(min_targets_per_image,max_targets_per_image-1)
        translations = generate_translations(background_img, num_targets_in_image, 180)
        
        for i in range(num_targets_in_image):
            shape = pick_random_shape()
            shape_color = pick_random_color()
            alphanum_color = pick_random_color()
            while alphanum_color == shape_color:
                alphanum_color = pick_random_color()
            alphanum_char = pick_random_alphanum()
            font_path = os.path.join('yolo', 'arial.ttf')
            angle = random.randint(0, 361);
            scale = random.uniform(0.3, 1.2)
            background_img, points, centroid = draw_shape(background_img, shape, translations[i], angle, scale, shape_color, alphanum_color, alphanum_char, font_path, 10, 32)

            normalized_points = points / np.array(background_img.size)
            shape_id = get_shape_class_id(shape)
            cls_sample_name = generate_random_string(10)
            cls_img_file_path = os.path.join(cls_img_dir_path, shape, f"{cls_sample_name}.png")



            # Object Detection Dataset
            with open(obj_label_file_path, '+a') as label_file:
                min_x = np.min(normalized_points[:, 0])
                max_x = np.max(normalized_points[:, 0])
                min_y = np.min(normalized_points[:, 1])
                max_y = np.max(normalized_points[:, 1])
                label_file.write(f"{shape_id} {(max_x+min_x)/2} {(max_y+min_y)/2} {max_x-min_x} {max_y-min_y}\n")



            # Segmentation Dataset
            with open(seg_label_file_path, '+a') as label_file:
                label_file.write(f"{shape_id} ")
                for point in normalized_points:
                    label_file.write(f"{point[0]} {point[1]} ")
                label_file.write(f"{normalized_points[0][0]} {normalized_points[0][1]}")
                label_file.write(f"\n")


            # Classification Dataset
            padding = 20
            min_x = np.min(points[:, 0]) - padding
            max_x = np.max(points[:, 0]) + padding
            min_y = np.min(points[:, 1]) - padding
            max_y = np.max(points[:, 1]) + padding

            while min_x <= 0:
                min_x += 1
            while max_x >= background_img.width:
                max_x -= 1
            
            while min_y <= 0:
                min_y += 1
            while max_y >= background_img.height:
                max_x -= 1
            
            background_img.crop((min_x, min_y, max_x, max_y)).save(cls_img_file_path)
            
        background_img.save(img_file_path)
        background_img.show()
        




