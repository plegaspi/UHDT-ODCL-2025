from datetime import datetime
import glob
import os
import PIL
import random

from roboflow_utils import *
from utils import *




if __name__ == "__main__":
    num_imgs = 5
    max_targets_per_img = 25
    min_targets_per_img = 10
    min_angle = 0
    max_angle = 360
    min_scale = 0.5
    max_scale = 1.5
    min_blur_strength = 10
    max_blur_strength = 110
    roboflow_upload_enabled = True
    erase_after_upload = False
    object_dataset_path = "extract_objects\datasets"

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
        for j in range(num_targets_in_img):
            print(f"\tGenerating target {j+1}/{num_targets_in_img}")
            target_class = select_random_target()
            target_id = translate_class_to_id(target_class)
            target_imgs = glob.glob(f"{object_dataset_path}/{target_class}/*.png")
            target_img_path = target_imgs[random.randint(0, len(target_imgs) - 1)]
            target_img = Image.open(target_img_path)
            scale_factor = random.uniform(min_scale, max_scale)
            target_img = scale_target(target_img, scale_factor)
            angle = random.randint(min_angle, max_angle)
            target_img = rotate_target(target_img, angle)
            targets.append(target_img)
            class_ids.append(target_id)
        
        dataset_img, annotations = generate_translations(background_img, targets, class_ids)
        dataset_img_path = f"{img_dir_path}/{img_name}"
        dataset_img.save(dataset_img_path)
        write_annotations(obj_label_file_path, annotations)

        if roboflow_upload_enabled:
            print(upload_to_roboflow(rf_project, batch_name, dataset_img_path, obj_label_file_path, annotation_map_file_path))


