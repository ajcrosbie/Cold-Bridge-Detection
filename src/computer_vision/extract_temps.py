import re
import cv2
import numpy as np
import pytesseract
from dataclasses import dataclass
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor


# For ease of configurablity once we have some actual data.
@dataclass
class Box:
    yt:int # y axis most top
    yb:int # y axis most bottom
    xl:int # x axis most left
    xr:int # x axis most right



# defining a bunch of constants

INNER_BAR_BOX_FLIR = Box(29, 209, 306, 313)
OUTER_BAR_BOX_FLIR = Box(26, 213, 303, 317)
TOP_BOX_FLIR = Box(5, 25, 274, 314)
BOTTOM_BOX_FLIR = Box(215, 235, 274, 314)
CROSSHAIR_BOX_FLIR = Box(4, 25, 4, 69)
LOGO_BOX_FLIR = Box(219, 235, 4, 56)

FLIR_UI_BOXES = [OUTER_BAR_BOX_FLIR, TOP_BOX_FLIR, BOTTOM_BOX_FLIR, CROSSHAIR_BOX_FLIR, LOGO_BOX_FLIR]

INNER_BAR_BOX_HIKMICRO = Box(182, 379, 11, 25)
OUTER_BAR_BOX_HIKMICRO = Box(180, 382, 8, 27)
TOP_BOX_HIKMICRO = Box(139, 172, 9, 94)
BOTTOM_BOX_HIKMICRO = Box(389, 422, 9, 94)
MENU_BOX_HIKMICRO = Box(412, 459, 542, 629)
MIN_MAX_BOX_HIKMICRO = Box(7, 89, 8, 125)
EMISSIVITY_BOX_HIKMICRO = Box(444, 469, 10, 103)

HIKMICRO_UI_BOXES = [OUTER_BAR_BOX_HIKMICRO, TOP_BOX_HIKMICRO, BOTTOM_BOX_HIKMICRO, MENU_BOX_HIKMICRO, MIN_MAX_BOX_HIKMICRO, EMISSIVITY_BOX_HIKMICRO]


def getBoxes(FLIR: bool) -> tuple[Box, Box, Box, list[Box]]:
    if FLIR:
        TOP_BOX = TOP_BOX_FLIR
        BOTTOM_BOX = BOTTOM_BOX_FLIR
        INNER_BAR_BOX = INNER_BAR_BOX_FLIR
        UI_BOXES = FLIR_UI_BOXES
    else:
        # assuming we're only adding Hikmicro
        TOP_BOX = TOP_BOX_HIKMICRO
        BOTTOM_BOX = BOTTOM_BOX_HIKMICRO
        INNER_BAR_BOX = INNER_BAR_BOX_HIKMICRO
        UI_BOXES = HIKMICRO_UI_BOXES
    return TOP_BOX, BOTTOM_BOX, INNER_BAR_BOX, UI_BOXES 



def find_text_float(img: np.ndarray) -> float:    
    #convert to greyscale
    if len(img.shape) == 3:
        processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        processed_img = img.copy()
        
    #scale up image to approx 30 px.
    processed_img = cv2.resize(processed_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # otsu's thresholding to get black/white pixels and invert for black text on white bg
    _, processed_img = cv2.threshold(processed_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # flag only allow digits and a decimal point and minus sign
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=-0123456789.'
    
    text = pytesseract.image_to_string(processed_img, config=custom_config) 
    
    clean_text = re.sub(r'[^\d.-]', '', text)
    
    try:
        temp = float(clean_text)
        while temp > 40:
            temp = temp / 10
    except ValueError:
        print(f"Warning: Could not convert '{clean_text}' to float. Original text was: '{text}'")
        temp = 20.0 # toby plaster fix
    
    return temp


def make_colour_to_temp_map(t_min: float, t_max:float, bar:np.ndarray) -> KNeighborsRegressor:
    """
    Return a Regressor object to convert colours into temperatures, using the temperature bar ``bar``.

    Parameters:
    t_min (float): The minimum temperature in the image.

    t_max (float): The maximum temperature in the image.

    bar (np.ndarray): A 3D numpy array which is a crop of the temperature bar present in the thermal image.

    Returns:
    knn_model (sklearn.neighbors.KNeighborsRegressor): A K-Nearest-Neighbours regression model used to find the temperature
    to map a given BGR value to.
    """

    known_colours = []
    known_temps = []
    bar_h, bar_w, _ = bar.shape

    for i in range(bar_h):        
        temp = t_max - (i / bar_h) * (t_max - t_min)
        for x in range(bar_w):
            known_colours.append(bar[i, x])

            known_temps.append(temp)


    knn_model = KNeighborsRegressor(n_neighbors=3, weights='distance')
    knn_model.fit(known_colours, known_temps)
    return knn_model


def extract_from_box(img:np.ndarray, box:Box) -> np.ndarray:
    return img[box.yt:box.yb,
              box.xl:box.xr]

def image_to_temperature_map(img:np.ndarray, boxes: tuple[Box, Box, Box, list[Box]]) -> tuple[np.ndarray, float, float]:
    """
    Load the argument ``image_path`` as an array representing the BGR image. Use the temperature bar present in the 
    thermal image to convert the BGR image into a 2D array of the temperature image. 

    Parameters:
    image_path (PathLike): The path to the thermal image to be loaded.

    Returns:
    (tuple[np.ndarray, float, float]): The first element of the tuple contains a 2D numpy array of datatype float64,
    where each value is the temperature of the corresponding pixel in the loaded argument image.

    The second element of the tuple is the minimum temperature in the image.

    The third element is the maximum temperature in the image.
    """
    h, w, _ = img.shape
    TOP_BOX, BOTTOM_BOX, INNER_BAR_BOX, _ = boxes

    top = extract_from_box(img, TOP_BOX)
    
    bottom = extract_from_box(img, BOTTOM_BOX)

    bar = extract_from_box(img, INNER_BAR_BOX)
    t_min, t_max = find_text_float(bottom), find_text_float(top) 
          
    
    
    bar_h = bar.shape[0]

    knn_model = make_colour_to_temp_map(t_min, t_max, bar)


    predicted_temps = knn_model.predict(img.reshape(-1, 3))
    temp_img = predicted_temps.reshape(h, w)


    return temp_img, t_min, t_max
