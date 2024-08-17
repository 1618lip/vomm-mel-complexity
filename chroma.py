from music21 import converter, note, stream, pitch, harmony, chord
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MaxNLocator
import math as m
import cmath
import sys
import numpy as np

def partition_measure(measure, num_partitions=4):  # split each measure into 4 beats
    measure_duration = measure.duration.quarterLength
    partition_length = measure_duration / num_partitions
    partitions = []
    for i in range(num_partitions):
        start_offset = i * partition_length
        end_offset = (i + 1) * partition_length
        partitions.append((start_offset, end_offset))
    return partitions

def extract_elements_in_range(measure, start_offset, end_offset):
    elements_in_range = []
    for element in measure.flatten().notesAndRests.getElementsByOffset(start_offset, end_offset, includeEndBoundary=False):
        if isinstance(element, (note.Note, note.Rest)):  # Include both notes and rests
            elements_in_range.append(element)
    return elements_in_range

def chromareorder(chroma):
    if chroma == []: return []
    new = [0] * len(chroma)
    for i in range(0, len(chroma)):
        new[i] = chroma[(7*i) % 12]
    return new
def resultant(chroma):
    if chroma == []:
        return -1
    total = 0
    for n in range(0, len(chroma)): 
        if chroma[n] != 0: 
            theta = (2*cmath.pi*n)/12
            total += chroma[n]*cmath.exp(theta*1j)
        else: 
            continue
    return abs(total)
def chroma(measury, window):
    final = []
    if measury == []: return []
    if window == "bar": 
        for bar in measury:
            c = [0] * 12
            if bar == []: 
                final.append([])
                continue
            for k in bar:
                if k == 'C':
                    c[0] = c[0]+1
                elif k == 'C#' or k == 'Db':
                    c[1] = c[1]+1
                elif k == 'D':
                    c[2] = c[2]+1   
                elif k == 'D#' or k == 'Eb':
                    c[3] = c[3]+1 
                elif k == 'E':
                    c[4] = c[4]+1   
                elif k == 'F':
                    c[5] = c[5]+1 
                elif k == 'F#' or k == 'Gb':
                    c[6] = c[6]+1   
                elif k == 'G':
                    c[7] = c[7]+1 
                elif k == 'G#' or k == 'Ab':
                    c[8] = c[8]+1   
                elif k == 'A':
                    c[9] = c[9]+1 
                elif k == 'A#' or k == 'Bb':
                    c[10] = c[10]+1   
                elif k == 'B':
                    c[11] = c[11]+1 
            for e in range(0, len(c)):
                c[e] = c[e] / len(bar)
            final.append(c)
        return final
    elif window == "full": 
        c = [0] * 12
        count = 0
        for bar in measury:
            for k in bar:
                if k == 'C':
                    c[0] = c[0]+1
                elif k == 'C#' or k == 'Db':
                    c[1] = c[1]+1
                elif k == 'D':
                    c[2] = c[2]+1   
                elif k == 'D#' or k == 'Eb':
                    c[3] = c[3]+1 
                elif k == 'E':
                    c[4] = c[4]+1   
                elif k == 'F':
                    c[5] = c[5]+1 
                elif k == 'F#' or k == 'Gb':
                    c[6] = c[6]+1   
                elif k == 'G':
                    c[7] = c[7]+1 
                elif k == 'G#' or k == 'Ab':
                    c[8] = c[8]+1   
                elif k == 'A':
                    c[9] = c[9]+1 
                elif k == 'A#' or k == 'Bb':
                    c[10] = c[10]+1   
                elif k == 'B':
                    c[11] = c[11]+1
            count += len(bar)
        for e in range(0, len(c)):
            c[e] = c[e] / count
        return c
def Gamma(c):
    c = resultant(chromareorder(c))
    if c == -1: return -1
    return m.sqrt(1-c)

file_path = str(sys.argv[1])
score = converter.parse(file_path) 

for part in score.parts:
    """
    In this part, you have to edit the chord changes by yourself to fit the length of the solo.
    No way to automate this :(((
    """
           
    """"""
    full = []
    
    for measure in part.getElementsByClass('Measure'):
        measure_number = measure.measureNumber
        partitions = partition_measure(measure)
        bar = []
        for i, (start_offset, end_offset) in enumerate(partitions):
            section_elements = extract_elements_in_range(measure, start_offset, end_offset)
            for el in section_elements:
                if isinstance(el, note.Note):
                    bar.append(el.name)
                elif isinstance(el, note.Rest):
                    continue
        full.append(bar)    
        
    break



# print(full)
# #plt.ion()
x = []
for i in range(1, len(full)+1):
    x.append(i)
y = []
for i in range(0, len(full)):
    print(abs(resultant(chroma(full, "bar")[i])))
    y.append(Gamma(chroma(full, "bar")[i]))

#print(abs(resultant(chroma(full, "full"))))
#ax = plt.figure().gca()
plt.figure(figsize=(12, 6))
plt.plot(x, np.ma.masked_outside(y, -0.1,1.1), '-o', label = "per bar")
plt.plot(x, np.ma.masked_outside([Gamma(chroma(full, "full"))] * len(x),-0.1,1.1), '-o', label = "as a whole")
plt.xlabel('Measure Number')
plt.ylabel('Normalized Complexity')
ax = plt.gca()
ax.set_xlim([0.8, len(y)+0.1])
ax.set_ylim([-0.05, 1.05])
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.title('Complexity from Chroma Method')
plt.grid(True)
plt.legend()
#plt.show()

categories = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'Ab', 'Eb', 'Bb', 'F']
values = chroma(full, "full")
print(values)
print(chromareorder(values))
colors = [
    '#1f77b4',  # Blue
    '#ff7f0e',  # Orange
    '#2ca02c',  # Green
    '#d62728',  # Red
    '#9467bd',  # Purple
    '#8c564b',  # Brown
    '#e377c2',  # Pink
    '#7f7f7f',  # Gray
    '#bcbd22',  # Yellow-green
    '#17becf',  # Cyan
    '#393b79',  # Dark Blue
    '#b15928'   # Dark Orange
]

# Create a circular bar plot
fig, ax = plt.subplots(subplot_kw=dict(polar=True))
bars = ax.bar(np.arange(len(categories)) * 2 * np.pi /
              len(categories), values, color=colors, alpha=1)

# Add labels to each bar
for i, (label, angle) in enumerate(zip(categories, np.arange(len(categories)) * 2 * np.pi / len(categories))):
    x = angle
    y = max(values) + 0.1  # Adjust height for label placement
    ax.text(x, y, label, ha='center', va='center', fontsize=8, color='red')

# angle = cmath.phase(resultant(chromareorder(values)))
# mag = abs(resultant(chromareorder(values)))
# print(abs(resultant(chromareorder(values))))
#print(chromareorder(values))
#ax.annotate('', xy=(angle, 1*mag), xytext=(0,0),arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle="->", linewidth=2))
# Customizing the plot
ax.set_theta_offset(np.pi / 2)  # Offset to start the bars from the top
ax.set_theta_direction(-1)  # Clockwise direction for bars
# Adjust the y-axis limit for better visualization
ax.set_ylim(0, max(values)+0.2)
ax.set_yticks([max(values)/2,max(values)])  # Hide the y-axis ticks

#plt.arrow(0,0,, abs(), color="red", linewidth=2, head_width=0.7, head_length=0.1)
plt.show()
sys.exit(0)