#!/usr/bin/env python
# Display a runtext with double-buffering.
try:
    from samplebase import SampleBase
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    from rgbmatrix import graphics
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
    runningOnPi = True
except ModuleNotFoundError:
    runningOnPi = False
    class matrix:
        def __init__(self):
            self.width = 128
            self.height = 32
    matrix = matrix()

from PIL import Image, ImageDraw
import datetime
import time
import os
import sys
import numpy as np


class ForestFire():
    def __init__(self, timestep, probs, sigmaProb, density=0.5, num_burn_points=3, seed = 1000, *args, **kwargs):
        """
        Initialize the ForestFire class with customizable inputs.
        
        :param timestep: Time delay between frames.
        :param meanProb: Probability for a tree to catch fire.
        :param sigmaProb: Spread probability for fire.
        :param density: Density of trees in the forest, 1 for full.
        :param num_burn_points: Number of initial random fire points.
        """
        self.timestep = timestep
        self.probArray = probs
        self.sigmaProb = sigmaProb
        self.density = density
        self.num_burn_points = num_burn_points
        # Create a PRNG object with a specific seed
        self.prng = np.random.default_rng(seed)       
        self.run()


    def run(self):
        width, height = matrix.width, matrix.height

        size = width * height

        # Initialize forest array and reshape
        self.forest = np.zeros((height, width), dtype=int)  # Create a 2D array
        num_ones = int(size * self.density)
        indices = self.prng.choice(size, num_ones, replace=False)

        self.forest.flat[indices] = 1

        # Initialize random old growth trees
        StartOldGrowth=30
        oldgrowth_indices = self.prng.choice(size, StartOldGrowth, replace=False)
        for index in oldgrowth_indices:
            row, col = divmod(index, width)
            self.forest[row, col] = 3

        def clear_terminal():
            print("\033[H\033[J", end="")  # ANSI sequence to clear screen and reset cursor

        while True:
            self.burn( TreeType=1,
                FireSpreadRate          =self.probArray['BasicTree']['FireSpreadRate'], 
                FireDeathRate           =self.probArray['BasicTree']['FireDeathRate'], 
                FireExtinguishRate      =self.probArray['BasicTree']['FireExtinguishRate'] )  # Spread the fire
            self.grow(  TreeType=1,
                GrowthSpreadRate        =self.probArray['BasicTree']['GrowthSpreadRate'], 
                NaturalDeathRate        =self.probArray['BasicTree']['NaturalDeathRate'], 
                LightningRate           =self.probArray['BasicTree']['LightningRate'] )  # Grow back trees
            self.burn( TreeType=3,
                FireSpreadRate          =self.probArray['OldGrowth']['FireSpreadRate'], 
                FireDeathRate           =self.probArray['OldGrowth']['FireDeathRate'], 
                FireExtinguishRate      =self.probArray['OldGrowth']['FireExtinguishRate'] )  # Spread the fire
            self.grow(  TreeType=3,
                GrowthSpreadRate        =self.probArray['OldGrowth']['GrowthSpreadRate'], 
                NaturalDeathRate        =self.probArray['OldGrowth']['NaturalDeathRate'], 
                LightningRate           =self.probArray['OldGrowth']['LightningRate'] )  # Grow back trees

            clear_terminal()  # Clear the screen
            # get counts for the various tree states
            unique, counts = np.unique(self.forest, return_counts=True)
            treeCount = dict(zip(unique, counts))
            try:
                fire = treeCount[2]
            except KeyError:
                fire = 0
            print(treeCount)
            print("|-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- Trees -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --|")
            print("|\tUnder Growth\t|\tOld Growth\t|\tOn Fire  \t|\tDead    \t|\tTotal     \t|")
            print(f"|\t   {treeCount[1]}  \t|\t    {treeCount[3]}   \t|\t   {fire}    \t|\t {treeCount[0]}     \t|\t  {self.forest.size}  \t|")  # Print the new value
            print("|-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --|")
            # Send to Panel
            if runningOnPi:
                matrix.SetImage(self.forestToImage().convert('RGB'))
            # wait
            # input("continue")
            time.sleep(self.timestep)

    def burn(self, TreeType, FireSpreadRate=0.9, FireDeathRate=0.1, FireExtinguishRate=0.1):
        """Simulate fire spreading based on adjacency to burning trees"""
        height, width = self.forest.shape
        new_forest = self.forest.copy()

        # Define directions for adjacent cells (N, S, E, W)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for i in range(height):
            for j in range(width):
                if self.forest[i, j] == TreeType:  # Tree is alive
                    # Check if any of the adjacent cells is burning
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < height and 0 <= nj < width and self.forest[ni, nj] == 2:
                            if self.prng.uniform(0,1) < FireSpreadRate:  # Spread fire with a probability
                                new_forest[i, j] = 2  # Set fire
                                break  # No need to check further neighbors

                elif self.forest[i, j] == 2:  # Burning tree
                    if self.prng.uniform(0,1) < FireDeathRate:
                        new_forest[i, j] = 0  # Tree is burned down
                    elif self.prng.uniform(0,1) < FireExtinguishRate:
                        new_forest[i, j] = TreeType  # Tree fire goes out

        self.forest = new_forest

    def grow(self, TreeType, GrowthSpreadRate=0.005, NaturalDeathRate=0.005, LightningRate=0.00005):
        """Simulate trees growing based on adjacency to alive trees"""
        height, width = self.forest.shape
        new_forest = self.forest.copy()

        # Define directions for adjacent cells (N, S, E, W)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for i in range(height):
            for j in range(width):
                if self.forest[i, j] == 0:  # Tree is dead
                    # Check if any of the adjacent cells is alive
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < height and 0 <= nj < width and self.forest[ni, nj] == TreeType:
                            if self.prng.uniform(0,1) < GrowthSpreadRate:  # Spread growth with probability
                                new_forest[i, j] = TreeType  # tree grows
                                break  # No need to check further neighbors
                
                # sometimes trees die
                elif self.forest[i, j] == TreeType:
                    if self.prng.uniform(0,1) < NaturalDeathRate:
                        new_forest[i, j] = 0  # Tree dies
                    if self.prng.uniform(0,1) < LightningRate:
                        new_forest[i, j] = 2  # Tree gets hit by Lightning, set on fire

        self.forest = new_forest

    def forestToImage(self):
        '''turn the forest array into an image'''
        height, width = self.forest.shape
        image_data = np.zeros((height, width, 3), dtype=np.uint8)

        # Define Colors:

        # # Good Colors:
        # alive = (70, 125, 4)
        # oldGrowth = (2, 234, 86)
        # burning = (252, 94, 3)

        # Random:
        alive = (70, 25, 140)
        oldGrowth = (200, 234, 0)
        burning = (210, 94, 190)
        dead = (0, 0, 0)

        for i in range(height):
            for j in range(width):
                if self.forest[i, j] == 1:
                    image_data[i, j] = alive 
                elif self.forest[i, j] == 2:
                    image_data[i, j] = burning 
                elif self.forest[i, j] == 3:
                    image_data[i, j] = oldGrowth 
                else:
                    image_data[i, j] = dead

        # Create and save the image
        image = Image.fromarray(image_data, 'RGB')
        assert image_data.shape == (self.forest.shape[0], self.forest.shape[1], 3), "Image dimensions mismatch!"
        return image

# Main function
if __name__ == "__main__":
    # Instantiate the class with your desired parameters
    probabilities = {
        'BasicTree' : {
            'GrowthSpreadRate'  : 0.02,
            'NaturalDeathRate'  : 0.01,
            'LightningRate'     : 0.00001,
            'FireSpreadRate'    : 0.9,
            'FireDeathRate'     : 0.1,
            'FireExtinguishRate': 0.1
        },
        'OldGrowth' : {
            'GrowthSpreadRate'  : 0.001,
            'NaturalDeathRate'  : 0.0005,
            'LightningRate'     : 0.0000005,
            'FireSpreadRate'    : 0.3,          # Resistance to burning
            'FireDeathRate'     : 0.001,
            'FireExtinguishRate': 0.01
        }
    }
    run_text = ForestFire(
        timestep=0.03,
        probs=probabilities,
        sigmaProb=0.03
    )
