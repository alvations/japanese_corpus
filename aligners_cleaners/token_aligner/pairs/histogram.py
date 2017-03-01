"""
quick script for histograming a list of numbers


python histogram.py daddicts_matched/distribution.txt daddicts

"""


import numpy as np
import random
from matplotlib import pyplot as plt
import sys





data = np.array([float(x) for x in open(sys.argv[1]).read().split(',')])

nonzero = np.count_nonzero(data)
n =  len(data)
perc_nonzero = nonzero * 1.0 / n

bins = np.linspace(0, 1, 20, dtype=np.float32) # fixed bin size

plt.xlim([min(data), max(data)+0.2])
plt.hist(data, bins=bins, alpha=0.5)
plt.title(sys.argv[2] + ' -  {:.2f}% nonzero - {} healthy pairs'.format(perc_nonzero, nonzero))
plt.xlabel('score')
plt.ylabel('count')

plt.show()
