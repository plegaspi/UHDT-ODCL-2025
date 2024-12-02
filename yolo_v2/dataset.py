from datetime import datetime
import glob
import os
import PIL
import random
import sys
from roboflow_utils import *
from utils import *

os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin")


if __name__ == "__main__":
    num_imgs = 4000
    max_targets_per_img = 25
    min_targets_per_img = 10
    min_angle = 0
    max_angle = 360
    min_scale = 1.3
    max_scale = 2
    #min_blur_strength = 10
    #max_blur_strength = 110
    roboflow_upload_enabled = False
    erase_after_upload = False
    object_dataset_path = "extract_objects/filtered_datasets"

    obj_scale_config = {
        'person': 0.75,
        'car': 1,
        'motorcycle': 1,
        'airplane': 2, 
        'bus': 2, 
        'boat': 1, 
        'stop_sign': 0.35, 
        'snowboard': 0.5,
        'umbrella': 0.5, 
        'sports_ball': 0.25, 
        'baseball_bat': 0.4, 
        'bed': 1, 
        'tennis_racket': 0.5, 
        'suitcase': 0.5, 
        'skis': 0.5
    }

    current_date = datetime.now()
    batch_name = f"{current_date.year}_{current_date.month}_{current_date.day}_{current_date.hour}_{current_date.minute}_{current_date.second}"
    backgrounds_dir = os.path.join("yolo_v2", "backgrounds")
    backgrounds = [background_img_path for background_img_path in os.listdir(backgrounds_dir) if background_img_path.lower().endswith(('.png', '.jpg', '.jpeg')) and not background_img_path.startswith('.')]
    dataset_base_path = os.path.join("yolo_v2", "datasets",f"{current_date.year}_{current_date.month}_{current_date.day}_{current_date.hour}_{current_date.minute}_{current_date.second}")
    img_dir_path = os.path.join(dataset_base_path, "images")
    cls_img_dir_path = os.path.join(dataset_base_path, "cls-images")
    obj_label_dir_path = os.path.join(dataset_base_path, "obj_labels")
    annotation_map_file_path = os.path.join('yolo_v2', 'classes.labels')

    if roboflow_upload_enabled:
        rf_project = initialize_roboflow_project() 
    
    for i in range(num_imgs):
        if not os.path.exists(img_dir_path):
            os.makedirs(img_dir_path)

        # Object Detection Label Folder
        if not os.path.exists(obj_label_dir_path):
            os.makedirs(obj_label_dir_path)

        background_index = random.randint(0, len(backgrounds)-1)
        background_img_path = os.path.join(backgrounds_dir, backgrounds[background_index])
        background_img = Image.open(background_img_path)
        num_targets_in_img = random.randint(min_targets_per_img, max_targets_per_img - 1)
        sample_name = generate_random_string(10)
        img_name = f"{sample_name}.jpg"
        obj_label_file_path = os.path.join(obj_label_dir_path, f"{sample_name}.txt")

        targets = []
        class_ids = []
        print(f"Generating image #{i+1}/{num_imgs}")
        scale_factor = random.uniform(min_scale, max_scale)
        for j in range(num_targets_in_img):
            print(f"\tGenerating target {j+1}/{num_targets_in_img}")
            target_class = select_random_target()
            target_id = translate_class_to_id(target_class)
            target_imgs = glob.glob(f"{object_dataset_path}/{target_class}/*.png")
            target_img_path = target_imgs[random.randint(0, len(target_imgs) - 1)]
            target_img = Image.open(target_img_path)
            #scale_factor = random.uniform(min_scale, max_scale)
            #target_img = scale_target(target_img, background_img, target_class, scale_factor)
            target_img = scale_target(target_img, background_img, target_class, obj_scale_config, scale_factor=1.0, sr_model_path="yolo_v2\EDSR_x4.pb", min_res=(500, 500))
            angle = random.randint(min_angle, max_angle)
            target_img = rotate_target(target_img, angle)
            targets.append(target_img)
            class_ids.append(target_id)
        
        dataset_img, annotations = generate_translations(background_img, targets, class_ids)
        dataset_img_path = f"{img_dir_path}/{img_name}"
        dataset_img.save(dataset_img_path)
        write_annotations(obj_label_file_path, annotations)

        if roboflow_upload_enabled:
            try:
                print(upload_to_roboflow(rf_project, batch_name, dataset_img_path, obj_label_file_path, annotation_map_file_path))
            except:
                print("Skipping image upload.")
            if erase_after_upload:
                os.remove(dataset_img_path)
                os.remove(obj_label_file_path)


