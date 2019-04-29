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

    def ative_algorithm(self, filename, img, guided_line, parameter_list):
        # img = io.imread('upscaled.png')
        # # img = data.astronaut()
        # img = rgb2gray(img)
        # img = img[:, 0:1000]

        # def active_contour(image, snake, alpha=0.01, beta=0.1,
        #                    w_line=0, w_edge=1, gamma=0.01,
        #                    bc='periodic', max_px_move=1.0,
        #                    max_iterations=2500, convergence=0.1):

        # init2 = numpy_rect.create_rectangle(start_x, end_x, start_y, end_y)
        init2 = guided_line
        start = time.time()
        snake = active_contour(gaussian(img,3),
                               init2, alpha=parameter_list[0], beta=parameter_list[1], w_line=parameter_list[2], w_edge=parameter_list[3],
                               gamma=parameter_list[4], bc=parameter_list[5], max_px_move=parameter_list[6], max_iterations=parameter_list[7], convergence=parameter_list[8])

        print('Time =', time.time()-start)
        return snake, init2, img,  time.time()-start

    def create_outline_for_extraction(self, list_of_points):
        final_init = np.array([list_of_points[0][0], list_of_points[0][1]])
        for i, each in enumerate(list_of_points):
            if i < len(list_of_points)-1:
                start_x,start_y = list_of_points[i][0], list_of_points[i][1]
                end_x, end_y = list_of_points[i+1][0], list_of_points[i+1][1]
                x = np.linspace(start_x, end_x, 10)
                y = np.linspace(start_y, end_y, 10)
                init = np.array([x, y]).T
                final_init = np.vstack((final_init, init))
            # else:
            #     start_x,start_y = list_of_points[-1][0], list_of_points[-1][1]
            #     end_x, end_y = list_of_points[0][0], list_of_points[0][1]
            #     x = np.linspace(start_x, end_x, 10)
            #     y = np.linspace(start_y, end_y, 10)
            #     init = np.array([x, y]).T
            #     final_init = np.vstack((final_init, init))

        init_for_drawing = final_init.astype('uint8')
        # init_for_drawing = np.unique(init_for_drawing, axis=1)
        new_array = [tuple(row) for row in init_for_drawing]
        init_for_drawing = np.unique(new_array)
        return final_init
