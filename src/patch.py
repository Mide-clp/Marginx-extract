import cv2
from PIL import Image

# Load the image
# image = cv2.imread("/Users/apple/PycharmProject/marginz/src/img_1.png")


# Load the original image and a background image (without the puzzle)
original_image = cv2.imread("/Users/apple/PycharmProject/marginz/src/img.png")
background_image = cv2.imread("/Users/apple/PycharmProject/marginz/src/img_1.png")
import cv2
import numpy as np


def detect_unmatched_region(image_path, background_path, threshold=50):
    # Read the images
    image = cv2.imread(image_path)
    background = cv2.imread(background_path)

    # Convert the images to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)

    # Calculate the absolute difference between the image and the background
    diff = cv2.absdiff(gray_image, gray_background)

    # Threshold the difference image to create a binary mask
    _, binary_mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

    # Find contours in the binary mask
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour that represents the unmatched region
    max_area = 0
    largest_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            largest_contour = contour

    # Draw the largest contour on the original image
    if largest_contour is not None:
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show the image with the detected unmatched region
    cv2.imshow("Detected Unmatched Region", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    image_path = "/Users/apple/PycharmProject/marginz/src/img-removebg-preview.png"  # Replace with the path to your image file
    background_path = "/Users/apple/PycharmProject/marginz/src/img_3.png"  # Replace with the path to your background/reference image
    threshold_value = 50  # Adjust the threshold value as needed

    detect_unmatched_region(image_path, background_path, threshold=threshold_value)
