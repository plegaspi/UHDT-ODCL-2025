import torch
import torchvision
from PIL import Image
import os
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
import numpy as np
import supervision as sv
from annotations import *
import matplotlib.pyplot as plt
from sam2.utils.amg import (
    area_from_rle,
    batch_iterator,
    batched_mask_to_box,
    box_xyxy_to_xywh,
    build_all_layer_point_grids,
    coco_encode_rle,
    generate_crop_boxes,
    is_box_near_crop_edge,
    mask_to_rle_pytorch,
    MaskData,
    remove_small_regions,
    rle_to_mask,
    uncrop_boxes_xyxy,
    uncrop_masks,
    uncrop_points,
)


# select the device for computation
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"using device: {device}")


sam2_checkpoint = "sam2/checkpoints/sam2.1_hiera_large.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
sam2_model = build_sam2(model_cfg, sam2_checkpoint, device=device)
predictor = SAM2ImagePredictor(sam2_model)

img = Image.open("train/images/242BD63E5645CD1C0A_jpg.rf.746f02b57766ed2b7aed8b88a7c8d370.jpg")
img.show()
object_class, object_center_x, object_center_y, object_width, object_height = extract_yolo_class_and_coords("0 0.178125 0.465625 0.35625 0.8625")
input_box = convert_yolo_coords_to_pixel_coords(img, object_center_x, object_center_y, object_width, object_height)

point_coords = np.array([[object_center_x, object_center_y]])
point_labels = np.array([1])

predictor.set_image(img)

result = predictor.predict(
    point_coords=None,
    point_labels=None,
    box=input_box[None, :],
    multimask_output=False
)

masks, scores, logits = result

def show_mask(mask, ax, random_color=False, borders = True):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask = mask.astype(np.uint8)
    mask_image =  mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    if borders:
        import cv2
        contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
        # Try to smooth contours
        contours = [cv2.approxPolyDP(contour, epsilon=0.01, closed=True) for contour in contours]
        mask_image = cv2.drawContours(mask_image, contours, -1, (1, 1, 1, 0.5), thickness=2) 
    ax.imshow(mask_image)

def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)   

def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0, 0, 0, 0), lw=2))    

def show_masks(image, masks, scores, point_coords=None, box_coords=None, input_labels=None, borders=True):
    for i, (mask, score) in enumerate(zip(masks, scores)):
        plt.figure(figsize=(10, 10))
        plt.imshow(image)
        show_mask(mask, plt.gca(), borders=borders)
        if point_coords is not None:
            assert input_labels is not None
            show_points(point_coords, input_labels, plt.gca())
        if box_coords is not None:
            # boxes
            show_box(box_coords, plt.gca())
        if len(scores) > 1:
            plt.title(f"Mask {i+1}, Score: {score:.3f}", fontsize=18)
        plt.axis('off')
        plt.show()

show_masks(img, masks, scores, point_coords=point_coords, box_coords=input_box, input_labels=point_labels, borders=False)

import numpy as np

def calculate_mask_area(mask):
    if not np.array_equal(mask, mask.astype(bool)):
        raise ValueError("Mask must be a binary array")

    area = np.sum(mask)

    return area


def calculate_bbox(mask):
    y_coords, x_coords = np.where(mask == 1)

    if len(x_coords) == 0 or len(y_coords) == 0:
        return (0, 0, 0, 0)
    
    x_min, x_max = x_coords.min(), x_coords.max()
    y_min, y_max = y_coords.min(), y_coords.max()
    
    w = x_max - x_min + 1
    h = y_max - y_min + 1
    
    return (x_min, y_min, w, h)


from PIL import Image
import numpy as np

def apply_mask_crop_and_save(image, mask, output_path="masked_cropped_image.png", margin=5):
    """
    Apply a binary mask to an image, make areas outside the mask transparent, crop it with a margin, and save as PNG.
    
    Parameters:
        image (PIL.Image): Original image as a Pillow Image.
        mask (np.ndarray): Binary NumPy mask array (2D, with 0 for transparent and 255 for opaque).
        output_path (str): Path to save the cropped and masked image. Default is "masked_cropped_image.png".
        margin (int): Margin (in pixels) to add around the masked area when cropping.
    """
    # Convert the image to RGBA to support transparency
    image = image.convert("RGBA")
    
    # Convert the binary mask to a grayscale Pillow Image (L mode)
    mask_image = Image.fromarray(mask * 255).convert("L")
    
    # Resize mask if necessary to match the image size
    mask_image = mask_image.resize(image.size)
    
    # Apply the mask as an alpha channel
    image.putalpha(mask_image)
    
    # Get the bounding box of the mask
    mask_bounds = mask_image.getbbox()  # Returns (left, upper, right, lower)
    if mask_bounds is None:
        print("No masked area found in the image.")
        return
    
    # Add a margin to the bounding box
    left = max(0, mask_bounds[0] - margin)
    upper = max(0, mask_bounds[1] - margin)
    right = min(image.width, mask_bounds[2] + margin)
    lower = min(image.height, mask_bounds[3] + margin)
    cropped_box = (left, upper, right, lower)
    
    # Crop the image to the bounding box with margin
    cropped_image = image.crop(cropped_box)
    
    # Save the cropped image as a PNG to preserve transparency
    cropped_image.save(output_path, format="PNG")
    print(f"Cropped masked image saved to {output_path}")

# Example usage with a Pillow image and a binary NumPy mask
# img is a Pillow Image and mask is a binary NumPy mask array
apply_mask_crop_and_save(img, masks[0])




