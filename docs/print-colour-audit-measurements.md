# gp-dimm-city print colour audit — measurements

The output of `python3 scripts/measure-palette-crpc1.py <mode>` for each mode below, regenerated after the fix
(release 1.10.2). Every hex token in `styles/dc-palette.css` and `styles/dc-identity.css`,
and every `color-mix()` of two palette tokens in `styles/`, converted sRGB -> CMYK
through the CGATS21_CRPC1 profile gutterpress ships, with LittleCMS (Pillow) at
perceptual intent.

- **printed**: the CMYK printed back to sRGB; **dE**: OKLab distance x100 between screen
  and print (> 6 is a visible shift, > 10 a different colour).
- **mixes**: **max** is the tint's strongest ink, **min** its weakest non-zero one (a
  1-2% dot does not hold on HP Indigo or inkjet).
- **contrast**: WCAG 2 contrast on the sRGB values.
- **dupes**: hex tokens closer than OKLab 6 (aliases are not listed: they are one colour).

These are the profile's numbers, not the build's. Ghostscript, which the build converts
with, was not run. gutterpress #331 measured the real build at `#000` -> C47 M42 Y40 K100;
this method gives C50 M46 Y44 K100.

## tokens

```
token                    hex      CMYK (perceptual)     TAC printed     dE    okL   okC  okH
--bg                     #c8c5bf  C14 M11 Y13 K0         38 #c8c6c1    0.3   0.82 0.009   85
--concrete-pale          #dcdad5  C9 M7 Y9 K0            25 #dcdad6    0.1   0.89 0.007   89
--paper-cream            #ffffff  C0 M0 Y0 K0             0 #ffffff    0.0   1.00 0.000   90
--paper-stain            #b0a89c  C19 M16 Y22 K4         61 #afa89d    0.2   0.73 0.019   78
--ink                    #1e1d1c  C42 M36 Y33 K85       196 #1c1b1a    0.9   0.23 0.002   68
--ink-dark               #2f2622  C36 M36 Y33 K76       181 #2e2623    0.3   0.28 0.015   45
--ink-smoke              #4d4339  C32 M33 Y37 K55       157 #4d443b    0.4   0.39 0.021   67
--ink-mid                #594f43  C31 M31 Y38 K47       147 #595045    0.4   0.43 0.023   72
--ink-dust               #665b4e  C30 M29 Y37 K38       134 #655c4f    0.3   0.48 0.025   72
--crimson                #e1261c  C0 M93 Y93 K1         187 #d13c31    3.4   0.59 0.221   29
--blood                  #901a12  C0 M88 Y65 K37        190 #8e1e14    0.5   0.42 0.154   29
--orange                 #d4500a  C0 M71 Y98 K4         173 #cd542e    2.1   0.60 0.180   41
--orange-deep            #a03808  C0 M76 Y89 K27        192 #a03817    0.8   0.48 0.147   40
--rust                   #b23a12  C0 M82 Y91 K17        190 #b13b20    0.9   0.52 0.163   37
--amber                  #7a5a20  C13 M28 Y77 K41       159 #7a5c24    0.6   0.49 0.085   79
--deep-rust              #70200e  C4 M71 Y56 K54        185 #6f210e    0.3   0.37 0.116   34
--amber-dark             #5c3c10  C15 M36 Y71 K60       182 #5b3d14    0.4   0.38 0.073   70
--brand-magenta          #bf308f  C10 M92 Y0 K6         108 #ba3881    2.8   0.56 0.201  345
--brand-magenta-deep     #76115e  C28 M97 Y2 K29        156 #721b52    2.7   0.39 0.155  340
--brand-cyan             #00bcd4  C48 M0 Y7 K0           55 #51b7ce    2.8   0.73 0.126  211
--brand-yellow           #ffd700  C1 M4 Y91 K0           96 #f6d745    2.3   0.89 0.182   95
--brand-violet           #5d3b88  C66 M86 Y0 K4         156 #563f77    3.4   0.43 0.125  302
--signal-indigo          #4b65ab  C69 M44 Y0 K3         116 #4f6597    3.2   0.52 0.115  267
--hud-blue               #1f6f94  C73 M24 Y4 K13        114 #1d6f94    0.1   0.51 0.094  233
--hud-blue-dark          #14516e  C75 M32 Y8 K30        145 #11526f    0.3   0.41 0.077  234
--hud-blue-dim           #7ab8d0  C37 M4 Y5 K1           47 #7bb8d0    0.1   0.75 0.072  224
--surface-tint-3         #f2f0ec  C4 M3 Y4 K0            11 #f1efec    0.3   0.96 0.006   85
--surface-orange-tint    #d8cfb4  C10 M9 Y21 K0          40 #d8cfb5    0.1   0.85 0.038   92
--fungi-glow             #c8e040  C17 M0 Y75 K0          92 #c1ca53    6.5   0.86 0.179  118
--fungi-rot              #30461e  C39 M17 Y64 K62       182 #2f4721    0.4   0.37 0.069  133
--crystal-amethyst       #835198  C41 M71 Y0 K4         116 #7e5387    3.0   0.52 0.121  315
--crystal-aqua           #4a98a8  C53 M9 Y14 K6          82 #4998a9    0.2   0.64 0.080  213
--crystal-slate          #52626f  C48 M28 Y18 K27       121 #4f6371    0.5   0.49 0.029  243
--streetwarden-accent    #4db840  C46 M0 Y82 K0         128 #69ab4f    4.9   0.70 0.187  142
--cybersurgeon-accent    #a8b4b8  C23 M12 Y13 K2         50 #a9b5b9    0.3   0.76 0.015  220
--augmerc-dark           #003a40  C63 M25 Y25 K58       171 #043c42    0.8   0.32 0.054  206
--cybersurgeon-dark      #303840  C48 M34 Y21 K58       161 #313941    0.4   0.34 0.018  248
--wirephreak-dark        #1e0f50  C86 M83 Y0 K45        214 #1a1541    3.1   0.24 0.110  285
--technosorcerer-dark    #4c290f  C18 M44 Y56 K69       187 #4c2b12    0.6   0.32 0.065   54
--etherlock-dark         #46360c  C23 M30 Y66 K68       187 #45360f    0.3   0.34 0.061   87
--dualist-dark           #143a4a  C64 M33 Y16 K52       165 #133b4c    0.4   0.33 0.051  229
--generalist-dark        #212a32  C50 M36 Y22 K68       176 #232b32    0.5   0.28 0.019  245
--augmerc-mid            #006878  C69 M17 Y17 K26       129 #046979    0.4   0.48 0.083  213
--proxy-mid              #9a227d  C22 M97 Y1 K15        135 #952a6f    2.8   0.48 0.181  340
--streetwarden-mid       #347828  C51 M2 Y90 K29        172 #377732    1.2   0.51 0.134  141
--gutterdruid-mid        #4d6020  C33 M11 Y80 K45       169 #4e6123    0.4   0.46 0.092  124
--wirephreak-mid         #1c327d  C95 M75 Y0 K16        186 #22346a    3.4   0.35 0.130  267
--technosorcerer-mid     #7a3008  C3 M63 Y74 K48        188 #79320e    0.5   0.41 0.114   44
--etherlock-mid          #8a6a00  C9 M20 Y95 K35        159 #886b1a    1.0   0.54 0.111   88
--generalist-mid         #3a4854  C52 M33 Y19 K44       148 #3a4955    0.3   0.39 0.027  244
aliases: --paper-form -> --paper-cream, --paper-zine -> --concrete-pale, --paper-light -> --paper-cream, --paper-aged -> --concrete-pale, --hud-blue-bright -> --brand-cyan, --hud-magenta -> --brand-magenta, --hud-panel -> --concrete-pale, --border-hairline -> --ink, --tint-magenta-rose -> --brand-magenta, --tint-hud-teal -> --hud-blue, --augmerc-accent -> --brand-cyan, --proxy-accent -> --brand-magenta, --gutterdruid-accent -> --fungi-glow, --wirephreak-accent -> --signal-indigo, --technosorcerer-accent -> --orange, --etherlock-accent -> --brand-yellow, --dualist-accent -> --crystal-aqua, --generalist-accent -> --crystal-slate, --proxy-dark -> --brand-magenta-deep, --streetwarden-dark -> --fungi-rot, --gutterdruid-dark -> --fungi-rot, --cybersurgeon-mid -> --crystal-slate, --dualist-mid -> --augmerc-mid
```

## mixes

```
where                                  mix                                              hex      CMYK                TAC  max  min
components/callouts.css:208            srgb --hud-blue-dark 50% --ink                   #193745  C61 M33 Y18 K55     167   61   18
components/callouts.css:217            oklch --brand-yellow 25% --paper-cream           #fff6d4  C1 M1 Y12 K0         14   12    1
components/callouts.css:292            oklch --brand-violet 22% --paper-cream           #d9d2e5  C9 M9 Y1 K0          19    9    1
components/callouts.css:326            oklch --surface-orange-tint 55% --paper-cream    #e9e4d5  C6 M5 Y11 K0         22   11    5
components/callouts.css:342            oklch --hud-blue-dim 30% --paper-cream           #d8eaf1  C9 M2 Y2 K0          13    9    2
components/callouts.css:380            srgb --fungi-rot 85% --fungi-glow                #475d23  C36 M12 Y76 K47     171   76   12
components/data.css:711                srgb --brand-magenta 38% --paper-cream           #e7b0d4  C5 M22 Y1 K0         28   22    1
components/entries.css:192             oklch --crystal-amethyst 25% --paper-cream       #dfd2e5  C7 M10 Y1 K0         18   10    1
components/entries.css:198             oklch --crystal-amethyst 40% --paper-cream       #ccb7d6  C12 M17 Y1 K0        30   17    1
components/entries.css:232             oklch --fungi-glow 24% --paper-cream             #f1f8d8  C4 M0 Y10 K0         14   10    4
components/entries.css:434             oklch --hud-blue-dim 38% --paper-cream           #cde4ed  C12 M2 Y3 K0         17   12    2
components/entries.css:439             oklch --crimson 22% --paper-cream                #ffd6cf  C1 M11 Y8 K0         20   11    1
components/section.css:852             srgb --crimson 40% --paper-cream                 #f3a8a4  C1 M25 Y16 K0        42   25    1
components/section.css:1031            oklch --blood 18% --paper-light                  #efd6d2  C3 M11 Y8 K0         22   11    3
components/section.css:1063            oklch --brand-violet 25% --paper-form            #d4cce2  C10 M11 Y1 K0        22   11    1
components/section.css:1157            oklch --brand-violet 25% --paper-cream           #d4cce2  C10 M11 Y1 K0        22   11    1
components/section.css:1158            srgb --brand-violet 72% --ink                    #4b336a  C66 M82 Y1 K18      167   82    1
components/section.css:1170            oklch --blood 18% --paper-cream                  #efd6d2  C3 M11 Y8 K0         22   11    3
components/specialty-identity.css:157  srgb --paper-cream 34% --augmerc-accent          #57d3e3  C32 M0 Y7 K0         39   32    7
components/specialty-identity.css:185  srgb --paper-cream 45% --cybersurgeon-accent     #cfd6d8  C12 M6 Y7 K0         25   12    6
components/specialty-identity.css:205  srgb --technosorcerer-accent 87% --paper-cream   #da672a  C0 M56 Y88 K3       147   88    3
components/specialty-identity.css:244  srgb --paper-cream 22% --wirephreak-accent       #7387bd  C44 M27 Y0 K2        73   44    2
components/specialty-identity.css:299  srgb --ink 30% --brand-magenta-deep              #5c154a  C33 M89 Y5 K41      168   89    5
components/specialty-identity.css:301  srgb --paper-cream 26% --brand-magenta-deep      #9a4f88  C24 M74 Y1 K7       106   74    1
components/specialty-identity.css:325  srgb --gutterdruid-mid 38% --gutterdruid-accent  #99af34  C25 M1 Y90 K6       122   90    1
components/specialty-identity.css:355  srgb --paper-cream 38% --etherlock-accent        #ffe661  C1 M2 Y64 K0         67   64    1
components/specialty-identity.css:384  srgb --paper-cream 34% --dualist-accent          #88bbc6  C33 M5 Y10 K1        49   33    1
components/specialty-identity.css:409  srgb --ink 26% --generalist-accent               #445059  C48 M31 Y21 K41     141   48   21
dc-component-defaults.css:387          oklch --ink-dark 18% --paper-cream               #d6d4d3  C10 M8 Y8 K0         26   10    8
dc-component-defaults.css:454          srgb --brand-yellow 30% --paper-aged             #e6d995  C6 M4 Y38 K0         48   38    4
```

## contrast

```
16.83:1  AAA      body text on paper
14.78:1  AAA      --ink-dark on paper
12.05:1  AAA      --ink on --paper-aged (field chip, code)
 9.77:1  AAA      --ink on the wall
12.05:1  AAA      --ink on --concrete-pale (pullquote, dm)
 7.69:1  AAA      --ink on --hud-blue-dim (alert, reference bar)
12.00:1  AAA      --ink on --brand-yellow
11.37:1  AAA      --ink on --fungi-glow (hit row)
11.80:1  AAA      --ink on --dc-tape-bg
 5.92:1  AA       white on magenta bar (90% over ink)
 5.20:1  AA       white on --brand-magenta
 5.20:1  AA       --brand-magenta on white (h1, large)
10.44:1  AAA      white on --brand-magenta-deep (chevron, crit, VAR chip, proxy band)
10.44:1  AAA      --brand-magenta-deep on white (default accent ink)
 7.47:1  AAA      --brand-magenta-deep on --concrete-pale (pullquote ink)
12.64:1  AAA      white on proxy band facet (30% ink)
 9.33:1  AAA      magenta 38% term on --wirephreak-dark
10.44:1  AAA      --proxy-dark on white (proxy chip)
10.44:1  AAA      white on --proxy-dark (sticker)
 7.24:1  AAA      white on --proxy-mid (tab)
 8.58:1  AAA      white on --brand-violet (chip, badge)
 8.58:1  AAA      --brand-violet on white (treasure ink)
 5.85:1  AA       --brand-violet on vibe sheet (accent ink)
 9.07:1  AAA      --ink on the darkest tint (treasure ornament)
 6.50:1  AA       --blood on the flaws/cult tint
 6.97:1  AA       --hud-blue-dark on the ideals/reference tint
10.60:1  AAA      white on lore bar (violet 72% over ink)
 5.84:1  AA       white on --crystal-amethyst (chip)
 5.60:1  AA       white on --signal-indigo (wirephreak band, chip)
 5.60:1  AA       --signal-indigo on white (classtag)
11.66:1  AAA      --wirephreak-mid on white (spec ink)
11.66:1  AAA      white on --wirephreak-mid (tab)
16.94:1  AAA      white on --wirephreak-dark
 8.64:1  AAA      white on --hud-blue-dark (AP chip, block title)
 8.64:1  AAA      --hud-blue-dark on white
 5.99:1  AA       white on --rust (chapter chip)
 4.67:1  AA       white on --crimson (card band default)
 4.24:1  AA-large --orange dot on white (classtag; non-text, needs 3:1)
 6.85:1  AA       --orange-deep on white (lede ink)
 6.85:1  AA       white on --orange-deep (mixed row)
 8.97:1  AAA      white on --blood (miss row)
10.39:1  AAA      white on --fungi-rot (fail row)
 9.96:1  AAA      white on --amber-dark
 4.97:1  AA       --fungi-glow on visit bg (accent ink)
 7.35:1  AAA      white on visit bg (body)
 6.43:1  AA       --brand-cyan on --ink-dark (dm accent)
 3.85:1  AA-large --ink-dust on the wall
 7.33:1  AAA      augmerc: on-band type on band
 7.33:1  AAA      augmerc: tier chip
 6.46:1  AA       augmerc: text ink on paper
 6.46:1  AA       augmerc: cream on --augmerc-mid (tab)
12.51:1  AAA      augmerc: cream on --augmerc-dark (chip)
 4.77:1  AA       technosorcerer: on-band type on band
12.87:1  AAA      technosorcerer: tier chip
 9.32:1  AAA      technosorcerer: text ink on paper
 9.32:1  AAA      technosorcerer: cream on --technosorcerer-mid (tab)
12.87:1  AAA      technosorcerer: cream on --technosorcerer-dark (chip)
 6.67:1  AA       technosorcerer: text ink on --paper-aged
 6.61:1  AA       streetwarden: on-band type on band
 6.61:1  AA       streetwarden: tier chip
10.39:1  AAA      streetwarden: text ink on paper
 5.44:1  AA       streetwarden: cream on --streetwarden-mid (tab)
10.39:1  AAA      streetwarden: cream on --streetwarden-dark (chip)
11.37:1  AAA      gutterdruid: on-band type on band
11.37:1  AAA      gutterdruid: tier chip
10.39:1  AAA      gutterdruid: text ink on paper
 6.98:1  AA       gutterdruid: cream on --gutterdruid-mid (tab)
10.39:1  AAA      gutterdruid: cream on --gutterdruid-dark (chip)
 7.44:1  AAA      gutterdruid: text ink on --paper-aged
 7.92:1  AAA      cybersurgeon: on-band type on band
 7.92:1  AAA      cybersurgeon: tier chip
11.90:1  AAA      cybersurgeon: text ink on paper
 6.30:1  AA       cybersurgeon: cream on --cybersurgeon-mid (tab)
11.90:1  AAA      cybersurgeon: cream on --cybersurgeon-dark (chip)
 5.60:1  AA       wirephreak: on-band type on band
 5.60:1  AA       wirephreak: tier chip
11.66:1  AAA      wirephreak: text ink on paper
11.66:1  AAA      wirephreak: cream on --wirephreak-mid (tab)
16.94:1  AAA      wirephreak: cream on --wirephreak-dark (chip)
10.44:1  AAA      proxy: on-band type on band
10.44:1  AAA      proxy: tier chip
10.44:1  AAA      proxy: text ink on paper
 7.24:1  AAA      proxy: cream on --proxy-mid (tab)
10.44:1  AAA      proxy: cream on --proxy-dark (chip)
12.00:1  AAA      etherlock: on-band type on band
12.00:1  AAA      etherlock: tier chip
11.71:1  AAA      etherlock: text ink on paper
 5.07:1  AA       etherlock: cream on --etherlock-mid (tab)
11.71:1  AAA      etherlock: cream on --etherlock-dark (chip)
 8.38:1  AAA      etherlock: text ink on --paper-aged
 5.09:1  AA       dualist: on-band type on band
 5.09:1  AA       dualist: tier chip
 6.46:1  AA       dualist: text ink on paper
 6.46:1  AA       dualist: cream on --dualist-mid (tab)
12.11:1  AAA      dualist: cream on --dualist-dark (chip)
 6.30:1  AA       generalist: on-band type on band
 6.30:1  AA       generalist: tier chip
 9.40:1  AAA      generalist: text ink on paper
 9.40:1  AAA      generalist: cream on --generalist-mid (tab)
14.56:1  AAA      generalist: cream on --generalist-dark (chip)
```

## dupes

```
dE  2.4  --augmerc-dark           #003a40  ~  --dualist-dark           #143a4a
dE  3.4  --ink-dark               #2f2622  ~  --generalist-dark        #212a32
dE  3.5  --cybersurgeon-dark      #303840  ~  --dualist-dark           #143a4a
dE  3.8  --orange-deep            #a03808  ~  --rust                   #b23a12
dE  4.1  --technosorcerer-dark    #4c290f  ~  --etherlock-dark         #46360c
dE  4.2  --paper-stain            #b0a89c  ~  --cybersurgeon-accent    #a8b4b8
dE  4.2  --bg                     #c8c5bf  ~  --surface-orange-tint    #d8cfb4
dE  4.4  --ink-smoke              #4d4339  ~  --ink-mid                #594f43
dE  4.4  --ink-mid                #594f43  ~  --ink-dust               #665b4e
dE  4.4  --deep-rust              #70200e  ~  --technosorcerer-mid     #7a3008
dE  4.5  --paper-cream            #ffffff  ~  --surface-tint-3         #f2f0ec
dE  4.6  --concrete-pale          #dcdad5  ~  --surface-orange-tint    #d8cfb4
dE  4.7  --augmerc-dark           #003a40  ~  --cybersurgeon-dark      #303840
dE  4.8  --ink                    #1e1d1c  ~  --ink-dark               #2f2622
dE  4.9  --amber-dark             #5c3c10  ~  --etherlock-dark         #46360c
dE  4.9  --ink-smoke              #4d4339  ~  --generalist-mid         #3a4854
dE  5.0  --hud-blue               #1f6f94  ~  --augmerc-mid            #006878
dE  5.2  --ink-smoke              #4d4339  ~  --amber-dark             #5c3c10
dE  5.3  --hud-blue-dark          #14516e  ~  --generalist-mid         #3a4854
dE  5.3  --ink                    #1e1d1c  ~  --generalist-dark        #212a32
dE  5.4  --ink-dust               #665b4e  ~  --crystal-slate          #52626f
dE  5.5  --blood                  #901a12  ~  --technosorcerer-mid     #7a3008
dE  5.6  --fungi-rot              #30461e  ~  --etherlock-dark         #46360c
dE  5.6  --augmerc-dark           #003a40  ~  --generalist-dark        #212a32
dE  5.7  --cybersurgeon-dark      #303840  ~  --generalist-dark        #212a32
dE  5.9  --cybersurgeon-dark      #303840  ~  --generalist-mid         #3a4854
dE  5.9  --dualist-dark           #143a4a  ~  --generalist-dark        #212a32
dE  5.9  --hud-blue-dim           #7ab8d0  ~  --cybersurgeon-accent    #a8b4b8
dE  5.9  --amber                  #7a5a20  ~  --etherlock-mid          #8a6a00
```

## converge

```

== purples: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==
  --brand-magenta        --proxy-mid              8.4 ->   8.5  (printed #ba3881 vs #952a6f)
  --proxy-mid            --brand-magenta-deep     9.3 ->   9.1  (printed #952a6f vs #721b52)
  --proxy-mid            --crystal-amethyst       9.6 ->   9.1  (printed #952a6f vs #7e5387)
  --crystal-amethyst     --brand-violet           9.5 ->   9.6  (printed #7e5387 vs #563f77)
  --crystal-amethyst     --signal-indigo          9.7 ->   8.3  (printed #7e5387 vs #4f6597)
  --brand-violet         --wirephreak-mid        11.1 ->   9.5  (printed #563f77 vs #22346a)

== warm reds: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==
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

== teals: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==
  --brand-cyan           --crystal-aqua          10.4 ->   9.3  (printed #51b7ce vs #4998a9)
  --brand-cyan           --hud-blue-dim           6.2 ->   3.8  (printed #51b7ce vs #7bb8d0)
  --hud-blue             --hud-blue-dark         10.2 ->   9.9  (printed #1d6f94 vs #11526f)
  --hud-blue             --augmerc-mid            5.0 ->   4.7  (printed #1d6f94 vs #046979)
  --hud-blue-dark        --augmerc-mid            7.0 ->   7.1  (printed #11526f vs #046979)

== greens: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==
  --fungi-glow           --brand-yellow           7.5 ->   8.6  (printed #c1ca53 vs #f6d745)
  --streetwarden-mid     --gutterdruid-mid        7.4 ->   6.6  (printed #377732 vs #4e6123)
```
