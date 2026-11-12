from glyphs import *
E,A,R,T,U,N,Pp,C,K=(src(n) for n in ['E','A','R','T','U','N','P','C','K'])
G['R']=R; G['E']=E; G['A']=A; G['T']=T; G['P']=Pp; G['N']=N
# C: the logo's C is a diagonal and reads as '<' in running text, so the default
# C is E with its middle arm cut out (stem, top arm, bottom arm); the logo C is C.swsh.
G['C']=E & ~P([(13.2,18.2),(70,20.2),(70,33.8),(13.2,33.6)],rough=0.35,soft=0.2)
# U: the logo's U has a short left stem and reads as 'J'; the default U carries the
# left stem up to cap height. The logo U is U.swsh.
G['U']=U | P([(0.2,18),(8.6,18),(9.6,44.2),(5,44.6),(0.9,43.8)],rough=0.4)
G['U.swsh']=U
# swash forms straight from the logo: the tall C and the long-legged K
G['C.swsh']=canon('C',k=1.1,base=77); G['K.swsh']=K
# K: logo K with the arm spike and the leg tail cut back to cap-height proportions
k=clip(K,[(-5,-15),(60,-15),(60,2),(64,4.5),(60,8),(57,44),(53,54),(27,44),(-5,44)],rough=0.3)
G['K']=k
# I: R's stem (keeps the drip)
G['I']=clip(R,[(-5,-15),(11.2,-15),(11.4,50),(-5,50)],rough=0.25)
# L: E minus top and middle arms
G['L']=(E|P([(8.6,43.6),(17,43.8),(16,16),(6,16)])) & ~P([(16.5,18.6),(70,20.5),(70,70),(16.5,70)],rough=0.3,soft=0)
# F: E minus bottom arm
G['F']=(E & ~P([(13.2,20.0),(70,22),(70,-20),(13.2,-20)],rough=0.3,soft=0)) | P([(1,5),(13.2,8),(13,-0.5),(9,-1.2),(3,1)])
# H: A with the counter filled and a top slot cut to mirror its bottom slot
h=A | R_(15,27,38,36,rough=0.2)
G['H']=h & ~P([(18.6,50),(37.2,50),(36.6,27.8),(19.2,27)],rough=0.4,soft=0.3)
# B: E with both slits closed on the right and a waist notch
b=E | P([(33,24.5),(46.5,25.5),(47,37.5),(33,37)]) | P([(38,14),(47.5,15),(48,27.5),(38,27)])
b=b & ~P([(70,37),(47.2,37),(46.5,70),(70,70)],soft=0) & ~P([(52,21.5),(52,29.5),(44.5,25.6)],rough=0.2,soft=0.2)
G['B']=b
# J: U with the left stem cut down to a hook
G['J']=U & ~P([(-5,7),(11,12.5),(11.5,60),(-5,60)],rough=0.3,soft=0)
# Z: C's diagonal + bottom bar, topped with T's ragged crossbar (spike trimmed)
tb=clip(T,[(-5,34.6),(41,34.6),(41,50),(-5,50)],rough=0.2)
G['Z']=C | sh(tb,1,0)
# S: E's upper half + a mirrored E's lower half
e0,e1=xr(E); ef=flip(E,(e0+e1)/2)
G['S']=clip(E,[(-5,21.5),(70,21.5),(70,60),(-5,60)]) | clip(ef,[(-5,-15),(70,-15),(70,26),(-5,26)])

# O: A with the bottom slot filled; counter opened into a tall slit
o=A | P([(14,-2.5),(30,-1.5),(42,2),(44,6),(44,21),(14,21)],rough=0.4)
o=o | R_(16,28,37,36,rough=0.2)
G['O']=o & ~P([(19.5,10),(29.5,10.5),(30.5,32),(20,32.5)],rough=0.35,soft=0.3)
# D: O with a square stem side (fill the left chamfers) and a clipped top-right
d=G['O'] | P([(0.5,8),(9,8),(9,-2),(4,-2),(0.5,0)],rough=0.3)
G['D']=d & ~P([(30,50),(60,50),(60,14)],rough=0.4,soft=0) & ~P([(30,-6),(60,-6),(60,22)],rough=0.4,soft=0)
# Q: O + K's swept leg as the tail
tail=clip(G['K'],[(21,-15),(70,-15),(70,20),(21,17)])
G['Q']=G['O'] | sh(tail,-2,-11)
# G: C with a spur rising off the bottom bar
G['G']=C | P([(41,8),(51.5,8),(52,25),(31,24.5),(31.5,17),(41.5,17)],rough=0.4)
# V: blocky V with N-style spiked tips and a deep top notch
vb=P([(0,46.5),(4,43),(17,42),(23,42),(36,43),(41,47),(31,-1),(12,-1.5)],rough=0.45)
G['V']=vb & ~P([(12.5,49),(28.5,49),(21,12)],rough=0.4,soft=0.3)
# M: two stems with N's spiked tips and a deep V between them, open below the V
# (a shallow notch over a filled middle read as 'H').
m=P([(0,46.5),(4,43),(11.5,42.5),(21,27),(30.5,42.5),(38,43),(42,46.5),(41.5,-1),(31,-1),(31,23.5),(21,9),(11,23.5),(11,-1),(0.5,-1.5)],rough=0.45)
G['M']=m
# W: two Vs overlapped
G['W']=G['V'] | sh(G['V'],23,0)
# Y: top of V on R's stem
yb=P([(0,46.5),(4,43),(17,42),(23,42),(36,43),(41,47),(26.5,20),(26,8),(14,8),(14,20)],rough=0.45)
G['Y']=(yb & ~P([(12.5,49),(28.5,49),(20.5,25)],rough=0.4,soft=0.3)) | sh(clip(G['I'],[(-5,-15),(20,-15),(20,22),(-5,22)]),14.5,0)
# X: K's arm crossing a mirrored arm
G['X']=P([(0,44),(12,44),(48,0),(36,-1)],rough=0.5) | P([(0,-1),(12,0),(52,50),(40,44)],rough=0.5)

def rot180(m,cx,cy): return vflip(flip(m,cx),cy)
def mid(m): a,b=xr(m); return (a+b)/2
# ---- digits
G['zero']=scale(G['O'],0.84,1,0,0)
G['one']=sh(G['I'],7,0) | P([(-1,34),(7.5,44.3),(9,44.3),(9,36),(3,30)],rough=0.35)
G['two']=flip(G['S'],mid(G['S']))
G['three']=flip(E,mid(E))
G['four']=G['H'] & ~P([(-5,19.5),(19.6,19.5),(19.6,-15),(-5,-15)],rough=0.3,soft=0)
spike=clip(T,[(38,30),(60,30),(60,50),(38,50)])
G['five']=G['S'] & ~P([(36,36),(70,36),(70,60),(36,60)],soft=0) | sh(spike,0,0) | P([(30,36.2),(40,36.2),(40,44),(30,44)],rough=0.2)
six=E | P([(38,14),(47.5,15),(48,27.5),(38,27)])
G['six']=six & ~P([(38,33.6),(70,33.6),(70,60),(38,60)],rough=0,soft=0) | P([(30,36),(48,36.5),(52,44.5),(30,44)],rough=0.4)
G['seven']=sh(clip(T,[(-5,34.6),(30,34.6),(30,50),(-5,50)],rough=0.2),8,0) | (clip(C,[(-5,15.5),(28,15.5),(70,60),(-5,60)])) | P([(8,17.5),(20,17.5),(5,-1),(-7.5,-1.5)],rough=0.45)
G['eight']=G['B'] & ~P([(-6,21.5),(-6,29.5),(4,25.5)],rough=0.2,soft=0.2)
G['nine']=rot180(G['six'],mid(G['six']),22)
# ---- punctuation
dot=P([(0.5,0),(9.5,0.5),(10.5,8.5),(1.5,9)],rough=0.35)
G['period']=dot
G['comma']=dot | P([(-3,-9),(2,0.5),(10,1),(0.5,-9.5)],rough=0.35)
G['colon']=dot | sh(dot,0,22)
G['semicolon']=G['comma'] | sh(dot,0,22)
G['exclam']=P([(1,44.5),(12,44),(9,15),(5,14)],rough=0.4) | dot
G['question']=P([(0,44.5),(33,44),(33,24),(17,23.5),(16.5,14),(8,14),(8.5,31),(23,31),(23,37),(0,36.5)],rough=0.45) | sh(dot,7,0)
G['hyphen']=sh(clip(E,[(13.5,24.5),(40,24.5),(40,33.6),(13.5,33.6)]),-13.5,-10)
G['underscore']=sh(clip(C,[(-5,-15),(70,-15),(70,12.6),(-5,12.6)]),0,-10)
G['quotesingle']=P([(1,45),(10,45),(7,32),(4,32)],rough=0.3)
G['quotedbl']=G['quotesingle'] | sh(G['quotesingle'],12,0)
G['slash']=P([(0,-2),(10,-2.5),(40,46),(30,46)],rough=0.45)
G['backslash']=flip(G['slash'],20)
G['parenleft']=P([(12,47),(19,47),(9,30),(9,10),(19,-7),(12,-7),(1,10),(1,30)],rough=0.4)
G['parenright']=flip(G['parenleft'],10)
G['bracketleft']=P([(0,-7),(17,-7),(17,0.5),(9,0.5),(9,39),(17,39),(17,46.5),(0,46.5)],rough=0.4)
G['bracketright']=flip(G['bracketleft'],8.5)
G['less']=P([(30,40),(30,32),(12,22),(30,12),(30,4),(0,19),(0,25)],rough=0.4)
G['greater']=flip(G['less'],15)
G['plus']=P([(11,4),(20,4),(20,36),(11,36)],rough=0.4) | P([(0,16),(31,16),(31,24.5),(0,24.5)],rough=0.4)
G['equal']=sh(G['hyphen'],0,-6) | sh(G['hyphen'],0,8)
G['asterisk']=(P([(9,26),(16,26),(16,46),(9,46)],rough=0.3) | P([(0,30),(4,26),(25,42),(21,46)],rough=0.3) | P([(0,42),(4,46),(25,30),(21,26)],rough=0.3))
G['numbersign']=(P([(6,-2),(13,-2),(17,46),(10,46)],rough=0.4) | P([(22,-2),(29,-2),(33,46),(26,46)],rough=0.4)
                 | P([(0,10),(38,10),(38,17),(0,17)],rough=0.4) | P([(1,27),(39,27),(39,34),(1,34)],rough=0.4))
sq=P([(0,0),(9,0),(9.5,10),(0.5,10)],rough=0.35)
G['percent']=G['slash'] | sh(sq,-1,33) | sh(sq,31,0)
G['bar']=clip(R,[(-5,-15),(11.2,-15),(11.4,50),(-5,50)],rough=0.25) & ~P([(-5,-15),(20,-15),(20,-2),(-5,-2)],soft=0)
G['dollar']=G['S'] | P([(22,-7),(29,-7),(29,51),(22,51)],rough=0.35)
amp=scale(G['B'],0.8,0.8,0,0)
G['ampersand']=amp | sh(tail,8,-4)
G['ellipsis']=dot | sh(dot,15,0) | sh(dot,30,0)
G['space']=np.zeros_like(E)
