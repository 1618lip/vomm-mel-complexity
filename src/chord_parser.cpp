// Parse Chords from text file, contents copied from WJazz
// Author: Philip Pincencia
// Last Updated: July 1st, 2024

#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <regex>

using namespace std;

// Character-based chord naming conversion
unordered_map<char, string> changeNaming {
    {'-', "min"}, {'j', "maj"}, {'o', "dim"},
    {'+', "aug"}, {'b', "-"}, {'m', "min"}
    // TODO: Add more naming conversion rules
};

// --- Helper Functions --- //

// Trim '|' characters from the edges
string trim(const string& str) {
    size_t first = str.find_first_not_of('|');
    if (first == string::npos) return "";
    size_t last = str.find_last_not_of('|');
    return str.substr(first, last - first + 1);
}

// Split string by delimiter
vector<string> split(const string& str, char delimiter) {
    vector<string> tokens;
    stringstream ss(str);
    string token;
    while (getline(ss, token, delimiter)) {
        tokens.push_back(trim(token));
    }
    return tokens;
}

// Extract chords using regex
vector<string> splitChords(const string& measure, bool withSpace) {
    string pattern = withSpace
        ? R"(\s|([A-G](#|b)?(-|m|j|o|\+|sus|add)?([1-9])?(\/ [A-G](#|b)?)?))"
        : R"(([A-G](#|b)?(-|m|j|o|\+|sus|add)?([1-9])?(\/ [A-G](#|b)?)?))";
    regex chordRegex(pattern);

    vector<string> chords;
    for (auto it = sregex_iterator(measure.begin(), measure.end(), chordRegex);
         it != sregex_iterator(); ++it) {
        chords.push_back(it->str());
    }
    return chords;
}

// Parse a measure into exactly 4 beats
vector<string> parseMeasure(const string& measure) {
    vector<string> chordsWithSpace = splitChords(measure, true);
    vector<string> chords = splitChords(measure, false);
    vector<string> beats(4, "");

    size_t n = chords.size();
    if (n == 1) beats = {chords[0], chords[0], chords[0], chords[0]};
    else if (n == 2) beats = {chords[0], chords[0], chords[1], chords[1]};
    else if (n == 3) {
        int spaceIdx = 0;
        for (int i = 0; i < 4; i++) {
            if (chordsWithSpace[i] == " ") {
                spaceIdx = i;
                break;
            }
        }
        if (spaceIdx == 1) beats = {chords[0], chords[0], chords[1], chords[2]};
        else if (spaceIdx == 2) beats = {chords[0], chords[1], chords[1], chords[2]};
        else if (spaceIdx == 3) beats = {chords[0], chords[1], chords[2], chords[2]};
    }
    else if (n == 4) beats = chords;

    return beats;
}

// Check if a measure is empty
bool isEmptyMeasure(const vector<string>& measure) {
    for (const auto& beat : measure) {
        if (!beat.empty()) return false;
    }
    return true;
}

// Apply chord naming conversion
string changeChordNaming(const string& chord) {
    string newName;
    for (char ch : chord) {
        if (changeNaming.count(ch)) newName += changeNaming[ch];
        else newName += ch;
    }
    return newName;
}

// --- Main Function --- //

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "ERROR: Exactly one input file expected." << endl;
        return 1;
    }

    ifstream inputFile(argv[1]);
    if (!inputFile.is_open()) {
        cerr << "ERROR: Could not open input file." << endl;
        return 1;
    }

    // Read file contents in reverse for correct output order
    string input, line;
    while (getline(inputFile, line)) {
        input = line + '\n' + input;
    }

    vector<string> lines = split(input, '\n');
    unordered_map<string, vector<vector<string>>> sections;

    for (const auto& line : lines) {
        if (line.empty()) continue;

        size_t colonPos = line.find(':');
        if (colonPos == string::npos) continue;

        string section = line.substr(0, colonPos);
        string chords = trim(line.substr(colonPos + 1));

        if (chords.front() == '|') chords = chords.substr(1);
        if (chords.back() == '|') chords.pop_back();

        vector<string> measures = split(chords, '|');
        vector<vector<string>> parsedMeasures;

        for (const auto& measure : measures) {
            auto beats = parseMeasure(measure);
            if (!isEmptyMeasure(beats)) parsedMeasures.push_back(beats);
        }

        if (!parsedMeasures.empty()) {
            sections[section] = parsedMeasures;
        }
    }

    // Output results
    string outputFilename = string(argv[1]).substr(0, string(argv[1]).find(".txt")) + "_parsed.txt";
    ofstream outputFile(outputFilename);

    for (const auto& section : sections) {
        outputFile << section.first << "\n";
        for (const auto& measure : section.second) {
            outputFile << "[";
            for (size_t i = 0; i < measure.size(); ++i) {
                outputFile << changeChordNaming(measure[i]);
                if (i != measure.size() - 1) outputFile << ", ";
            }
            outputFile << "], ";
        }
        outputFile << "\n";
    }

    outputFile.close();

    cout << "Success! Output written to " << outputFilename << endl;
    return 0;
}
