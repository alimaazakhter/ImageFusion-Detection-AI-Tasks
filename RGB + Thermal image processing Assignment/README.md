# RGB-Thermal Image Overlay

## Objective

This project provides a Python script to align and overlay thermal images onto their corresponding RGB counterparts. The images are captured from two different cameras and are not perfectly aligned by default. This script automates the process of processing all image pairs in an input folder and generating aligned, overlaid output images.

## File Structure

-   `input-images-20250621T091834Z-1-001/input-images/`: Contains the source thermal (`*_T.JPG`) and RGB (`*_Z.JPG`) images.
-   `output-images/`: The directory where the final overlaid images (`*_AT.JPG`) are saved. This is created automatically if it doesn't exist.
-   `rgboverlay.py`: The main Python script that performs the image processing.
-   `requirements.txt`: A list of the Python libraries required to run the script.

## Requirements

-   Python 3.x
-   OpenCV for Python
-   NumPy

## How to Run

1.  **Clone the repository or download the files.**

2.  **Install the dependencies:**
    Open a terminal or command prompt in the project directory and run the following command to install the necessary libraries:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the script:**
    After the installation is complete, execute the main script with this command:
    ```bash
    python rgboverlay.py
    ```

The script will then process all the images and save the output in the `output-images` folder.

## Script Logic

1.  **Image Pairing:** The script first scans the input directory and pairs up thermal and RGB images based on their shared sequence number (e.g., `_0001_`, `_0002_`).

2.  **Feature Matching:** For each pair, it uses the ORB (Oriented FAST and Rotated BRIEF) feature detector to find keypoints and descriptors in both the RGB and thermal images.

3.  **Alignment:** A Brute-Force matcher is used to find the best matches between the features. From these matches, a homography matrix is computed, which represents the perspective transformation required to align the thermal image with the RGB image.

4.  **Overlay:** The thermal image is then warped using this transformation. Finally, the aligned thermal image is blended with the original RGB image (with 50% transparency) to create the final output.
