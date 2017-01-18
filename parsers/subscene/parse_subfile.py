"""
parse stuff

=== IMPORTANT PRECONDITION
Subs to be organized in a directory structure looking like this:

   subs_root/
      movie-1/
         en/
           english subs for movie 1
         jp/
           jp subs for movie 1
      tv-show-thats-rly-cool
         en/
           subs
         jp/
           subs
      ... 

"""
import sys
import os
import collections
import numpy as np

def distance(source, target):
    """FAST Levenschtein distance between two strings
       Used for fuzzy matching of subs to titles
       
       might not need!
    """
    if len(source) < len(target):
        return distance(target, source)

    if len(target) == 0:
        return len(source)

    # make np character arrays
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # use normal dp algorithm. throw away everything but last two rows of matrix
    previous_row = np.arange(target.size + 1)
    for s in source:
        # insertion (cost of 1)
        current_row = previous_row + 1

        # substitution (cost of 1) or matching (cost of 0)
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # deletion (cost of 1)
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]


root = sys.argv[1]

# {movie title: subs for that title}  mapping
SUBS = {title: {'en': [], 'jp': []} for title in os.listdir(root)}


for title in SUBS:
    print os.listdir(root + '/' + title + '/en/')
    print os.listdir(root + '/' + title + '/jp/')
