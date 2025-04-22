# @author Philip Pincencia

import sys
import math
import re
import matplotlib.pyplot as plt
from random import gauss
from music21 import pitch, scale, chord, harmony

# --- Utility Functions --- #

def frequency_to_note(freq):
    """Convert a frequency (Hz) to a note name with octave."""
    p = pitch.Pitch()
    p.frequency = freq
    return p.nameWithOctave

def note_to_frequency(note_name):
    """Convert a note name to its frequency (rounded Hz)."""
    return round(pitch.Pitch(note_name).frequency)

def midi_to_frequency(midi_note):
    """Map MIDI note number to frequency (focus on C4-B4 range)."""
    if not (0 <= midi_note <= 128):
        raise ValueError("MIDI note number must be in the range 0-128.")
    mapped_midi = 60 + (midi_note % 12)
    freq = 440.0 * 2 ** ((mapped_midi - 69) / 12.0)
    return round(freq)

def transpose_to_octave(ch, target_octave):
    """Transpose all notes in a chord to a specific octave."""
    for n in ch.notes:
        n.octave = target_octave
    return ch

def chord_to_notes(chord_name):
    """Convert chord name string to a list of note names."""
    try:
        chord_symbol = harmony.ChordSymbol(chord_name)
        return [p.nameWithOctave for p in chord_symbol.pitches]
    except Exception as e:
        print(f"Error processing chord '{chord_name}': {e}")
        return []

# --- Setup --- #

# Define all reference notes and scales
all_notes = ['C4', 'C#4', 'D4', 'Eb4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'Bb4', 'B4']
all_notes = [note_to_frequency(n) for n in all_notes]

maj7_scales = [scale.MajorScale, scale.LydianScale, scale.WholeToneScale]
min7_scales = [scale.MinorScale, scale.DorianScale, scale.HarmonicMinorScale, scale.MelodicMinorScale, scale.PhrygianScale, scale.LocrianScale]
dom7_scales = [scale.MixolydianScale, scale.WholeToneScale, scale.DorianScale, scale.PhrygianScale, scale.LydianScale, scale.LocrianScale, scale.HarmonicMinorScale, scale.MelodicMinorScale]
dim7_scales = [scale.LocrianScale]

scale_choice = [maj7_scales, min7_scales, dom7_scales, dim7_scales]

# --- Main Probability Distribution Function --- #

def create_distribution(input_chord, midi):
    """
    Create a probability distribution over notes based on the chord.

    Parameters:
    input_chord (str): Chord name (e.g., "Cmaj7", "Am7").
    midi (int): MIDI note number.

    Returns:
    float: Probability associated with the input MIDI note.
    """
    # Select scale family based on chord type
    if re.search(r"([A-G](#|-)?min.*)", input_chord):
        scale_types = scale_choice[1]
    elif re.search(r"([A-G](#|-)?dim.*)", input_chord):
        scale_types = scale_choice[3]
    elif re.search(r"([A-G](#|-)?[1-9].*)", input_chord):
        scale_types = scale_choice[2]
    else:
        scale_types = scale_choice[0]

    # Transpose chord to 4th octave
    chord_notes = transpose_to_octave(chord.Chord(chord_to_notes(input_chord)), 4)
    chord_frequencies = [note_to_frequency(n.nameWithOctave) for n in chord_notes.notes]

    # Identify candidate scales
    possible_scales = []
    for scale_type in scale_types:
        candidate_scale = scale_type(chord_notes.root().name)
        candidate_notes = [p.name for p in candidate_scale.getPitches()]
        if all(p.name in candidate_notes for p in chord_notes.pitches):
            possible_scales.append(candidate_scale)

    # Build weight vector for notes
    weights = [0] * len(all_notes)

    for idx, note in enumerate(all_notes):
        if note == chord_frequencies[0]:
            weights[idx] = gauss(2.5, math.sqrt(0.005))
        elif note in chord_frequencies:
            weights[idx] = gauss(2.25, math.sqrt(0.005))
        elif len(possible_scales) > 0 and note in [note_to_frequency(p.nameWithOctave) for p in possible_scales[0].getPitches()]:
            weights[idx] = gauss(1.75, math.sqrt(0.005))
        elif len(possible_scales) > 1 and note in [note_to_frequency(p.nameWithOctave) for p in possible_scales[1].getPitches()]:
            weights[idx] = gauss(1.5, math.sqrt(0.005))
        elif len(possible_scales) > 2 and note in [note_to_frequency(p.nameWithOctave) for p in possible_scales[2].getPitches()]:
            weights[idx] = gauss(1.25, math.sqrt(0.005))
        else:
            weights[idx] = gauss(1, math.sqrt(0.005))

    # Normalize weights using softmax
    denom = sum(math.exp(w) for w in weights)
    softmax = [math.exp(w) / denom for w in weights]

    return softmax[all_notes.index(midi_to_frequency(midi))]
