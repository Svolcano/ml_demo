import cv2 as cv
import numpy as np

width = 400
height = 300
data = np.random.randint(0, 255, size=height*width*3, dtype=np.uint8)
image = data.reshape((width, height, 3))
#

p = 'C:/Users/shica/Desktop/a/a.png'
img_a = cv.imread(p)

cv.imshow('a', img_a)

a_width, a_height, a_channel = img_a.shape
data = np.zeros(img_a.shape, dtype=np.uint8)
data[:width,:height,:] = image[:,:,:]

img_new = np.vstack((img_a, data))

cv.rectangle(img_new, (100,100), (200,200), (0,0,255), 10)

cv.imshow('data', img_new)
cv.waitKey()
cv.destroyAllWindows()