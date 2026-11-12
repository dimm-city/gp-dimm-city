# Build 8x high-res masks of each yellow letter from the source image.
from PIL import Image; import numpy as np
from scipy import ndimage as nd
S=8
a=np.array(Image.open('creaturepunk-logo.png').convert('RGB')).astype(float)
field=np.clip((a[...,0]-a[...,2])/255.0,0,1)
yel=field>0.5
lab,n=nd.label(yel)
objs=nd.find_objects(lab)
order=sorted(range(n),key=lambda i:objs[i][1].start)
names=['C','R','E','A','T','U','R2','E2','P','U2','N','K']
# assign every pixel to nearest component
dist,(iy,ix)=nd.distance_transform_edt(lab==0,return_indices=True)
owner=lab[iy,ix]
out={}
for nm,i in zip(names,order):
    m=(owner==i+1)&(dist<3)
    f=np.where(m,field,0.0)
    s=objs[i]; y0,y1=s[0].start-3,s[0].stop+3; x0,x1=s[1].start-3,s[1].stop+3
    crop=f[y0:y1,x0:x1]
    im=Image.fromarray(crop.astype(np.float32),'F').resize(((x1-x0)*S,(y1-y0)*S),Image.BICUBIC)
    big=np.array(im)>0.5
    # keep largest component + its holes only
    l2,n2=nd.label(big); sizes=nd.sum(big,l2,range(1,n2+1))
    big=l2==(np.argmax(sizes)+1)
    np.save(f'm_{nm}.npy',big); out[nm]=(x0,y0)
    Image.fromarray((~big*255).astype(np.uint8)).save(f'm_{nm}.png')
import json; json.dump(out,open('offsets.json','w'))
print(out)
