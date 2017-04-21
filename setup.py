#!/usr/bin/env python
try:
    from sugar.activity import bundlebuilder
    bundlebuilder.start("x2o")
except ImportError:
    import os
    os.system("find ./ | sed 's,^./,x2o.activity/,g' > MANIFEST")
    os.chdir('..')
    os.system('zip -r x2o.xo x2o.activity')
    os.system('mv x2o.xo ./x2o.activity')
    os.chdir('x2o.activity')

