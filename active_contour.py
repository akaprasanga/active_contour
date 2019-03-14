import numpy as np
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage import data
from skimage.filters import gaussian
from skimage.segmentation import active_contour
from skimage import io

img = io.imread('salsa_20.jpg')
# img = data.astronaut()
img = rgb2gray(img)

s = np.linspace(0, 2*np.pi, 300)
x = 600 + 150*np.cos(s)
y = 600 + 150*np.sin(s)
init = np.array([x, y]).T
print(init)

w = np.linspace(500, 700, 400)
# line1 = list(line1)
h = np.linspace(100, 300, 400)

w1 = 200 + 1*w
h1 = 200 + 1*h
init2 = np.array([w1, h1])
# init2 = np.array([lx, ly]).T
print(init2)
#
snake = active_contour(gaussian(img, 3),
                       init2, alpha=0.015, beta=10, gamma=0.001, w_line= -2)

fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(img, cmap=plt.cm.gray)
ax.plot(init2[:, 0], init2[:, 1], '--r', lw=3)
ax.plot(snake[:, 0], snake[:, 1], '-b', lw=3)
ax.set_xticks([]), ax.set_yticks([])
ax.axis([0, img.shape[1], img.shape[0], 0])