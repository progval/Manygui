from glob import glob
import sys, os

try:
    skip_tests = os.environ['ANYGUI_SKIP'].split()
except:
    skip_tests = []
skip_tests.sort()
if skip_tests:
    print 'skipping %d tests:'%len(skip_tests),
    for test in skip_tests:
        print test,
    print

run_tests = [test for test in glob('test_*.py') if test not in skip_tests]
run_tests.sort()
print 'running %d tests:'%len(run_tests),
for test in run_tests:
    print test,
print

for filename in run_tests:
    print "Running", filename
    execfile(filename, {})
