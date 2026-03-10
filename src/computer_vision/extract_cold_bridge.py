from .extract_temps import *
import numpy as np
import cv2

# The expected control flow is that image_to_temperature_map() is called on the image path. 
# Then the returned temp_img is passed to detect_cold_mask(), and the mask returned.
# Then the returned mask is passed to find_bridge(), and the Box containing the cold bridge returned.

def clean_mask(mask: np.ndarray) -> np.ndarray:
    """
    Removes noisy regions of the argument ``mask`` using morphological transforms.

    Parameters:
    mask (np.ndarray): A 2D numpy array with datatype uint8 representing a mask to be applied on the temperature image.

    Returns:
    (np.ndarray): The argument ``mask`` but de-noised.
    """

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def detect_cold_mask(t_min: float, t_max: float, threshold: float, temp_img: np.ndarray, UI_BOXES) -> np.ndarray:
    """
    Create a mask to include the coldest regions of the image and exclude all other regions. Additionally exclude UI 
    components from the mask.

    Parameters:
    t_min (float): The minimum temperature in the image.

    t_max (float): The maximum temperature in the image.

    temp_img (np.ndarray): A 2D numpy array with datatype float64, where each value represents the temperature of the 
    corresponding pixel in the original BGR thermal image.

    Returns:
    mask (np.ndarray): A 2D numpy array with datatype uint8 representing as a mask of the coldest regions of the image.
    """

    upper_threshold_temp = t_min + (t_max - t_min) * threshold
    
    # The aim is to create a mask that includes the temperatures in the lowest 20% of the temperature bar.
    h, w, _ = temp_img.shape

    mask = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            mask[y,x] = 255 if temp_img[y,x] < upper_threshold_temp else 0

    # mask away the UI
    for box in UI_BOXES:
        cv2.rectangle(mask, (box.xl, box.yt), (box.xr, box.yb), 0, -1)

    mask = clean_mask(mask)
    return mask


def find_bridge_from_mask(mask: np.ndarray, want_rectangle: bool = True) -> Box:
    """
    Find the connected components of the argument ``mask`` and return the component that is the thinnest 
    while still having sufficient area (these are characteristic traits of cold bridges).

    Parameters:
    mask (np.ndarray): A 2D numpy array with datatype uint8 representing a mask to be applied on the temperature image.

    want_rectangle (bool): This represents whether we want constraints on the aspect ratio of detected cold bridges, 
    i.e. if we want a roughly rectangular shape.

    Returns:
    bridge (Box): The coordinates of the corners of the rectangle containing the cold bridge.
    """

    # iterate through the connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

    bridges = []

    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]

        # ignore small patches of low temperatures
        if area < 500:  
            continue

        aspect_ratio = max(w / h, h / w)

        # Want thin rectangular-looking bridges
        if not want_rectangle or aspect_ratio > 2:
            bridges.append((x, y, w, h))

    if not bridges:
        return None

    # Want biggest bridge of the ones found. We take the one with the biggest width or height
    bridge_x, bridge_y, bridge_w, bridge_h = max(bridges, key=lambda b: max(b[2], b[3]))
    return Box(bridge_y, bridge_y + bridge_h, bridge_x, bridge_x + bridge_w)


def find_bridge_from_img(t_min: float, t_max: float, temp_img: np.ndarray) -> np.ndarray:
    """
    Find the best candidate cold bridge region of the image ``temp_img``. This is done by iteratively changing the
    threshold temperature to find a mask of the image, and detecting connected components from the mask.

    Parameters:
    t_min (float): The minimum temperature in the image.

    t_max (float): The maximum temperature in the image.

    temp_img (np.ndarray): A 2D numpy array with datatype float64, where each value represents the temperature of the 
    corresponding pixel in the original BGR thermal image.

    Returns:
    bridge (Box): The coordinates of the corners of the rectangle containing the cold bridge.
    """

    thresholds = [0.13, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 0.9]
    bridge = None

    mask = detect_cold_mask(t_min, t_max, thresh[0], temp_img)
    bridge = find_bridge_from_mask(mask, want_rectangle=True)
    if bridge:
        return bridge

    for thresh in thresholds[1:]:
        mask = detect_cold_mask(t_min, t_max, thresh, temp_img)
        bridge = find_bridge_from_mask(mask, want_rectangle=False)
        if bridge:
            break

    return bridge   # it is theoretically possible for this to return None
    


def draw_bridge(image: np.ndarray, bridge: Box) -> np.ndarray:
    """
    Draw a rectangle onto a copy of the argument ``image`` at the location of the cold bridge ``bridge``.

    Parameters:
    image (np.ndarray): A 3D numpy array which is the original BGR thermal image. 

    bridge (Box): The coordinates of the corners of the rectangle containing the cold bridge.

    Returns:
    output_image (np.ndarray): A 3D numpy array which is the original BGR thermal image but with a green rectangle drawn
    at the location of the cold bridge.
    """

    output = image.copy()
    xl, xr, yb, yt, = bridge.xl, bridge.xr, bridge.yb, bridge.yt
    cv2.rectangle(output, (xl,yt), (xr,yb), (0,255,0), 2)

    return output


def find_mean(temp_img: np.ndarray, bridge: Box, UI_BOXES) -> float:
    """
    Find the mean temperature in the argument ``temp_img``, excluding the UI components and the cold bridge. The aim is
    to get a good approximation of the surrounding temperature.

    Parameters:
    temp_img (np.ndarray): A 2D numpy array with datatype float64, where each value represents the temperature of the 
    corresponding pixel in the original BGR image.

    bridge (Box): The coordinates of the corners of the rectangle containing the cold bridge.

    Returns:
    avg_temp (float): The average temperature surrounding the cold bridge.
    
    """

    h, w = temp_img.shape
    mask = np.full((h, w), 255, dtype=np.uint8)

    # Want to divide by the total number of pixels that are not masked away. So for each mask, add the total number of pixels
    # masked away, and then use this to subtract from the total number of pixels and compute the average temperature.

    masked_area = 0     # number of pixels that the masks remove

    # mask away UI boxes and the cold bridge
    for box in [*UI_BOXES, bridge]:
        cv2.rectangle(mask, (box.xl, box.yt), (box.xr, box.yb), 0, -1)
        masked_area += (box.yb - box.yt) * (box.xr - box.xl)

    masked_temp_img = cv2.bitwise_and(temp_img, temp_img, mask=mask)
    sum_temp = np.sum(masked_temp_img)
    avg_temp = sum_temp / ((h * w) - masked_area)

    return avg_temp