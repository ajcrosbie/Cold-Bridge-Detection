from fastapi import FastAPI
from pydantic import BaseModel
from src.image import Image
from aggregate_calculations import *
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

GRAPHDIR = "plots"
os.makedirs(GRAPHDIR, exist_ok=True)

app.mount("/plots", StaticFiles(directory=GRAPHDIR), name="plots")

class ImagePayload(BaseModel):
    name: str
    pixels: list[float]
    int_amb_temp: float
    ext_temp: float
    emissivity:float
    pixel_length: float
    wall_height: float


@app.post("/analyse-images")
def analyse_images(images : list[ImagePayload]):
    images = {i.name: Image(i.pixels, None, None, i.int_amb_temp, i.ext_temp, i.emissivity, i.pixel_length, i.wall_height) for i in images}
    images = process(images)  # placeholder function, expected to provide cold bridge pixels and sf_pix

    psis = get_psis(images)  # returns the psi values as a numpy array
    cold_bridges = [i.get_cb() for i in images]

    plot_sensitivies(images.values())  # saves the plot
    plot_psis(images)
    plot_severities(images)

    plot_urls = []
    for plot_name in ["sensitivity", "psis", "severities"]:
        plot_urls.append(f"{GRAPHDIR}/{plot_name}")
    
    return {
        "psis": psis.tolist(), 
        "cold_bridges": cold_bridges, 
        "plots": plot_urls
    }

