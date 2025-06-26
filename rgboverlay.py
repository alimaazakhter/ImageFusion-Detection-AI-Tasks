import cv2
import numpy as np
import os
import glob

def align_images(rgb_image, thermal_image):
    """
    Aligns the thermal image to the RGB image using feature matching.
    Returns the aligned thermal image.
    """
    # Convert images to grayscale
    rgb_gray = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
    # The thermal image might already be grayscale, but cvtColor is safe.
    thermal_gray = cv2.cvtColor(thermal_image, cv2.COLOR_BGR2GRAY)

    # Initialize ORB detector
    orb = cv2.ORB_create(nfeatures=5000)

    # Find keypoints and descriptors
    keypoints1, descriptors1 = orb.detectAndCompute(rgb_gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(thermal_gray, None)

    if descriptors1 is None or descriptors2 is None:
        print("Could not find descriptors in one of the images.")
        return None

    # Match features using Brute-Force Matcher
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(descriptors1, descriptors2)

    # Sort them in the order of their distance
    matches = sorted(matches, key=lambda x: x.distance)

    # Keep only the best matches (e.g., top 15%)
    num_good_matches = int(len(matches) * 0.15)
    matches = matches[:num_good_matches]

    # Minimum number of matches required
    MIN_MATCH_COUNT = 10
    if len(matches) < MIN_MATCH_COUNT:
        print(f"Not enough matches are found - {len(matches)}/{MIN_MATCH_COUNT}")
        return None

    # Extract location of good matches
    src_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Find homography
    h, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    if h is None:
        print("Homography could not be computed.")
        return None

    # Warp thermal image
    height, width, channels = rgb_image.shape
    aligned_thermal = cv2.warpPerspective(thermal_image, h, (width, height))

    return aligned_thermal

def main():
    """
    Main function to process image pairs.
    """
    # Input and output directories
    input_dir = 'input-images-20250621T091834Z-1-001/input-images'
    output_dir = 'output-images'

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Find all thermal and RGB images
    all_jpgs = glob.glob(os.path.join(input_dir, '*.JPG'))
    
    thermal_map = {}
    rgb_map = {}

    for img_path in all_jpgs:
        basename = os.path.basename(img_path)
        parts = basename.split('_')
        # Expecting filenames like DJI_20250530121540_0001_T.JPG
        if len(parts) >= 3:
            seq_id = parts[-2]
            if basename.endswith('_T.JPG'):
                thermal_map[seq_id] = img_path
            elif basename.endswith('_Z.JPG'):
                rgb_map[seq_id] = img_path

    for seq_id, thermal_path in thermal_map.items():
        rgb_path = rgb_map.get(seq_id)

        if not rgb_path:
            print(f"Corresponding RGB image not found for {os.path.basename(thermal_path)}")
            continue

        print(f"Processing pair: {os.path.basename(thermal_path)} and {os.path.basename(rgb_path)}")

        # Read images
        thermal_image = cv2.imread(thermal_path)
        rgb_image = cv2.imread(rgb_path)

        if thermal_image is None or rgb_image is None:
            print("Error reading one of the images.")
            continue

        # Align images
        aligned_thermal = align_images(rgb_image, thermal_image)

        if aligned_thermal is None:
            print(f"Could not align {os.path.basename(thermal_path)}")
            continue

        # Create the overlay by blending the RGB and aligned thermal images
        # A weight of 0.5 gives 50% transparency to the thermal overlay.
        alpha = 0.5
        overlay = cv2.addWeighted(rgb_image, 1 - alpha, aligned_thermal, alpha, 0)

        # Save the output
        output_filename = os.path.basename(thermal_path).replace('_T.JPG', '_AT.JPG')
        output_path = os.path.join(output_dir, output_filename)
        cv2.imwrite(output_path, overlay)
        print(f"Successfully saved overlay to {output_path}")

if __name__ == '__main__':
    main()
