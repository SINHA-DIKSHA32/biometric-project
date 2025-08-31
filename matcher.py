import cv2
import os

def match_fingerprints(scan_path, folder_path):
    # Load the scanned image and convert to grayscale
    scan_img = cv2.imread(scan_path, cv2.IMREAD_GRAYSCALE)
    if scan_img is None:
        return None

    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(scan_img, None)

    best_match_name = None
    max_matches = 0

    for filename in os.listdir(folder_path):
        if filename == "temp_scan.png":
            continue

        file_path = os.path.join(folder_path, filename)
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        kp2, des2 = sift.detectAndCompute(img, None)
        if des2 is None:
            continue

        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        # Apply ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        if len(good_matches) > max_matches:
            max_matches = len(good_matches)
            best_match_name = filename.replace(".png", "")

    # Return the best matched patient name
    return best_match_name if max_matches > 10 else None
