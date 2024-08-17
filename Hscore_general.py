from music21 import converter, note, stream, pitch, harmony, chord
import matplotlib.pyplot as plt
import math, re
from itertools import combinations
import sys

# H = 1/nC2 {sum of all pairs of i,j}[(vi+vj)/gcd(vi, vj)]
def harmony_score(V):
    # Number of notes in the set
    n = len(V)
    # Calculate the number of combinations of 2 out of n
    num_combinations = math.comb(n, 2)
    # Calculate the sum of the given formula
    total = 0
    for v_i, v_j in combinations(V, 2):
        gcd = math.gcd(int(v_i), int(v_j))
        total += (int(v_i) + int(v_j)) / gcd
    # Calculate the harmony score
    H = total / num_combinations
    return round(H, 2)

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

def note_to_frequency(note_name):
    # Create a Pitch object from the note name
    p = pitch.Pitch(note_name)
    # Get the frequency of the pitch
    frequency = round(p.frequency)
    return frequency

def chordToNotes(chord_name):
    try:
        # Create a ChordSymbol object from the chord name
        chord_symbol = harmony.ChordSymbol(chord_name)
        # Get the pitches of the chord
        pitches = chord_symbol.pitches
        # Convert pitches to note names
        note_names = [note_to_frequency(p.nameWithOctave) for p in pitches]
        return note_names
    except Exception as e:
        print(f"Error processing chord '{chord_name}': {e}")
        return []

def readFile(file_path):
    sections = []
    with open(file_path, 'r') as file:
        text = file.read()
        # Initialize an empty list to store the sections

        # Split the text by lines and process each line
        for line in text.splitlines():
            if not line.startswith("A") and not line.startswith("B"):
                # Split the line into chord groups and process each group
                chords = line.strip("[], ").split("], [")
                for chord_group in chords:
                    # Split each chord group into individual chords and add to sections
                    c = chord_group.split(", ")
                    for i in range(0,len(c)):
                        c[i]= chordToNotes(c[i])
                        
                    sections.append(c)
    return sections

print(readFile("Parsed_chordchanges/Control1_parsed.txt"))