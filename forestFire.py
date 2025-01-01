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
    def __init__(self, timestep, probs, density=0.000245, mutation_rate=0.01, seed = 1000, *args, **kwargs):
        """
        Initialize the ForestFire class with customizable inputs.
        
        :param timestep: Time delay between frames.
        :param meanProb: Probability for a tree to catch fire.
        :param mutation_rate: Mutation rate (standard deviation) that new trees will differ from parent
        :param density: Density of trees in the forest, 1 for full.
        """
        self.timestep = timestep
        self.probArray = probs
        self.density = density
        self.generation = 0  # Start from generation 0
        self.mutation_rate = mutation_rate  
        # Create a PRNG object with a specific seed
        self.prng = np.random.default_rng(seed)       

        width, height = matrix.width, matrix.height

        size = width * height

        # Initialize forest array and reshape

                                    # tree type (0 dead, 1/3 tree), burn state (0,1), and 6 characteristics:
        characteristics = 8         # GrowthSpreadRate, NaturalDeathRate, LightningRate, 
                                    # FireSpreadRate, FireDeathRate, FireExtinguishRate

        self.forest = np.zeros((height, width, characteristics), dtype=float)  # Create a 3D array
        StartNewGrowth=204
        StartOldGrowth=204

        # Initialize random old growth trees
        newgrowth_indices = self.prng.choice(size, StartNewGrowth, replace=False)
        for index in newgrowth_indices:
            row, col = divmod(index, width)
            self.forest[row, col][0] = 1
            for index, cc in enumerate(self.probArray['BasicTree']):
                self.forest[row, col][index + 2] = self.probArray['BasicTree'][cc]

        # Initialize random old growth trees
        oldgrowth_indices = self.prng.choice(size, StartOldGrowth, replace=False)
        for index in oldgrowth_indices:
            row, col = divmod(index, width)
            self.forest[row, col][0] = 2
            for index, cc in enumerate(self.probArray['OldGrowth']):
                self.forest[row, col][index + 2] = self.probArray['OldGrowth'][cc]

    def run(self):
        def clear_terminal():
            print("\033[H\033[J", end="")  # ANSI sequence to clear screen and reset cursor

        while True:
            self.cycle()       # perscribed grow-burn cycle 
            # # self.evolve()  # Apply evolution after each cycle
            # self.generation += 1  # Increment generation counter

            clear_terminal()  # Clear the screen
            # get counts for the various tree states
            unique, counts = np.unique(self.forest[:,:,0], return_counts=True)
            treeCount = dict(zip(unique, counts))
            
            try:
                treeCount[1]
            except KeyError:
                raise SystemError("No New Growth Remain")
            
            try:
                treeCount[2]
            except KeyError:
                raise SystemError("No Old Growth Remain")
            
            try:
                unique, counts = np.unique(self.forest[:,:,1], return_counts=True)
                fire = dict(zip(unique, counts))
                fire = fire[1]
            except KeyError:
                fire = 0

            size = self.forest.shape[0]*self.forest.shape[1]
            
            print("|-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- TREES -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --|")
            print("|\tUnder Growth\t|\tOld Growth\t|\t On Fire \t|\t  Dead  \t|\t Total \t     |")
            print(f"|\t{str(treeCount[1]).center(12)}\t|\t{str(treeCount[2]).center(10)}\t|\t{str(fire).center(9)}\t|\t{str(size - treeCount[1] - treeCount[2]).center(8)}\t|\t{str(size).center(7)}\t     |")  # Print the new value
            # Print the header for parameters
            print("|-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --|")

            # Generate and print stats for the forest
            self.forest_stats()

            # Send to Panel
            if runningOnPi:
                matrix.SetImage(self.forestToImage().convert('RGB'))
            # wait
            # input("continue")
            time.sleep(self.timestep)

    def cycle(self):
        """
        Part 1:
            Simulate the growth and decay of trees based on adjacency to alive trees, 
            when trees sperad they have a chance to mutate, see mutation function
        Part 2:
            Simulate fire spreading based on adjacency to burning trees, 
            burning trees have a chance to either burn down or self-extingusih 
        """
        height, width, chars = self.forest.shape
        new_forest = self.forest.copy()

        # Define directions for adjacent cells (N, S, E, W)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        ### -- Growth Phase -- ###
        for i in range(height):
            for j in range(width):
                if self.forest[i, j][0] == 0:  # Tree is dead (no tree)
                    # Check if any of the adjacent cells is alive
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < height and 0 <= nj < width and self.forest[ni, nj][0] != 0:    # Adjacent is alive
                            if self.prng.uniform(0,1) < self.forest[ni, nj][2]:  # Spread growth with probability
                                new_forest[i, j] = self.mutate(self.forest[ni,nj])  # tree grows
                                break  # No need to check further neighbors, tree cant grow twice
                
                # sometimes trees die
                elif self.forest[i, j][1] != 1: # tree is alive but not burning
                    if self.prng.uniform(0,1) < self.forest[i, j][3]:
                        new_forest[i, j] = [0,0,0,0,0,0,0,0]  # Tree dies
                    if self.prng.uniform(0,1) < self.forest[i, j][4]:
                        new_forest[i, j][1] = 1  # Tree gets hit by Lightning, set on fire

        ### -- Burn Phase -- ###
        for i in range(height):
            for j in range(width):
                if self.forest[i, j][0] != 0:  # Tree is alive
                    # Check if any of the adjacent cells is burning
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < height and 0 <= nj < width and self.forest[ni, nj][1] == 1:   # Adjacent is on fire
                            if self.prng.uniform(0,1) < self.forest[ni,nj][5]:  # Spread fire with a probability, dependant on adjacent cells' prob of burning
                                new_forest[i, j][1] = 1  # Set fire
                                break  # No need to check further neighbors, tree cant get set on fire twice

                elif self.forest[i, j][1] == 1:  # Burning tree
                    if self.prng.uniform(0,1) < self.forest[i, j][6]:
                        new_forest[i, j] = [0,0,0,0,0,0,0,0]  # Tree is burned down
                    elif self.prng.uniform(0,1) < self.forest[i, j][7]:
                        new_forest[i, j][1] = 0  # Tree fire goes out, reset to alive 

        self.forest = new_forest

    
    def mutate(self,treeProps):
        """
        Apply mutations changes to tree properties based on survival metrics.
        expects an individual 'parent' tree [type,characteristics...], that will then 
        return the properties for the children, based on a normal distribution around 1
        with a sigma specified. Only effects growth spread rate and natural death rate for now...
        """
        childTree = [treeProps[0]]

        probs_to_change = [1,2]     # 1 indexed probabilites to change
        for index in range(1,len(treeProps)):
            if index in childTree:
                change = self.prng.normal(1,self.mutation_rate)
                childTree.append(treeProps[index]*change)
            else:
                childTree.append(treeProps[index])
            
        return childTree

    def forestToImage(self):
        '''turn the forest array into an image'''
        height, width, chars = self.forest.shape
        image_data = np.zeros((height, width, 3), dtype=np.uint8)

        # Define Colors:

        # Green - Red:
        # alive = (70, 125, 4)
        # oldGrowth = (2, 234, 86)
        # burning = (252, 94, 3)

        # Purple - pink:
        # alive = (70, 25, 140)
        # oldGrowth = (200, 234, 0)
        # burning = (210, 94, 190)

        # Yellow - Blue:
        alive = (170, 125, 10)
        oldGrowth = (210, 34, 30)
        burning = (0, 94, 245)

        # Secondary:
        # alive = (255, 0, 255)
        # oldGrowth = (0, 255, 255)
        # burning = (255, 255, 0)    

        dead = (0, 0, 0)

        for i in range(height):
            for j in range(width):
                if self.forest[i, j][0] == 1:
                    image_data[i, j] = alive 
                elif self.forest[i, j][0] == 2:
                    image_data[i, j] = burning 
                elif self.forest[i, j][0] == 3:
                    image_data[i, j] = oldGrowth 
                else:
                    image_data[i, j] = dead

        # Create and save the image
        image = Image.fromarray(image_data, 'RGB')
        assert image_data.shape == (self.forest.shape[0], self.forest.shape[1], 3), "Image dimensions mismatch!"
        return image

    def forest_stats(self):
        '''
        pull the stats of the forest
        '''
        height, width, chars = self.forest.shape
        stats = {
            'BasicTree' : {
                'Count'             : 0,
                'CountFire'         : 0,
                'GrowthSpreadRate'  : [],
                'NaturalDeathRate'  : [],
                'LightningRate'     : [],
                'FireSpreadRate'    : [],
                'FireDeathRate'     : [],
                'FireExtinguishRate': []
            },
            'OldGrowth' : {
                'Count'             : 0,
                'CountFire'         : 0,
                'GrowthSpreadRate'  : [],
                'NaturalDeathRate'  : [],
                'LightningRate'     : [],
                'FireSpreadRate'    : [],
                'FireDeathRate'     : [],
                'FireExtinguishRate': []
            }
        }
        for i in range(height):
            for j in range(width):
                if self.forest[i,j,0] == 0:
                    continue
                elif self.forest[i,j,0] == 1:
                    stats['BasicTree']['Count'] += 1
                    if self.forest[i,j,1] == 1:
                        stats['BasicTree']['CountFire'] += 1
                    for x,val in enumerate(stats['BasicTree']):
                        if val == 'Count' or val == 'CountFire': continue 
                        stats['BasicTree'][val].append(self.forest[i,j,x])
                elif self.forest[i,j,0] == 2:
                    stats['OldGrowth']['Count'] += 1
                    if self.forest[i,j,1] == 1:
                        stats['OldGrowth']['CountFire'] += 1
                    for x,val in enumerate(stats['OldGrowth']):
                        if val == 'Count' or val == 'CountFire': continue 
                        stats['OldGrowth'][val].append(self.forest[i,j,x])

        print("\n|-- -- -- -- TREE PARAMETERS -- -- -- -- -- -- --|")
        for tree_type, params in stats.items():
            print(f"| {tree_type.center(29)}   mean    max    |")
            for param, value in params.items():
                if param == 'Count' or param == 'CountFire': 
                    print(f"| {param}: \t\t\t{str(value).center(7)}\t  --  \t |")
                else:
                    print(f"| {param}: \t\t{np.mean(value):.5f}\t{np.max(value):.5f}\t |")
            print("|-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- |")  # New line after each tree type
     

# Main function
if __name__ == "__main__":
    # Instantiate the class with your desired parameters
    probabilities = {
        'BasicTree' : {
            'GrowthSpreadRate'  : 0.02,
            'NaturalDeathRate'  : 0.01,
            'LightningRate'     : 0.00001,      # 0.0000001
            'FireSpreadRate'    : 0.9,
            'FireDeathRate'     : 0.4,
            'FireExtinguishRate': 0.1
        },
        'OldGrowth' : {
            'GrowthSpreadRate'  : 0.001,
            'NaturalDeathRate'  : 0.0005,
            'LightningRate'     : 0.0000005,    # 0.000005
            'FireSpreadRate'    : 0.3,   # 0.03 # Resistance to burning
            'FireDeathRate'     : 0.01,
            'FireExtinguishRate': 0.01
        }
    }
    # probabilities = {
    #     'BasicTree' : {
    #         'GrowthSpreadRate'  : 0.02,
    #         'NaturalDeathRate'  : 0.01,
    #         'LightningRate'     : 0.0000001,      # 0.0000001
    #         'FireSpreadRate'    : 0.9,
    #         'FireDeathRate'     : 0.3,
    #         'FireExtinguishRate': 0.1
    #     },
    #     'OldGrowth' : {
    #         'GrowthSpreadRate'  : 0.02,
    #         'NaturalDeathRate'  : 0.01,
    #         'LightningRate'     : 0.0000001,      # 0.0000001
    #         'FireSpreadRate'    : 0.9,
    #         'FireDeathRate'     : 0.3,
    #         'FireExtinguishRate': 0.1
    #     }
    # }

    run_fire = ForestFire(
        timestep=0.001,
        density=0.05,#0.00025*2,
        probs=probabilities
    )
    run_fire.run()

# nohup sudo python forestFire.py &