import cv2
import numpy as np
from PIL import Image

img = cv2.imread("clean.png")
h, w = img.shape[:2]
mask = np.zeros((h+2, w+2), np.uint8)

cv2.floodFill(img, mask, (1,1), (0,0,255))  #fill from a guaranteed-white point

cv2.imwrite("filled.png", img)

im = Image.open('filled.png')
pixels = im.load()
w, h = im.size

fill = False

im = Image.open("filled.png").convert("RGB")
pixels = im.load()
w, h = im.size

for i in range(w):
    for j in range(h):
        if pixels[i, j] != (255, 255, 255):
            pixels[i, j] = (0, 0, 0)

im.save("filled.png")


count = 0
print(pixels[0,0])


for i in range(w):
    for j in range(h):
        if pixels[i,j] != (0,0,0):
            count += 1

print(count)

 