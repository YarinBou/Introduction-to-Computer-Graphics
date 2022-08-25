# Pre-requisites
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from functools import partial
from numba import jit
import sys

# Global parameter
greyscale_wt = [0.299, 0.587, 0.114]

def get_greyscale_image(image, colour_wts):
    """
    Gets an image and weights of each colour and returns the image in greyscale
    :param image: The original image
    :param colour_wts: the weights of each colour in rgb (ints > 0)
    :returns: the image in greyscale
    """
    R, G, B = image[:,:,0], image[:,:,1], image[:,:,2]
    greyscale_image = colour_wts[0] * R + colour_wts[1] * G + colour_wts[2] * B
    return greyscale_image
    
def reshape_bilinear(image, new_shape):
    """
    Resizes an image to new shape using bilinear interpolation method
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :returns: the image resized to new_shape
    """
    in_height, in_width, c = image.shape  # the dimension of an original image 
    out_height, out_width = new_shape     # the dimension of a desired image
    new_image = np.zeros((out_height, out_width, c))      # initiallize an image with desired height and width
    
    # Calculates a horizontal, and a vertical scaling factor
    w_scale_factor = in_width / out_width if out_height != 0 else 0
    h_scale_factor = in_height / out_height if out_width != 0 else 0
    
    # Resizes an image to new shape using bilinear interpolation method
    for i in range(out_height):
        for j in range(out_width):
            # map the coordinates back to the original image
            x = i * h_scale_factor
            y = j * w_scale_factor
            # calculate the coordinate values for 4 surrounding pixels.
            x_floor = math.floor(x)
            x_ceil = min(in_height - 1, math.ceil(x))
            y_floor = math.floor(y)
            y_ceil = min(in_width - 1, math.ceil(y))

            if (x_ceil == x_floor) and (y_ceil == y_floor):
                q = image[int(x), int(y), :]
            elif x_ceil == x_floor:
                q1 = image[int(x), int(y_floor), :]
                q2 = image[int(x), int(y_ceil), :]
                q = q1 * (y_ceil - y) + q2 * (y - y_floor)
            elif y_ceil == y_floor:
                q1 = image[int(x_floor), int(y), :]
                q2 = image[int(x_ceil), int(y), :]
                q = (q1 * (x_ceil - x)) + (q2 * (x - x_floor))
            else:
                v1 = image[x_floor, y_floor, :]
                v2 = image[x_ceil, y_floor, :]
                v3 = image[x_floor, y_ceil, :]
                v4 = image[x_ceil, y_ceil, :]

                q1 = v1 * (x_ceil - x) + v2 * (x - x_floor)
                q2 = v3 * (x_ceil - x) + v4 * (x - x_floor)
                q = q1 * (y_ceil - y) + q2 * (y - y_floor)
                
            new_image[i,j,:] = q
            
    return new_image.astype(np.uint8)
    
def gradient_magnitude(image, colour_wts):
    """
    Calculates the gradient image of a given image
    :param image: The original image
    :param colour_wts: the weights of each colour in rgb (> 0) 
    :returns: The gradient image
    """
    greyscale = get_greyscale_image(image, colour_wts)
    height, width = greyscale.shape
    gradient = np.zeros((height, width))
    # fill the image
    for i in range(height - 1):
        for j in range(width - 1):
            dx = greyscale[i + 1][j] - greyscale[i, j]
            dy = greyscale[i][j + 1] - greyscale[i, j]
            magnitude = (np.sqrt(np.power(dx, 2) + np.power(dy, 2)))
            gradient[i, j] = magnitude

    # fill the last row and colum
    for j in range(width - 1):
        dx = greyscale[0][j] - greyscale[height - 1, j]
        dy = greyscale[height - 1][j + 1] - greyscale[height - 1, j]
        magnitude = (np.sqrt(np.power(dx, 2) + np.power(dy, 2)))
        gradient[height - 1, j] = magnitude
    for i in range(height - 1):
        dx = greyscale[i + 1][width - 1] - greyscale[i, width - 1]
        dy = greyscale[i][0] - greyscale[i, width - 1]
        magnitude = (np.sqrt(np.power(dx, 2) + np.power(dy, 2)))
        gradient[i, width - 1] = magnitude
    # fill the corner pixel
    dx = greyscale[0][width - 1] - greyscale[height - 1, width - 1]
    dy = greyscale[height - 1][0] - greyscale[height - 1, width - 1]
    magnitude = (np.sqrt(np.power(dx, 2) + np.power(dy, 2)))
    gradient[height - 1, width - 1] = magnitude
    return gradient


# Implementation of seams carving algorithm
# We added a bunch of auxiliary methods.

def get_vertical_seams(image, seams_number):
    vertical_seams_list = []
    for i in range(seams_number):
        M, backtrack = calculate_cost_matrix(image)
        vertical_seams_list.append(find_seam(M, backtrack))
        image = remove_seam(image, vertical_seams_list[i])
    return vertical_seams_list, image
                  
        
def get_horizontal_seams(image, seams_number):
    # Rotate an array by 90 degrees in the plane k times.
    image = np.rot90(image, k=1)
    horizontal_seams_list, image = get_vertical_seams(image, seams_number)
    if seams_number != 0:
        # Reverse the order of elements in an array along the given axis
        horizontal_seams_list = np.flip(horizontal_seams_list, axis=2) 
    image = np.rot90(image, k=3)                     
    return horizontal_seams_list, image
        
def calculate_cost_matrix(image):
    height, width, _ = image.shape
    energy_map = gradient_magnitude(image, greyscale_wt)
    image = get_greyscale_image(image, greyscale_wt)                       
    # M represents the energy of the lowest-energy vertical seam that starts at the top of the image
    M = calculate_cost(energy_map, image)
    # Back pointers to know which of the pixels in the previous row led to that energy
    backtrack = np.zeros_like(M, dtype=int)
    # Skip the first row in the following loop.
    for i in range(1, height):
        for j in range(0, width):
            # Determine the range of x values to iterate over in the previous
            # row. The range depends on if the current pixel is in the middle of
            # the image, or on one of the edges.
            if j == 0:
                idx = np.argmin(M[i-1, j : j+2])
                backtrack[i, j] = idx + j
            else:
                idx = np.argmin(M[i - 1, j - 1:j + 2])
                backtrack[i, j] = idx + j - 1
    return M, backtrack
               
def calculate_cost(energy_map, image):
    M = energy_map.copy()
    for row in range(1, M.shape[0]):
        for col in range(M.shape[1]):
            M[row, col] += find_min_neighbor_cost(M, image, row, col)
    return M

def find_seam(M, backtrack):
    j = np.argmin(M[-1])
    seam = []
    for row in reversed(range(M.shape[0])):
        seam.append([row, j])
        j = backtrack[row, j]   
    return seam

def remove_seam(image, seam):
    height, width, rgb = image.shape
    mask = np.ones_like(image, dtype=bool)
    for s in seam:
        mask[s[0], s[1]] = False
    image = image[mask].reshape(height, width - 1, rgb)
    return image
      
def calc_edges(image, height, width, neighbor):
    cost = 0
    if width == 0 and neighbor == 'vertical':
        return cost
    elif width == image.shape[1] - 1 and neighbor == 'vertical':
        return cost
    if width != 0 and width != image.shape[1] - 1:
        cost = abs(image[height, width + 1] - image[height, width - 1])
    if neighbor == 'left':
        cost += abs(image[height - 1, width] - image[height, width - 1])
    elif neighbor == 'right':
        cost += abs(image[height, width + 1] - image[height - 1, width])
    return cost

def find_min_neighbor_cost(matrix, image, height, width):
    left, vertical, right = sys.maxsize, sys.maxsize, sys.maxsize
    if width != 0:
        left = matrix[height - 1, width - 1] + calc_edges(image, height, width, 'left')
    if width != matrix.shape[1] - 1:
        right = matrix[height - 1, width + 1] + calc_edges(image, height, width, 'right')
        
    vertical = matrix[height - 1, width] + calc_edges(image, height, width, 'vertical')
    return np.min(np.array([left, vertical, right]))


def colouring_seams(image, list_of_seams, colour):
    for seam in list_of_seams:
        for s in seam:
            #image = np.array(Image.open(filename))
            image[s[0], s[1]] = colour
    return image

def visualise_seams(image, new_shape, show_horizontal, colour=[255,0,0]):
    """
    Visualises the seams that would be removed when reshaping an image to new image (see example in notebook)
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :param show_horizontal: the carving scheme to be used.
    :param colour: the colour of the seams (an array of size 3)
    :returns: an image where the removed seams have been coloured.
    """
    new_height, new_width = new_shape
    while new_height > image.shape[0] or new_width > image.shape[1]:
        new_height = int(input("Warning! The new image size is bigger than the original image\nInsert new image height: "))
        new_width = int(input("Insert new image width: "))    
    copy_image = image.copy()
    if (show_horizontal):
        number_of_seams = image.shape[0] - new_height
        seams_to_visualise, _ = get_horizontal_seams(copy_image, number_of_seams)
    else:
        number_of_seams = image.shape[1] - new_width
        seams_to_visualise, _ = get_vertical_seams(copy_image, number_of_seams)
    return colouring_seams(copy_image, seams_to_visualise, colour)
    
def reshape_seam_carving(image, new_shape, carving_scheme):
    """
    Resizes an image to new shape using seam carving
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :param carving_scheme: the carving scheme to be used.
    :returns: the image resized to new_shape
    """
    ###Your code here###
    ###**************###
    new_height, new_width = new_shape
    while new_height > image.shape[0] or new_width > image.shape[1]:
        new_height = int(input("Warning! The new image size is bigger than the original image\nInsert new image height: "))
        new_width = int(input("Insert new image width: "))
        
    new_image = image.copy()    
    number_of_horizontal_seams = image.shape[0] - new_height
    number_of_vertical_seams = image.shape[1] - new_width
    horizontal_seams_to_remove = []
    vertical_seams_to_remove = []
    
    if carving_scheme == 0:
        _, new_image = get_vertical_seams(new_image, number_of_vertical_seams)
        _, new_image = get_horizontal_seams(new_image, number_of_horizontal_seams)
    elif carving_scheme == 1:
        _, new_image = get_horizontal_seams(new_image, number_of_horizontal_seams)
        _, new_image = get_vertical_seams(new_image, number_of_vertical_seams)
    elif carving_scheme == 2:
        while number_of_horizontal_seams > 0 or number_of_vertical_seams > 0:
            if number_of_vertical_seams > 0:
                _, new_image = get_vertical_seams(new_image, 1)
                number_of_vertical_seams -= 1
            if number_of_horizontal_seams > 0:
                _, new_image = get_horizontal_seams(new_image, 1)
                number_of_horizontal_seams -= 1
    
    return new_image
