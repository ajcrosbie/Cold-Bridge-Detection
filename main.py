from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from PIL import Image as PILImage
from src.image import Image
from src.aggregate_calculations import *
import os
from pathlib import Path
import shutil
from uuid import uuid4
from src.computer_vision.imageRunnner import run_images
import numpy as np
from src.value_calculation import calc_pixel_length
import logging

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],       # Allow all headers
)


# Plots directory
PLOT_DIR = "plots"
os.makedirs(PLOT_DIR, exist_ok=True)
app.mount("/plots", StaticFiles(directory=PLOT_DIR), name="plots")


@app.post("/analyse-images/")
def analyse_images(
    files: list[UploadFile] = File(...),
    locations: list[str] = Form(...),
    int_amb_temps: list[float] = Form(...),
    ext_temps: list[float] = Form(...),
    emissivities: list[float] = Form(...),
    wall_heights: list[float] = Form(...),
    camera_types: list[str] = Form(...)
):
    """
    Accept multiple image files, a location name per image, and payload parameters.
    Returns a dictionary containing data to be used by the frontend
    """
    with open("Backendlogs.txt", "a") as f:
        f.write("Request received\n")

    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir(exist_ok=True)

    file_paths: list[Path] = []
    
    for file in files:
        # create unique filename to avoid collisions
        ext = Path(file.filename).suffix
        unique_name = f"{uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / unique_name
        
        # save file to disk
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        file_paths.append(file_path)

    # Validate lengths
    if not (len(files) == len(locations) == len(int_amb_temps) == len(ext_temps) == len(emissivities)
            == len(wall_heights) == len(camera_types)):
        return {"error": "Mismatch between number of files, locations, and payload parameters"}

    # Dictionary mapping location -> list of Image objects
    location_dict = {}

    for idx, file in enumerate(files):

        # Create Image object
        img_obj = Image(
            None,
            None,
            None,
            int_amb_temps[idx],
            ext_temps[idx],
            emissivities[idx],
            calc_pixel_length(camera_types[idx]),
            wall_heights[idx]
        )

        # Append to location list
        loc = locations[idx]
        if loc not in location_dict:
            location_dict[loc] = []
        location_dict[loc].append(img_obj)

    # Process all images
    processed_results = run_images(file_paths, camera_types)

    # Collect all images in the order they were processed
    all_images = []
    for img_list in location_dict.values():
        all_images.extend(img_list)

    # Map processed results back to Image objects
    for idx, img in enumerate(all_images):
        img.cb_pix = processed_results[idx][0]
        # processed_results returns (cb_pixels, surface_temp)
        img.sf_temp = processed_results[idx][1]  # update sf_temp so psi calc uses correct value

    # float[][] of psi values for each image for each cold bridge
    psi_lists = [get_psis(img_list) for img_list in location_dict.values()]

    # calculate error margins for each cold bridge
    psi_values = [calculate_psi_ci(psi_list)[0] for psi_list in psi_lists]
    error_margins = [calculate_psi_ci(psi_list)[1] for psi_list in psi_lists]

    psi_severities = [psi_to_severity(psi) for psi in psi_values]

    plot_paths = []
    for img_list in location_dict.values():
        plot_paths.append(plot_sensitivities(img_list))

    plot_paths.append(plot_severities(location_dict))
    plot_paths.append(plot_psis(location_dict))
    plot_paths.append(plot_frsis(location_dict)) 

    print("List lengths equal: " + str(len(psi_lists)==len(psi_severities)==len(error_margins)))

    # Clean up uploaded files
    for file_path in file_paths:
        try:
            file_path.unlink()
        except OSError:
            pass  # Ignore if file already deleted or inaccessible

    return {
        "locations": list(location_dict.keys()),
        "psis": psi_lists.tolist(),
        "psi_severities": psi_severities,
        "error_margins": error_margins.tolist(),
        "plots": plot_paths
    }