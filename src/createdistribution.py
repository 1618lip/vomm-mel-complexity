#@author Philip Pincencia
from music21 import * 
import sys
import math
import matplotlib.pyplot as plt
import re
from random import gauss
# Define the range
def frequency_to_note(freq):
    pitch_object = pitch.Pitch()
    pitch_object.frequency = freq
    return pitch_object.nameWithOctave

def note_to_frequency(note_name):
    # Create a Pitch object from the note name
    p = pitch.Pitch(note_name)
    # Get the frequency of the pitch
    frequency = round(p.frequency)
    return frequency
def midi_to_frequency(midi_note):
    """
    Map a MIDI note number to the range [C4, C#4, ..., B4] and convert it to frequency in Hz.

    Parameters:
    midi_note (int): MIDI note number (0-127)

    Returns:
    float: Frequency in Hz
    """
    if not (0 <= midi_note <= 128):
        raise ValueError("MIDI note number must be in the range 0-128")

    # Map the MIDI note to the range 60-71
    mapped_midi_note = 60 + (midi_note % 12)

    # Calculate the frequency
    frequency = 440.0 * 2 ** ((mapped_midi_note - 69) / 12.0)
    return round(frequency)
all_notes = ['C4', 'C#4', 'D4', 'Eb4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'Bb4', 'B4']
all_notes = [note_to_frequency(m) for m in all_notes]
# List of scales to check

maj7 = [scale.MajorScale, scale.LydianScale, scale.WholeToneScale]
min7 = [scale.MinorScale, scale.DorianScale, scale.HarmonicMinorScale, scale.MelodicMinorScale, scale.PhrygianScale, scale.LocrianScale]
dominant7 = [scale.MixolydianScale, scale.WholeToneScale, scale.DorianScale, scale.PhrygianScale, scale.LydianScale,
    scale.LocrianScale, scale.HarmonicMinorScale, scale.MelodicMinorScale]
dim7 = [scale.LocrianScale]
scale_choice = [
    maj7, min7, dominant7, dim7
]
scales_precedence = []
# transpose the chord to the target octave
#
#  @param: 
#   - ch: chord to be transposed\
#   - target_octave: octave where the chord should be transposed
# @return:
# return the channel 
def transpose_to_octave(ch, target_octave):
    # Transpose each note to the target octave

    for n in ch.notes:
        n.octave = target_octave
    return ch

# Transpose the chord to the 4th octave

def chordToNotes(chord_name):
    try:
        # Create a ChordSymbol object from the chord name
        chord_symbol = harmony.ChordSymbol(chord_name)
        # Get the pitches of the chord
        pitches = chord_symbol.pitches
        # Convert pitches to note names
        note_names = [p.nameWithOctave for p in pitches]
        return (note_names)
    except Exception as e:
        print(f"Error processing chord '{chord_name}': {e}")
        return []
# def rename(pitch):
#     if "-" in pitch:
#         pitch = pitch.replace("-", )
def createDistribution(input_chord, midi):
    # if midi == 10:
    #     return 1/12
    if re.search("(([A-G](#|-)?min([1-9]*)?((#|-)[1-9]*)?))", input_chord):
        scale_types = scale_choice[1]
        # THIS IS TO PRIORITIZE MINOR CHORD
    elif re.search(R"(([A-G](#|-)?dim([1-9]*)?((#|-)[1-9]*)?))", input_chord):
        scale_types = scale_choice[3]
        # PRIORITIZE DIMINISHED CHORD
    elif re.search(R"(([A-G](#|-)?([1-9]*)((#|-)[1-9]*)?(\/[A-G](#|b)?)?))", input_chord):
        scale_types = scale_choice[2]
        #PRIORITIZE DOMINANT CHORD
    elif re.search(R"(([A-G](#|-)?(maj)?([1-9]*)?((#|-)[1-9]*)?(\/[A-G](#|b)?)?))", input_chord):
        scale_types = scale_choice[0]
        # MAJOR CHORD
    chordier = transpose_to_octave(chord.Chord(chordToNotes(input_chord)), 4)
    chordy = [n.nameWithOctave for n in chordier.notes]

    possible_scales = []

    # Check each scale type
    for scale_type in scale_types:
        candidate_scale = scale_type(chordier.root().name)
        #print(candidate_scale.getPitches())
        for p in candidate_scale.getPitches():
            #print(p.name)
            candidate_scl = [p.name for p in candidate_scale.getPitches()]
        chordierrr = [p.name for p in chordier.pitches]
        
        #print(chordierrr)
        if all(p in candidate_scl for p in chordierrr):
            possible_scales.append(candidate_scale)

    candidates = []
    # Print possible scales
    #print("Possible scales for the chord:")
    for sc in possible_scales:
        candidates.append([note_to_frequency(p.nameWithOctave) for p in sc.getPitches()])

    weights = [0] * len(all_notes)
    chordy = [note_to_frequency(m) for m in chordy]
    for note in all_notes:
        if note == chordy[0]:
            weights[all_notes.index(note)] = gauss(2.5, math.sqrt(0.005))
        elif note in chordy:
            weights[all_notes.index(note)] = gauss(2.25, math.sqrt(0.005))
        elif len(candidates) > 0 and (note in candidates[0]):
            weights[all_notes.index(note)] = gauss(1.75, math.sqrt(0.005))
        elif len(candidates) > 1 and (note in candidates[1]):
            weights[all_notes.index(note)] = gauss(1.5, math.sqrt(0.005))
        elif len(candidates) > 2 and (note in candidates[2]):
            weights[all_notes.index(note)] = gauss(1.25, math.sqrt(0.005))
        else: 
            weights[all_notes.index(note)] = gauss(1, math.sqrt(0.005))

    denom = 0
    for w in weights: 
        denom += math.pow(math.e, w)

    softmax = [0] * len(all_notes)
    for note in all_notes:
        softmax[all_notes.index(note)] = math.pow(math.e, weights[all_notes.index(note)]) / denom

    # fig = plt.figure(figsize=(12,6))
    # ax = fig.add_axes(rect=(0.1,0.1,0.8,0.8))
    # ax.plot([i for i in range(1,len(all_notes)+1)], softmax, '-o')

    # ax.set_xlabel('Notes')
    # ax.set_ylabel('Probability')
    # ax.set_title('Probability distribution given ' + input_chord)
    # ax.set_xticks([1, 2, 3, 4, 5, 6,7,8,9,10,11, 12])
    # ax.set_xticklabels(['C', 'C#', 'D','Eb','E','F','F#','G','G#','A','Bb','B'])
    # plt.grid(True)
    # plt.show()
    return softmax[all_notes.index(midi_to_frequency(midi))]