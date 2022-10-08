import cv2 as cv

p = 'C:/Users/shica/Desktop/a/a.png'
image = cv.imread(p)
cv.imshow('a', image)

image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
t, img2 = cv.threshold(image, 177, 255, cv.THRESH_BINARY)

cv.imshow('b', img2)

t, img3 = cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
cv.imshow('c', img3)

cv.waitKey()
cv.destroyAllWindows()