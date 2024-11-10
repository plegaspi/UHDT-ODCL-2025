import cv2
import numpy as np
from pathlib import Path
import yaml
import sys


def extract_yolo_class_and_coords(annotation: str):
    #processed_annotations = []
    #full_annotation = annotation.split(" ")
    #for i in range(1, len(full_annotation), 5):
    #    object_class = full_annotation[0]
    #    print(f"Len: {len(full_annotation)}")
    #    object_center_x, object_center_y, object_width, object_height = full_annotation[i:i+4]
    #    processed_annotations.append([int(object_class), float(object_center_x), float(object_center_y), float(object_width), float(object_height)])
    #print(processed_annotations)
    object_class, object_center_x, object_center_y, object_width, object_height = annotation.split(" ")
    object_class = int(object_class)
    object_center_x = float(object_center_x)
    object_center_y = float(object_center_y)
    object_width = float(object_width)
    object_height = float(object_height)
    return object_class, object_center_x, object_center_y, object_width, object_height


def convert_yolo_coords_to_pixel_coords(base_img, object_center_x, object_center_y, object_width, object_height):
    img_height, img_width, img_channels = base_img.shape
    top_left_x = object_center_x * img_width - object_width * img_width / 2
    top_left_y = object_center_y * img_height - object_height * img_height / 2
    bottom_right_x = object_center_x * img_width + object_width * img_width / 2
    bottom_right_y =  object_center_y * img_height + object_height * img_height / 2
    return np.array([int(x) for x in (top_left_x, top_left_y, bottom_right_x, bottom_right_y)])

def extract_classes_from_yaml(yaml_data_path):
    class_list = None
    with open(yaml_data_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
        class_list = yaml_data['names']
    return class_list

def extract_classes_from_yaml_2(yaml_data_path):
    class_list = []
    with open(yaml_data_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
        class_mapping = dict(yaml_data['names'])
        class_ids = class_mapping.keys()
        for class_id in class_ids:
            class_list.append(class_mapping[class_id])
    return class_list

def translate_class_to_id(translated_class_name):
    object_class_list = ['person', 'car', 'motorcycle', 'airplane', 'bus', 'boat', 'stop_sign', 'snowboard', 'umbrella', 'sports_ball', 'baseball_bat', 'bed', 'tennis_racket', 'suitcase', 'skis']
    for object_class_id, object_class in enumerate(object_class_list):
        if translated_class_name == object_class:
            return object_class_id
    raise ValueError(f"{translated_class_name} is not a valid class")

def translate_id_to_class(translated_class_id):
    object_class_list = ['person', 'car', 'motorcycle', 'airplane', 'bus', 'boat', 'stop_sign', 'snowboard', 'umbrella', 'sports_ball', 'baseball_bat', 'bed', 'tennis_racket', 'suitcase', 'skis']
    return object_class_list[translated_class_id]

def get_image_path_from_label_path(label_path):
    image_path = label_path.replace("labels", "images").replace(".txt", ".jpg")
    return image_path

def filter_annotations(annotation_file_path, dataset_class_list, target_class_names, translated_class_names, dataset_img_ext=".jpg"):
    annotation_file_path = Path(annotation_file_path)
    dataset_subset_root = annotation_file_path.parent.parent
    annotation_obj = {
        'img_path': get_image_path_from_label_path(str(annotation_file_path)),
        'annotations': []
    }
    matching_annotations = []
    with open(annotation_file_path, 'r') as file:
        """
        for ci, line in enumerate(file):
            #print(ci)
            annotation = line.strip()
            processed_annotations = extract_yolo_class_and_coords(annotation)
            for processed_annotation in processed_annotations:
                object_class_id, object_center_x, object_center_y, object_width, object_height = processed_annotation
                object_class = dataset_class_list[object_class_id]
                #sys.exit()
                for translated_class_name_index, target_class_name in enumerate(target_class_names):
                    if object_class == target_class_name:
                        translated_object_class = translated_class_names[translated_class_name_index]
                        translated_object_class_id = translate_class_to_id(translated_object_class)
                        translated_annotation = f"{translated_object_class_id} {object_center_x} {object_center_y} {object_width} {object_height}"
                        annotation_obj['annotations'].append(translated_annotation)
        """
        for ci, line in enumerate(file):
            annotation = line.strip()
            object_class_id, object_center_x, object_center_y, object_width, object_height = extract_yolo_class_and_coords(annotation)
            object_class = dataset_class_list[object_class_id]
            #sys.exit()
            for translated_class_name_index, target_class_name in enumerate(target_class_names):
                if object_class == target_class_name:
                    translated_object_class = translated_class_names[translated_class_name_index]
                    translated_object_class_id = translate_class_to_id(translated_object_class)
                    translated_annotation = f"{translated_object_class_id} {object_center_x} {object_center_y} {object_width} {object_height}"
                    annotation_obj['annotations'].append(translated_annotation)
    return annotation_obj

if __name__ == "__main__":

    result = filter_annotations('Mannequins detection.v1i.yolov8/train/labels/images-1-_jpg.rf.74238d74591df0aa15f8c3500661ef1e.txt', 
                            extract_classes_from_yaml("Mannequins detection.v1i.yolov8/data.yaml"),
                            ['manikin'], 
                            ['person'])
    print(result['annotations']) 

    print(extract_classes_from_yaml_2('yolo_v2/test.yaml'))


