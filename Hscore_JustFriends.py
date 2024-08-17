from Hscore_general import *

file_path = str(sys.argv[1])
score = converter.parse(file_path) 

file = r"" + sys.argv[2]
chord_changes = readFile(file)

# Extract notes and partition measure
for part in score.parts:
    """
    In this part, you have to edit the chord changes by yourself to fit the length of the solo.
    No way to automate this :(((
    """
    for i in range(0, 8):
            chord_changes.append(chord_changes[i])

    """"""
    print(chord_changes)
    for measure in part.getElementsByClass('Measure'):
        measure_number = measure.measureNumber
        partitions = partition_measure(measure)
        prev = 0
        for i, (start_offset, end_offset) in enumerate(partitions):
            section_elements = extract_elements_in_range(measure, start_offset, end_offset)
          
            if not isinstance(chord_changes[measure_number-1][i], list):
                #chord_changes[measure_number-1][i] = 0
                continue
            count = 0
            avg = 0
            for el in section_elements:
                s = chord_changes[measure_number-1][i]
                if isinstance(el, note.Note):
                    #formatted_elements.append(f'({el.nameWithOctave}, {el.quarterLength})')
                    #print(isinstance(chord_changes[measure_number-1][i], list))
                    s.append(note_to_frequency(el.nameWithOctave))
                    avg += harmony_score(s)
                    count = count + 1
                elif isinstance(el, note.Rest):
                    #formatted_elements.append(f'(R, {el.quarterLength})')
                    continue
            #print(isinstance(chord_changes[measure_number-1][i], list))
            #s = chord_changes[measure_number-1][i]
            if count == 0:
                if i == 0:
                    chord_changes[measure_number-1][i] = chord_changes[measure_number-2][3]
                else:   
                    chord_changes[measure_number-1][i] = chord_changes[measure_number-1][i-1]
            else:
                chord_changes[measure_number-1][i] = (avg / count)*math.log(count*math.e)
            
            
            
            # Print formatted elements for the partition
            # formatted_elements_str = ", ".join(formatted_elements)
            # print(f'Measure {measure_number}, Partition {i + 1}: {{{formatted_elements_str}}}')
            
    break
print(chord_changes)

measures = []
hscore = []
for m in range(0, len(chord_changes)):
    avg = 0
    for n in range(0, len(chord_changes[m])):
        avg = avg+float(chord_changes[m][n])
        x = m+1 + n/4
        measures.append(x)
        hscore.append(float(chord_changes[m][n]))
    avg = avg / len(chord_changes[m])
    # measures.append(m+1)
    # hscore.append(avg)
#plt.ion()
plt.figure(figsize=(12, 6))
plt.plot(measures, hscore, '-o')

plt.xlabel('Measure Number')
plt.ylabel('Harmonic Score')
plt.title('Harmonic Score per measure')
plt.grid(True)
plt.show()

sys.exit(0)