import cv2
import PySimpleGUI as sg
import numpy as np
import time, os
from datetime import date
import pytesseract
from pytesseract import Output
from PIL import ImageGrab
from mss import mss

# Mention the installed location of Tesseract-OCR in your system
# Production
pytesseract.pytesseract.tesseract_cmd = (
    r"C:/Users/shipping3/AppData/Local/Programs/Tesseract-OCR/tesseract"
)
# DEV
# pytesseract.pytesseract.tesseract_cmd = (
#     r"C:/Users/NateS/AppData/Local/Programs/Tesseract-OCR/tesseract"
# )
########### GUI ###############################################
sg.theme("Black")
layout = [
    [
        sg.Text(
            "Dolly Vision",
            size=(15, 1),
            font=("Helvetica", 20),
            justification="center",
        )
    ],
    [
        sg.Image(filename="", key="video"),
        sg.Image(filename="", key="video2"),
        sg.Image(filename="", key="video3"),
    ],
    [
        sg.Text(
            "Camera 1 (Left)",
            font=("helvetica", 20),
            justification="center",
        ),
        sg.Text(
            "Fail",
            background_color="red",
            key="cam-1",
            font=("helvetica", 16),
            size=(7, 1),
            justification="center",
        ),
    ],
    [
        sg.Text(
            "Camera 2 (Right)",
            font=("helvetica", 20),
            justification="center",
        ),
        sg.Text(
            "Fail",
            background_color="red",
            key="cam-2",
            font=("helvetica", 16),
            size=(7, 1),
            justification="center",
        ),
    ],
    [
        sg.Text(
            "Serial Number",
            font=("helvetica", 20),
            justification="center",
        ),
        sg.Text(
            "Not Found",
            background_color="red",
            key="cam-serial",
            font=("helvetica", 16),
            size=(15, 1),
            justification="center",
        ),
    ],
    [
        sg.Text(
            "Status: ",
            font=("helvetica", 20),
            justification="center",
        ),
        sg.Text(
            "Waiting...",
            font=("Helvetica", 16),
            background_color=("#328ba8"),
            size=(15, 1),
            justification="center",
            key="output",
        ),
        sg.Button("Exit", size=(7, 1), pad=(600, 0), font=("Helvetica", 14)),
    ],
]
# create the window and show it without the plot
window = sg.Window("Dolly Vision", layout, no_titlebar=False, location=(0, 0))


################################################################
path = "retainer-712.xml"  # PATH OF THE CASCADE
objectName = "Retainer Found"  # OBJECT NAME TO DISPLAY
frameWidth = 640  # DISPLAY WIDTH
frameHeight = 480  # DISPLAY HEIGHT
color = (0, 255, 0)
#################################################################
cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
cap3 = cv2.VideoCapture(2)

cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap2.set(3, frameWidth)
cap2.set(4, frameHeight)
cap3.set(3, 400)
cap3.set(4, 300)


# LOAD THE CLASSIFIERS DOWNLOADED
cascade = cv2.CascadeClassifier(path)

retainer1_detected = False
retainer2_detected = False
serial_detected = False


# left side cam
def cam1():
    global retainer1_detected
    global frame1

    # SET CAMERA BRIGHTNESS
    event, values = window.read(timeout=20)
    if values["-BRIGHTNESS-"]:
        cap.set(10, values["-BRIGHTNESS-"])
    if values["-KNN-"]:
        neighSlider = int(values["-KNN-"])
    if values["-SCALE-"]:
        scale = int(values["-SCALE-"])

    # GET CAMERA IMAGE AND CONVERT TO GRAYSCALE
    success, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # DETECT THE OBJECT USING THE CASCADE
    scaleVal = 1 + (scale / 1000)
    neig = neighSlider
    objects = cascade.detectMultiScale(gray, scaleVal, neig)
    # DISPLAY THE DETECTED OBJECTS
    if len(objects) > 0:
        window["cam-1"].update("PASS", background_color="green")
        retainer1_detected = True

    else:
        window["cam-1"].update("Fail", background_color="red")
        retainer1_detected = False
    imgbytes = cv2.imencode(".png", img)[1].tobytes()
    frame1 = img
    window["video"].update(data=imgbytes)


# right side cam
def cam2():
    global retainer2_detected
    global frame2

    # SET CAMERA BRIGHTNESS
    event, values = window.read(timeout=20)
    if values["-BRIGHTNESS-"]:
        cap2.set(10, values["-BRIGHTNESS-"])
    if values["-KNN-"]:
        neighSlider = int(values["-KNN-"])
    if values["-SCALE-"]:
        scale = int(values["-SCALE-"])

    # GET CAMERA IMAGE AND CONVERT TO GRAYSCALE
    success, img = cap2.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # DETECT THE OBJECT USING THE CASCADE
    scaleVal = 1 + (scale / 1000)
    neig = neighSlider
    objects = cascade.detectMultiScale(gray, scaleVal, neig)
    # DISPLAY THE DETECTED OBJECTS
    if len(objects) > 0:
        window["cam-2"].update("PASS", background_color="green")
        retainer2_detected = True

    else:
        window["cam-2"].update("Fail", background_color="red")
        retainer2_detected = False
    imgbytes = cv2.imencode(".png", img)[1].tobytes()
    frame2 = img
    window["video2"].update(data=imgbytes)


# serial cam
def cam3():
    global serial_detected
    global serialNumber
    global frame3

    ##screen cap stuff
    # GET CAMERA IMAGE AND CONVERT TO GRAYSCALE
    # bounding_box = {"top": 100, "left": 25, "width": 400, "height": 300}
    # sct = mss()
    # sct_img = sct.grab(bounding_box)
    # frame = np.array(sct_img)

    success, frame = cap3.read()

    # Read image from which text needs to be extracted
    d = pytesseract.image_to_data(frame, output_type=Output.DICT)
    n_boxes = len(d["text"])
    for i in range(n_boxes):
        if int(float(d["conf"][i])) > 30:
            if "SN:" in d["text"][i]:
                (x, y, w, h) = (
                    d["left"][i],
                    d["top"][i],
                    d["width"][i],
                    d["height"][i],
                )
                (x2, y2, w2, h2) = (
                    d["left"][i + 1],
                    d["top"][i + 1],
                    d["width"][i + 1],
                    d["height"][i + 1],
                )
                padding = 5
                cv2.rectangle(
                    frame,
                    (x2 - padding, y2 - padding),
                    (x2 + w2 + padding, y2 + h2 + padding),
                    color,
                    2,
                )
                cv2.putText(
                    frame,
                    "Serial Number: {}".format(d["conf"][i]),
                    (x2, y2 - 25),
                    cv2.FONT_HERSHEY_COMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
                # print(d["text"][i], d["text"][i + 1])
                window["cam-serial"].update(
                    "{}".format(d["text"][i + 1]),
                    background_color="green",
                )
                serialNumber = d["text"][i + 1]
                serial_detected = True

    imgbytes = cv2.imencode(".png", frame)[1].tobytes()
    frame3 = frame
    window["video3"].update(data=imgbytes)


def snapProof():
    global retainer1_detected, retainer2_detected, serial_detected
    # get all 3 images, combine, name, save on server. Profit.
    if not os.path.exists("saved-serial/{}".format(serialNumber)):
        os.mkdir("saved-serial/{}".format(serialNumber))
    cv2.imwrite(
        "saved-serial/{}/{}-{}-left.jpg".format(
            serialNumber, date.today(), serialNumber
        ),
        frame1,
    )
    cv2.imwrite(
        "saved-serial/{}/{}-{}-right.jpg".format(
            serialNumber, date.today(), serialNumber
        ),
        frame2,
    )
    cv2.imwrite(
        "saved-serial/{}/{}-{}-serial.jpg".format(
            serialNumber, date.today(), serialNumber
        ),
        frame3,
    )
    print("Snapping Proof!")
    retainer1_detected = False
    retainer2_detected = False
    serial_detected = False


def startApp():
    while True:
        event, values = window.read(timeout=20)

        cam1()
        cam2()
        cam3()
        if (
            retainer1_detected == True
            and retainer2_detected == True
            and serial_detected == True
        ):
            snapProof()
            window["output"].update(
                "Saved Images!",
                font=("Helvetica", 14),
                background_color=("green"),
            )
        else:
            window["output"].update(
                "Waiting...",
                font=("Helvetica", 14),
                background_color=("#328ba8"),
            )
        if window == sg.WIN_CLOSED:
            break
        if event == sg.WIN_CLOSED or event == "Exit":
            window.close()


startApp()
