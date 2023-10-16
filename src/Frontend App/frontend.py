import tkinter as tk
from tkinter import END, Entry, filedialog
import cv2
import numpy as np
import imutils

# Initialize the stitched image
stitched_img = None

# Browse images
def browse_images():
    global images
    images.clear()
    # Get the list of image files
    image_paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("PNG Files", "*.png"), ("JPG Files", "*.jpg"), ("BMP Files", "*.bmp")])

    # Load the images
    for image_path in image_paths:
        image = cv2.imread(image_path)
        images.append(image)
        info.delete(0, END)
        info.insert(0, "Import Successful")

# Stitch images
def stitch_images():
    global stitched_img

    # Check if there are enough images
    if len(images) < 2:
        info.delete(0, END)
        info.insert(0, "Not enough images to stitch!")
        return

    # Create the stitcher object
    stitcher = cv2.Stitcher_create()

    # Stitch the images
    (status, stitched_img) = stitcher.stitch(images)

    # Check if the stitching was successful
    if status != cv2.STITCHER_OK:
        info.delete(0, END)
        info.insert(0, "Stitching failed!")
        return

    # Display the stitched image
    cv2.imwrite("stitchedOutput.png", stitched_img)
    #cv2.imshow("Stitched Image", stitched_img)
    info.delete(0, END)
    info.insert(0, "Stitch Successful and Image Saved")
    cv2.waitKey(0)

# Process image
def process_image():
    global stitched_img
    stitched_img = cv2.copyMakeBorder(stitched_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, (0,0,0))

    gray = cv2.cvtColor(stitched_img, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.threshold(gray, 0, 255 , cv2.THRESH_BINARY)[1]

    # cv2.imshow("Threshold Image", thresh_img)
    # cv2.waitKey(0)

    contours = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)
    areaOI = max(contours, key=cv2.contourArea)

    mask = np.zeros(thresh_img.shape, dtype="uint8")
    x, y, w, h = cv2.boundingRect(areaOI)
    cv2.rectangle(mask, (x,y), (x + w, y + h), 255, -1)

    minRectangle = mask.copy()
    sub = mask.copy()

    while cv2.countNonZero(sub) > 0:
        minRectangle = cv2.erode(minRectangle, None)
        sub = cv2.subtract(minRectangle, thresh_img)

    contours = cv2.findContours(minRectangle.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)
    areaOI = max(contours, key=cv2.contourArea)

    # cv2.imshow("minRectangle Image", minRectangle)
    # cv2.waitKey(0)

    x, y, w, h = cv2.boundingRect(areaOI)

    stitched_img = stitched_img[y:y + h, x:x + w]

    cv2.imwrite("stitchedOutputProcessed.png", stitched_img)

    # cv2.imshow("Stitched Image Processed", stitched_img)
    info.delete(0, END)
    info.insert(0, "Post Processing Successful and Image Saved")

    cv2.waitKey(0)

# Create the main window
root = tk.Tk()
root.title("Image Stitcher")
root.config(bg='#e1f1f7')
root.geometry("1280x720")


# Create the list to store the images
images = []

# Create the buttons
browse_button = tk.Button(root, text="Browse Images", command=browse_images)
browse_button.place(x=400, y=300, width=100, height=50)

stitch_button = tk.Button(root, text="Stitch Images", command=stitch_images)
stitch_button.place(x=600, y=300, width=100, height=50)

process_button = tk.Button(root, text="Process Image", command=process_image)
process_button.place(x=800, y=300, width=100, height=50)

### create text boxes
info = Entry(root, width=30)
info.place(x=475, y=200, width=400, height=50)

# Start the main loop
root.mainloop()