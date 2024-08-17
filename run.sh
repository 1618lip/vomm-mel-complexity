#!/bin/bash


file = "$1"
./a.exe "Unparsed_chordchanges/$file.txt" 
&& python midi_rep.py $file.mxl
&& python sliding_window.py $2 $3 "$file_MIDI_representation.txt" "Parsed_chordchanges/$file_parsed.txt"
