from fastapi import FastAPI
from pydantic import BaseModel
from src.image import Image
from aggregate_calculations import get_psis

class ImagePayload(BaseModel):
    pixels: list[float]
    int_amb_temp: float
    ext_temp: float
    pixel_length: float
    wall_height: float


app = FastAPI()

@app.get("/analyse-image")
def psi_values(images : list[ImagePayload]):
    images : list[Image] = process(images)  # placeholder function, expected to return Image instances with calculated fields
    psis = get_psis(images)  # returns the psi values as a numpy array
    cold_bridges = [i.cb_pix for i in images]
    
    return {"psis": psis.tolist(), "cold_bridges": cold_bridges}

