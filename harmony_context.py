import xml.etree.ElementTree as ET
from sklearn.metrics import log_loss
import random 
import os
import sys
import math as m
import time

# from createdistribution import createDistribution

start = time.time()
f = open("solo_representation.txt", "r")
q = f.read()
Q = list(q.split(":"))
Q.pop()
"""
Q will be like [note1, dur1, note2, dur2, ...]
Get the (i+1)th note = Q[2i]
Get the (i+1)th dur = Q[2i+1]

"""
cum_time = 0 # Start of song
weights  = [1] * (len(Q) // 2)
"""
We propose that the downbeats are in beat 1 and 3 (2 and 4 are not really). 
Let b = 12

->       || # . #  .  | #  .  #  .  ||  
cum_time || 0 b 2b 3b | 4b 5b 6b 7b ||   <-- cum_time

if the cum_time mod 48 = 0 OR 24, then it is downbeat. 

Map every note to the range 10 - 99 so that every 'note' is using two symbols. 

1/5 * P(b|""a) = 0.14
i(observing note: observing chord): log2(p(note|chord)|p(note)) = 
Without context, it is said that P(a) = 1/|S|. But without context BUT know the chords, the probability of observing the note is 
 P(a|"") = 1/|S|, what is a better one such that 
Let T = note without know chord and S = note with know chord. Then, i(t:s) = log2(create_dist()/1/11)=log2(11*create_dist()).

P(x|x1...x(i-1)) = P(x|x1...x(i-D))(1+ai(t:s))
 i(note: )
"""
for i in range(0, len(Q) // 2):
    if cum_time % 48 == 0: 
        weights[i] = 1.2 # First
    elif cum_time % 48 == 24:
        weights[i] = 1.1
    cum_time += int(Q[2*i+1])
print(Q)


end = time.time()
print(f"Time elapsed = {end - start} seconds")

