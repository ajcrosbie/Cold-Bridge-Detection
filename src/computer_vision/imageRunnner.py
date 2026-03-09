from extract_cold_bridge  import *
from extract_temps import *



def run_images(img_paths:list[PathLike]) -> list[tuple[np.ndarray, float]]:
    l = []
    for i in img_paths:
        timg, tmin, tmax = image_to_temperature_map(i)
        cb = find_bridge(detect_cold_mask(tmin, tmax, timg))
        l.append(extract_from_box(timg, cb), find_mean(timg, cb))
        
    return l

