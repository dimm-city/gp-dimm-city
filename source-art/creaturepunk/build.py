import sys, math, time, json
import potrace
from defs import *
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

UPM=1000; U=700/CAP; SLANT=0.5; SB=2.5
RSB={'T':-6.0}          # T's crossbar spike hangs over the next letter, as in the logo
CMAP={}
for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    CMAP[ord(ch)]=ch; CMAP[ord(ch.lower())]=ch
digits='zero one two three four five six seven eight nine'.split()
for i,n in enumerate(digits): CMAP[0x30+i]=n
punct={'space':[0x20,0xA0],'period':[0x2E],'comma':[0x2C],'colon':[0x3A],'semicolon':[0x3B],'exclam':[0x21],
 'question':[0x3F],'hyphen':[0x2D,0x2010,0x2011,0x2012,0x2013,0x2014],'underscore':[0x5F],'quotesingle':[0x27,0x2018,0x2019],
 'quotedbl':[0x22,0x201C,0x201D],'slash':[0x2F],'backslash':[0x5C],'parenleft':[0x28],'parenright':[0x29],
 'bracketleft':[0x5B],'bracketright':[0x5D],'less':[0x3C],'greater':[0x3E],'plus':[0x2B],'equal':[0x3D],
 'asterisk':[0x2A],'numbersign':[0x23],'percent':[0x25],'bar':[0x7C],'dollar':[0x24],'ampersand':[0x26],'ellipsis':[0x2026]}
for n,cps in punct.items():
    for cp in cps: CMAP[cp]=n

def trace(m):
    m=smooth(m,0.25)
    rr=np.nonzero(m.any(1))[0]; cc=np.nonzero(m.any(0))[0]
    r0,r1,c0,c1=rr[0]-4,rr[-1]+5,cc[0]-4,cc[-1]+5
    sub=m[r0:r1,c0:c1]
    path=potrace.Bitmap(~sub).trace(turdsize=12,alphamax=1.0,opticurve=True,opttolerance=0.2)
    def tf(p): return ((X0+(p.x+c0)/S)*U, (Y1-(p.y+r0)/S)*U)
    contours=[]
    for curve in path:
        segs=[('move',tf(curve.start_point))]
        for s in curve.segments:
            if s.is_corner: segs+= [('line',tf(s.c)),('line',tf(s.end_point))]
            else: segs.append(('curve',tf(s.c1),tf(s.c2),tf(s.end_point)))
        contours.append(segs)
    xmin=(X0+cc[0]/S)*U; xmax=(X0+(cc[-1]+1)/S)*U
    return contours,xmin,xmax

def draw(contours,pen,dx):
    def t(p): x,y=p[0]+dx,p[1]; return (round(x+SLANT*y,2), round(y,2))
    for segs in contours:
        pen.moveTo(t(segs[0][1]))
        for s in segs[1:]:
            if s[0]=='line': pen.lineTo(t(s[1]))
            else: pen.curveTo(t(s[1]),t(s[2]),t(s[3]))
        pen.closePath()

order=['.notdef']+[c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']+digits+list(punct)+['C.swsh','U.swsh','K.swsh']
glyphs={}; metrics={}
t0=time.time()
for n in order:
    if n in ('.notdef','space'):
        pen=TTGlyphPen(None)
        if n=='.notdef':
            for (a,b,c,d) in [((50,0),(450,0),(450,700),(50,700))]:
                pen.moveTo(a);pen.lineTo(d);pen.lineTo(c);pen.lineTo(b);pen.closePath()
                pen.moveTo((100,50));pen.lineTo((400,50));pen.lineTo((400,650));pen.lineTo((100,650));pen.closePath()
        glyphs[n]=pen.glyph(); metrics[n]=(500 if n=='.notdef' else 280,0); continue
    contours,xmin,xmax=trace(G[n])
    dx=SB*U - xmin
    rec=RecordingPen(); draw(contours,rec,dx)
    # potrace contours come out counter-clockwise for outlines in y-up space; TrueType wants clockwise
    pen=TTGlyphPen(None)
    rec.replay(ReverseContourPen(Cu2QuPen(pen,max_err=1.0,reverse_direction=False)))
    g=pen.glyph()
    adv=round(xmax-xmin + SB*U + RSB.get(n,SB)*U)
    glyphs[n]=g; metrics[n]=(adv,0)
print('traced in %.1fs'%(time.time()-t0))

fb=FontBuilder(UPM,isTTF=True)
fb.setupGlyphOrder(order)
fb.setupCharacterMap(CMAP)
fb.setupGlyf(glyphs)
gs=fb.font['glyf']
for n in order:
    g=gs[n]; g.recalcBounds(gs)
    metrics[n]=(metrics[n][0], getattr(g,'xMin',0))
fb.setupHorizontalMetrics(metrics)
ymax=max(getattr(gs[n],'yMax',0) for n in order); ymin=min(getattr(gs[n],'yMin',0) for n in order)
fb.setupHorizontalHeader(ascent=900,descent=-250,caretSlopeRise=2,caretSlopeRun=1)
fb.setupNameTable({'familyName':'Creaturepunk','styleName':'Regular','uniqueFontIdentifier':'Creaturepunk-Regular-1.000',
    'fullName':'Creaturepunk Regular','psName':'Creaturepunk-Regular','version':'Version 1.000',
    'description':'Graffiti display caps traced from the CREATUREPUNK logo lettering; the missing letters, digits and punctuation are built from pieces of the traced ones.',
    'copyright':'Copyright (c) 2026 Dimm City','licenseDescription':'This font is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).',
    'licenseInfoURL':'https://creativecommons.org/licenses/by/4.0/'})
fb.setupOS2(sTypoAscender=900,sTypoDescender=-250,sTypoLineGap=0,usWinAscent=max(1050,ymax),usWinDescent=max(250,-ymin),
    sxHeight=700,sCapHeight=700,achVendID='NONE',fsSelection=0x80|0x40,usWeightClass=400,version=4)
fb.setupPost(italicAngle=-math.degrees(math.atan(SLANT)))
from fontTools.misc.timeTools import timestampNow
fb.setupHead(unitsPerEm=UPM,created=timestampNow(),modified=timestampNow())
addOpenTypeFeaturesFromString(fb.font,'''
languagesystem DFLT dflt;
languagesystem latn dflt;
@plain=[C U K]; @swash=[C.swsh U.swsh K.swsh];
feature swsh { sub @plain by @swash; } swsh;
feature ss01 { featureNames { name "Logo forms: tall C, short-stemmed U, long-legged K"; }; sub @plain by @swash; } ss01;
''')
out=sys.argv[1] if len(sys.argv)>1 else '../../fonts/creaturepunk/Creaturepunk.ttf'
fb.save(out)
print('wrote',out)
print('ymax',ymax,'ymin',ymin)
