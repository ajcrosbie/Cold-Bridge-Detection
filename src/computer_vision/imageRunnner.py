from extract_cold_bridge  import *
from extract_temps import *


def run_images(img_path:PathLike):
    timg, tmin, tmax = image_to_temperature_map(img_path)
    return find_bridge(detect_cold_mask(tmin, tmax, timg))