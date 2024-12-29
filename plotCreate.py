import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
from PIL import ImageDraw
import time
import random as rand
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from samplebase import SampleBase


# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)


def plots():
    x = range(128)
    y1 = [i + 16 for i in x]
    y2 = [-.5*i**2 + 8*i + 16 for i in x]
    print(x)
    print(y1,y2)
    pitch = 2.5*0.0393701
    h = 32
    w = 128

    plt.figure()
    # fig,ax = plt.subplots(figsize=(w*pitch,h*pitch))
    plt.plot(x,y1,color = 'blue')
    plt.plot(x,y2,color = 'red')

    plt.savefig('test.png')
    # return fig

def drawOnPanel():
    matrix.Clear()
    matrix.SetImage(plots(), 0,0)
    input("FJDOIFOS")

plots()
# drawOnPanel()