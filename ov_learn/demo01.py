import cv2 as cv
import numpy as np


def show(b):
    cv.imshow('d', b)
    cv.waitKey()
    cv.destroyAllWindows()

p = 'C:/Users/shica/Desktop/a/a.png'

image = cv.imread(p)
b,g,r = cv.split(image)

rm = np.zeros(r.shape, dtype='uint8')
rm = np.zeros(r.shape)
rm.dtype = 'uint8'

print(rm.dtype, rm.shape, rm.size)
print(r.dtype, r.shape, r.size)

m = cv.merge([b, g, rm])
show(m)

