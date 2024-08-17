Introduction
===========

This repository is based on the paper *"Using Variable Order Markov Model in Measuring Temporal Dynamics of Melodic Complexity in Jazz Improvisation"* by Philip Pincencia (2024).


Project sturcture:

```
| Paper_and_Conference_Slides
  | Paper.pdf
  | Conference_Slides.pdf
| LaTeX files   % ONLY REPO OWNER CAN ACCESS
  | # HIDDEN
| 
| chord_parser.cpp
| 
| Harmony_Score_Approach
  | Hscore_general.py
|
| Chroma_Key_Approach
  | chroma.py
|
| Variable_Order_Markov_Model_Approach
  | midi_rep.py
  | createdistribution.py
  | vomm_ppm.py
  | sliding_window.py
|
| run.sh
```

<h1>Details</h1>

Here I detail the steps of each of the approaches

Variable Order Markov Model (VOMM) Approach
---
I used the VOMM algorithm called Predict by Partial Match (PPM), which is implemented as a Multiway Trie. This is based on the paper *"On Prediction Using Variable
Order Markov Models"* by Ron Begleiter, Ran El-Yaniv, and Golan Yona in
the Journal of Artificial Intelligence Research 22 (2004) 385-421.

To learn the PPM model consists of several steps:

1. Convert to training sequence: `xml` file is parsed by `midi_rep.py` 
```{python}
#

```
2. Instantiate an object of the appropriate class. Example:
```{python}
import vomm
my_model = vomm.ppm()
```
3. Learn a model from the data.
```{python}
import vomm
my_model  = vomm.ppm()
my_model.fit(training_data, d=2)
```

Internals
=========
Denote $q$ as the training sequence.\
Learning a model consists of

1. Construct the set $S$ consisting of contexts of length at most $D$ in the training sequence. Precisely, $S=\{s\in q ~|~|s|\leq D\}$.
2. Building the Mutliway Trie $\mathcal{T}$ 
2. Estimating the probability distribution $\hat P(\sigma|s)$ for each context $s$ and symbol $\sigma$ in the alphabet.

After creating an object $x$ of whichever class you chose and *fitted*
to the training data, the object $x$ will have several attributes of
which 3 are important:

* pdf_dict -- this is a dictionary with key context $s$ and value the probability distribution $Pr(|s)$.
* logpdf_dict -- it's similar to pdf_dict, but the value is the log of the probability distribution.
* context_child -- this is a dictionary with key context $s$ and value
  the set of possible longer children contexts $\{ xs \}$ which are in
  the set of contexts recovered in step 1. This dictionary speeds up
  finding the largest context $s$ which matches the tail end of a
  sequence of symbols.

Future Implementation
===========
- Develop a web server to let users drop in an `xml` file and the associated chord changes pasted from WJazzDatabase
- Animate the sliding window analysis to better understand the how the measure behaves
- Convert `music21`-independent python files to `C++` to speed things up.