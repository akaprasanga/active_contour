from skimage import io
from skimage import data, img_as_float
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.measure import compare_psnr
from skimage.util import random_noise
from skimage.transform import rescale

img = io.imread('loft_basic_002.jpg')
img = rescale(img, 3)
io.imsave('upscaled.png', img)