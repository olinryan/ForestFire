
from PIL import Image
from PIL import ImageDraw
import time
import random as rand
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from samplebase import SampleBase

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.led_rgb_sequence = 'RBG'    
options.pixel_mapper_config = 'Rotate:180'

matrix = RGBMatrix(options = options)


class runBounce(SampleBase):
    def __init__(self,SquareDim = 10,tick=0.05):
        self.dim = SquareDim
        self.tick = tick
        self.rainbow = self.generate_rainbow()
        self.color = self.rainbow[0]
        self.loopBounce()

    def createSquare(self):
        # RGB example w/graphics prims.
        # Note, only "RGB" mode is supported currently.
        self.img = Image.new("RGB", (self.dim+1, self.dim+1))
        draw = ImageDraw.Draw(self.img)
        # Draw some shapes into image
        draw.rectangle((0, 0, self.dim, self.dim), fill=(0, 0, 0), outline=self.color)
        draw.line((0, 0, self.dim, self.dim), fill='pink')
        draw.line((0, self.dim, self.dim, 0), fill='yellow')

    def drawOnPanel(self,loc):
        matrix.Clear()
        matrix.SetImage(self.img, loc['x'],loc['y'])
        time.sleep(0.1)

    def loopBounce(self):

        heightLim = matrix.height-self.dim-1
        widLim = matrix.width-self.dim-1
        x_inc = 1
        y_inc = 1

        loc = {'x':rand.randint(1,widLim),'y':rand.randint(1,heightLim)}
        sz = 0

        print("Runnning Bounce Loop. Press ctrl+C to continue...")

        while True:
            self.createSquare()
            self.drawOnPanel(loc)
            if loc['x'] >= widLim or loc['x'] < 1:
                x_inc = x_inc*-1
            if loc['y'] >= heightLim or loc['y'] < 1:
                y_inc = y_inc*-1
            if sz == 305:
                sz = 0
            else:
                sz += 1

            loc['x'] += x_inc
            loc['y'] += y_inc

            self.color = self.rainbow[sz]

    def generate_rainbow(self):
        stp=5
        colors = []
        r, g, b = 255, 0, 0  # Start with Red
        
        # Red to Yellow
        while g < 255:
            g += stp
            g = min(255, g)  # Ensure value does not exceed 255
            colors.append((r, g, b))
        
        # Yellow to Green
        while r > 0:
            r -= stp
            r = max(0, r)  # Ensure value does not go below 0
            colors.append((r, g, b))
        
        # Green to Cyan
        while b < 255:
            b += stp
            b = min(255, b)
            colors.append((r, g, b))
        
        # Cyan to Blue
        while g > 0:
            g -= stp
            g = max(0, g)
            colors.append((r, g, b))
        
        # Blue to Magenta
        while r < 255:
            r += stp
            r = min(255, r)
            colors.append((r, g, b))
        
        # Magenta to Red
        while b > 0:
            b -= stp
            b = max(0, b)
            colors.append((r, g, b))
        
        return colors
if __name__ == "__main__":
    runBounce()
