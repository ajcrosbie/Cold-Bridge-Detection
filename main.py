from fastapi import FastAPI
from pydantic import BaseModel
from src.image import Image
from aggregate_calculations import get_psis

class ImagePayload(BaseModel):
    pixels: list[float]
    int_amb_temp: float
    ext_temp: float
    emissivity:float
    pixel_length: float
    wall_height: float


app = FastAPI()

@app.get("/analyse-images")
def analyse_images(images : list[ImagePayload]):
    images = [Image(i.pixels, None, None, i.int_amb_temp, i.ext_temp, i.emissivity, i.pixel_length, i.wall_length) for i in images]
    images = process(images)  # placeholder function, expected to calculate and fill in the None fields
    psis = get_psis(images)  # returns the psi values as a numpy array
    cold_bridges = [i.cb_pix for i in images]
    
    return {"psis": psis.tolist(), "cold_bridges": cold_bridges}

