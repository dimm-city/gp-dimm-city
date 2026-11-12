# gp-dimm-city print colour audit — measurements

The output of `python3 scripts/measure-palette-crpc1.py <mode>` for each mode below (`--write`
regenerates the blocks; `--check`, which CI runs, fails when one differs from a fresh run). Every hex token in `styles/dc-palette.css` and `styles/dc-identity.css`,
and every `color-mix()` of two palette tokens in `styles/`, converted sRGB -> CMYK the way
the PDF/X build does it: a swatch of each colour through Ghostscript's pdfwrite with the
CGATS21_CRPC1 profile gutterpress ships as the output profile, at Ghostscript's default
intent (relative colorimetric with black-point compensation). The CMYK operands are read
back out of the PDF, so these are the build's figures to the digit.

- **printed**: the CMYK converted back to sRGB with LittleCMS at the same intent, so a colour
  inside the gamut round-trips to itself; **dE**: OKLab distance x100 between screen and
  print (> 6 is a visible shift, > 10 a different colour).
- **mixes**: **max** is the tint's strongest ink, **min** its weakest non-zero one (a
  1-2% dot does not hold on HP Indigo or inkjet).
- **contrast**: WCAG 2 contrast on the sRGB values.
- **dupes**: hex tokens closer than OKLab 6 (aliases are not listed: they are one colour).

Until 1.10.2-alpha.1 this file was LittleCMS at perceptual intent, which the build never
used: its figures ran under the build's by 10-30% TAC on the purples and by 15-20% on
the inks.

## tokens

```
token                    hex      CMYK (build)          TAC printed     dE    okL   okC  okH
--bg                     #c8c5bf  C18 M15 Y18 K2         53 #c9c6c0    0.3   0.82 0.009   85
--concrete-pale          #dcdad5  C12 M9 Y12 K0          33 #dddbd6    0.3   0.89 0.007   89
--paper-cream            #ffffff  C0 M0 Y0 K0             0 #ffffff    0.0   1.00 0.000   90
--paper-stain            #b0a89c  C23 M20 Y27 K11        81 #b0a99d    0.3   0.73 0.019   78
--ink                    #1e1d1c  C44 M38 Y37 K92       211 #1e1e1e    0.4   0.23 0.002   68
--ink-dark               #2f2622  C39 M38 Y38 K87       202 #302926    1.1   0.28 0.015   45
--ink-smoke              #4d4339  C32 M33 Y39 K71       175 #4e463d    1.0   0.39 0.021   67
--ink-mid                #594f43  C32 M32 Y40 K62       166 #5a5247    1.0   0.43 0.023   72
--ink-dust               #665b4e  C31 M31 Y41 K53       156 #675e51    0.9   0.48 0.025   72
--crimson                #e1261c  C0 M100 Y100 K6       206 #e33e39    3.1   0.59 0.221   29
--blood                  #901a12  C2 M92 Y65 K48        207 #952627    2.6   0.42 0.154   29
--orange                 #d4500a  C0 M71 Y100 K13       184 #d75a34    2.7   0.60 0.180   41
--orange-deep            #a03808  C1 M76 Y88 K39        204 #a54022    2.3   0.48 0.147   40
--rust                   #b23a12  C0 M80 Y100 K30       210 #b64223    1.9   0.52 0.163   37
--amber                  #7a5a20  C17 M33 Y75 K52       177 #7c5e2c    1.4   0.49 0.085   79
--deep-rust              #70200e  C11 M73 Y58 K65       207 #712821    2.2   0.37 0.116   34
--amber-dark             #5c3c10  C21 M40 Y62 K70       193 #5e4225    2.4   0.38 0.073   70
--brand-magenta          #cf217e  C2 M100 Y1 K12        115 #d53e86    3.9   0.57 0.216  355
--brand-magenta-deep     #690045  C24 M94 Y15 K56       189 #6c1546    2.5   0.34 0.144  349
--brand-cyan             #00bcd4  C67 M0 Y11 K0          78 #10bcd5    0.3   0.73 0.126  211
--brand-yellow           #ffd700  C0 M5 Y100 K1         106 #fddd29    1.4   0.89 0.182   95
--brand-violet           #662d87  C62 M100 Y0 K16       178 #693f85    4.2   0.42 0.149  311
--signal-indigo          #396cb7  C86 M54 Y0 K0         140 #3d6fb1    1.5   0.53 0.130  258
--hud-blue               #1f6f94  C78 M29 Y8 K24        139 #1d7095    0.3   0.51 0.094  233
--hud-blue-dark          #14516e  C74 M34 Y12 K46       166 #1c5470    1.2   0.41 0.077  234
--hud-blue-dim           #7ab8d0  C46 M9 Y8 K3           66 #7abad2    0.6   0.75 0.072  224
--surface-tint-3         #f2f0ec  C4 M4 Y5 K0            13 #f3f1ed    0.3   0.96 0.006   85
--surface-orange-tint    #d8cfb4  C13 M12 Y26 K1         52 #d9d1b5    0.5   0.85 0.038   92
--fungi-glow             #c8e040  C19 M0 Y95 K0         114 #ced741    2.4   0.86 0.179  118
--fungi-rot              #30461e  C44 M20 Y60 K73       197 #364a2b    2.2   0.37 0.069  133
--crystal-amethyst       #905aa5  C45 M80 Y0 K2         127 #945da2    1.3   0.56 0.126  316
--crystal-aqua           #4a98a8  C62 M13 Y18 K12       105 #4a99a9    0.3   0.64 0.080  213
--crystal-slate          #52626f  C50 M31 Y22 K42       145 #546370    0.4   0.49 0.029  243
--neon-orange            #ef713d  C0 M60 Y97 K2         159 #f0743f    0.7   0.69 0.169   42
--neon-orange-core       #fadac6  C2 M12 Y17 K0          31 #fadac6    0.0   0.91 0.045   54
--neon-orange-ring-1     #7b371f  C12 M62 Y64 K56       194 #7c3d2b    1.7   0.42 0.102   40
--neon-orange-ring-2     #4d3122  C28 M42 Y47 K76       193 #4e372c    2.0   0.34 0.048   49
--neon-cyan              #12bbd4  C67 M1 Y11 K0          79 #15bbd4    0.1   0.73 0.125  212
--neon-cyan-core         #c5e8f0  C18 M0 Y4 K0           22 #c7e8f1    0.3   0.91 0.038  213
--neon-cyan-ring-1       #096979  C74 M20 Y19 K38       151 #0d6a7a    0.4   0.48 0.082  213
--neon-cyan-ring-2       #173e43  C57 M28 Y30 K71       186 #234245    2.0   0.34 0.044  207
--neon-yellow            #fcdc2a  C0 M4 Y99 K1          104 #fce02b    1.0   0.89 0.177   98
--neon-yellow-core       #fcf4bd  C2 M0 Y27 K0           29 #faf5bd    0.4   0.96 0.071  101
--neon-yellow-ring-1     #8c6e1f  C13 M26 Y84 K42       165 #8e722b    1.3   0.55 0.101   87
--neon-yellow-ring-2     #473a1f  C29 M32 Y51 K78       190 #483d28    1.3   0.36 0.045   84
--neon-pink              #f14693  C0 M100 Y5 K1         106 #f24794    0.3   0.66 0.216  357
--neon-pink-core         #f8c8df  C2 M22 Y0 K0           24 #f7c8df    0.1   0.88 0.062  348
--neon-pink-ring-1       #9e2d65  C14 M96 Y13 K30       153 #9f3365    1.1   0.49 0.157  354
--neon-pink-ring-2       #6b1345  C24 M89 Y18 K56       187 #6d1d46    1.7   0.36 0.130  351
--neon-fungi             #ced741  C16 M0 Y93 K0         109 #d3d943    0.9   0.85 0.166  113
--neon-fungi-core        #f2f3cc  C5 M0 Y20 K0           25 #f3f4cc    0.3   0.95 0.051  109
--neon-fungi-ring-1      #51632d  C40 M16 Y71 K53       180 #546736    1.5   0.47 0.081  125
--neon-fungi-ring-2      #35492b  C44 M21 Y54 K70       189 #3a4c34    1.7   0.38 0.055  136
--neon-civic             #60b54e  C54 M0 Y98 K0         152 #6bb74f    1.3   0.70 0.163  140
--neon-civic-core        #d4e8cc  C15 M0 Y20 K0          35 #d5e8cc    0.1   0.91 0.043  137
--neon-civic-ring-1      #3c7c34  C57 M5 Y85 K35        182 #427f3d    1.5   0.53 0.125  142
--neon-chrome            #a8b4b9  C29 M16 Y16 K6         67 #a8b5ba    0.3   0.76 0.015  225
--neon-chrome-core       #e9ecee  C8 M4 Y4 K0            16 #e9edef    0.2   0.94 0.004  236
--neon-chrome-ring-1     #536370  C50 M31 Y22 K42       145 #546471    0.4   0.49 0.029  243
--neon-chrome-ring-2     #343b40  C45 M33 Y29 K74       181 #373d40    0.9   0.35 0.013  239
--neon-azure             #288fc9  C76 M26 Y0 K1         103 #2b92ca    0.9   0.62 0.126  239
--neon-azure-core        #bee3f5  C22 M2 Y0 K0           24 #bde3f6    0.2   0.90 0.046  229
--neon-azure-ring-1      #0e527a  C81 M40 Y7 K38        166 #17557b    1.1   0.42 0.092  241
--neon-azure-ring-2      #1b3046  C59 M42 Y22 K71       194 #263648    2.6   0.30 0.048  251
--neon-dead              #675d51  C31 M31 Y40 K52       154 #685f53    0.6   0.48 0.023   72
--neon-dead-core         #8a8078  C29 M28 Y32 K29       118 #8a8179    0.3   0.61 0.017   61
--streetwarden-accent    #4db840  C58 M0 Y100 K0        158 #61b54e    2.5   0.70 0.187  142
--cybersurgeon-accent    #a8b4b8  C28 M16 Y16 K6         66 #a9b5ba    0.4   0.76 0.015  220
--augmerc-dark           #003a40  C60 M28 Y30 K73       191 #183f43    2.6   0.32 0.054  206
--cybersurgeon-dark      #303840  C47 M35 Y28 K74       184 #343b40    1.3   0.34 0.018  248
--wirephreak-dark        #181b45  C66 M58 Y16 K69       209 #222647    4.0   0.25 0.078  276
--technosorcerer-dark    #4c290f  C25 M45 Y51 K79       200 #4e3123    2.9   0.32 0.065   54
--etherlock-dark         #46360c  C28 M32 Y57 K80       197 #47391d    1.8   0.34 0.061   87
--generalist-dark        #212a32  C49 M38 Y31 K82       200 #282e34    1.9   0.28 0.019  245
--augmerc-mid            #006878  C75 M20 Y19 K38       152 #096a7a    0.7   0.48 0.083  213
--proxy-mid              #9c0f63  C12 M100 Y8 K32       152 #9e2d65    3.7   0.46 0.182  352
--streetwarden-mid       #347828  C57 M3 Y92 K38        190 #3d7c34    1.9   0.51 0.134  141
--gutterdruid-mid        #4d6020  C39 M14 Y76 K56       185 #51632d    1.7   0.46 0.092  124
--wirephreak-mid         #093c81  C100 M73 Y0 K27       200 #18427f    2.2   0.37 0.127  258
--technosorcerer-mid     #7a3008  C10 M66 Y71 K59       206 #7b371f    2.0   0.41 0.114   44
--etherlock-mid          #8a6a00  C11 M25 Y91 K45       172 #8c6e1f    1.6   0.54 0.111   88
--generalist-mid         #3a4854  C51 M34 Y24 K61       170 #3d4a55    0.8   0.39 0.027  244
aliases: --paper-form -> --paper-cream, --paper-zine -> --concrete-pale, --paper-light -> --paper-cream, --paper-aged -> --concrete-pale, --hud-blue-bright -> --brand-cyan, --hud-magenta -> --brand-magenta, --hud-panel -> --concrete-pale, --border-hairline -> --ink, --tint-magenta-rose -> --brand-magenta, --tint-hud-teal -> --hud-blue, --neon-civic-ring-2 -> --neon-fungi-ring-2, --augmerc-accent -> --brand-cyan, --proxy-accent -> --brand-magenta, --gutterdruid-accent -> --fungi-glow, --wirephreak-accent -> --signal-indigo, --technosorcerer-accent -> --orange, --etherlock-accent -> --brand-yellow, --dualist-accent -> --crystal-aqua, --generalist-accent -> --crystal-slate, --proxy-dark -> --brand-magenta-deep, --streetwarden-dark -> --fungi-rot, --gutterdruid-dark -> --fungi-rot, --dualist-dark -> --augmerc-dark, --cybersurgeon-mid -> --crystal-slate, --dualist-mid -> --augmerc-mid
```

## mixes

```
where                                  mix                                              hex      CMYK                TAC  max  min
components/data.css:816                srgb --brand-magenta 38% --paper-cream           #edabce  C5 M34 Y1 K0         40   34    1
components/enclosures.css:121          srgb --crimson 40% --paper-cream                 #f3a8a4  C2 M35 Y24 K1        62   35    1
components/enclosures.css:433          srgb --brand-violet 72% --ink                    #522969  C58 M92 Y2 K38      190   92    2
components/specialty-identity.css:157  srgb --paper-cream 34% --augmerc-accent          #57d3e3  C50 M0 Y9 K0         59   50    9
components/specialty-identity.css:186  srgb --paper-cream 45% --cybersurgeon-accent     #cfd6d8  C17 M9 Y10 K0        36   17    9
components/specialty-identity.css:206  srgb --technosorcerer-accent 87% --paper-cream   #da672a  C0 M60 Y100 K11     171  100   11
components/specialty-identity.css:252  srgb --paper-cream 22% --wirephreak-accent       #658cc7  C59 M34 Y0 K3        96   59    3
components/specialty-identity.css:309  srgb --ink 30% --brand-magenta-deep              #520939  C32 M74 Y22 K68     196   74   22
components/specialty-identity.css:311  srgb --paper-cream 26% --brand-magenta-deep      #904275  C27 M80 Y9 K27      143   80    9
components/specialty-identity.css:336  srgb --gutterdruid-mid 38% --gutterdruid-accent  #99af34  C28 M0 Y99 K13      140   99   13
components/specialty-identity.css:367  srgb --paper-cream 38% --etherlock-accent        #ffe661  C1 M2 Y71 K0         74   71    1
components/specialty-identity.css:397  srgb --paper-cream 34% --dualist-accent          #88bbc6  C41 M9 Y14 K4        68   41    4
components/specialty-identity.css:423  srgb --ink 26% --generalist-accent               #445059  C48 M32 Y25 K57     162   57   25
dc-component-defaults.css:501          srgb --brand-yellow 30% --paper-aged             #e6d995  C9 M7 Y43 K1         60   43    1
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
 5.78:1  AA       white on magenta bar (90% over ink)
 5.03:1  AA       white on --brand-magenta
 5.03:1  AA       --brand-magenta on white (h1, large)
12.45:1  AAA      white on --brand-magenta-deep (chevron, crit, VAR chip, proxy band)
12.45:1  AAA      --brand-magenta-deep on white (default accent ink)
 8.91:1  AAA      --brand-magenta-deep on --concrete-pale (pullquote ink)
14.41:1  AAA      white on proxy band facet (30% ink)
 8.83:1  AAA      magenta 38% term on --wirephreak-dark
12.45:1  AAA      --proxy-dark on white (proxy chip)
12.45:1  AAA      white on --proxy-dark (sticker)
 7.89:1  AAA      white on --proxy-mid (tab)
 9.17:1  AAA      white on --brand-violet (chip, badge)
 9.17:1  AAA      --brand-violet on white (treasure ink)
 6.16:1  AA       --brand-violet on vibe sheet (accent ink)
 9.59:1  AAA      --ink on the darkest tint (treasure ornament)
 6.50:1  AA       --blood on the flaws/cult tint
 6.97:1  AA       --hud-blue-dark on the ideals/reference tint
11.17:1  AAA      white on lore bar (violet 72% over ink)
 5.01:1  AA       white on --crystal-amethyst (chip)
 5.25:1  AA       white on --signal-indigo (wirephreak band, chip)
 5.25:1  AA       --signal-indigo on white (classtag)
10.63:1  AAA      --wirephreak-mid on white (spec ink)
10.63:1  AAA      white on --wirephreak-mid (tab)
16.39:1  AAA      white on --wirephreak-dark
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
 5.25:1  AA       wirephreak: on-band type on band
 5.25:1  AA       wirephreak: tier chip
10.63:1  AAA      wirephreak: text ink on paper
10.63:1  AAA      wirephreak: cream on --wirephreak-mid (tab)
16.39:1  AAA      wirephreak: cream on --wirephreak-dark (chip)
12.45:1  AAA      proxy: on-band type on band
12.45:1  AAA      proxy: tier chip
12.45:1  AAA      proxy: text ink on paper
 7.89:1  AAA      proxy: cream on --proxy-mid (tab)
12.45:1  AAA      proxy: cream on --proxy-dark (chip)
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
12.51:1  AAA      dualist: cream on --dualist-dark (chip)
 6.30:1  AA       generalist: on-band type on band
 6.30:1  AA       generalist: tier chip
 9.40:1  AAA      generalist: text ink on paper
 9.40:1  AAA      generalist: cream on --generalist-mid (tab)
14.56:1  AAA      generalist: cream on --generalist-dark (chip)
```

## dupes

```
dE  0.1  --neon-chrome            #a8b4b9  ~  --cybersurgeon-accent    #a8b4b8
dE  0.3  --brand-cyan             #00bcd4  ~  --neon-cyan              #12bbd4
dE  0.4  --crystal-slate          #52626f  ~  --neon-chrome-ring-1     #536370
dE  0.4  --neon-cyan-ring-1       #096979  ~  --augmerc-mid            #006878
dE  0.7  --ink-dust               #665b4e  ~  --neon-dead              #675d51
dE  1.3  --neon-chrome-ring-2     #343b40  ~  --cybersurgeon-dark      #303840
dE  1.3  --brand-yellow           #ffd700  ~  --neon-yellow            #fcdc2a
dE  1.6  --neon-yellow-ring-1     #8c6e1f  ~  --etherlock-mid          #8a6a00
dE  1.7  --neon-fungi-ring-1      #51632d  ~  --gutterdruid-mid        #4d6020
dE  1.7  --surface-tint-3         #f2f0ec  ~  --neon-chrome-core       #e9ecee
dE  1.8  --neon-civic-ring-1      #3c7c34  ~  --streetwarden-mid       #347828
dE  1.9  --neon-cyan-core         #c5e8f0  ~  --neon-azure-core        #bee3f5
dE  2.0  --hud-blue-dark          #14516e  ~  --neon-azure-ring-1      #0e527a
dE  2.0  --fungi-rot              #30461e  ~  --neon-fungi-ring-2      #35492b
dE  2.0  --neon-orange-ring-1     #7b371f  ~  --technosorcerer-mid     #7a3008
dE  2.1  --neon-yellow-ring-2     #473a1f  ~  --etherlock-dark         #46360c
dE  2.2  --brand-magenta-deep     #690045  ~  --neon-pink-ring-2       #6b1345
dE  2.2  --neon-cyan-ring-2       #173e43  ~  --augmerc-dark           #003a40
dE  2.3  --neon-yellow-core       #fcf4bd  ~  --neon-fungi-core        #f2f3cc
dE  2.4  --fungi-glow             #c8e040  ~  --neon-fungi             #ced741
dE  2.4  --neon-civic             #60b54e  ~  --streetwarden-accent    #4db840
dE  2.8  --neon-orange-ring-2     #4d3122  ~  --technosorcerer-dark    #4c290f
dE  3.1  --neon-orange-ring-2     #4d3122  ~  --neon-yellow-ring-2     #473a1f
dE  3.3  --neon-cyan-ring-2       #173e43  ~  --cybersurgeon-dark      #303840
dE  3.4  --ink-dark               #2f2622  ~  --generalist-dark        #212a32
dE  3.5  --neon-cyan-ring-2       #173e43  ~  --neon-chrome-ring-2     #343b40
dE  3.7  --neon-pink-ring-1       #9e2d65  ~  --proxy-mid              #9c0f63
dE  3.7  --neon-azure-ring-2      #1b3046  ~  --generalist-dark        #212a32
dE  3.8  --neon-orange-ring-2     #4d3122  ~  --etherlock-dark         #46360c
dE  3.8  --orange-deep            #a03808  ~  --rust                   #b23a12
dE  4.1  --technosorcerer-dark    #4c290f  ~  --etherlock-dark         #46360c
dE  4.2  --paper-stain            #b0a89c  ~  --cybersurgeon-accent    #a8b4b8
dE  4.2  --bg                     #c8c5bf  ~  --surface-orange-tint    #d8cfb4
dE  4.2  --neon-azure-ring-2      #1b3046  ~  --augmerc-dark           #003a40
dE  4.3  --amber-dark             #5c3c10  ~  --neon-yellow-ring-2     #473a1f
dE  4.3  --paper-stain            #b0a89c  ~  --neon-chrome            #a8b4b9
dE  4.3  --ink-smoke              #4d4339  ~  --neon-yellow-ring-2     #473a1f
dE  4.4  --concrete-pale          #dcdad5  ~  --neon-civic-core        #d4e8cc
dE  4.4  --ink-smoke              #4d4339  ~  --ink-mid                #594f43
dE  4.4  --ink-mid                #594f43  ~  --ink-dust               #665b4e
dE  4.4  --deep-rust              #70200e  ~  --technosorcerer-mid     #7a3008
dE  4.4  --concrete-pale          #dcdad5  ~  --neon-orange-core       #fadac6
dE  4.5  --paper-cream            #ffffff  ~  --surface-tint-3         #f2f0ec
dE  4.6  --neon-azure-ring-2      #1b3046  ~  --cybersurgeon-dark      #303840
dE  4.6  --concrete-pale          #dcdad5  ~  --surface-orange-tint    #d8cfb4
dE  4.6  --surface-tint-3         #f2f0ec  ~  --neon-fungi-core        #f2f3cc
dE  4.7  --hud-blue               #1f6f94  ~  --neon-cyan-ring-1       #096979
dE  4.7  --augmerc-dark           #003a40  ~  --cybersurgeon-dark      #303840
dE  4.7  --concrete-pale          #dcdad5  ~  --neon-cyan-core         #c5e8f0
dE  4.8  --neon-cyan-core         #c5e8f0  ~  --neon-chrome-core       #e9ecee
dE  4.8  --ink                    #1e1d1c  ~  --ink-dark               #2f2622
dE  4.8  --neon-yellow-ring-2     #473a1f  ~  --technosorcerer-dark    #4c290f
dE  4.9  --amber-dark             #5c3c10  ~  --etherlock-dark         #46360c
dE  4.9  --neon-chrome-ring-2     #343b40  ~  --generalist-mid         #3a4854
dE  4.9  --ink-smoke              #4d4339  ~  --generalist-mid         #3a4854
dE  5.0  --hud-blue               #1f6f94  ~  --augmerc-mid            #006878
dE  5.0  --neon-cyan-ring-2       #173e43  ~  --neon-azure-ring-2      #1b3046
dE  5.0  --neon-cyan-core         #c5e8f0  ~  --neon-civic-core        #d4e8cc
dE  5.0  --ink-mid                #594f43  ~  --neon-dead              #675d51
dE  5.1  --neon-yellow-ring-2     #473a1f  ~  --neon-fungi-ring-2      #35492b
dE  5.1  --neon-fungi-core        #f2f3cc  ~  --neon-civic-core        #d4e8cc
dE  5.1  --crystal-slate          #52626f  ~  --neon-dead              #675d51
dE  5.2  --neon-chrome-ring-1     #536370  ~  --neon-dead              #675d51
dE  5.2  --ink-smoke              #4d4339  ~  --amber-dark             #5c3c10
dE  5.2  --concrete-pale          #dcdad5  ~  --neon-azure-core        #bee3f5
dE  5.2  --ink-smoke              #4d4339  ~  --neon-fungi-ring-2      #35492b
dE  5.2  --fungi-rot              #30461e  ~  --neon-yellow-ring-2     #473a1f
dE  5.3  --hud-blue-dark          #14516e  ~  --generalist-mid         #3a4854
dE  5.3  --neon-chrome-ring-2     #343b40  ~  --augmerc-dark           #003a40
dE  5.3  --ink                    #1e1d1c  ~  --generalist-dark        #212a32
dE  5.4  --amber-dark             #5c3c10  ~  --neon-orange-ring-2     #4d3122
dE  5.4  --concrete-pale          #dcdad5  ~  --neon-chrome-core       #e9ecee
dE  5.4  --ink-dust               #665b4e  ~  --crystal-slate          #52626f
dE  5.4  --ink-smoke              #4d4339  ~  --neon-chrome-ring-2     #343b40
dE  5.5  --blood                  #901a12  ~  --technosorcerer-mid     #7a3008
dE  5.5  --ink-dust               #665b4e  ~  --neon-chrome-ring-1     #536370
dE  5.5  --neon-civic-core        #d4e8cc  ~  --neon-chrome-core       #e9ecee
dE  5.5  --neon-fungi-core        #f2f3cc  ~  --neon-chrome-core       #e9ecee
dE  5.5  --ink-smoke              #4d4339  ~  --neon-orange-ring-2     #4d3122
dE  5.6  --fungi-rot              #30461e  ~  --etherlock-dark         #46360c
dE  5.6  --augmerc-dark           #003a40  ~  --generalist-dark        #212a32
dE  5.7  --cybersurgeon-dark      #303840  ~  --generalist-dark        #212a32
dE  5.7  --blood                  #901a12  ~  --neon-orange-ring-1     #7b371f
dE  5.7  --deep-rust              #70200e  ~  --neon-orange-ring-1     #7b371f
dE  5.8  --neon-chrome-ring-2     #343b40  ~  --neon-azure-ring-2      #1b3046
dE  5.8  --neon-yellow-ring-2     #473a1f  ~  --neon-chrome-ring-2     #343b40
dE  5.8  --neon-orange-core       #fadac6  ~  --neon-civic-core        #d4e8cc
dE  5.8  --neon-orange-core       #fadac6  ~  --neon-chrome-core       #e9ecee
dE  5.9  --hud-blue-dim           #7ab8d0  ~  --neon-chrome            #a8b4b9
dE  5.9  --cybersurgeon-dark      #303840  ~  --generalist-mid         #3a4854
dE  5.9  --paper-cream            #ffffff  ~  --neon-chrome-core       #e9ecee
dE  5.9  --crystal-slate          #52626f  ~  --neon-cyan-ring-1       #096979
dE  5.9  --hud-blue-dim           #7ab8d0  ~  --cybersurgeon-accent    #a8b4b8
dE  5.9  --amber                  #7a5a20  ~  --etherlock-mid          #8a6a00
dE  6.0  --neon-cyan-ring-1       #096979  ~  --neon-chrome-ring-1     #536370
```

## converge

```
== purples: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==

== warm reds: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==
  --crimson              --orange                 6.1 ->   5.1  (printed #e33e39 vs #d75a34)
  --crimson              --rust                   9.2 ->   9.1  (printed #e33e39 vs #b64223)
  --orange               --rust                   8.5 ->   8.6  (printed #d75a34 vs #b64223)
  --rust                 --orange-deep            3.8 ->   3.5  (printed #b64223 vs #a54022)
  --rust                 --blood                  9.6 ->   9.4  (printed #b64223 vs #952627)
  --orange-deep          --blood                  6.7 ->   6.6  (printed #a54022 vs #952627)
  --orange-deep          --technosorcerer-mid     8.4 ->   9.1  (printed #a54022 vs #7b371f)
  --blood                --deep-rust              6.8 ->   7.6  (printed #952627 vs #712821)
  --blood                --technosorcerer-mid     5.5 ->   6.0  (printed #952627 vs #7b371f)
  --deep-rust            --technosorcerer-mid     4.4 ->   4.4  (printed #712821 vs #7b371f)

== teals: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==
  --brand-cyan           --hud-blue-dim           6.2 ->   6.0  (printed #10bcd5 vs #7abad2)
  --hud-blue             --hud-blue-dark         10.2 ->   9.4  (printed #1d7095 vs #1c5470)
  --hud-blue             --augmerc-mid            5.0 ->   4.6  (printed #1d7095 vs #096a7a)
  --hud-blue-dark        --augmerc-mid            7.0 ->   6.7  (printed #1c5470 vs #096a7a)

== greens: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==
  --fungi-glow           --brand-yellow           7.5 ->   6.9  (printed #ced741 vs #fddd29)
  --streetwarden-mid     --gutterdruid-mid        7.4 ->   7.6  (printed #3d7c34 vs #51632d)
```
