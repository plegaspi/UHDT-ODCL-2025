import os
import cv2 as cv
from Color import classify_color
if __name__ == "__main__":
    base_dir = os.path.join('cropped_images', 'datasets', 'processed', '3-8-24 DJI Images-10')
    dest_dir = os.path.join('shape', 'datasets','processed', os.path.dirname(base_dir))
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    img_paths = os.listdir(base_dir)
    for i in range(len(img_paths)):
        img_path = img_paths[i]
        img_full_path = os.path.join(base_dir, img_path)
        print(f'({i+1}/{len(img_paths)}):Generating image for {img_full_path}')

        base_name, file_ext = os.path.splitext(img_path)
        if file_ext in ['.png', '.jpg']:
            img = cv.imread(img_full_path)
            img, colors, bg_masked, alphanum_masked, shape_mask, alphanum_mask = classify_color(img)
            shape_output_path = os.path.join(dest_dir, f"{base_name}_shape{file_ext}" )
            print(shape_output_path)
            cv.imwrite(shape_output_path, shape_mask + alphanum_mask)