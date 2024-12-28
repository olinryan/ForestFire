import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from forestFire import *

plt.rcParams.update({"axes.facecolor":"silver",'axes.labelcolor':'silver','legend.frameon':'False','axes.grid':'True','axes.edgecolor':'silver','text.color':'silver','xtick.color':'silver','ytick.color':'silver'})

def run(ForestFire, tsteps):
    '''
    given a forest fire object, initialized with parameters
    run for tsteps and plot the quanitites
    '''
    forestDF = pd.DataFrame()
    for _ in range(tsteps):
        ForestFire.cycle()
        # get counts for the various tree states
        unique, counts = np.unique(ForestFire.forest, return_counts=True)
        treeCount = dict(zip(unique, counts))
        try:
            fire = treeCount[2]
        except KeyError:
            fire = 0
        forestDF = forestDF._append({"New Growth":treeCount[1], "Old Growth":treeCount[3], "On Fire":fire, "Dead":treeCount[0] }, ignore_index=True)

    fig,ax = plt.subplots()
    for f in forestDF:
        ax.plot(forestDF[f],label=f)
    ax.legend(loc='best')
    ax.set_ylim([0,4096])
    ax.set_xlabel("Step")
    ax.set_ylabel("Quantity")
    fig.savefig("Results.png", transparent=True)


if __name__ == "__main__":

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
            'GrowthSpreadRate'  : 0.01,
            'NaturalDeathRate'  : 0.0005,
            'LightningRate'     : 0.0000005,
            'FireSpreadRate'    : 0.3,          # Resistance to burning
            'FireDeathRate'     : 0.001,
            'FireExtinguishRate': 0.01
        }
    }
    run_fire = ForestFire(
        timestep=0.03,
        probs=probabilities
        # density=0.00025
    )
    run(run_fire,5000)