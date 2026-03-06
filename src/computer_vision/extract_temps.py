
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


BAR_BOX_FLIR = Box(29, 210, 306, 314)
TOP_BOX_FLIR = Box(5, 25, 274, 314) 
BOTTOM_BOX_FLIR = Box(215, 235, 274, 314)
AVERAGE_BOX_FLIR = Box(4, 25, 4, 69)
LOGO_BOX_FLIR = Box(219, 235, 4, 56)


#TODO: Set this using master functionz
FLIR = True

if FLIR:
    TOP_BOX = TOP_BOX_FLIR
    BOTTOM_BOX = BOTTOM_BOX_FLIR
    BAR_BOX = BAR_BOX_FLIR
else:
    #TODO: POPULATE
    pass


    
# TODO: check behaviour of undefined stuff here to include appropriate errors.
def find_min_max(img: np.ndarray) ->  tuple[float, float]:    
    
    top = img[TOP_BOX.yt:TOP_BOX.yb,
              TOP_BOX.xl:TOP_BOX.xr]
    
    bottom = img[BOTTOM_BOX.yt:BOTTOM_BOX.yb,
              BOTTOM_BOX.xl:BOTTOM_BOX.xr]

    top_text = pytesseract.image_to_string(top) # This might be crap but I have seen it before
    bottom_text = pytesseract.image_to_string(bottom)

    t_max = float(top_text.strip().replace("°C", "")) # More processing may be needed here fore more the non flir
    t_min = float(bottom_text.strip().replace("°C", "")) # More processing may be needed here fore more the non flir
    return t_min, t_max


def make_colour_to_temp_map(t_min: float, t_max:float, bar:np.ndarray) -> KNeighborsRegressor:
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


def extract_from_box(img:np.ndarray, box:Box):
    return img[box.yt:box.yb,
              box.xl:box.xr]

def image_to_temperature_map(image_path: PathLike):

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not loaded")

    h, w, _ = img.shape

    t_min, t_max = 10, 13 #find_min_max(img) TODO:REMOVE THIS PRE PUSH

    top = extract_from_box(img, TOP_BOX)
    
    bottom = extract_from_box(img, BOTTOM_BOX)

    bar = extract_from_box(img, BAR_BOX)
          
    
    
    bar_h = bar.shape[0]

    knn_model = make_colour_to_temp_map(t_min, t_max, bar)


    predicted_temps = knn_model.predict(img.reshape(-1, 3))
    temp_img = predicted_temps.reshape(h, w)


    return temp_img
