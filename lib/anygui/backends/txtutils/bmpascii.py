# A foolish dream: automate the process of producing ASCII
# art from arbitrary monochrome bitmaps.
#
# Idea: assume each character corresponds to a 4x6-pixel
# area. Take 4x6 chunks of the input bitmap, and find the
# character whose Gray code, when converted to normal binary
# representation, is numerically closest to that of the
# bitmap block's. The hope is that if we pick a character
# that's close in this manner, it will have the minimal
# number of bit-inversions difference from the picture
# fragment. It's not ideal, but it beats doing a bit-
# by-bit comparison of each character.

import sys
from graycode import *

def flatten(seq):
    '''Flatten a sequence. If seq is not a sequence, return [seq].
    If seq is empty, return [].'''
    if type(seq) == type(""):
        return [seq]
    try:
        if len(seq) > 0:
            seq[0]
    except:
        return [seq]
    result = []
    for item in seq:
        result += flatten(item)
    return result

char2grayStr = { ' ':\
                 "0000"
                 "0000"
                 "0000"
                 "0000"
                 "0000"
                 "0000",
                 'A':\
                 "0110"
                 "1001"
                 "1001"
                 "1111"
                 "1001"
                 "1001",
                 'B':\
                 "1110"
                 "1001"
                 "1010"
                 "1111"
                 "1001"
                 "1110",
                 'C':\
                 "0110"
                 "1001"
                 "1000"
                 "1000"
                 "1001"
                 "0110",
                 'D':\
                 "1110"
                 "1001"
                 "1001"
                 "1001"
                 "1001"
                 "1110",
                 'E':\
                 "1111"
                 "1000"
                 "1110"
                 "1000"
                 "1000"
                 "1111",
                 'F':\
                 "1111"
                 "1000"
                 "1110"
                 "1000"
                 "1000"
                 "1000",
                 'G':\
                 "0110"
                 "1001"
                 "1000"
                 "1011"
                 "1001"
                 "0110",
                 'H':\
                 "1001"
                 "1001"
                 "1111"
                 "1001"
                 "1001"
                 "1001",
                 'I':\
                 "0111"
                 "0010"
                 "0010"
                 "0010"
                 "0010"
                 "0111",
                 'J':\
                 "0001"
                 "0001"
                 "0001"
                 "0001"
                 "1001"
                 "0110",
                 'K':\
                 "1001"
                 "1010"
                 "1100"
                 "1100"
                 "1010"
                 "1001",
                 'L':\
                 "1000"
                 "1000"
                 "1000"
                 "1000"
                 "1000"
                 "1111",
                 'M':\
                 "1011"
                 "1111"
                 "1111"
                 "1001"
                 "1001"
                 "1001",
                 'N':\
                 "1001"
                 "1101"
                 "1101"
                 "1011"
                 "1011"
                 "1001",
                 'O':\
                 "0110"
                 "1001"
                 "1001"
                 "1001"
                 "1001"
                 "0110",
                 'P':\
                 "0110"
                 "1001"
                 "1001"
                 "1110"
                 "1000"
                 "1000",
                 'Q':\
                 "0110"
                 "1001"
                 "1001"
                 "1001"
                 "1011"
                 "0111",
                 'R':\
                 "1110"
                 "1001"
                 "1110"
                 "1100"
                 "1010"
                 "1001",
                 'S':\
                 "0110"
                 "1001"
                 "1100"
                 "0010"
                 "1001"
                 "0110",
                 'T':\
                 "1111"
                 "0010"
                 "0010"
                 "0010"
                 "0010"
                 "0010",
                 'U':\
                 "1001"
                 "1001"
                 "1001"
                 "1001"
                 "1001"
                 "0110",
                 'V':\
                 "1001"
                 "1001"
                 "1001"
                 "0110"
                 "0110"
                 "0110",
                 'W':\
                 "1001"
                 "1001"
                 "1001"
                 "1001"
                 "0110"
                 "0110",
                 'X':\
                 "1001"
                 "1001"
                 "0110"
                 "0110"
                 "1001"
                 "1001",
                 'Y':\
                 "1001"
                 "0110"
                 "0010"
                 "0010"
                 "0010"
                 "0010",
                 'Z':\
                 "1111"
                 "0010"
                 "0100"
                 "0100"
                 "1000"
                 "1111",
                 '\\':\
                 ["1000"
                  "1000"
                  "0100"
                  "0010"
                  "0001"
                  "0001",
                  "1000"
                  "0100"
                  "0010"
                  "0010"
                  "0001"
                  "0000",
                  "1000"
                  "1100"
                  "0110"
                  "0011"
                  "0001"
                  "0000",
                  "0100"
                  "0010"
                  "0001"
                  "0000"
                  "0000"
                  "0000",
                  "0000"
                  "0000"
                  "0000"
                  "1000"
                  "0100"
                  "0010",
                  "1000"
                  "0100"
                  "0010"
                  "0001"
                  "0000"
                  "0000",
                  "0000"
                  "1000"
                  "1000"
                  "0100"
                  "0010"
                  "0001",
                  "1100"
                  "0110"
                  "0011"
                  "0001"
                  "0000"
                  "0000",
                  ],
                 '/':\
                 ["0001"
                  "0001"
                  "0010"
                  "0100"
                  "1000"
                  "1000",
                  "0000"
                  "0001"
                  "0010"
                  "0010"
                  "0100"
                  "1000",
                  "0000"
                  "0000"
                  "0001"
                  "0010"
                  "0100"
                  "1000",
                  "0001"
                  "0010"
                  "0010"
                  "0100"
                  "1000"
                  "0000",
                  "0001"
                  "0010"
                  "0100"
                  "1000"
                  "0000"
                  "0000",
                  "0001"
                  "0011"
                  "0110"
                  "1100"
                  "1000"
                  "0000",
                  "0010"
                  "0100"
                  "1000"
                  "0000"
                  "0000"
                  "0000",
                  "0000"
                  "0000"
                  "0000"
                  "0001"
                  "0010"
                  "0100",
                  ],
                 '|':\
                 ["0100"
                  "0100"
                  "0100"
                  "0100"
                  "0100"
                  "0100",
                  "1000"
                  "1000"
                  "1000"
                  "1000"
                  "1000"
                  "1000",
                  "0010"
                  "0010"
                  "0010"
                  "0010"
                  "0010"
                  "0010",
                  "0001"
                  "0001"
                  "0001"
                  "0001"
                  "0001"
                  "0001",
                  ],
                 '-':\
                 ["1111"
                  "0000"
                  "0000"
                  "0000"
                  "0000"
                  "0000",
                  "0000"
                  "1111"
                  "0000"
                  "0000"
                  "0000"
                  "0000",
                  "0000"
                  "0000"
                  "1111"
                  "0000"
                  "0000"
                  "0000",
                  "0000"
                  "0000"
                  "0000"
                  "1111"
                  "0000"
                  "0000",
                  "0000"
                  "0000"
                  "0000"
                  "0000"
                  "1111"
                  "0000",
                  "0000"
                  "0000"
                  "0000"
                  "0000"
                  "0000"
                  "1111",
                  ],
                 '*':\
                 "0110"
                 "1111"
                 "0110"
                 "0110"
                 "1111"
                 "0110",
                 'a':\
                 "0000"
                 "0000"
                 "0110"
                 "1001"
                 "1001"
                 "0111",
                 'b':\
                 "1000"
                 "1000"
                 "1000"
                 "1110"
                 "1001"
                 "1110",
                 'c':\
                 "0000"
                 "0000"
                 "0000"
                 "0111"
                 "1000"
                 "0111",
                 'd':\
                 "0001"
                 "0001"
                 "0001"
                 "0111"
                 "1001"
                 "0111",
                 'e':\
                 "0000"
                 "0000"
                 "0110"
                 "1111"
                 "1000"
                 "0110",
                 'f':\
                 "0110"
                 "1001"
                 "1000"
                 "1110"
                 "1000"
                 "1000",
                 'g':\
                 "0000"
                 "0110"
                 "1001"
                 "0111"
                 "0001"
                 "0110",
                 'h':\
                 "1000"
                 "1000"
                 "1000"
                 "1110"
                 "1001"
                 "1001",
                 'i':\
                 "0000"
                 "0100"
                 "0000"
                 "0100"
                 "0100"
                 "0100",
                 'j':\
                 "0010"
                 "0000"
                 "0010"
                 "0010"
                 "1010"
                 "0100",
                 'k':\
                 "1000"
                 "1000"
                 "1010"
                 "1100"
                 "1010"
                 "1001",
                 'l':\
                 "0100"
                 "0100"
                 "0100"
                 "0100"
                 "0100"
                 "0100",
                 'm':\
                 "0000"
                 "0000"
                 "0000"
                 "0110"
                 "1111"
                 "1001",
                 'n':\
                 "0000"
                 "0000"
                 "0000"
                 "1100"
                 "1010"
                 "1010",
                 'o':\
                 "0000"
                 "0000"
                 "0110"
                 "1001"
                 "1001"
                 "0110",
                 'p':\
                 "0110"
                 "1001"
                 "1110"
                 "1000"
                 "1000"
                 "1000",
                 'q':\
                 "0110"
                 "1001"
                 "0111"
                 "0001"
                 "0001"
                 "0001",
                 'r':\
                 "0000"
                 "0000"
                 "0000"
                 "1110"
                 "1000"
                 "1000",
                 's':\
                 "0000"
                 "0000"
                 "0111"
                 "1000"
                 "0111"
                 "1110",
                 't':\
                 "0100"
                 "0100"
                 "1110"
                 "0100"
                 "0101"
                 "0010",
                 'u':\
                 "0000"
                 "0000"
                 "0000"
                 "1010"
                 "1010"
                 "1110",
                 'v':\
                 "0000"
                 "0000"
                 "0000"
                 "1010"
                 "1010"
                 "0100",
                 'w':\
                 "0000"
                 "0000"
                 "0000"
                 "1001"
                 "1111"
                 "0110",
                 'x':\
                 "0000"
                 "0000"
                 "1001"
                 "0110"
                 "0110"
                 "1001",
                 'y':\
                 "0101"
                 "0101"
                 "0011"
                 "0001"
                 "1001"
                 "0110",
                 'z':\
                 "0000"
                 "0000"
                 "1111"
                 "0010"
                 "0100"
                 "1111",
                 '`':\
                 "0100"
                 "0100"
                 "0000"
                 "0000"
                 "0000"
                 "0000",
                 '~':\
                 "0000"
                 "0000"
                 "0101"
                 "1010"
                 "0000"
                 "0000",
                 '1':\
                 "0010"
                 "0110"
                 "0010"
                 "0010"
                 "0010"
                 "0111",
                 '2':\
                 "0110"
                 "1001"
                 "0001"
                 "0010"
                 "0100"
                 "1111",
                 '3':\
                 "1111"
                 "0010"
                 "0110"
                 "0001"
                 "1001"
                 "0110",
                 '4':\
                 "0001"
                 "0011"
                 "0101"
                 "1111"
                 "0001"
                 "0001",
                 '5':\
                 "1111"
                 "1000"
                 "1110"
                 "0001"
                 "1001"
                 "0110",
                 '6':\
                 "0110"
                 "1001"
                 "1000"
                 "1110"
                 "1001"
                 "0110",
                 '7':\
                 "1111"
                 "0001"
                 "0010"
                 "0010"
                 "0100"
                 "1000",
                 '8':\
                 "0110"
                 "1001"
                 "0110"
                 "1001"
                 "1001"
                 "0110",
                 '9':\
                 "0110"
                 "1001"
                 "0111"
                 "0001"
                 "0001"
                 "0110",
                 '0':\
                 "0110"
                 "1001"
                 "1001"
                 "1001"
                 "1001"
                 "0110",
                 '=':\
                 ["0000"
                  "0000"
                  "1111"
                  "0000"
                  "1111"
                  "0000",
                  "0000"
                  "1111"
                  "0000"
                  "0000"
                  "1111"
                  "0000",
                  ],
                 ';':\
                 "0000"
                 "0000"
                 "0010"
                 "0000"
                 "0010"
                 "0010",
                 '\'':\
                 "0010"
                 "0010"
                 "0000"
                 "0000"
                 "0000"
                 "0000",
                 ',':\
                 "0000"
                 "0000"
                 "0000"
                 "0000"
                 "0010"
                 "0100",
                 '.':\
                 "0000"
                 "0000"
                 "0000"
                 "0000"
                 "0000"
                 "0010",
                 '!':\
                 "0010"
                 "0010"
                 "0010"
                 "0010"
                 "0000"
                 "0010",
                 '@':\
                 "0110"
                 "1001"
                 "1111"
                 "1101"
                 "1010"
                 "0111",
                 '#':\
                 "0000"
                 "0110"
                 "1111"
                 "1111"
                 "0110"
                 "0000",
                 '$':\
                 "0111"
                 "1010"
                 "1010"
                 "0110"
                 "0101"
                 "1110",
                 '%':\
                 "1001"
                 "0001"
                 "0010"
                 "0100"
                 "1000"
                 "1001",
                 '^':\
                 "0100"
                 "1010"
                 "0000"
                 "0000"
                 "0000"
                 "0000",
                 '&':\
                 "0100"
                 "1010"
                 "1010"
                 "0111"
                 "1010"
                 "0111",
                 '(':\
                 "0010"
                 "0100"
                 "1000"
                 "1000"
                 "0100"
                 "0010",
                 ')':\
                 "0100"
                 "0010"
                 "0001"
                 "0001"
                 "0010"
                 "0100",
                 '_':\
                 "0000"
                 "0000"
                 "0000"
                 "0000"
                 "0000"
                 "1111",
                 '+':\
                 ["1111"
                  "1000"
                  "1000"
                  "1000"
                  "1000"
                  "1000",
                  "1111"
                  "0100"
                  "0100"
                  "0100"
                  "0100"
                  "0100",
                  "1111"
                  "0010"
                  "0010"
                  "0010"
                  "0010"
                  "0010",
                  "1111"
                  "0001"
                  "0001"
                  "0001"
                  "0001"
                  "0001",
                  "1000"
                  "1111"
                  "1000"
                  "1000"
                  "1000"
                  "1000",
                  "0100"
                  "1111"
                  "0100"
                  "0100"
                  "0100"
                  "0100",
                  "0010"
                  "1111"
                  "0010"
                  "0010"
                  "0010"
                  "0010",
                  "0001"
                  "1111"
                  "0001"
                  "0001"
                  "0001"
                  "0001",
                  "1000"
                  "1000"
                  "1111"
                  "1000"
                  "1000"
                  "1000",
                  "0100"
                  "0100"
                  "1111"
                  "0100"
                  "0100"
                  "0100",
                  "0010"
                  "0010"
                  "1111"
                  "0010"
                  "0010"
                  "0010",
                  "0001"
                  "0001"
                  "1111"
                  "0001"
                  "0001"
                  "0001",
                  "1000"
                  "1000"
                  "1000"
                  "1111"
                  "1000"
                  "1000",
                  "0100"
                  "0100"
                  "0100"
                  "1111"
                  "0100"
                  "0100",
                  "0010"
                  "0010"
                  "0010"
                  "1111"
                  "0010"
                  "0010",
                  "0001"
                  "0001"
                  "0001"
                  "1111"
                  "0001"
                  "0001",
                  "1000"
                  "1000"
                  "1000"
                  "1000"
                  "1111"
                  "1000",
                  "0100"
                  "0100"
                  "0100"
                  "0100"
                  "1111"
                  "0100",
                  "0010"
                  "0010"
                  "0010"
                  "0010"
                  "1111"
                  "0010",
                  "0001"
                  "0001"
                  "0001"
                  "0001"
                  "1111"
                  "0001",
                  "1000"
                  "1000"
                  "1000"
                  "1000"
                  "1000"
                  "1111",
                  "0100"
                  "0100"
                  "0100"
                  "0100"
                  "0100"
                  "1111",
                  "0010"
                  "0010"
                  "0010"
                  "0010"
                  "0010"
                  "1111",
                  "0001"
                  "0001"
                  "0001"
                  "0001"
                  "0001"
                  "1111",
                  ],
                 ':':\
                 "0000"
                 "0000"
                 "0000"
                 "0010"
                 "0000"
                 "0010",
                 '"':\
                 "0101"
                 "0101"
                 "0000"
                 "0000"
                 "0000"
                 "0000",
                 '<':\
                 "0000"
                 "0010"
                 "0100"
                 "1000"
                 "0100"
                 "0010",
                 '>':\
                 "0000"
                 "1000"
                 "0100"
                 "0010"
                 "0100"
                 "1000",
                 '?':\
                 "0110"
                 "1001"
                 "0001"
                 "0010"
                 "0000"
                 "0010",
                 '[':\
                 "0110"
                 "0100"
                 "0100"
                 "0100"
                 "0100"
                 "0110",
                 ']':\
                 "0110"
                 "0010"
                 "0010"
                 "0010"
                 "0010"
                 "0110",
                 '{':\
                 "0010"
                 "0100"
                 "0100"
                 "1000"
                 "0100"
                 "0010",
                 '}':\
                 "0100"
                 "0010"
                 "0010"
                 "0001"
                 "0010"
                 "0100",
                 }

char2gray = {}
gray2char = {}
charGrayNums = []
charBitCountMap = [ [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     ]
def dummy():
    pass

# Set up the data.
#
# char2grayStr is just for us humans to associate characters
# with their bitmaps.
#
# char2gray associates each character with the integer
# representation of its bitmap (which means character
# bitmaps must have 31 bits or less).
#
# gray2char associates each bitmap number with its
# character.
#
# charGrayNums is a sorted list of the de-Graycoded
# bitmaps. This is what we use to find the closest
# character bitmap to a supplied picture fragment.

def countBitsOn(n):
    result = 0
    while n:
        if n & 1:
            result += 1
        n = n >> 1
    return result

for ch in char2grayStr.keys():
    char2gray[ch] = []
    for bitmap in flatten(char2grayStr[ch]):
        char2gray[ch].append(stringbits(bitmap))
for ch in char2gray.keys():
    if ch == ' ':
        #print "char2gray[ ] is [%s]"%char2gray[ch]
        pass
    for bits in char2gray[ch]:
        gray2char[bits] = ch
for num in gray2char.keys():
    charGrayNums.append(inversegray(num))
    bits = countBitsOn(num)
    charBitCountMap[bits].append(num)
charGrayNums.sort()

#def findClosestChar(bmpval):
#    try:
#        return gray2char[bmpval]
#    except:
#        pass
#    ig = inversegray(bmpval)
#    move = int(len(charGrayNums)/4)
#    where = move*2
#    while move:
#        if charGrayNums[where] == ig:
#            break
#        if charGrayNums[where] > ig:
#            where -= move
#        if charGrayNums[where] < ig:
#            where += move
#        move = move >> 1
#    rc = gray2char[gray(charGrayNums[where])]
#    return rc

#def findClosestChar(bmpval):
#    try:
#        return gray2char[bmpval]
#    except:
#        pass
#    ig = inversegray(bmpval)
#    for i in range(len(charGrayNums)-1):
#        if ig>=charGrayNums[i] and ig<=charGrayNums[i+1]:
#            if ig-charGrayNums[i] < charGrayNums[i+1]-ig:
#                rc = gray2char[gray(charGrayNums[i])]
#                #print "    Returns",rc
#                return rc
#            else:
#                rc = gray2char[gray(charGrayNums[i+1])]
#                #print "    Returns",rc
#                return rc
#    rc = gray2char[gray(charGrayNums[len(charGrayNums)-1])]
#    #print "    Returns",rc
#    return rc

def countMatchingBits(n1,n2):
    bits = 0
    for i in range(24):
        if n1&1 == n2&1:
            bits += 1
        n1 /= 2
        n2 /= 2
    return bits

def findCharList(bmpval):
    bits = countBitsOn(bmpval)
    while not charBitCountMap[bits]:
        bits -= 1
    return charBitCountMap[bits]

def findClosestChar(bmpval):
    try:
        return gray2char[bmpval]
    except:
        pass

    bestmatch = 0
    bestmatchbits = 0

    clist = findCharList(bmpval)
    
    for cbmp in clist:
        matchbits = countMatchingBits(cbmp,bmpval)
        if matchbits >= 24: # Good enough.
           return gray2char[cbmp]
        if matchbits >= bestmatchbits:
            bestmatchbits = matchbits
            bestmatch = cbmp
    return gray2char[bestmatch]

# This function expects a bitmap with x dimension
# divisible by 4 and y dimension divisible by 6,
# expressed as a list of lists of 1s and 0s
# (integers). It returns a string representing
# the ASCII version of the bitmap.
import operator as op
def bmp2ascii(bmp):
    rows = len(bmp)
    cols = len(bmp[0])
    rlim = rows/6
    clim = cols/4
    result = []
    for y in range(rlim):
        for x in range(clim):
            bmpval = 0
            for yy in range(y*6,y*6+6):
                #line = ""
                for xx in range(x*4,x*4+4):
                    #line = line + "%s"%bmp[yy][xx]
                    try:
                        bmpval += bmp[yy][xx]
                    except:
                        #print "Exception: %s+%s"%(bmpval,bmp[xx][yy])
                        pass
                    bmpval += bmpval
                #print line
            bmpval = bmpval >> 1
            result.append(findClosestChar(bmpval))
        result += '\n'
        #print y*100/rlim,' ',
        sys.stdout.flush()

    result = reduce(op.add,result)
    return result

def string2bmp(str,width):
    print "string2bmp..."
    xtra = ""
    xtra = xtra + '0'*(width%4)
    ls = len(str)
    where = 0
    result = []
    while where<ls:
        print '.',
        sys.stdout.flush()
        line = str[where:where+width]+xtra
        result.append(line)
        where += width
    for i in range(len(result)):
        result[i] = map(int,result[i])
    xtra_lines = len(result)%6
    if xtra_lines:
        xline = [0] * len(result[0])
        for i in range(xtra_lines):
            result.append(xline[:])
    print "...done."
    sys.stdout.flush()
    return result

import string

def invertString(s):
    return s.replace('1','x').replace('0','1').replace('x','0')

def loadPbm(fname):
    f = open(fname,'r')
    f.readline()
    l = f.readline()
    while l[0] == '#':
        l = f.readline()
    sw,sh = l.split()
    width = int(sw)
    result = []
    line = f.readline().split()
    while line:
        print '.',
        sys.stdout.flush()
        result += line
        line = f.readline().split()
    print "Reducing..."
    rc = reduce(op.add,result),width
    print "...done."
    return rc

if __name__ == "__main__":
    print "OK"
    ok = \
       "01101001"\
       "10011010"\
       "10011100"\
       "10011100"\
       "10011010"\
       "01101001"
    bmp = string2bmp(ok,8)
    print bmp2ascii(bmp)

    ok = \
       "11101000"\
       "10011000"\
       "00111110"\
       "01010100"\
       "10111010"\
       "01111001"
    bmp = string2bmp(ok,8)
    print bmp2ascii(bmp)

    ok = \
       "11111111"\
       "11111111"\
       "11111111"\
       "11111111"\
       "11111111"\
       "11111111"
    bmp = string2bmp(ok,8)
    print bmp2ascii(bmp)

    ok = \
       "00000000"\
       "00000000"\
       "00000000"\
       "00000000"\
       "00000000"\
       "00000000"
    bmp = string2bmp(ok,8)
    print bmp2ascii(bmp)


    print "Loading..."
    ok,width = loadPbm('/home/joe/src/wolf.pbm')
    #print "Inverting..."
    #ok = invertString(ok)
    print "Done"
    bmp = string2bmp(ok,width)
    print bmp2ascii(bmp)
    
