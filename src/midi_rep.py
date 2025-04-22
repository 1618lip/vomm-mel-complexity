import sys
from music21 import converter, note

def partition_measure(measure):
    """
    Partition a measure into sections.
    Currently returns the full measure as a single partition.
    
    Parameters:
    measure (music21.stream.Measure): The measure to partition.

    Returns:
    List of (start_offset, end_offset) tuples.
    """
    return [(0, measure.duration.quarterLength)]

def extract_elements_in_range(measure, start_offset, end_offset):
    """
    Extracts elements within a specific offset range from a measure.

    Parameters:
    measure (music21.stream.Measure): The measure to extract from.
    start_offset (float): Starting offset.
    end_offset (float): Ending offset.

    Returns:
    List of music21 elements within the range.
    """
    elements = []
    for el in measure.elements:
        if start_offset <= el.offset < end_offset:
            elements.append(el)
    return elements

def map_to_piano_range(midi_value):
    """
    Maps a MIDI value from 21-108 to 11-98 (internally shifted by 10).

    Parameters:
    midi_value (int): The MIDI note number.

    Returns:
    int: The mapped MIDI value.
    """
    if midi_value < 21 or midi_value > 108:
        raise ValueError("MIDI value should be between 21 and 108.")
    return midi_value - 10
    
def note_duration_to_units(duration):
    """
    Converts a note duration (in quarter lengths) to units.

    1 quarter note = 12 units.

    Parameters:
    duration (float): Note duration in quarter lengths.

    Returns:
    int: Duration in units.
    """
    return int(duration * 12)

def process_measure(measure):
    """
    Processes a measure and converts its notes/rests into custom string format.

    Parameters:
    measure (music21.stream.Measure): The measure to process.

    Returns:
    str: Encoded melody segment for the measure.
    """
    melody_segment = ""
    partitions = partition_measure(measure)

    for start_offset, end_offset in partitions:
        section_elements = extract_elements_in_range(measure, start_offset, end_offset)

        for el in section_elements:
            if isinstance(el, note.Note):
                midi_number = map_to_piano_range(el.pitch.midi)
                duration_units = note_duration_to_units(el.quarterLength)
                melody_segment += f"{midi_number}:{duration_units}:"
            elif isinstance(el, note.Rest):
                duration_units = note_duration_to_units(el.quarterLength)
                melody_segment += f"10:{duration_units}:"  # 10 is reserved for rests

    return melody_segment


"""
Process!!! 
"""
file_path = sys.argv[1]
score = converter.parse(file_path)
part = score.parts[0]  # Process only the first part

full_melody = ""
for measure in part.getElementsByClass('Measure'):
    full_melody += process_measure(measure)

# Save to output file
output_file = file_path[:-4] + "_MIDI_representation.txt"
with open(output_file, "w") as f:
    f.write(full_melody)
f.close()
print(f"Melody representation saved to {output_file}")


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
