from glob import glob

for filename in glob('test_*.py'):
    execfile(filename, {})
