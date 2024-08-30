// Parse Chords from text file, whose contents are directly copy-pasted from WJazz
// Made by Philip Pincencia
// Last Updated: July 1st, 2024
#include <iostream>
#include <sstream>
#include <fstream>

#include <vector>
#include <string>
#include <unordered_map>
#include <regex>


using namespace std;
auto changeNaming  = unordered_map<char, string>
                            {
                                {'-', "min"}, 
                                {'j', "maj"},
                                {'o', "dim"},
                                {'+', "aug"}, 
                                {'b', "-"},
                                {'m', "min"}
                                // TODO: add more naming conversion rules
                            };
// Trim whitespace from a string
string trim(const string& str) {
    size_t first = str.find_first_not_of('|');
    if (first == string::npos) return "";
    size_t last = str.find_last_not_of('|');
    return str.substr(first, last - first + 1);
}

// Split a string by a delimiter and return a vector of strings
vector<string> split(const string& str, char delimiter) {
    vector<std::string> tokens;
    stringstream ss(str);
    string token;
    while (getline(ss, token, delimiter)) {
        tokens.push_back(trim(token));
    }
    return tokens;
}
// Use regular expressions to identify and split chords
vector<string> splitChords(const string& measure, bool withspace) {
    vector<string> chords;
    string rgx;
    if (withspace) {
        //rgx = R"(\s|([A-G](#|b)?(-|m|j|o|\+|sus|add)?([1-9])?((#|b)([1-9]|1[012]))?(\/[A-G](#|b)?)?))";
        rgx = R"(\s|([A-G](#|b)?(-|m|j|o|\+|sus|add)?([1-9])?(\/[A-G](#|b)?)?))";
    }
    else {
        //rgx = R"(([A-G](#|b)?(-|m|j|o|\+|sus|add)?([1-9])?((#|b)([1-9]|1[012]))?(\/[A-G](#|b)?)?))";
        rgx = R"(([A-G](#|b)?(-|m|j|o|\+|sus|add)?([1-9])?(\/[A-G](#|b)?)?))";
    }
    regex chordRegex(rgx);
    
    sregex_iterator words_begin = sregex_iterator(measure.begin(), measure.end(), chordRegex);
    sregex_iterator words_end = sregex_iterator();

    for (sregex_iterator i = words_begin; i != words_end; i++) {
        chords.push_back(i->str());
    }
    return chords;
}

// Parse measures into exactly 4 beats
vector<string> parseMeasure(const string& measure) {
    vector<string> chordswspace = splitChords(measure, true);
    vector<string> beats(4, ""); // Initialize with 4 empty beats
    vector<string> chords = splitChords(measure, false);
    size_t numChords = chords.size();
    if (numChords == 1) {
        beats = { chords[0], chords[0], chords[0], chords[0] }; // Repeat the single chord
    } else if (numChords == 2) {
        beats = { chords[0], chords[0], chords[1], chords[1] }; // Two chords, each gets two beats
    } else if (numChords == 3) {
        // Handle the case with three chords and spaces
        int spaceIndex = 0;
        for (int i = 0; i < 4; i++) {
            if (chordswspace[i] == " ") {
                spaceIndex = i;
                break;
            }
        }
        if (spaceIndex == 1) {
            // First chord is held for two beats
            beats = { chords[0], chords[0], chords[1], chords[2] };
        } else if (spaceIndex == 2) {
            // Second chord is held for two beats
            beats = { chords[0], chords[1], chords[1], chords[2] };
        } else if (spaceIndex == 3) {
            // Third chord is held for two beats
            beats = { chords[0], chords[1], chords[2], chords[2] };
        } 
    } else if (numChords == 4) {
        beats = chords; // Four chords, each gets one beat
    }

    return beats;
}

// Function to check if a measure is empty
bool isEmptyMeasure(const vector<string>& measure) {
    for (const auto& beat : measure) {
        if (!beat.empty()) return false;
    }
    return true;
}

string changeChordNaming(const string& chord) {
    string newName = "";
    for (size_t i = 0; i < chord.size(); ++i) {
        //cout << (chord[i]);
        if (changeNaming.count(chord[i]) != 0) {
            // Apply the mapping for the character (e.g., 'b' -> '-')
            newName += changeNaming[chord[i]];

            // // // Check if the next character is a digit, and if so, move it to after the replacement
            // if (i + 1 < chord.length() && isdigit(chord[i + 1])) {
            //     newName += chord[i + 1];
            //     ++i; // Skip the digit in the next iteration
            // }
        } else {
            // Otherwise, just add the character as is
            newName += chord[i];
        }
    }
    return newName;
}
int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "ERROR: There should be just one input file." << endl; 
        exit(1);
    }
    // Open the input file
    ifstream inputFile(argv[1]); 
  
    // Check if the file is successfully opened 
    if (!inputFile.is_open()) { 
        cerr << "Error opening your file!" << endl; 
        return 1; 
    } 

    string line, input;
    while (getline(inputFile, line)) {
        input = line + '\n' + input; 
        // we do it in reverse so the output file is ordered
    }

    char delim = '\n';
    // Split the input into lines
    vector<std::string> lines = split(input, delim);

    // Map to store sections with their measures
    unordered_map<string, vector<vector<string>>> sections; // vector of vector of strings :((

    for (const auto& line : lines) {
        if (line.empty()) continue;

        // Split line into section name and chords
        size_t colonPos = line.find(':');
        string section = line.substr(0, colonPos);
        string chords = line.substr(colonPos + 1);

        // Remove leading and trailing bars and spaces
        chords = trim(chords);
        if (chords.front() == '|') chords = chords.substr(1);
        if (chords.back() == '|') chords.pop_back();

        // Split the chords by measures
        vector<std::string> measures = split(chords, '|');
        vector<std::vector<std::string>> parsedMeasures;

        for (const auto& measure : measures) {
            // Parse each measure into exactly 4 beats
            vector<string> beats = parseMeasure(measure);

            // Skip empty measures
            if (!isEmptyMeasure(beats)) {
                parsedMeasures.push_back(beats);
            }
        }

        if (!parsedMeasures.empty()) {
            sections[section] = parsedMeasures;
        }
    }

    // Output the sections in a format that a Python file can read
    // get name of the original file
    string getName = argv[1];
    getName = getName.substr(0, getName.find(".txt"));
    ofstream outputFile;
    outputFile.open(getName + "_parsed.txt");
    for (const auto& section : sections) {
        outputFile << section.first << "\n";
        for (const auto& measure : section.second) {
            outputFile << "[";
            for (size_t i = 0; i < measure.size(); ++i) {
                outputFile <<  changeChordNaming(measure[i]);
                if (i != measure.size() - 1) outputFile << ", ";
            }
            outputFile << "], ";
        }
        outputFile << "\n";
    }
    
    outputFile.close();

    cout << "Success!\n";
    return 0;
}