import graphviz
from collections import defaultdict, Counter
import os
import sys
import time
import itertools
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

alphabet = [':']
for i in range(0, 10):
    alphabet.append(str(i))

class TrieNode:
    def __init__(self):
        self.children = {}
        self.count = 0

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, context, symbol):
        node = self.root
        for char in context:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.count += 1
        if symbol not in node.children:
            node.children[symbol] = TrieNode()
        node.children[symbol].count += 1

    def get_counts(self, context):
        node = self.root
        for char in context:
            if char in node.children:
                node = node.children[char]
            else:
                return None
        return node.children

# class ppm:
#     def __init__(self):
        
def construct_trie(sequence, D):
    trie = Trie()
    n = len(sequence)
    for i in range(n):
        context = sequence[max(0, i - D):i]  # if i-D < 0, that means context length is less than D
        symbol = sequence[i]
        trie.insert(context, symbol)
    return trie

def get_contexts(training_data, D):
    contexts = set().union(['']) # EMPTY CONTEXT
    N = len(training_data)
    for k in range(1, D + 1):
        contexts = contexts.union([training_data[t:t + k] for t in range(N - k  + 1)])
    return sorted(contexts)

def unique_symbols(training_data):
    sym = set()
    for c in training_data:
        sym = sym.union([c])
    return sym

def count_occurrences(training_data, D):
    contexts = get_contexts(training_data, D)#get_contexts(training_data, D)
    counts = {context: {sigma: 0 for sigma in alphabet} for context in contexts}
    N = len(training_data)
    for i in range(1, D + 1):
        for j in range(0, N - i):
            s = training_data[j:j + i]
            sigma = training_data[j + i]
            counts[s][sigma] += 1
    return counts

def print_probabilities(probabilities):
    for context, symbols in probabilities.items():
        for sigma, prob in symbols.items():
            if prob >= 1:
                raise "Probability > 1: Please notify the author for this mistake"
            if context == "":
                print(f"P({sigma}) = {prob}")
            else:
                print(f"P({sigma}|{context}) = {prob}")
                
def visualize_trie(trie):
    dot = graphviz.Digraph()
    nodes = [(trie.root, "")]
    idx = 0
    node_ids = {trie.root: str(idx)}
    dot.node(str(idx), "root")
    while nodes:
        node, context = nodes.pop()
        parent_id = node_ids[node]
        for symbol, child in node.children.items():
            idx += 1
            child_id = str(idx)
            node_ids[child] = child_id
            dot.node(child_id, f"{symbol} ({child.count})")
            dot.edge(parent_id, child_id, label=symbol)
            nodes.append((child, symbol))
    return dot
def traverse_path(trie, path):
    node = trie.root
    counters = []
    for char in path:
        if char in node.children:
            node = node.children[char]
            counters.append((char, node.count))
        else:
            return None  # Path does not exist in the trie
    return counters

def context_children_and_counters(trie, context, symbol, escape):
    node = trie.root
    for char in context:
        if char in node.children:
            node = node.children[char]
        else:
            return (0,0)
        
    end_of_context = node
    #print(list(node.children.keys()))
    total = 0 
    for child in list(node.children.keys()):
        if escape and child == symbol:
            continue # COMMENT THIS IF STATEMENT IF YOU DON'T WANT TO USE THE EXCLUSION MECHANISM
        get_count = node.children[child]
        total += int(get_count.count)
    toReturn = (len(list(end_of_context.children.keys())), total)
    return toReturn 

def escape_prob(trie, context, sigma, training_data):
    prob = 1
    temp = context
    counters = traverse_path(trie, temp+sigma)
    
    if counters != None and context != "":
        new, new_total_count = context_children_and_counters(trie, context, sigma, False)
        return counters[-1][1] / (new + new_total_count) 
    if context == "":
        return 1/len(alphabet)
    new, new_total_count = context_children_and_counters(trie, context, sigma, True)
    if ((new, new_total_count) == (0,0)):
        return 1/len(alphabet)
    prob *= new / (new+new_total_count)
    return prob * escape_prob(trie, temp[1:], sigma, training_data) # recurse on shorter context
      
def compute_ppm(counts, training_data, D):
    trie = construct_trie(training_data, D)
    probs = counts # same format, but just change the value from counts to probability
    for s in get_contexts(training_data, D):
        for sigma in alphabet:
            probs[s][sigma] = escape_prob(trie, s, sigma, training_data)
            if int(probs[s][sigma]) == 0:
                probs[s][sigma] = 1/len(alphabet) #len(unique_symbols(training_data))
    return probs

# sequence = sys.argv[2]
# D = int(sys.argv[1])  # Set context size
# counts = count_occurrences(sequence, D)
# trie = construct_trie(sequence, D)

# dot = visualize_trie(trie)

# # Display the nodes with counters
# # print("Nodes with counters:")
# # for node in nodes_with_counters:
# #     print(node)
# # Render the trie visualization
# dot.render('trie', format='png', view=True)

# start = time.time()
# print(compute_ppm(counts, sequence, D))
# end = time.time()
# print(f"Time elapsed = {end - start} seconds")