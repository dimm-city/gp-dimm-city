import numpy as np, json
from scipy import ndimage as nd
from PIL import Image, ImageDraw
S=8; X0=-20; X1=140; Y0=-25; Y1=75   # canonical frame in src px, y up, baseline 0, cap 44
W=(X1-X0)*S; H=(Y1-Y0)*S
CAP=44.0
rows=np.arange(H); cols=np.arange(W)
YY=(Y1 - (rows[:,None]+0.5)/S)*np.ones((1,W))
XX=(X0 + (cols[None,:]+0.5)/S)*np.ones((H,1))

def show(masks, fn, labels=None, scale=4, xr=None, yr=(-12,66)):
    tiles=[]
    for k,m in enumerate(masks):
        cs=np.nonzero(m.any(0))[0]
        xa=int(np.floor(X0+cs[0]/S))-3 if xr is None else xr[0]
        xb=int(np.ceil(X0+cs[-1]/S))+3 if xr is None else xr[1]
        sub=m[(Y1-yr[1])*S:(Y1-yr[0])*S, (xa-X0)*S:(xb-X0)*S]
        f=S//scale
        img=Image.fromarray(np.where(sub,0,255).astype(np.uint8)).resize((sub.shape[1]//f,sub.shape[0]//f),Image.BILINEAR)
        t=Image.new('RGB',(img.width+26,img.height),'white'); t.paste(Image.merge('RGB',[img]*3),(26,0))
        dr=ImageDraw.Draw(t)
        for y in range(yr[0],yr[1]+1):
            Y=(yr[1]-y)*scale
            if y%10==0 or y==CAP: dr.line([(0,Y),(t.width,Y)],fill=(255,60,60) if y in (0,CAP) else (255,150,150)); dr.text((0,Y-6),str(y),fill='red')
            elif y%2==0: dr.line([(26,Y),(t.width,Y)],fill=(205,205,255))
        for x in range(xa,xb+1):
            X=26+(x-xa)*scale
            if x%10==0: dr.line([(X,0),(X,t.height)],fill=(255,150,150)); dr.text((X+1,t.height-11),str(x),fill='red')
            elif x%2==0: dr.line([(X,0),(X,t.height)],fill=(228,228,228))
        if labels: dr.text((30,2),labels[k],fill='blue')
        tiles.append(t)
    Wt=sum(t.width+6 for t in tiles); sh=Image.new('RGB',(Wt,tiles[0].height),'white'); x=0
    for t in tiles: sh.paste(t,(x,0)); x+=t.width+6
    sh.save(fn)
