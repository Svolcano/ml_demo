import numpy as np 
import cv2 as cv
import matplotlib.pyplot as plt
import math

def vec_to_image_data(v1):
    plt.plot(range(len(v1)), v1)
    plt.axis('off')
    

    canvas = plt.gca().figure.canvas
    canvas.draw()
    data = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
    image = data.reshape(canvas.get_width_height()[::-1] + (3,))
    return image
v1 = [math.cos(i) for i in range(1,100)]

v1 = vec_to_image_data(v1)
v1 = cv.cvtColor(v1, cv.COLOR_BGR2GRAY)
contours, hierarchy = cv.findContours(v1, 3, 2)
# img_color = cv.cvtColor(v1, cv.COLOR_GRAY2BGR)  # 用于绘制的彩色图

# cnt_a, cnt_b, cnt_c = contours[0], contours[1], contours[2]
# cv.drawContours(img_color,[cnt_a],0,[255,0,0],2)
# cv.drawContours(img_color,[cnt_b],0,[0,255,0],2)
# cv.drawContours(img_color,[cnt_c],0,[0,0,255],2)

# # 参数3：匹配方法；参数4：opencv预留参数
# print('b,b = ',cv.matchShapes(cnt_b, cnt_b, 1, 0.0))  # 0.0
# print('b,c = ',cv.matchShapes(cnt_b, cnt_c, 1, 0.0))  # 2.17e-05
# print('b,a = ',cv.matchShapes(cnt_b, cnt_a, 1, 0.0))  # 0.418

cv.imshow('result',v1)
cv.waitKey(0)
cv.destroyAllWindows()