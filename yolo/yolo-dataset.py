from PIL import Image, ImageDraw, ImageFont, ImageFilter
import glob
import numpy as np
import os
import random
import string
from datetime import datetime
import roboflow
from dotenv import load_dotenv
import sys
import cv2 as cv

load_dotenv()



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


def draw_shape(background_img, shape, translation=(0, 0), rotation=0, scale=1, shape_color=(255, 0, 0), alphanum_color=(0,0,0), text='A', font_path='arial.ttf', padding=0, cross_thickness=32):
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


def apply_motion_blur(image, direction='horizontal', blur_strength=15):
    unblurred_img = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    
    if blur_strength <= 0:
        raise ValueError("Blur strength must be a positive integer greater than 0")

    kernel = np.zeros((blur_strength, blur_strength))
    
    if direction.lower() == 'horizontal':
        kernel[int((blur_strength - 1) / 2), :] = np.ones(blur_strength)
        
    elif direction.lower() == 'vertical':
        kernel[:, int((blur_strength - 1) / 2)] = np.ones(blur_strength)

    elif direction.lower() == 'diagonal':
        np.fill_diagonal(kernel, 1)

    else:
        raise ValueError("Direction must be 'horizontal', 'vertical', or 'diagonal'")

    kernel = kernel / blur_strength
    blurred_image = cv.filter2D(unblurred_img, -1, kernel)
    blurred_image = Image.fromarray(cv.cvtColor(blurred_image, cv.COLOR_BGR2RGB))
    
    return blurred_image

if __name__ == "__main__":
    num_of_images = 1000
    max_targets_per_image = 26
    min_targets_per_image = 10
    max_cls_targets = 9000
    cls_targets_counter = 0
    min_angle = 0
    max_angle = 360
    min_scale = 0.25
    max_scale = 0.8
    min_cls_padding = 0
    max_cls_padding = 20
    min_cls_blur_strength = 10
    min_img_blur_strength = 100
    max_cls_blur_strength = 23
    max_img_blur_strength = 110
    erase_after_upload = False
    
    enable_mode = {
        'obj': True,
        'seg': True,
        'cls': True
    }
    
    enable_roboflow = {
        'obj': True,
        'seg': True,
        'cls': False
    }
    
    obj_project_id = os.environ.get("OBJ_PROJ_ID")
    seg_project_id = os.environ.get("SEG_PROJ_ID")
    cls_project_id = os.environ.get("CLS_PROJ_ID")
    

    OBJ_ROBOFLOW_API_KEY = os.environ.get("OBJ_ROBOFLOW_API_KEY")
    SEG_ROBOFLOW_API_KEY = os.environ.get("SEG_ROBOFLOW_API_KEY")
    CLS_ROBOFLOW_API_KEY = os.environ.get("CLS_ROBOFLOW_API_KEY")
    rf_obj = roboflow.Roboflow(api_key=OBJ_ROBOFLOW_API_KEY)
    obj_workspace = rf_obj.workspace()
    obj_project = rf_obj.project(obj_project_id)

    rf_seg = roboflow.Roboflow(api_key=SEG_ROBOFLOW_API_KEY)
    seg_workspace = rf_seg.workspace()
    seg_project = seg_workspace.project(seg_project_id)

    rf_cls = roboflow.Roboflow(api_key=CLS_ROBOFLOW_API_KEY)
    cls_workspace = rf_cls.workspace()
    cls_project = cls_workspace.project(cls_project_id)

    current_date = datetime.now()
    batch_name = f"{current_date.year}_{current_date.month}_{current_date.day}_{current_date.hour}_{current_date.minute}_{current_date.second}"
    backgrounds_dir = os.path.join("yolo", "backgrounds")
    backgrounds = [background_img_path for background_img_path in os.listdir(backgrounds_dir) if background_img_path.lower().endswith(('.png', '.jpg', '.jpeg')) and not background_img_path.startswith('.')]
    dataset_base_path = os.path.join("yolo", "datasets",f"{current_date.year}_{current_date.month}_{current_date.day}_{current_date.hour}_{current_date.minute}_{current_date.second}")
    img_dir_path = os.path.join(dataset_base_path, "images")
    cls_img_dir_path = os.path.join(dataset_base_path, "cls-images")
    obj_label_dir_path = os.path.join(dataset_base_path, "obj_labels")
    seg_label_dir_path = os.path.join(dataset_base_path, "seg_labels")
    cls_label_dir_path = os.path.join(dataset_base_path, "cls_labels")
    annotation_map_file_path = os.path.join('yolo', 'label_map.txt')
    
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
            if not os.path.exists(shape_dir_path):
                os.mkdir(shape_dir_path)
        if not os.path.exists(cls_label_dir_path):
            os.makedirs(cls_label_dir_path)

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
            fonts_dir = os.path.join('yolo', 'fonts')
            font_paths = os.listdir(fonts_dir)
            font_index = random.randint(0, len(font_paths)-1)
            font_path = os.path.join('yolo', 'fonts', font_paths[font_index])
            angle = random.randint(min_angle, max_angle)
            scale = random.uniform(min_scale, max_scale)

            background_img, points, centroid = draw_shape(background_img, shape, translations[i], angle, scale, shape_color, alphanum_color, alphanum_char, font_path, 10, 32)
            normalized_points = points / np.array(background_img.size)
            shape_id = get_shape_class_id(shape)
            cls_sample_name = generate_random_string(10)
            cls_img_file_path = os.path.join(cls_img_dir_path, shape, f"{cls_sample_name}.png")
            cls_label_file_path = os.path.join(cls_label_dir_path, f"{cls_sample_name}.txt")



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


            cls_padding = random.randint(min_cls_padding, max_cls_padding)
            if cls_targets_counter < max_cls_targets:
                # Classification Dataset
                min_x = np.min(points[:, 0]) - cls_padding
                max_x = np.max(points[:, 0]) + cls_padding
                min_y = np.min(points[:, 1]) - cls_padding
                max_y = np.max(points[:, 1]) + cls_padding

                while min_x <= 0:
                    min_x += 1
                while max_x >= background_img.width:
                    max_x -= 1
                
                while min_y <= 0:
                    min_y += 1
                while max_y >= background_img.height:
                    max_x -= 1
                
                
                cls_img = background_img.crop((min_x, min_y, max_x, max_y))
                blur_type = random.choice(['horizontal', 'vertical', 'diagonal', 'none'])
                if blur_type != "none":
                    blur_strength = random.randint(min_cls_blur_strength,max_cls_blur_strength)
                    cls_img = apply_motion_blur(cls_img, blur_type, blur_strength)
                cls_img.save(cls_img_file_path)
                with open(cls_label_file_path, "+a") as label_file:
                    label_file.write(f"{shape_id} 0.5 0.5 1 1")
                

                if (enable_roboflow['cls']):
                    print(
                        cls_project.single_upload(
                        batch_name=batch_name,
                        image_path=cls_img_file_path,
                        annotation_path=cls_label_file_path,
                        annotation_labelmap=annotation_map_file_path,
                        )
                    )

                if erase_after_upload:
                    os.remove(cls_img_file_path)
                    os.remove(cls_label_file_path)

        blur_type = random.choice(['horizontal', 'vertical', 'diagonal', 'none'])
        if blur_type != "none":
            blur_strength = random.randint(min_img_blur_strength,max_img_blur_strength)
            print(blur_strength)
            background_img = apply_motion_blur(background_img, blur_type, blur_strength)
        background_img.save(img_file_path)
        if enable_roboflow['obj'] == True:
            print(
                obj_project.single_upload(
                batch_name=batch_name,
                image_path=img_file_path,
                annotation_path=obj_label_file_path,
                annotation_labelmap=annotation_map_file_path,
                )
            )
        if enable_roboflow['seg'] == True:
            print(
                seg_project.single_upload(
                batch_name=batch_name,
                image_path=img_file_path,
                annotation_path=seg_label_file_path,
                annotation_labelmap=annotation_map_file_path,
                )
            )        
        if erase_after_upload:
            os.remove(img_file_path)
            os.remove(obj_label_file_path)
            os.remove(seg_label_file_path)
