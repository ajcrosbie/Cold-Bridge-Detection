from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from PIL import Image as PILImage
from src.image import Image
from src.aggregate_calculations import *
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
        # Load PIL image directly from memory
        pil_image = PILImage.open(file.file).convert("RGB")

        # Create Image object
        img_obj = Image(
            pil_image,
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

    plot_sensitivities(processed_images)
    plot_severities(location_dict)
    plot_frsis(location_dict)

    plot_urls = ["/plots/sensitivity.jpeg", "/plots/severities.jpeg", "/plots/frsis.jpeg"]


    return {
        "psis": psi_values.tolist(),
        "psi_severities": psi_severities,
        "plots": plot_urls
    }