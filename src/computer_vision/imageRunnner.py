from .extract_cold_bridge  import *
from .extract_temps import *



def run_images(img_paths:list[str], FLIR:list[str]) -> list[tuple[np.ndarray, float]]:
    l = []
    for i in range(len(img_paths)):
        boxes = getBoxes(FLIR[i]== "FLIR E40bx")
        timg, tmin, tmax = image_to_temperature_map(img_paths[i], boxes)
        cb = find_bridge(detect_cold_mask(tmin, tmax, timg, boxes[-1]))
        l.append((extract_from_box(timg, cb), find_mean(timg, cb, boxes[-1])))
        
    return l

