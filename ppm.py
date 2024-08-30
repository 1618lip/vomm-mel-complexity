import xml.etree.ElementTree as ET
from sklearn.metrics import log_loss
import random 
from xml.dom import minidom
import zipfile
import os
import mido # type: ignore
from mido import MidiFile, MidiTrack, Message # type: ignore

# Step 1: Parse the MIDI Channel
def parse_midi_channel(midi_string):
    notes = midi_string.strip().split(':')
    sequence = []
    for i in range(0, len(notes) - 1, 2):  # Process every pair of elements
        midi_number = notes[i]
        duration = notes[i + 1]
        sequence.append(f"{midi_number}:{duration}")
    return sequence

# Step 2: Preprocess the Data
def preprocess_melody(melody):
    unique_notes = list(set(melody))
    note_to_int = {note: i for i, note in enumerate(unique_notes)}
    int_to_note = {i: note for note, i in note_to_int.items()}
    encoded_melody = [note_to_int[note] for note in melody]
    return encoded_melody, note_to_int, int_to_note

# Step 3: Implement the PPM Algorithm
class PPMNode:
    def __init__(self):
        self.counts = {}
        self.children = {}

def ppm_learn(sequence, max_order):
    root = PPMNode()
    for i in range(len(sequence)):
        for order in range(1, max_order + 1):
            if i + order >= len(sequence):
                break
            context = tuple(sequence[i:i + order])
            next_note = sequence[i + order] if i + order < len(sequence) else None
            node = root
            for note in context:
                if note not in node.children:
                    node.children[note] = PPMNode()
                node = node.children[note]
                if next_note is not None:
                    if next_note not in node.counts:
                        node.counts[next_note] = 0
                    node.counts[next_note] += 1
    return root

def ppm_predict(root, context, max_order):
    for order in range(max_order, 0, -1):
        node = root
        found = True
        for note in context[-order:]:
            if note in node.children:
                node = node.children[note]
            else:
                found = False
                break
        if found:
            total_counts = sum(node.counts.values())
            if total_counts > 0:
                return {note: count / total_counts for note, count in node.counts.items()}
    return {note: 1 / len(note_to_int) for note in range(len(note_to_int))}

def ppm_generate(root, start_context, length, max_order):
    generated_sequence = start_context[:]
    for _ in range(length):
        context = generated_sequence[-max_order:]
        probs = ppm_predict(root, context, max_order)
        next_note = random.choices(list(probs.keys()), list(probs.values()))[0]
        generated_sequence.append(next_note)
    return generated_sequence
# Step 4: Evaluate the Predictions
def evaluate_algorithm(algorithm, sequence, train_size, context_size, max_order=None):
    train_seq = sequence[:train_size]
    test_seq = sequence[train_size:]
    predictions = []
    actuals = []
    if algorithm == 'ctw':
        root = ctw_learn(train_seq, context_size)
        for i in range(len(test_seq) - context_size):
            context = test_seq[i:i + context_size]
            next_note = test_seq[i + context_size]
            prob = ctw_predict(root, context)
            predictions.append(prob)
            actuals.append(next_note)
    elif algorithm == 'ppm':
        root = ppm_learn(train_seq, max_order)
        for i in range(len(test_seq) - max_order):
            context = test_seq[i:i + max_order]
            next_note = test_seq[i + max_order]
            predictions_dict = ppm_predict(root, context, max_order)
            prob = [predictions_dict.get(note, 1 / len(note_to_int)) for note in range(len(note_to_int))]
            predictions.append(prob)
            actuals.append(next_note)
    return log_loss(actuals, predictions, labels=list(range(len(note_to_int))))
# Step 5: Generate Data Based on the Training Data
# def generate_ctw_data(root, context, length):
#     generated_sequence = context[:]
#     for _ in range(length):
#         prob = ctw_predict(root, generated_sequence[-len(context):])
#         next_note = random.choices(range(len(prob)), prob)[0]
#         generated_sequence.append(next_note)
#     return generated_sequence

# def generate_ppm_data(root, context, length, max_order):
#     generated_sequence = context[:]
#     for _ in range(length):
#         predictions_dict = ppm_predict(root, generated_sequence[-max_order:], max_order)
#         prob = [predictions_dict.get(note, 1 / len(note_to_int)) for note in range(len(note_to_int))]
#         next_note = random.choices(range(len(prob)), prob)[0]
#         generated_sequence.append(next_note)
#     return generated_sequence
# Example usage
# Function to translate MIDI number to note name
# Function to translate MIDI number to note name
def midi_to_note_name(midi_number):
    pitch_step = midi_number % 12
    pitch_octave = midi_number // 12 - 1  # MIDI octave calculation
    step_dict = {0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F", 6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B"}
    step = step_dict[pitch_step]
    return f"{step}{pitch_octave}"

# Function to translate duration to note length
def duration_to_note_length(duration):
    duration = float(duration)
    if duration >= 2000:
        return "whole"
    elif duration >= 1000:
        return "half"
    elif duration >= 500:
        return "quarter"
    elif duration >= 250:
        return "eighth"
    elif duration >= 125:
        return "16th"
    elif duration >= 62.5:
        return "32nd"
    else:
        return "64th"

# Function to translate MIDI sequence to note names and lengths
def translate_midi_sequence(generated_sequence):
    translated_sequence = []
    for note in generated_sequence:
        midi_number, duration = note.split(':')
        if float(midi_number) == -1:
            translated_sequence.append(f"rest:{duration_to_note_length(duration)}")
        else:
            midi_number = int(midi_number)
            note_name = midi_to_note_name(midi_number)
            note_length = duration_to_note_length(duration)
            translated_sequence.append(f"{note_name}:{note_length}")
    return translated_sequence

def convert_to_midi(generated_sequence, output_filename):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo (optional, you can adjust the tempo as needed)
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
    
    for note in generated_sequence:
        midi_number, duration = note.split(':')
        duration_ms = float(duration)
        if float(midi_number) == -1:  # Handle rest
            track.append(Message('note_off', note=0, velocity=0, time=int(duration_ms / 500 * 480)))
        else:
            midi_number = int(midi_number)
            # Add note_on and note_off messages
            track.append(Message('note_on', note=midi_number, velocity=64, time=0))
            track.append(Message('note_off', note=midi_number, velocity=64, time=int(duration_ms / 500 * 480)))
    
    mid.save(output_filename)
midi_string = ("-1:666.67:-1:166.67:63:166.67:65:166.67:67:166.67:68:166.67:67:166.67:65:166.67:64:166.67:63:166.67:61:166.67:60:111.11:61:111.11:62:111.11:63:166.67:60:166.67:61:166.67:63:166.67:63:333.33:-1:333.33:-1:666.67:-1:333.33:-1:166.67:60:166.67:67:166.67:65:166.67:62:166.67:58:166.67:60:333.33:-1:333.33:-1:1333.33:-1:166.67:58:83.33:61:83.33:65:111.11:68:111.11:72:111.11:75:166.67:74:166.67:73:166.67:72:166.67:70:166.67:69:166.67:68:166.67:67:166.67:66:166.67:65:166.67:64:166.67:62:166.67:63:333.33:-1:333.33:-1:166.67:61:166.67:60:333.33:-1:666.67:70:166.67:66:166.67:63:166.67:-1:166.67:68:166.67:64:166.67:65:111.11:68:111.11:72:111.11:75:166.67:73:166.67:73:333.33:-1:333.33:-1:166.67:78:166.67:76:166.67:68:166.67:71:166.67:75:166.67:73:166.67:-1:166.67:-1:333.33:-1:166.67:72:166.67:72:333.33:75:166.67:73:166.67:72:166.67:70:166.67:69:333.33:63:333.33:66:111.11:68:111.11:66:111.11:65:166.67:63:166.67:62:166.67:65:166.67:68:166.67:72:166.67:67:333.33:70:166.67:67:166.67:68:166.67:65:166.67:-1:333.33:-1:666.67:-1:166.67:58:83.33:61:83.33:65:166.67:68:166.67:67:166.67:65:166.67:63:166.67:58:166.67:66:166.67:65:166.67:64:333.33:-1:166.67:60:166.67:61:166.67:64:166.67:63:166.67:61:166.67:60:166.67:58:166.67:57:166.67:60:166.67:63:166.67:57:166.67:66:166.67:65:166.67:62:166.67:60:166.67:67:166.67:65:166.67:62:166.67:58:166.67:60:333.33:-1:333.33:-1:1333.33:-1:333.33:67:166.67:65:166.67:64:111.11:67:111.11:70:111.11:73:166.67:72:166.67:72:333.33:70:55.56:72:55.56:70:55.56:68:166.67:67:166.67:65:166.67:64:166.67:55:166.67:58:166.67:61:166.67:60:166.67:58:166.67:56:333.33:72:166.67:70:166.67:68:166.67:66:166.67:64:166.67:59:166.67:61:166.67:64:166.67:63:166.67:61:166.67:60:166.67:63:166.67:65:166.67:67:166.67:70:166.67:68:166.67:67:166.67:65:166.67:64:166.67:55:166.67:58:166.67:61:166.67:58:166.67:55:166.67:60:166.67:55:166.67:58:166.67:62:166.67:56:166.67:53:166.67:-1:666.67:-1:1333.33:-1:166.67:59:166.67:60:111.11:63:111.11:67:111.11:68:166.67:65:166.67:67:166.67:68:166.67:67:55.56:68:55.56:67:55.56:65:166.67:68:333.33:-1:333.33:-1:166.67:59:166.67:60:111.11:63:111.11:67:111.11:68:166.67:65:166.67:67:166.67:68:166.67:67:55.56:68:55.56:67:55.56:65:166.67:68:333.33:-1:166.67:59:166.67:60:111.11:63:111.11:67:111.11:68:166.67:65:166.67:67:166.67:68:166.67:67:55.56:68:55.56:67:55.56:65:166.67:68:166.67:67:166.67:65:166.67:64:166.67:63:166.67:61:166.67:60:166.67:58:166.67:57:166.67:66:166.67:63:166.67:64:166.67:65:166.67:62:166.67:58:166.67:56:166.67:60:333.33:-1:333.33:-1:1333.33:-1:166.67:58:83.33:61:83.33:65:111.11:68:111.11:72:111.11:75:166.67:74:166.67:73:166.67:72:166.67:70:166.67:69:166.67:68:166.67:67:166.67:66:166.67:65:166.67:64:166.67:62:166.67:63:166.67:59:166.67:60:111.11:63:111.11:67:111.11:70:166.67:66:166.67:63:166.67:58:166.67:61:166.67:59:166.67:60:166.67:64:166.67:64:166.67:63:166.67:68:166.67:66:166.67:65:333.33:-1:166.67:61:166.67:63:166.67:60:166.67:61:166.67:64:166.67:64:333.33:-1:333.33:-1:666.67:-1:666.67:71:166.67:72:166.67:75:166.67:79:166.67:79:333.33:77:166.67:76:166.67:75:166.67:73:166.67:72:166.67:70:166.67:69:333.33:63:166.67:60:166.67:66:166.67:68:83.33:66:83.33:65:166.67:63:166.67:62:166.67:65:166.67:68:166.67:72:166.67:67:111.11:68:111.11:69:111.11:70:166.67:67:166.67:68:333.33:-1:333.33:-1:166.67:58:166.67:60:166.67:61:166.67:61:333.33:-1:333.33:66:166.67:65:166.67:64:166.67:62:166.67:63:166.67:60:166.67:-1:333.33:-1:666.67:-1:333.33:-1:166.67:60:166.67:67:166.67:65:166.67:63:166.67:61:166.67:60:166.67:58:166.67:57:111.11:58:111.11:60:111.11:63:166.67:66:166.67:65:166.67:63:166.67:62:166.67:67:166.67:-1:333.33:-1:666.67:-1:666.67:67:166.67:65:166.67:64:111.11:67:111.11:70:111.11:73:333.33:67:166.67:72:166.67:72:333.33:70:166.67:67:166.67:68:166.67:65:166.67:-1:333.33:-1:666.67:-1:1333.33:-1:166.67:59:166.67:60:111.11:63:111.11:67:111.11:70:166.67:68:166.67:67:166.67:65:166.67:64:166.67:55:166.67:58:166.67:61:166.67:58:166.67:55:166.67:60:166.67:55:166.67:58:166.67:55:166.67:56:166.67:53:166.67:53:333.33:-1:333.33:-1:166.67:59:166.67:60:111.11:63:111.11:67:111.11:70:166.67:68:166.67:67:166.67:65:166.67:63:166.67:61:166.67:60:166.67:58:166.67:57:166.67:66:166.67:63:166.67:64:166.67:65:166.67:61:166.67:58:166.67:56:166.67:55:166.67:64:166.67:61:166.67:62:166.67:63:166.67:59:166.67:60:166.67:63:166.67:70:166.67:67:166.67:68:333.33:-1:333.33:-1:166.67:72:166.67:72:333.33:75:166.67:70:166.67:")
melody_sequence = parse_midi_channel(midi_string)
encoded_melody, note_to_int, int_to_note = preprocess_melody(melody_sequence)

train_size = int(len(encoded_melody) * 0.6)
context_size = 50
max_order = 16


ppm_log_loss = evaluate_algorithm('ppm', encoded_melody, train_size, context_size, max_order)

print("PPM Log Loss:", ppm_log_loss)

# Generate new sequence using CTW

start_context = encoded_melody[train_size-context_size:train_size]


#print("Generated sequence by CTW:", generated_sequence_ctw_notes)

# Generate new sequence using PPM
ppm_root = ppm_learn(encoded_melody[:train_size], max_order)
generated_sequence_ppm = ppm_generate(ppm_root, start_context, int(len(encoded_melody) * 0.5), max_order)
generated_sequence_ppm_notes = [int_to_note[note] for note in generated_sequence_ppm]
print("Generated sequence by PPM:", generated_sequence_ppm_notes)

translated_sequence = translate_midi_sequence(generated_sequence_ppm_notes)
for note in translated_sequence:
    #print(note)
    None
convert_to_midi(generated_sequence_ppm_notes, "generated_music.mid")