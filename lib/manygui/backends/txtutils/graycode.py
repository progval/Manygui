# Routines for Gray-encoding and -decoding integers.
# Gray coding is a binary representation in which
# each integer differs from its predecessor at only
# a single bit position:
#
# 000 -> 000
# 001 -> 001
# 010 -> 011
# 011 -> 010
# 100 -> 110
# 101 -> 111
# 110 -> 101
# 111 -> 100
#
# et cetera.

def intlog(i):
  if i<2:          return 0
  if i<4:          return 1
  if i<8:          return 2
  if i<16:         return 3
  if i<32:         return 4
  if i<64:         return 5
  if i<128:        return 6
  if i<256:        return 7
  if i<512:        return 8
  if i<1024:       return 9
  if i<2048:       return 10
  if i<4096:       return 11
  if i<8192:       return 12
  if i<16384:      return 13
  if i<32768:      return 14
  if i<65536:      return 15
  if i<131072:     return 16
  if i<262144:     return 17
  if i<524288:     return 18
  if i<1048576:    return 19
  if i<2097152:    return 20
  if i<4194304:    return 21
  if i<8388608:    return 22
  if i<16777216:   return 23
  if i<33554432:   return 24
  if i<67108864:   return 25
  if i<134217728:  return 26
  if i<268435456:  return 27
  if i<536870912:  return 28
  if i<1073741824: return 29
  return 30

def gray(i):
  mod=0
  indx=4
  gray=0
  bit=0
  limit=i+i+i+i
  
  mod = i % indx + 1

  q1 = indx/4
  q4 = q1+q1+q1
    
  if ((mod > q1) and (mod <= q4)):
      gray |= 1 << bit

  indx = indx+indx
  bit += 1
  mod = i % indx + 1
  while indx <= limit:
      q1 = indx/4
      q4 = q1+q1+q1
    
      if ((mod > q1) and (mod <= q4)):
          gray |= 1 << bit

      indx = indx+indx
      bit += 1
      mod = i % indx + 1
    
  return gray

def inversegray(i):
    if (i==0):
        return 0
    if (i==1):
        return 1

    msb = (1 << intlog(i))
    nmsb = msb >> 1
    allbutmsb = i-msb
    abman = allbutmsb+nmsb
    recurs = abman % msb
    igr = inversegray(recurs)
    result = msb + igr

    return result

import operator
from functools import reduce
def bitstring(i):
    if i == 0: return '0'
    result = []
    while i:
        if i & 1:
            result += '1'
        else:
            result += '0'
        i = i >> 1
    result.reverse()
    return reduce(operator.add,result)

def stringbits(s):
    result = 0
    while s:
        if s[0] == '1':
            result += 1
        result += result
        s = s[1:]
    result = result >> 1
    return result
        
if __name__ == "__main__":
    for i in range(0,32):
        g = gray(i)
        ig = inversegray(g)
        print("%s --> %s <-- %s"%(bitstring(i),bitstring(g),bitstring(ig)))
        bsi = bitstring(i)
        ibsi = stringbits(bsi)
        print("%d --> %s <-- %d"%(i,bsi,ibsi))
