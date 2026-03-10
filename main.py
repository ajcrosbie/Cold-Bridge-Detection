from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from src.image import Image
from src.aggregate_calculations import *
import numpy as np
import cv2
import os

app = FastAPI()

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
    camera_type: str = Form(...)
):
    """
    Accept multiple image files, a location name per image, and payload parameters.
    Returns a dictionary containing data to be used by the frontend
    """

    # Validate lengths
    if not (len(files) == len(locations) == len(int_amb_temps) == len(ext_temps) == len(emissivities)
            == len(wall_heights)):
        return {"error": "Mismatch between number of files, locations, and payload parameters"}

    # Dictionary mapping location -> list of Image objects
    location_dict = {}

    for idx, file in enumerate(files):
        # Read file bytes and decode them directly into an OpenCV-ready BGR NumPy array
        contents = file.file.read()
        img_np = np.frombuffer(contents, np.uint8)
        img_cv2 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        # Create Image object
        img_obj = Image(
            img_cv2,
            None,
            None,
            int_amb_temps[idx],
            ext_temps[idx],
            emissivities[idx],
            None,
            wall_heights[idx]
        )

        # Append to location list
        loc = locations[idx]
        if loc not in location_dict:
            location_dict[loc] = []
        location_dict[loc].append(img_obj)

    # Process all images
    all_images = [img for imgs in location_dict.values() for img in imgs]
    processed_images = process(all_images)  # placeholder function, expected to fill in cb_pix and sf_pix

    # Map processed images back to locations
    processed_idx = 0
    for loc, img_list in location_dict.items():
        for i in range(len(img_list)):
            img_list[i] = processed_images[processed_idx]
            processed_idx += 1

    
    psi_values = get_psis(processed_images)
    psi_severities = [psi_to_severity(psi) for psi in psi_values]

    plot_paths = []
    for loc in location_dict.keys():
        plot_paths.append(plot_sensitivities(processed_images))

    plot_paths.append(plot_severities(location_dict))
    plot_paths.append(psi_plot = plot_psis(location_dict))
    plot_paths.append(frsis_plot = plot_frsis(location_dict))   

    return {
        "psis": psi_values.tolist(),
        "psi_severities": psi_severities,
        "plots": plot_paths
    }