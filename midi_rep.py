import sys
from music21 import converter, note

def partition_measure(measure):
    # Implement partition logic if needed
    return [(0, measure.duration.quarterLength)]

def extract_elements_in_range(measure, start_offset, end_offset):
    # Extract elements within the given offset range
    elements = []
    for el in measure.elements:
        if el.offset >= start_offset and el.offset < end_offset:
            elements.append(el)
    return elements

def map_to_piano_range(value):
    """
    Maps a value from the range 21-108 to the range 10-97.

    Parameters:
    value (int): The value to be mapped.

    Returns:
    int: The mapped value in the new range.
    """
    if value < 21 or value > 108:
        raise ValueError("Value should be between 10 and 97")
    return value - 10

file_path = str(sys.argv[1])
score = converter.parse(file_path)

# Extract notes and partition measure
part = (score.parts)[0]
melody = ""
for measure in part.getElementsByClass('Measure'):
    measure_number = measure.measureNumber
    partitions = partition_measure(measure)
    for i, (start_offset, end_offset) in enumerate(partitions):
        section_elements = extract_elements_in_range(measure, start_offset, end_offset)
        
        for el in section_elements:
            if isinstance(el, note.Note):
                midi_number = el.pitch.midi
                melody += str(map_to_piano_range(midi_number))+":"+str(int(el.quarterLength*12))+":"
            elif isinstance(el, note.Rest):
                # Rest is denoted as 10. 
                melody += "10:"+str(int(el.quarterLength*12))+":" 


output_file = r""+sys.argv[1]
f = open(output_file[:len(output_file)-4]+"_MIDI_representation.txt", "w")
f.write(melody)
f.close()

"""
| Note Type                  | Value |
|----------------------------|-------|
| Whole note (semibreve)     | 48    |           
| Half note (minim)          | 24    |           
| Quarter note (crotchet)    | 12    |
| Eighth note (quaver)       | 6     |
| Sixteenth note (semiquaver)| 3     |
| Quarter note triplet       | 8     |
| Eighth note triplet        | 4     |
| Sixteenth note triplet     | 2     |

Using these values, we can represent all note lengths without decimals and maintain the duration ratios 
"""