from extract_temps import Box
import numpy as np
import cv2

# The expected control flow is that image_to_temperature_map() is called on the image path. 
# Then the returned temp_img is passed to detect_cold_mask(), and the mask returned.
# Then the returned mask is passed to find_bridge(), and the Box containing the cold bridge returned.

# IMPORTANT: The mask MUST be cropped and have the UI elements removed before find_bridge() is called.

def clean_mask(mask: np.ndarray) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def detect_cold_mask(t_min: float, t_max: float, temp_img: np.ndarray) -> np.ndarray:
    threshold = 0.2     # somewhat arbitrary
    upper_threshold_temp = t_min + (t_max - t_min) * threshold

    h, w, _ = temp_img.shape

    mask = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            mask[y,x] = 255 if temp_img[y,x] < upper_threshold_temp else 0

    mask = clean_mask(mask)
    return mask


def find_bridge(mask: np.ndarray) -> Box:
    # iterate through the connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

    bridges = []

    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]

        # ignore small patches of low temperatures
        if area < 500:  
            continue

        aspect_ratio = max(w/h, h/w)

        # Want rectangular bridges
        if aspect_ratio > 2:
            bridges.append((x, y, w, h, area))

    # Want biggest bridge of the ones found. We take the one with the biggest width or height
    bridge_x, bridge_y, bridge_w, bridge_h = max(bridges, key=lambda b: max(b[2], b[3]))
    return Box(bridge_y, bridge_y + bridge_h, bridge_x, bridge_x + bridge_w)


def draw_bridge(image: np.ndarray, bridge: Box) -> np.ndarray:
    output = image.copy()
    xl, xr, yb, yt, = bridge.xl, bridge.xr, bridge.yb, bridge.yt
    cv2.rectangle(output, (xl,yt), (xr,yb), (0,255,0), 2)

    return output