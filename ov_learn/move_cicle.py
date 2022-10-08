import cv2 as cv
import time
import numpy as np

w, h = 300, 300
r = 20
x = r + 20
y = r + 100
x_offer = y_offer = 4

while cv.waitKey(1) == -1:
    if x> w -r or x<r:
        x_offer *= -1
    if y > h -r or y < r:
        y_offer *= -1
    x += x_offer 
    y += y_offer

    img = np.ones((w, h, 3), dtype=np.uint8) * 255
    cv.circle(img, (x, y), r, (255,0,0), -1)
    cv.imshow('m', img)
    time.sleep(1/600)
