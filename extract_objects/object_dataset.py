import cv2
import glob
import os
from pathlib import Path
import random
import string
import supervision as sv

# These are Python scripts. Download them from the GitHub repo.
from annotations import *
from extract_objects import *

# Function to generate a random string. Used to generate file names and avoid collisions and repeats.
def generate_random_string(length):
    characters = string.ascii_letters + string.digits  
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


if __name__ == "__main__":
    # #########################
    # Configurable parameters #
    ###########################
    dataset_folder_path = os.path.join("datasets","Tennis Racket Detection.v2i.yolov8")#"../datasets/coco"            #File path to dataset that you would like to extract objects from

    target_class_names = ["Tennis-racket"]#["Fixed-wing Aircraft", "Small Aircraft", "Cargo Plane", "Bus", "Small Car", "Pickup Truck", "Utility Truck", "Truck", "Truck w/Box", "Truck w/ Flatbed", "Passenger Car", "Cargo Car", "Maritime Vessel", "Motorboat", "Sailboat", "Tugboat", "Fishing Vessel", "Ferry", "Yacht"]#["person", "motorcycle", "car", "airplane", "bus", "boat", "stop sign", "snowboard", "umbrella", "sports ball", "baseball bat", "bed", "tennis_racket", "suitcase", "skis"]                                   # Class names that you would like extracted from the dataset specified in dataset_folder_path

    translated_class_names = ["tennis_racket "]#["airplane", "airplane", "airplane", "bus", "car", "car", "car", "car", "car", "car", "car", "car", "boat", "boat", "boat", "boat", "boat", "boat", "boat"]#["person", "motorcycle", "car", "airplane", "bus", "boat", "stop_sign", "snowboard", "umbrella", "sports_ball", "baseball_bat", "bed", "tennis_racket", "suitcase", "skis"]                                # Class names that correspond with the class names that you are extracting from the dataset. 
                                                                       # The number of arguments must match the number of arguments in target_class_names

    dataset_img_ext = ".jpg"                                           # The file extension of the objects in the dataset. It is assumed to be ".jpg" if left empty.c

    yaml_data_path = "datasets\Tennis Racket Detection.v2i.yolov8/data.yaml"#glob.glob(os.path.join(dataset_folder_path,"*.yaml"))[0]     # File path to data.yaml file for dataset. This line will attempt to find it automatically
                                                                       # based on the provided dataset folder path.
    dataset_class_list_configuration = 0                               # Use 1 if data.yaml specifies names as a list. Use 0 if data.yaml specifies names with keys.

    use_super_resolution = False                                       # Set to true to enable super resolution
    super_resolution_scale = 2                                         # Set the scale factor for super resolution

    #####################
    # Object Extraction #
    #####################
    dataset_class_list = extract_classes_from_yaml(yaml_data_path) if dataset_class_list_configuration == 1 else extract_classes_from_yaml_2(yaml_data_path)
    #label_files = glob.glob(f"{dataset_folder_path}/*/labels/*.txt")
    #label_files = glob.glob(os.path.join(dataset_folder_path,"labels","*.txt"))
    print(os.path.join(dataset_folder_path,"labels", "**", "*.txt"))
    label_files = glob.glob(os.path.join(dataset_folder_path, "**","labels", "**", "*.txt"), recursive=True)[358:]

    sr = None
    if use_super_resolution:
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        
        path = "extract_objects/EDSR_x4.pb"
        
        sr.readModel(path)
        
        sr.setModel("edsr",super_resolution_scale)
        
        

    
    for class_name in translated_class_names:
        if not os.path.exists(os.path.join("extract_objects", "datasets")):
            os.mkdir(os.path.join("extract_objects", "datasets"))
        if not os.path.exists(os.path.join("extract_objects", "datasets", class_name)):
            os.mkdir(os.path.join("extract_objects", "datasets", class_name))
    
    
    
    for annotation_file_count, annotation_file_path in enumerate(label_files):
        print(f"Processing {annotation_file_count + 1} / {len(label_files)}: {annotation_file_path}")

        annotations_obj = filter_annotations(annotation_file_path, dataset_class_list, target_class_names, translated_class_names, dataset_img_ext)
        img_path = annotations_obj['img_path']
        annotations = annotations_obj['annotations']
        for yolo_annotation in annotations:
            try:
                img = cv2.imread(img_path)
                if use_super_resolution == 1:
                    img = sr.upsample(img)
                    img = cv2.resize(img,dsize=None,fx=4,fy=4)
                object_class_id, object_center_x, object_center_y, object_width, object_height = extract_yolo_class_and_coords(yolo_annotation)
                object_class_name = translate_id_to_class(object_class_id)
                result = extract_object(img, yolo_annotation)
                file_name = f"{generate_random_string(10)}.png"
                full_path = os.path.join("extract_objects", "datasets", object_class_name, file_name)
                cv2.imwrite(full_path, result)
            except:
                print(f'Skipping annotation "{yolo_annotation}" for image {annotation_file_count + 1} / {len(label_files)}: {img_path}')


