import cv2
import numpy as np
import pytesseract
from dataclasses import dataclass
# For ease of configurablity once we have some actual data.
@dataclass
class Box:
    yt:float # y axis most top
    yb:float # y axis most bottom
    xl:float # x axis most left
    xr:float # x axis most right

# Overestimate better than under

TOP_TEXT_BOX = Box(0, 0.1, 0.8, 1) 
BOTTOM_TEXT_BOX = Box(0.9, 1, 0.8, 1) 

BAR_BOX = Box(0.05, 0.95,0.92, 0.98)


# TODO: check behaviour of undefined stuff here to include appropriate errors.
def find_min_max(img: np.Matlike) ->  tuple[float, float]:
    h, w, _ = img.shape
    
    
    top_crop = img[int(TOP_TEXT_BOX.yt*h):int(TOP_TEXT_BOX.yb*h), int(TOP_TEXT_BOX.xl*w):TOP_TEXT_BOX.xr*w]
    bottom_crop = img[int(BOTTOM_TEXT_BOX.yt*h):BOTTOM_TEXT_BOX.yb*h, int(BOTTOM_TEXT_BOX.xl*w):BOTTOM_TEXT_BOX.xr*w]

    top_text = pytesseract.image_to_string(top_crop) # This might be crap but I have seen it before
    bottom_text = pytesseract.image_to_string(bottom_crop)

    t_max = float(top_text[:-3]) # remove the 
    t_min = float(bottom_text[:-3])
    return t_min, t_max

def make_colour_to_temp_map(t_min: float, t_max:float, bar:MatLike) -> dict[[tuple[int, int, int]], float]:
    colour_to_temp = {}
    bar_h = bar.shape[0]
    for i in range(bar_h):
        colour = bar[i, 0] # assume bar is monchrome across and barbox is fully within the bar

        temp = t_max - (i / bar_h) * (t_max - t_min)
        colour_to_temp[colour] = temp
    return colour_to_temp

def image_to_temperature_map(image_path: PathLike):

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not loaded")

    h, w, _ = img.shape

    t_max, t_min = find_min_max(img)

    bar = img[int(BAR_BOX.yt*h):int(BAR_BOX.yb*h),
              int(BAR_BOX.xl*w):int(BAR_BOX.xr*w)]

    bar_h = bar.shape[0]


    colour_to_temp = make_colour_to_temp_map(t_min, t_max, bar)

    temp_img = np.zeros((h, w))    
    for y in range(h):
        for x in range(w):
            pixel = img[y, x]
            temp_img[x,y] = colour_to_temp[pixel]

    return temp_img
