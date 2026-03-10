# Cold-Bridge-Detection

detecting cold bridges
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


There also needs to be a public webpage that the users can interact with. The contents of this webpage can be found in /frontend.

# Challenges
It is also advised that a full penetration test is completed before actually being deployed to the internet. Because
