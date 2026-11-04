# gp-dimm-city print colour audit — measurements

Every token in styles/dc-palette.css and styles/dc-identity.css converted sRGB -> CMYK through gutterpress's own packages/cli/profiles/CGATS21_CRPC1.icc (LittleCMS via Pillow, perceptual intent). rt-hex = the colour printed back to sRGB; dEok = OKLab distance x100 between the screen colour and the printed colour (>6 is a visible shift, >10 a different colour). Ghostscript was not available in this session, so these are the ICC's numbers, not the build's; gutterpress #331 measured the real build at #000 -> 47/42/40/100 vs this method's 50/46/44/100.

```
profile: CGATS21_CRPC1.icc
token                    hex      CMYK (perceptual)       TAC rt-hex    dEok    okL   okC   okH
--bg                     #c8c5bf  C14 M11 Y13 K0           38 #c8c6c1    0.3   0.82 0.009    85
--concrete-pale          #dcdad5  C9 M7 Y9 K0              25 #dcdad6    0.1   0.89 0.007    89
--paper-cream            #ffffff  C0 M0 Y0 K0               0 #ffffff    0.0   1.00 0.000    90
--paper-form             #f5f3ee  C3 M2 Y4 K0               9 #f4f3ef    0.2   0.96 0.007    89
--paper-zine             #e9e6e0  C5 M4 Y7 K0              16 #eae7e1    0.3   0.93 0.009    85
--paper-light            #ffffff  C0 M0 Y0 K0               0 #ffffff    0.0   1.00 0.000    90
--paper-aged             #c8c2b8  C14 M12 Y16 K0           42 #c8c3ba    0.3   0.82 0.015    81
--paper-stain            #b0a89c  C19 M16 Y22 K4           61 #afa89d    0.2   0.73 0.019    78
--ink                    #1e1d1c  C42 M36 Y33 K85         196 #1c1b1a    0.9   0.23 0.002    68
--ink-dark               #2f2622  C36 M36 Y33 K76         181 #2e2623    0.3   0.28 0.015    45
--ink-smoke              #4d4339  C32 M33 Y37 K55         157 #4d443b    0.4   0.39 0.021    67
--ink-mid                #594f43  C31 M31 Y38 K47         147 #595045    0.4   0.43 0.023    72
--ink-dust               #665b4e  C30 M29 Y37 K38         134 #655c4f    0.3   0.48 0.025    72
--crimson                #e1261c  C0 M93 Y93 K1           187 #d13c31    3.4   0.59 0.221    29
--blood                  #901a12  C0 M88 Y65 K37          190 #8e1e14    0.5   0.42 0.154    29
--orange                 #d4500a  C0 M71 Y98 K4           173 #cd542e    2.1   0.60 0.180    41
--orange-deep            #a03808  C0 M76 Y89 K27          192 #a03817    0.8   0.48 0.147    40
--rust                   #b23a12  C0 M82 Y91 K17          190 #b13b20    0.9   0.52 0.163    37
--amber                  #7a5a20  C13 M28 Y77 K41         159 #7a5c24    0.6   0.49 0.085    79
--deep-rust              #70200e  C4 M71 Y56 K54          185 #6f210e    0.3   0.37 0.116    34
--amber-dark             #5c3c10  C15 M36 Y71 K60         182 #5b3d14    0.4   0.38 0.073    70
--brand-magenta          #c026d3  C34 M74 Y0 K1           109 #8e548b   16.1   0.59 0.257   323
--brand-magenta-deep     #8a0a9a  C51 M96 Y0 K6           153 #6a3a72   11.0   0.46 0.211   322
--brand-cyan             #00bcd4  C48 M0 Y7 K0             55 #51b7ce    2.8   0.73 0.126   211
--brand-yellow           #ffd700  C1 M4 Y91 K0             96 #f6d745    2.3   0.89 0.182    95
--brand-violet           #7030b8  C65 M82 Y0 K2           149 #5b447d   11.2   0.47 0.200   300
--signal-indigo          #4430e0  C90 M66 Y0 K3           159 #364882   15.8   0.47 0.247   276
--hud-blue               #1f6f94  C73 M24 Y4 K13          114 #1d6f94    0.1   0.51 0.094   233
--hud-blue-dark          #14516e  C75 M32 Y8 K30          145 #11526f    0.3   0.41 0.077   234
--hud-blue-dim           #7ab8d0  C37 M4 Y5 K1             47 #7bb8d0    0.1   0.75 0.072   224
--hud-panel              #eeece8  C4 M4 Y5 K0              13 #eeece8    0.0   0.94 0.006    85
--surface-tint-3         #f2f0ec  C4 M3 Y4 K0              11 #f1efec    0.3   0.96 0.006    85
--surface-orange-tint    #d8cfb4  C10 M9 Y21 K0            40 #d8cfb5    0.1   0.85 0.038    92
--border-hairline        #c8b898  C13 M13 Y28 K2           56 #c8b99a    0.3   0.79 0.047    85
--tint-magenta-rose      #e6007a  C0 M98 Y9 K2            109 #d5347b    4.0   0.60 0.243   360
--tint-hud-teal          #2a6a8a  C69 M25 Y7 K17          118 #286b8b    0.3   0.50 0.082   234
--fungi-glow             #c8e040  C17 M0 Y75 K0            92 #c1ca53    6.5   0.86 0.179   118
--fungi-rot              #30461e  C39 M17 Y64 K62         182 #2f4721    0.4   0.37 0.069   133
--crystal-amethyst       #6a3a8a  C58 M89 Y0 K4           151 #623f77    3.8   0.44 0.133   310
--crystal-aqua           #4a98a8  C53 M9 Y14 K6            82 #4998a9    0.2   0.64 0.080   213
--crystal-slate          #52626f  C48 M28 Y18 K27         121 #4f6371    0.5   0.49 0.029   243
--streetwarden-accent    #4db840  C46 M0 Y82 K0           128 #69ab4f    4.9   0.70 0.187   142
--cybersurgeon-accent    #a8b4b8  C23 M12 Y13 K2           50 #a9b5b9    0.3   0.76 0.015   220
--augmerc-dark           #003a40  C63 M25 Y25 K58         171 #043c42    0.8   0.32 0.054   206
--proxy-dark             #8a1a90  C45 M96 Y0 K7           148 #713a71    8.8   0.46 0.194   326
--cybersurgeon-dark      #303840  C48 M34 Y21 K58         161 #313941    0.4   0.34 0.018   248
--wirephreak-dark        #1e0f50  C86 M83 Y0 K45          214 #1a1541    3.1   0.24 0.110   285
--streetwarden-dark      #294c1f  C44 M13 Y70 K58         185 #274d24    0.6   0.38 0.082   139
--technosorcerer-dark    #4c290f  C18 M44 Y56 K69         187 #4c2b12    0.6   0.32 0.065    54
--gutterdruid-dark       #394017  C33 M21 Y64 K65         183 #3a4119    0.4   0.35 0.062   118
--etherlock-dark         #46360c  C23 M30 Y66 K68         187 #45360f    0.3   0.34 0.061    87
--dualist-dark           #143a4a  C64 M33 Y16 K52         165 #133b4c    0.4   0.33 0.051   229
--generalist-dark        #212a32  C50 M36 Y22 K68         176 #232b32    0.5   0.28 0.019   245
--augmerc-mid            #006878  C69 M17 Y17 K26         129 #046979    0.4   0.48 0.083   213
--proxy-mid              #9a1896  C34 M96 Y0 K8           138 #873876    7.9   0.49 0.207   330
--cybersurgeon-mid       #606870  C41 M27 Y20 K26         114 #5f6871    0.2   0.51 0.016   248
--streetwarden-mid       #347828  C51 M2 Y90 K29          172 #377732    1.2   0.51 0.134   141
--gutterdruid-mid        #4d6020  C33 M11 Y80 K45         169 #4e6123    0.4   0.46 0.092   124
--wirephreak-mid         #2f2290  C97 M88 Y0 K11          196 #28306a    7.2   0.35 0.170   278
--technosorcerer-mid     #7a3008  C3 M63 Y74 K48          188 #79320e    0.5   0.41 0.114    44
--etherlock-mid          #8a6a00  C9 M20 Y95 K35          159 #886b1a    1.0   0.54 0.111    88
--dualist-mid            #2a6878  C62 M20 Y17 K25         124 #296979    0.3   0.48 0.068   218
--generalist-mid         #3a4854  C52 M33 Y19 K44         148 #3a4955    0.3   0.39 0.027   244
```

## color-mix() tints, before and after --paper-cream = #ffffff
```
profile: CGATS21_CRPC1.icc
surface                      old (on #f0eee9)  TAC  new (on #fff)  CMYK new                TAC min nonzero ink %
warning callout bg           #f2ebc8            23  #fff9db        C1 M1 Y9 K0              11        1
vibe callout bg              #e8e3e6            15  #f6f3fb        C2 M2 Y1 K0               5        1
origin callout bg            #e3ddcc            26  #eae5d6        C5 M4 Y11 K0             20        4
location callout bg          #dde5e5            17  #eaf4f7        C4 M2 Y2 K0               8        2
augment entry                #e2e8e6            16  #eff6f9        C3 M2 Y1 K0               6        1
treasure entry               #e3dce0            19  #f0ebf3        C4 M4 Y2 K0              10        2
drug entry                   #e6ebc0            28  #f2f8d1        C4 M0 Y12 K0             16        4
field effects                #c3d9e0            23  #cce4ed        C12 M2 Y3 K0             17        2
field side-effects           #eed2cc            24  #fbe1df        C1 M7 Y5 K0              13        1
section-reference bg         #d6e2e4            19  #e2eff5        C6 M2 Y2 K0              10        2
section-lore bg              #e7e1e6            16  #f5f1fa        C3 M2 Y1 K0               6        1
faction megacorp             #dde5e5            17  #eaf4f7        C4 M2 Y2 K0               8        2
faction cabal                #e4dde5            16  #f2ecf9        C4 M4 Y1 K0               9        1
faction cult                 #e7dbd6            22  #f5eaea        C3 M4 Y4 K0              11        3
choice tint (footer well)    #e1ded9            21  #eeeeed        C4 M3 Y4 K0              11        3
crimson 40% (?)              #ea9e97            51  #f3a8a4        C1 M25 Y16 K0            42        1

-- tape: yellow 30% on paper-aged: #d8c881
-- blood 13% on paper-light old vs new: #d7c5bd #f1e1e0
```

## Text-on-fill contrast (WCAG, sRGB values)
```
profile: CGATS21_CRPC1.icc
16.83:1  AAA      body --ink on white (was cream)
 6.62:1  AA       --ink-dust on white
 5.71:1  AA       --ink-dust on old cream
 5.41:1  AA       cream(now white) on --brand-magenta bar @90% mix w/ ink
 4.71:1  AA       white on --brand-magenta (100%)
 2.73:1  FAIL     --bg (#c8c5bf) on --hud-magenta  [specialty-intro title default]
 8.64:1  AAA      white on --hud-blue-dark (ap chip, block title)
 5.99:1  AA       white on --rust (chapter chip)
 4.24:1  AA-large white on --orange
 4.67:1  AA       white on --crimson (specialty-card band default)
 7.49:1  AAA      white on --brand-violet
 8.12:1  AAA      white on --crystal-amethyst
 9.96:1  AAA      white on --amber-dark
 8.11:1  AAA      white on --brand-magenta-deep (chevron)
14.78:1  AAA      white on --ink-dark (dm-note, slate)
 7.69:1  AAA      --ink on --hud-blue-dim (alert body)
 6.75:1  AA       --ink-dark on --hud-blue-dim (alert label)
 8.64:1  AAA      --hud-blue-dark on white (definition term, path code)
 6.85:1  AA       --orange-deep on white (lede ink, stat-strip value)
 8.97:1  AAA      --blood on white
 7.49:1  AAA      --brand-violet on white (treasure ink)
 4.24:1  AA-large --orange on white (classtag)
 4.67:1  AA       --crimson on white
 4.71:1  AA       --brand-magenta on white
 8.11:1  AAA      --brand-magenta-deep on white (accent ink)
 9.51:1  AAA      --ink on --paper-aged (field, code)
 9.77:1  AAA      --ink on --bg wall
 3.85:1  AA-large --ink-dust on --bg wall
 4.42:1  AA-large --fungi-glow on visit bg (fungi-rot80/glow)
 6.54:1  AA       white on visit bg
11.37:1  AAA      --ink on --fungi-glow (outcome hit row)
 6.85:1  AA       white on --orange-deep (outcome mixed row)
 8.97:1  AAA      white on --blood (outcome miss)
10.39:1  AAA      white on --fungi-rot (outcome fail)
 8.11:1  AAA      white on --brand-magenta-deep (outcome crit)
 9.37:1  AAA      surreal term (magenta38/white) on --wirephreak-dark
16.94:1  AAA      white on --wirephreak-dark
 6.43:1  AA       --hud-blue-bright on --ink-dark (dm-note accent)
12.00:1  AAA      --brand-yellow on --ink (enforcer?)
12.00:1  AAA      --ink on --brand-yellow
10.02:1  AAA      --ink on --dc-tape-bg
12.05:1  AAA      --ink on --concrete-pale (pullquote, dm section)
 5.80:1  AA       --brand-magenta-deep on --concrete-pale (pullquote accent)
 9.64:1  AAA      --ink-smoke on white (npc secondary)
 8.00:1  AAA      --ink-mid on white
 6.34:1  AA       --amber on white
 5.99:1  AA       --rust on white
 5.59:1  AA       --hud-blue on white
 2.30:1  FAIL     --brand-cyan on white
 3.31:1  AA-large --crystal-aqua on white
 1.48:1  FAIL     --fungi-glow on white
 2.55:1  FAIL     --streetwarden-accent on white
 2.12:1  FAIL     --cybersurgeon-accent on white
```

## Hue families: distance before (screen) -> after (printed on CRPC1)
```
profile: CGATS21_CRPC1.icc

== purples: OKLab distance BEFORE (sRGB) -> AFTER (CRPC1 round-trip) ==
  --brand-magenta        --crystal-amethyst      19.6 ->  10.5  (printed #8e548b vs #623f77)
  --brand-magenta        --signal-indigo         23.4 ->  15.5  (printed #8e548b vs #364882)
  --brand-magenta        --proxy-dark            14.7 ->   9.3  (printed #8e548b vs #713a71)
  --brand-magenta        --proxy-mid             11.8 ->   6.9  (printed #8e548b vs #873876)
  --brand-magenta        --wirephreak-mid        30.0 ->  21.8  (printed #8e548b vs #28306a)
  --brand-magenta-deep   --brand-violet           8.2 ->   3.8  (printed #6a3a72 vs #5b447d)
  --brand-magenta-deep   --crystal-amethyst       8.8 ->   1.9  (printed #6a3a72 vs #623f77)
  --brand-magenta-deep   --signal-indigo         18.4 ->   9.2  (printed #6a3a72 vs #364882)
  --brand-magenta-deep   --proxy-dark             2.1 ->   1.4  (printed #6a3a72 vs #713a71)
  --brand-magenta-deep   --proxy-mid              3.9 ->   5.7  (printed #6a3a72 vs #873876)
  --brand-violet         --crystal-amethyst       7.7 ->   1.9  (printed #5b447d vs #623f77)
  --brand-violet         --signal-indigo         10.4 ->   5.8  (printed #5b447d vs #364882)
  --brand-violet         --proxy-dark             8.9 ->   4.8  (printed #5b447d vs #713a71)
  --brand-violet         --proxy-mid             10.5 ->   8.5  (printed #5b447d vs #873876)
  --crystal-amethyst     --signal-indigo         15.7 ->   7.4  (printed #623f77 vs #364882)
  --crystal-amethyst     --proxy-dark             7.7 ->   3.1  (printed #623f77 vs #713a71)
  --crystal-amethyst     --proxy-mid             10.3 ->   7.1  (printed #623f77 vs #873876)
  --signal-indigo        --proxy-dark            19.1 ->  10.4  (printed #364882 vs #713a71)
  --signal-indigo        --proxy-mid             20.8 ->  14.3  (printed #364882 vs #873876)
  --signal-indigo        --wirephreak-mid        14.1 ->   8.1  (printed #364882 vs #28306a)
  --signal-indigo        --tint-magenta-rose     35.2 ->  28.6  (printed #364882 vs #d5347b)
  --proxy-dark           --proxy-mid              3.4 ->   4.4  (printed #713a71 vs #873876)

== warm reds: OKLab distance BEFORE (sRGB) -> AFTER (CRPC1 round-trip) ==
  --crimson              --orange                 6.1 ->   4.3  (printed #d13c31 vs #cd542e)
  --crimson              --rust                   9.2 ->   6.6  (printed #d13c31 vs #b13b20)
  --orange               --rust                   8.5 ->   7.9  (printed #cd542e vs #b13b20)
  --rust                 --orange-deep            3.8 ->   3.7  (printed #b13b20 vs #a03817)
  --rust                 --blood                  9.6 ->   9.6  (printed #b13b20 vs #8e1e14)
  --orange-deep          --blood                  6.7 ->   6.4  (printed #a03817 vs #8e1e14)
  --orange-deep          --technosorcerer-mid     8.4 ->   8.4  (printed #a03817 vs #79320e)
  --blood                --deep-rust              6.8 ->   6.7  (printed #8e1e14 vs #6f210e)
  --blood                --technosorcerer-mid     5.5 ->   5.2  (printed #8e1e14 vs #79320e)
  --deep-rust            --technosorcerer-mid     4.4 ->   4.6  (printed #6f210e vs #79320e)

== teals: OKLab distance BEFORE (sRGB) -> AFTER (CRPC1 round-trip) ==
  --brand-cyan           --crystal-aqua          10.4 ->   9.3  (printed #51b7ce vs #4998a9)
  --brand-cyan           --hud-blue-dim           6.2 ->   3.8  (printed #51b7ce vs #7bb8d0)
  --hud-blue             --hud-blue-dark         10.2 ->   9.9  (printed #1d6f94 vs #11526f)
  --hud-blue             --tint-hud-teal          1.9 ->   1.6  (printed #1d6f94 vs #286b8b)
  --hud-blue             --augmerc-mid            5.0 ->   4.7  (printed #1d6f94 vs #046979)
  --hud-blue             --dualist-mid            4.5 ->   4.2  (printed #1d6f94 vs #296979)
  --hud-blue-dark        --tint-hud-teal          8.6 ->   8.6  (printed #11526f vs #286b8b)
  --hud-blue-dark        --augmerc-mid            7.0 ->   7.1  (printed #11526f vs #046979)
  --hud-blue-dark        --dualist-mid            7.6 ->   7.6  (printed #11526f vs #296979)
  --tint-hud-teal        --augmerc-mid            3.7 ->   3.6  (printed #286b8b vs #046979)
  --tint-hud-teal        --dualist-mid            2.9 ->   2.9  (printed #286b8b vs #296979)
  --augmerc-mid          --dualist-mid            1.9 ->   1.7  (printed #046979 vs #296979)

== greens: OKLab distance BEFORE (sRGB) -> AFTER (CRPC1 round-trip) ==
  --fungi-glow           --gutterdruid-mid       41.2 ->  35.1  (printed #c1ca53 vs #4e6123)
  --fungi-glow           --brand-yellow           7.5 ->   8.6  (printed #c1ca53 vs #f6d745)
  --streetwarden-mid     --gutterdruid-mid        7.4 ->   6.6  (printed #377732 vs #4e6123)
```

## Near-duplicate tokens (OKLab distance < 9)
```
profile: CGATS21_CRPC1.icc
dE_ok  0.0  --paper-cream            #ffffff  ~  --paper-light            #ffffff
dE_ok  0.9  --paper-form             #f5f3ee  ~  --surface-tint-3         #f2f0ec
dE_ok  1.0  --bg                     #c8c5bf  ~  --paper-aged             #c8c2b8
dE_ok  1.2  --hud-panel              #eeece8  ~  --surface-tint-3         #f2f0ec
dE_ok  1.8  --paper-zine             #e9e6e0  ~  --hud-panel              #eeece8
dE_ok  1.9  --augmerc-mid            #006878  ~  --dualist-mid            #2a6878
dE_ok  1.9  --hud-blue               #1f6f94  ~  --tint-hud-teal          #2a6a8a
dE_ok  2.0  --fungi-rot              #30461e  ~  --streetwarden-dark      #294c1f
dE_ok  2.1  --paper-form             #f5f3ee  ~  --hud-panel              #eeece8
dE_ok  2.1  --fungi-rot              #30461e  ~  --gutterdruid-dark       #394017
dE_ok  2.1  --brand-magenta-deep     #8a0a9a  ~  --proxy-dark             #8a1a90
dE_ok  2.4  --augmerc-dark           #003a40  ~  --dualist-dark           #143a4a
dE_ok  2.9  --crystal-slate          #52626f  ~  --cybersurgeon-mid       #606870
dE_ok  2.9  --tint-hud-teal          #2a6a8a  ~  --dualist-mid            #2a6878
dE_ok  3.0  --paper-zine             #e9e6e0  ~  --surface-tint-3         #f2f0ec
dE_ok  3.4  --proxy-dark             #8a1a90  ~  --proxy-mid              #9a1896
dE_ok  3.4  --ink-dark               #2f2622  ~  --generalist-dark        #212a32
dE_ok  3.5  --gutterdruid-dark       #394017  ~  --etherlock-dark         #46360c
dE_ok  3.5  --cybersurgeon-dark      #303840  ~  --dualist-dark           #143a4a
dE_ok  3.6  --paper-cream            #ffffff  ~  --paper-form             #f5f3ee
dE_ok  3.6  --paper-form             #f5f3ee  ~  --paper-light            #ffffff
dE_ok  3.7  --concrete-pale          #dcdad5  ~  --paper-zine             #e9e6e0
dE_ok  3.7  --tint-hud-teal          #2a6a8a  ~  --augmerc-mid            #006878
dE_ok  3.8  --orange-deep            #a03808  ~  --rust                   #b23a12
dE_ok  3.9  --paper-form             #f5f3ee  ~  --paper-zine             #e9e6e0
dE_ok  3.9  --brand-magenta-deep     #8a0a9a  ~  --proxy-mid              #9a1896
dE_ok  4.1  --streetwarden-dark      #294c1f  ~  --gutterdruid-dark       #394017
dE_ok  4.1  --technosorcerer-dark    #4c290f  ~  --etherlock-dark         #46360c
dE_ok  4.2  --paper-stain            #b0a89c  ~  --cybersurgeon-accent    #a8b4b8
dE_ok  4.2  --bg                     #c8c5bf  ~  --surface-orange-tint    #d8cfb4
dE_ok  4.3  --paper-aged             #c8c2b8  ~  --border-hairline        #c8b898
dE_ok  4.4  --crystal-slate          #52626f  ~  --dualist-mid            #2a6878
dE_ok  4.4  --ink-smoke              #4d4339  ~  --ink-mid                #594f43
dE_ok  4.4  --ink-mid                #594f43  ~  --ink-dust               #665b4e
dE_ok  4.4  --deep-rust              #70200e  ~  --technosorcerer-mid     #7a3008
dE_ok  4.5  --hud-blue               #1f6f94  ~  --dualist-mid            #2a6878
dE_ok  4.5  --paper-aged             #c8c2b8  ~  --surface-orange-tint    #d8cfb4
dE_ok  4.5  --paper-cream            #ffffff  ~  --surface-tint-3         #f2f0ec
dE_ok  4.5  --paper-light            #ffffff  ~  --surface-tint-3         #f2f0ec
dE_ok  4.6  --concrete-pale          #dcdad5  ~  --surface-orange-tint    #d8cfb4
dE_ok  4.7  --augmerc-dark           #003a40  ~  --cybersurgeon-dark      #303840
dE_ok  4.8  --ink                    #1e1d1c  ~  --ink-dark               #2f2622
dE_ok  4.9  --amber-dark             #5c3c10  ~  --etherlock-dark         #46360c
dE_ok  4.9  --ink-smoke              #4d4339  ~  --generalist-mid         #3a4854
dE_ok  5.0  --hud-blue               #1f6f94  ~  --augmerc-mid            #006878
dE_ok  5.2  --ink-smoke              #4d4339  ~  --amber-dark             #5c3c10
dE_ok  5.3  --bg                     #c8c5bf  ~  --border-hairline        #c8b898
dE_ok  5.3  --hud-blue-dark          #14516e  ~  --generalist-mid         #3a4854
dE_ok  5.3  --ink                    #1e1d1c  ~  --generalist-dark        #212a32
dE_ok  5.4  --ink-dust               #665b4e  ~  --cybersurgeon-mid       #606870
dE_ok  5.4  --ink-dust               #665b4e  ~  --crystal-slate          #52626f
dE_ok  5.5  --blood                  #901a12  ~  --technosorcerer-mid     #7a3008
dE_ok  5.5  --tint-hud-teal          #2a6a8a  ~  --crystal-slate          #52626f
dE_ok  5.5  --concrete-pale          #dcdad5  ~  --hud-panel              #eeece8
dE_ok  5.6  --fungi-rot              #30461e  ~  --etherlock-dark         #46360c
dE_ok  5.6  --augmerc-dark           #003a40  ~  --generalist-dark        #212a32
dE_ok  5.7  --cybersurgeon-dark      #303840  ~  --generalist-dark        #212a32
dE_ok  5.7  --paper-cream            #ffffff  ~  --hud-panel              #eeece8
dE_ok  5.7  --paper-light            #ffffff  ~  --hud-panel              #eeece8
dE_ok  5.9  --cybersurgeon-dark      #303840  ~  --generalist-mid         #3a4854
dE_ok  5.9  --dualist-dark           #143a4a  ~  --generalist-dark        #212a32
dE_ok  5.9  --hud-blue-dim           #7ab8d0  ~  --cybersurgeon-accent    #a8b4b8
dE_ok  5.9  --amber                  #7a5a20  ~  --etherlock-mid          #8a6a00
dE_ok  6.0  --paper-stain            #b0a89c  ~  --border-hairline        #c8b898
dE_ok  6.1  --paper-aged             #c8c2b8  ~  --cybersurgeon-accent    #a8b4b8
dE_ok  6.1  --crimson                #e1261c  ~  --orange                 #d4500a
dE_ok  6.1  --crystal-slate          #52626f  ~  --augmerc-mid            #006878
dE_ok  6.2  --ink-dust               #665b4e  ~  --amber                  #7a5a20
dE_ok  6.2  --cybersurgeon-mid       #606870  ~  --dualist-mid            #2a6878
dE_ok  6.2  --brand-cyan             #00bcd4  ~  --hud-blue-dim           #7ab8d0
dE_ok  6.2  --ink-smoke              #4d4339  ~  --gutterdruid-dark       #394017
dE_ok  6.3  --amber-dark             #5c3c10  ~  --gutterdruid-dark       #394017
dE_ok  6.3  --amber-dark             #5c3c10  ~  --technosorcerer-mid     #7a3008
dE_ok  6.4  --ink-smoke              #4d4339  ~  --etherlock-dark         #46360c
dE_ok  6.4  --border-hairline        #c8b898  ~  --cybersurgeon-accent    #a8b4b8
dE_ok  6.4  --ink-mid                #594f43  ~  --generalist-mid         #3a4854
dE_ok  6.4  --bg                     #c8c5bf  ~  --concrete-pale          #dcdad5
dE_ok  6.6  --ink-dark               #2f2622  ~  --technosorcerer-dark    #4c290f
dE_ok  6.6  --bg                     #c8c5bf  ~  --cybersurgeon-accent    #a8b4b8
dE_ok  6.6  --ink-smoke              #4d4339  ~  --cybersurgeon-dark      #303840
dE_ok  6.7  --blood                  #901a12  ~  --orange-deep            #a03808
dE_ok  6.7  --amber-dark             #5c3c10  ~  --technosorcerer-dark    #4c290f
dE_ok  6.7  --concrete-pale          #dcdad5  ~  --surface-tint-3         #f2f0ec
dE_ok  6.7  --ink-dark               #2f2622  ~  --cybersurgeon-dark      #303840
dE_ok  6.8  --surface-orange-tint    #d8cfb4  ~  --border-hairline        #c8b898
dE_ok  6.8  --ink-smoke              #4d4339  ~  --fungi-rot              #30461e
dE_ok  6.8  --blood                  #901a12  ~  --deep-rust              #70200e
dE_ok  6.9  --tint-hud-teal          #2a6a8a  ~  --cybersurgeon-mid       #606870
dE_ok  7.0  --ink-mid                #594f43  ~  --amber-dark             #5c3c10
dE_ok  7.0  --dualist-dark           #143a4a  ~  --generalist-mid         #3a4854
dE_ok  7.0  --hud-blue-dark          #14516e  ~  --augmerc-mid            #006878
dE_ok  7.1  --hud-blue               #1f6f94  ~  --crystal-slate          #52626f
dE_ok  7.3  --concrete-pale          #dcdad5  ~  --paper-aged             #c8c2b8
dE_ok  7.4  --deep-rust              #70200e  ~  --amber-dark             #5c3c10
dE_ok  7.4  --streetwarden-mid       #347828  ~  --gutterdruid-mid        #4d6020
dE_ok  7.5  --technosorcerer-dark    #4c290f  ~  --gutterdruid-dark       #394017
dE_ok  7.5  --ink-mid                #594f43  ~  --crystal-slate          #52626f
dE_ok  7.5  --amber                  #7a5a20  ~  --gutterdruid-mid        #4d6020
dE_ok  7.5  --paper-cream            #ffffff  ~  --paper-zine             #e9e6e0
dE_ok  7.5  --paper-zine             #e9e6e0  ~  --paper-light            #ffffff
dE_ok  7.5  --brand-yellow           #ffd700  ~  --fungi-glow             #c8e040
dE_ok  7.5  --streetwarden-dark      #294c1f  ~  --etherlock-dark         #46360c
dE_ok  7.6  --concrete-pale          #dcdad5  ~  --paper-form             #f5f3ee
dE_ok  7.6  --hud-blue-dark          #14516e  ~  --dualist-mid            #2a6878
dE_ok  7.6  --amber-dark             #5c3c10  ~  --fungi-rot              #30461e
dE_ok  7.7  --paper-zine             #e9e6e0  ~  --surface-orange-tint    #d8cfb4
dE_ok  7.7  --deep-rust              #70200e  ~  --technosorcerer-dark    #4c290f
dE_ok  7.7  --crystal-amethyst       #6a3a8a  ~  --proxy-dark             #8a1a90
dE_ok  7.7  --cybersurgeon-dark      #303840  ~  --gutterdruid-dark       #394017
dE_ok  7.7  --brand-violet           #7030b8  ~  --crystal-amethyst       #6a3a8a
dE_ok  7.8  --cybersurgeon-dark      #303840  ~  --etherlock-dark         #46360c
dE_ok  7.9  --hud-blue               #1f6f94  ~  --cybersurgeon-mid       #606870
dE_ok  7.9  --ink-smoke              #4d4339  ~  --streetwarden-dark      #294c1f
dE_ok  8.0  --augmerc-mid            #006878  ~  --cybersurgeon-mid       #606870
dE_ok  8.0  --ink-dark               #2f2622  ~  --augmerc-dark           #003a40
dE_ok  8.1  --paper-aged             #c8c2b8  ~  --paper-stain            #b0a89c
dE_ok  8.1  --ink-dust               #665b4e  ~  --gutterdruid-mid        #4d6020
dE_ok  8.2  --ink-smoke              #4d4339  ~  --technosorcerer-dark    #4c290f
dE_ok  8.2  --brand-magenta-deep     #8a0a9a  ~  --brand-violet           #7030b8
dE_ok  8.2  --ink-dark               #2f2622  ~  --etherlock-dark         #46360c
dE_ok  8.3  --ink-mid                #594f43  ~  --amber                  #7a5a20
dE_ok  8.3  --cybersurgeon-dark      #303840  ~  --technosorcerer-dark    #4c290f
dE_ok  8.3  --fungi-rot              #30461e  ~  --cybersurgeon-dark      #303840
dE_ok  8.3  --ink-mid                #594f43  ~  --gutterdruid-mid        #4d6020
dE_ok  8.4  --orange-deep            #a03808  ~  --technosorcerer-mid     #7a3008
dE_ok  8.4  --ink-dark               #2f2622  ~  --dualist-dark           #143a4a
dE_ok  8.4  --streetwarden-dark      #294c1f  ~  --gutterdruid-mid        #4d6020
dE_ok  8.5  --augmerc-dark           #003a40  ~  --generalist-mid         #3a4854
dE_ok  8.5  --orange                 #d4500a  ~  --rust                   #b23a12
dE_ok  8.6  --hud-blue-dark          #14516e  ~  --tint-hud-teal          #2a6a8a
dE_ok  8.7  --hud-blue-dark          #14516e  ~  --dualist-dark           #143a4a
dE_ok  8.8  --brand-magenta-deep     #8a0a9a  ~  --crystal-amethyst       #6a3a8a
dE_ok  8.8  --fungi-rot              #30461e  ~  --generalist-mid         #3a4854
dE_ok  8.8  --ink-smoke              #4d4339  ~  --ink-dust               #665b4e
dE_ok  8.8  --amber-dark             #5c3c10  ~  --streetwarden-dark      #294c1f
dE_ok  8.8  --fungi-rot              #30461e  ~  --augmerc-dark           #003a40
dE_ok  8.9  --ink-mid                #594f43  ~  --cybersurgeon-mid       #606870
dE_ok  8.9  --brand-violet           #7030b8  ~  --proxy-dark             #8a1a90
dE_ok  8.9  --augmerc-dark           #003a40  ~  --gutterdruid-dark       #394017
dE_ok  9.0  --ink-dust               #665b4e  ~  --dualist-mid            #2a6878
dE_ok  9.0  --bg                     #c8c5bf  ~  --paper-stain            #b0a89c
```
