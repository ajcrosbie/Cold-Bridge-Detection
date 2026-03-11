# Cold-Bridge-Detection

In a well-insulated building, a continuous path from exterior to interior can become a **cold bridge**, leaking indoor heat to the cold outdoors.
Our solution is a web-app where users can follow instructions for taking thermal images, upload them, and receive an assessment of the severity of their cold bridges.

The frontend uses JavaScript, HTML and CSS, with a FastAPI backend split into two components - one for physics calculations and one for extracting temperatures from images.

We implemented an existing methodology from O'Grady et al to calculate psi-value from thermal images, alongside standard definitions of temperature sensitivity and temperature factor, helping homeowners understand both heat loss severity and condensation risk. For non-expert users, we also developed a severity rating system.

To extract pixel temperatures, we used K-nearest neighbours against the colour bar in each image. For cold bridge detection, we apply a mask separating the coldest pixels, then find the largest connected component. The threshold starts at 13% and increments iteratively if no bridge is found, accounting for cases where the cold bridge is warmer than the lowest reported temperatures.

Physics calculations are based on the following paper:

[O’Grady, M., Lechowska, A.A. and Harte, A.M. (2017). Infrared thermography technique as an in-situ method of assessing heat loss through thermal bridging.](https://www.sciencedirect.com/science/article/pii/S0378778816315882)

# Dependencies
- numpy - helps with fast number and array calculations.
- matplotlib - allows you to draw graphs and plots.
- pytesseract - reads text from images (OCR).
- scikit-learn - contains tools for machine learning.
- opencv-python - helps with processing images and videos.
- scipy - has advanced math and scientific functions.
- dataclasses - lets you organize data in an easy-to-read way.
- tesseract - Required for pytesseract to work 
- fastAPI - allows the webpage and server to interact.


run:
```bash
pip install numpy matplotlib pytesseract scikit-learn opencv-python scipy dataclasses "fastapi[standard]"
```


Then you need to install tesseract
https://tesseract-ocr.github.io/tessdoc/Installation.html
Ensure it's added to your path


# How to run

to run the server
```
fastapi run main.py
```
The backend URL must be set via the BACKENDTARGET variable in script.js.

There also needs to be a public webpage that the users can interact with. The contents of this webpage can be found in /frontend.


# Deployment Notes
It is also advised that a full penetration test is completed before actually being deployed to the internet.
