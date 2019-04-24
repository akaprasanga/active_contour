import numpy as np
import matplotlib.pyplot as plt


def create_rectangle(start_x, end_x, start_y, end_y):
    # start_x = 200
    # end_x = 600
    # start_y = 100
    # end_y = 300

    horizontal_run1 = np.linspace(start_x, end_x, end_x - start_x)
    horizontal_run2 = np.linspace(end_x, start_x, end_x - start_x)
    vertical_run1 = np.linspace(start_y, end_y, end_y - start_y)
    vertical_run2 = np.linspace(end_y, start_y, end_y - start_y)

    # each_startx = np.ones(vertical_run1.shape)*start_x
    # each_endx = np.ones(vertical_run1.shape)*start_x

    array_of_strat_x = np.ones(vertical_run1.shape) * start_x
    array_of_end_x = np.ones(vertical_run1.shape) * end_x
    array_of_start_y = np.ones(horizontal_run1.shape) * start_y
    array_of_end_y = np.ones(horizontal_run1.shape) * end_y

    l1 = np.array([horizontal_run1, array_of_start_y]).T
    l2 = np.array([horizontal_run2, array_of_end_y]).T
    h1 = np.array([array_of_strat_x, vertical_run1]).T
    h2 = np.array([array_of_end_x, vertical_run2]).T

    abc = np.vstack((l1, h2))
    cda = np.vstack((l2, h1))

    rectangle = np.vstack((abc, cda))
    # plt.scatter(rectangle[:, 0], rectangle[:, 1])

    return rectangle
    # print(rectangle)

def create_line(start_x, end_x, start_y, end_y):
    # x = np.linspace(start_x, end_x, max(end_x,start_x)-min(end_x, start_x))
    # y = np.linspace(start_y, end_y, max(end_y, start_y)-min(end_y, start_y))
    x = np.linspace(start_x, end_x, 200)
    y = np.linspace(start_y, end_y, 200)
    init = np.array([x, y]).T
    return init