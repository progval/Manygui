''' Replace contents of a file between <date> and </date>
    with the current date. Assumes that both tags are on
    the same line.
'''

import fileinput, re, time

endings = ['st', 'nd', 'rd'] + 17 * ['th'] \
        + ['st', 'nd', 'rd'] +  7 * ['th'] \
        + ['st']

for line in fileinput.input():
    format = '<date>%B %%i%%s, %Y</date>'
    datestring = time.strftime(format)
    day = time.localtime()[2]
    ending = endings[day-1]
    datestring %= (day, ending)
    pattern = '<date>.*?</date>'
    print re.sub(pattern, datestring, line),
