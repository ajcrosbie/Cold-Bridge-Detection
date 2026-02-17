from fastapi import FastAPI
from pydantic import BaseModel
from aggregate_calculations import get_psis

class ImagePayload(BaseModel):
    pixels: list[float]
    int_amb_temp: float
    ext_temp: float
    pixel_length: float
    wall_height: float


app = FastAPI()

@app.get("/psis")
def psi_values(images : list[ImagePayload]):
    psis = get_psis(images)  # returns the psi values as a numpy array
    return {"psis": psis.tolist()}
