from ultralytics import YOLO
import cv2
import numpy as np

def convert_predicted_class_to_shape(predicted_class):
    shapes = {
        0: 'circle',
        1: 'cross',
        2: 'pentagon',
        3: 'quartercircle',
        4: 'rectangle',
        5: 'semicircle',
        6: 'star',
        7: 'triangle'
    }

    return shapes[predicted_class]

# Increase gamma to blur alphanumeric
def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)


# Returns an array of shape results (name, confidence, class, and the original image) in order of highest to lowest confidence
def shape_classification(img):
    processed_img = cv2.bilateralFilter(img, 30, 90, 90)
    processed_img = cv2.bilateralFilter(processed_img, 30, 50, 50)
    #processed_img = adjust_gamma(processed_img, 1.75)
    processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR)
    model = YOLO("weight/blurred-max-ncls.pt")
    results = model.predict(processed_img, stream=False, save=False, imgsz=320)
    for result in results:
        predictions = result.probs.top5
        confidence = result.probs.top5conf
        predicted_shapes = []
        for i in range(5):
            shape = {
                'name': convert_predicted_class_to_shape(predictions[i]),
                'confidence': confidence[i].item(),
                'class': predictions[i],
                'original_image': result.orig_img
            }
            predicted_shapes.append(shape)
        return predicted_shapes[0]["name"]
