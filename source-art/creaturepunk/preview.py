import sys; from defs import *
names=sys.argv[2].split(',')
show([G[n] for n in names],sys.argv[1],names,scale=4)
