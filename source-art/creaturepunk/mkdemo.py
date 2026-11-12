import base64,sys
s=open('demo.template.html').read()
s=s.replace('__WOFF2__',base64.b64encode(open('../../fonts/creaturepunk/Creaturepunk.woff2','rb').read()).decode())
s=s.replace('__SRC__',base64.b64encode(open('creaturepunk-logo.png','rb').read()).decode())
open(sys.argv[1],'w').write(s)
