import numpy as np, json
from PIL import Image, ImageDraw
from scipy import ndimage as nd
SL=0.5; S=8
off=json.load(open('offsets.json'))
BASE=78.0  # nominal global baseline in src px (refined per glyph later)
def deslant(n):
    m=np.load(f'm_{n}.npy'); x0,y0=off[n]
    H,W=m.shape
    # source pixel (X,Y) global = x0+x/S, y0+y/S ; deslanted X' = X + SL*(Y-BASE)
    P=400
    out=np.zeros((H,W+2*P),bool)
    for y in range(H):
        Y=y0+y/S
        sh=int(round(SL*(Y-BASE)*S))+P
        out[y,sh:sh+W]=m[y]
    return out,(x0*S-P,y0*S)
