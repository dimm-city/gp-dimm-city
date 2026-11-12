from lib import *
_c={n:canon(n) for n in REF}
rng=np.random.default_rng(7)
def src(n): return _c[n].copy()

def _rough_pts(pts, rough):
    pts=[np.array(p,float) for p in pts]; out=[]
    for i in range(len(pts)):
        a,b=pts[i],pts[(i+1)%len(pts)]
        L=np.hypot(*(b-a)); n=max(1,int(L/1.5))
        nrm=np.array([-(b-a)[1],(b-a)[0]])/(L+1e-9)
        noise=np.convolve(rng.normal(0,1,n+4),np.ones(3)/3,'same')[2:n+2]*rough if rough else np.zeros(n)
        for j in range(n):
            t=j/n; out.append(a+(b-a)*t + (nrm*noise[j] if j>0 else 0))
    return out
def P(pts, rough=0.45, soft=0.45):
    """filled polygon in canonical units (x, y-up), with hand-cut edge noise and rounded corners"""
    q=_rough_pts(pts,rough)
    im=Image.new('L',(W,H),0)
    ImageDraw.Draw(im).polygon([((x-X0)*S,(Y1-y)*S) for x,y in q],fill=255)
    a=np.asarray(im,np.float32)/255
    if soft: a=nd.gaussian_filter(a,soft*S)
    return a>0.5
def R_(x0,y0,x1,y1,**k): return P([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],**k)
def clip(m,pts,rough=0.0): return m & P(pts,rough=rough,soft=0)
def box(m,x0,y0,x1,y1): return m & ((XX>=x0)&(XX<x1)&(YY>=y0)&(YY<y1))
def sh(m,dx=0,dy=0): return nd.shift(m.astype(np.uint8),(-dy*S,dx*S),order=0)>0
def flip(m,cx): # mirror about x=cx
    out=np.zeros_like(m); c=int(round((cx-X0)*S)); 
    src_cols=2*c-1-np.arange(W); ok=(src_cols>=0)&(src_cols<W)
    out[:,ok]=m[:,src_cols[ok]]; return out
def vflip(m,cy):
    out=np.zeros_like(m); r=int(round((Y1-cy)*S))
    src_rows=2*r-1-np.arange(H); ok=(src_rows>=0)&(src_rows<H)
    out[ok]=m[src_rows[ok]]; return out
def xr(m): c=np.nonzero(m.any(0))[0]; return X0+c[0]/S, X0+(c[-1]+1)/S
def smooth(m,s=0.3): return nd.gaussian_filter(m.astype(np.float32),s*S)>0.5
def scale(m,sx,sy=1.0,cx=0,cy=0):
    # x' = cx+(x-cx)*sx
    return nd.affine_transform(m.astype(np.float32),[1/sy,1/sx],
        offset=[(Y1-cy)*S*(1-1/sy),(cx-X0)*S*(1-1/sx)],order=1)>0.5
G={}
