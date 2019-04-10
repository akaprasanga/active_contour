import numpy as np
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage import data
from skimage.filters import gaussian
from skimage.segmentation import active_contour
from skimage import io
import numpy_rect
import time


class ActiveContour:

    def __init__(self):
        pass

    def ative_algorithm(self, filename, img, start_x, end_x, start_y, end_y):
        # img = io.imread('upscaled.png')
        # # img = data.astronaut()
        # img = rgb2gray(img)
        # img = img[:, 0:1000]
        init2 = numpy_rect.create_rectangle(start_x, end_x, start_y, end_y)
        start = time.time()
        snake = active_contour(gaussian(img,3),
                               init2, alpha=0.15, beta=10, gamma=0.01, w_line=0, w_edge=10, max_iterations=2000)

        print('Time =', time.time()-start)
        return snake, init2, img
        # end = time.time()
        # print("time taken = ", end-start)
        #
        # fig, ax = plt.subplots(figsize=(15, 10))
        # ax.imshow(img, cmap=plt.cm.gray)
        # ax.plot(init2[:, 0], init2[:, 1], '--r', lw=1)
        # ax.plot(snake[:, 0], snake[:, 1], '-b', lw=1)
        # ax.set_xticks([]), ax.set_yticks([])
        # ax.axis([0, img.shape[1], img.shape[0], 0])
        # plt.savefig('test.png', bbox_inches="tight")
