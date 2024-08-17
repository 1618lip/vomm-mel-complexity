import sys
import math as m
from vomm_ppm import count_occurrences, compute_ppm
from createdistribution import createDistribution
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
"""
Perform sliding analysis. Window length is W >> D.

Heuristic constraints: L >> kW, where k is in an even positive integer. And W > 4D
"""
alphabet = [':']
for i in range(0, 10):
    alphabet.append(str(i))
# alphabet = {'0', '1', ..., '9', ':'}
start = time.time()

D = int(sys.argv[1])
W = 12*int(sys.argv[2]) # num beats
def map_to_piano_range(value):
    """
    Maps a value from the range 10-97 to the range 21-108

    Parameters:
    value (int): The value to be mapped.

    Returns:
    int: The mapped value in the new range.
    """
    if value < 10 or value > 98:
        raise ValueError("Value should be between 10 and 97")
    return value + 10
    
def chord_of_note(chords, Q):
    """
    |0 12 24 36 |48 60 72 84 |96
    """
    copy_Q = Q
    cum_time = 0
    chord_note_pos = []
    for i in range(0, len(chords)):
        while 12*i <= cum_time and cum_time < 12*(i+1):
            note = copy_Q.pop(0)
            dur = int(copy_Q.pop(0))
            if int(note) == 10:
                lmi = 0
            else:
                lmi = round(m.log2(12*createDistribution(chords[i], map_to_piano_range(int(note)))),3)
            chord_note_pos.append((note, chords[i], cum_time, dur, lmi))
            """
            Each note is represented as a 5-tuple in the following order:
            1. pitch (in modified MIDI number)
            2. Underlying chord name
            3. Position in the music in 12*beats
            4. Duration of note in 12*beats
            5. Local Mutual Information of note given chord
            """
            cum_time += dur
    return chord_note_pos

def sliding_window(chords, Q, window):
    note_info = chord_of_note(chords, Q)
    final = []
    for k in range(0, len(note_info)):
        note_in_window = []
        test_sequence = []
        for i in range(0, len(note_info)):
            if (12*k <= int(note_info[i][2]) and 12*k+window > note_info[i][2]) or (12*k - note_info[i][3] <= int(note_info[i][2]) and 12*k+window > note_info[i][2]):
                note_in_window.append(note_info[i])
            elif  (12*k + window <= int(note_info[i][2]) and 12*k+2*window > note_info[i][2]) or (12*k +window - note_info[i][3] <= int(note_info[i][2]) and 12*k+2*window > note_info[i][2]):
                test_sequence.append(note_info[i])
        if test_sequence == []:
            break
        final.append((note_in_window, test_sequence))
        
    return final

def read_sliding_window(slides):
    for pair in slides:
        print(f"\nTraining: {pair[0]} \n Test: {pair[1]}\n")

def readFile(file_path):
    sections = []
    with open(file_path, 'r') as file:
        text = file.read()
        # Split the text by lines and process each line
        for line in text.splitlines():
            if not line.startswith("A") and not line.startswith("B"):
                # Split the line into chord groups and process each group
                chords = line.strip("[], ").split("], [")
                for chord_group in chords:
                    # Split each chord group into individual chords and add to sections
                    c = chord_group.split(", ")
                    for x in c:    
                        sections.append(x)
    return sections

output_file = r""+sys.argv[3]
f = open(output_file, "r") 
q = f.read()
Q = list(q.split(":"))
Q.pop() # Get rid of the empty array at the end due to ':' being q's last character

def average_log_loss(training_and_test, a=0.7, b=0.3):  
    toReturn = []
    count = 0
    for pair in training_and_test:
        training, test = pair
        training_sequence = ""
        test_sequence = ""
        for x in training:
            training_sequence += str(x[0]) + ":" + str(x[3]) + ":"
        for y in test:
            test_sequence += str(y[0]) + ":" + str(y[3]) + ":"

        """
        Here we need to generate all the possible contexts of length maximum D from the alphabet.
        A naive approach is just to generate all such strings, which would take O((12)^D)  :(((
        However, I realized soon that we can just consider the contexts that appear in the test sequence 
        and then combine the contexts together. 
        If there are duplicates, the count in the training sequence overrides. The count for contexts not in 
        the training sequence is zeroed out. 

        All of this is just to avoid dictionary 'Key' error 
        """
        counts = count_occurrences(training_sequence, D)
        counts_test = count_occurrences(test_sequence, D)
        counts_test.update(counts) 
        for context in counts_test:
            if context not in counts:
                counts_test[context] = {sigma: 0 for sigma in alphabet}
        
        probs = compute_ppm(counts_test, training_sequence, D)
        
        # Let's try by just doing P(xT|x1...x(T-1)) and then for each P(note, dur|context), add the lmi.
        context = ""
        total = 0
        for n in test:  
            # probs[context][":"]*(1+a*n[4])
            context = context[max(0,len(context)-D):]
            
            #context += n[0]+":"+n[3] 
            prob_of_note = probs[context][str(n[0][0])] if probs[context][str(n[0][0])] != 0 else 1/len(alphabet)
            #total += m.log2(prob_of_note)
            context+=str(n[0][0])
            context = context[max(0,len(context)-D):]
            
            prob_of_note *= probs[context][str(n[0][1])] if probs[context][str(n[0][1])] != 0 else 1/len(alphabet)
            #total += m.log2(prob_of_note)
            context+=str(n[0][1])
            context = context[max(0,len(context)-D):]
          
            prob_of_note *= probs[context][':'] if probs[context][':'] != 0 else 1/len(alphabet)
            #total += m.log2(prob_of_note)
            
            context += ':'
            context = context[max(0,len(context)-D):]
         
            if len(str(n[3])) > 1:
                
                prob_of_note *= probs[context][str(n[3])[0]] if probs[context][str(n[3])[0]] != 0 else 1/len(alphabet)
                #total += m.log2(prob_of_note)
                context+=str(str(n[3])[0])
                context = context[max(0,len(context)-D):]
                prob_of_note *= probs[context][str(n[3])[1]] if probs[context][str(n[3])[1]] != 0 else 1/len(alphabet)
                #total += m.log2(prob_of_note)
                context+=str(str(n[3])[1])
                context = context[max(0,len(context)-D):]        
            else:
                prob_of_note *= probs[context][str(n[3])] if probs[context][str(n[3])] != 0 else 1/len(alphabet)
                #total += m.log2(prob_of_note)
                context+=str(n[3])
                context = context[max(0,len(context)-D):]
        
            prob_of_note *= probs[context][':'] if probs[context][':'] != 0 else 1/len(alphabet)
                        
            prob_of_note = prob_of_note*(1+a*float(n[4]))
            context += ":"
            context = context[max(0,len(context)-D):]
            
            total += m.log2(prob_of_note)
        total = - (total * max(m.log2(b*len(test)), 1))/ len(test)
        toReturn.append(total)
    return toReturn

def plot_numbers_over_time(numbers):
    """
    Plots an array of numbers over time.

    Parameters:
    numbers (list or array): Array of numbers to be plotted.
    """
    # Generate a list of time points (e.g., 0, 1, 2, 3, ...)
    time_points = []
    x = 2
    for i in range(0, len(numbers)):
        time_points.append(x)
        x += 0.25
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, numbers, marker='o', linestyle='-')

    # Add labels and title
    plt.xlabel('Measure')
    plt.ylabel('ModifiedAverage Log Loss')
    plt.title('Melodic Complexity')

    # Add grid for better readability
    plt.grid(True)

    # Display the plot
    plt.show()

# Plotting and Animation setup
complexity_values = average_log_loss(sliding_window(readFile(output_file[:output_file.index("_MIDI_")]+"_parsed.txt"), Q, W))
fig, ax = plt.subplots()
line, = ax.plot([], [], marker='o', linestyle='-')
ax.set_xlim(1.75, 2.15+len(complexity_values) * 0.25)
ax.set_ylim(min(complexity_values)-1, max(complexity_values)+1)
ax.set_xlabel('Measure Window ')
ax.set_ylabel('Modified Average Log Loss')
ax.set_title('Melodic Complexity')
ax.grid(True)

# Initialize function for animation
def init():
    line.set_data([], [])
    return line,

# Animation update function
def update(frame):
    xdata = [i * 0.25 + 2 for i in range(frame)]
    ydata = complexity_values[:frame]
    line.set_data(xdata, ydata)
    return line,

# Animate
ani = animation.FuncAnimation(fig, update, frames=len(complexity_values), init_func=init, interval=150, blit=True)
end = time.time()
# print(f"Time elapsed = {end - start} seconds")
plt.show()
plot_numbers_over_time(complexity_values)