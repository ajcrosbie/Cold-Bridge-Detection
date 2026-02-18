
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


def find_bar_coords(img: np.MatLike) -> tuple[int, int, int, int]:
    # hopefully generalisable function to find the location of the bar in the image
    # bar will be either on left of image or the right of image

    # the logic is that the border of the bar a greyscale value, so we scan each side of the image for greyscale pixels which have non-greyscale pixels above them.
    # these non-greyscale pixels are interpreted as being the beginning of the bar
    h, w, _ = img.shape

    # yt == 0 and yb == h for both the left and right boxes to be scanned through
    left_xl = 0
    left_xr = int(w * 0.15)
    right_xl = int(w * 0.85)
    right_xr = w

    bar_xl = 0
    bar_xr = 0
    bar_yt = 0
    bar_yb = 0
    

    scan_xl = left_xl
    scan_xr = left_xr

    # do 2 iterations, one for the left box and one for the right box
    # the expectation is that the while loop breaks either in the middle of the first iteration, or the middle of the second iteration. It should never run forever.
    while True:
        coords_set = False

        for y in range(h - 1, 0, -1):
            for x in range(scan_xl, scan_xr):
                b, g, r = img[y,x]

                if b == g and g == r:
                    above_b, above_g, above_r = img[y-1, x]     # rgb of the pixel above
                    if not (above_b == above_g and above_g == above_r):
                        bar_xl = x
                        bar_yb = y - 1
                        break
            
            for x in range(bar_xl, w):
                b, g, r = img[y,x]
                
                if b == g and g == r:
                    bar_xr = x - 1
                    break
            break
        
        for y in range(bar_yt, 0, -1):
            if b == g and g == r:
                bar_yt = y + 1
                coords_set = True
                break
        
        if coords_set:
            break

        scan_xl = right_xl
        scan_xr = right_xr

    return (bar_yt, bar_yb, bar_xl, bar_xr)

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
        colour = bar[i, 0] # assume bar is monochrome across and barbox is fully within the bar

        temp = t_max - (i / bar_h) * (t_max - t_min)
        colour_to_temp[colour] = temp
    return colour_to_temp

def image_to_temperature_map(image_path: PathLike):

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not loaded")

    h, w, _ = img.shape

    t_max, t_min = find_min_max(img)

    bar_coords = find_bar_coords(img)

    # bar = img[int(BAR_BOX.yt*h):int(BAR_BOX.yb*h),
    #           int(BAR_BOX.xl*w):int(BAR_BOX.xr*w)]

    bar = img[bar_coords[0] : bar_coords[1], bar_coords[2] : bar_coords[3]]

    bar_h = bar.shape[0]

    colour_to_temp = make_colour_to_temp_map(t_min, t_max, bar)

    temp_img = np.zeros((h, w))    
    for y in range(h):
        for x in range(w):
            pixel = img[y, x]
            temp_img[x,y] = colour_to_temp[pixel]

    return temp_img
