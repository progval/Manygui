from distutils.core import setup, Command
import os

class uninstall(Command):
    description = "Remove all installed files"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('build')
        build = self.get_finalized_command('build')
        install = self.get_finalized_command('install')
        self.announce("removing files")
        for n in 'platlib', 'purelib', 'headers', 'scripts', 'data':
            dstdir = getattr(install, 'install_' + n)
            try:
                srcdir = getattr(build, 'build_' + n)
            except AttributeError:
                pass
            else:
                self._removefiles(dstdir, srcdir)

    def _removefiles(self, dstdir, srcdir):
        # Remove all files in dstdir which are present in srcdir
        assert dstdir != srcdir
        if not os.path.isdir(srcdir):
            return
        for n in os.listdir(srcdir):
            name = os.path.join(dstdir, n)
            if os.path.isfile(name):
                self.announce("removing '%s'" % name)
                if not self.dry_run:
                    try:
                        os.remove(name)
                    except OSError, details:
                        self.warn("Could not remove file: %s" % details)
                    if os.path.splitext(name)[1] == '.py':
                        # Try to remove .pyc and -pyo files also
                        try:
                            os.remove(name + 'c')
                        except OSError:
                            pass
                        try:
                            os.remove(name + 'o')
                        except OSError:
                            pass
            elif os.path.isdir(name):
                self._removefiles(name, os.path.join(srcdir, n))
                if not self.dry_run:
                    try:
                        os.rmdir(name)
                    except OSError, details:
                        self.warn("Are there additional user files?\n"\
                              "  Could not remove directory: %s" % details)
            else:
                self.announce("skipping removal of '%s' (does not exist)" %\
                              name)


setup (name               = 'anygui',
       version            = open('VERSION.txt').read().strip(),
       maintainer         = 'Magnus Lie Hetland',
       maintainer_email   = 'magnus@hetland.org',
       description        = 'Generic GUI Package for Python',
       long_description   = 'Generic GUI Package for Python',
       license            = 'MIT License',
       url                = 'http://anygui.sf.net',
       platforms          = ['Any'],
       cmdclass           = {'uninstall': uninstall},
       package_dir        = {'': 'lib'},
       packages           = ['anygui', 'anygui.backends',
                             'anygui.backends.txtutils'])
