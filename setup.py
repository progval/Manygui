from distutils.core import setup

setup (name               = 'anygui',
       version            = open('VERSION').read().strip(),
       maintainer         = 'Magnus Lie Hetland',
       maintainer_email   = 'magnus@hetland.org',
       description        = 'Generic GUI Package for Python',
       long_description   = 'Generic GUI Package for Python',
       license            = 'MIT License',
       url                = 'http://anygui.sf.net',
       platforms          = ['Any'],
       package_dir        = {'': 'lib'},
       packages           = ['anygui', 'anygui.backends'])
