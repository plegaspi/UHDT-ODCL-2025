import cv2 as cv
import numpy as np
from ultralytics import SAM
import os
def apply_yolo_segmentation_with_yellow_background(image):
    model = SAM("sam2_b.pt")
    results = model(image)

    masks = results[0].masks


    image_height, image_width, _ = image.shape

    yellow_background = np.full((image_height, image_width, 3), (0, 255, 255), dtype=np.uint8)

    final_image = yellow_background.copy()

   
    binary_masks = masks.data  

    for mask in binary_masks:
        mask = mask.cpu().numpy()  
        mask = mask.astype('uint8')  

        if mask.shape[0] != image_height or mask.shape[1] != image_width:
            mask = cv.resize(mask, (image_width, image_height))

       
        mask = (mask * 255).astype(np.uint8)
        kernel = np.ones(2, np.uint8)
        mask = cv.erode(mask, kernel, iterations=100)

       
        masked_part = cv.bitwise_and(image, image, mask=mask)

       
        inverse_mask = cv.bitwise_not(mask)

       
        yellow_part = cv.bitwise_and(yellow_background, yellow_background, mask=inverse_mask)

        final_image = cv.add(masked_part, yellow_part)

    return final_image
