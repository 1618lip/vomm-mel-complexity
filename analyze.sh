#!/bin/bash

echo What is the name of the song you want to analyze?

read -p 'File Name: ' file

echo 'Context size'
read -p 'Max # of notes you want as context (D): ' D
read -p '# of beats you want as context (must be greater than D): ' W

./src/chord_parser.exe "examples/${file}/${file}.txt" && \
python src/midi_rep.py "examples/${file}/${file}.mxl" \
&& python src/sliding_window.py "$D" "$W" "examples/${file}/${file}_MIDI_representation.txt"
