from sklearn.cluster import KMeans
import cv2 as cv
import numpy as np
from rembg import remove


def segment_image(img, k):
    img = remove(img, bgcolor=[0,255,255,255])
    img = cv.cvtColor(img, cv.COLOR_BGRA2BGR)

    x = img.reshape((-1, 3))

    kmeans = KMeans(n_clusters=3, init="k-means++").fit(x)

    centers = np.uint8(kmeans.cluster_centers_)
    labels = np.uint8(kmeans.labels_)

    segmented_data = centers[labels.flatten()]
    segmented_image = segmented_data.reshape(img.shape)

    return centers, segmented_image

if __name__ == "__main__":
    img = cv.imread('images/test.jpg')
    centers, img = segment_image(img, 3)
    cv.imshow("Segmented Image", img)
    cv.waitKey(0)
    cv.destroyAllWindows()
