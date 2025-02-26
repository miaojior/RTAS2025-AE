# Call functions from other files to conduct experiments and generate figures.
from exp import *
from draw import *

batchsize=100
exp(batchsize)
draw()
print("finished!")
input("Press Enter to exit...")
