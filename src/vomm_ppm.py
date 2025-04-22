# @author Philip Pincencia

import sys
import math
import re
import time
import os
import itertools
import graphviz
from collections import defaultdict, Counter

# Configure Graphviz path
os.environ["PATH"] += os.pathsep + r"C:\\Program Files\\Graphviz\\bin"

# --- Global Alphabet Setup --- #
alphabet = [":"] + [str(i) for i in range(10)]

# --- Trie Data Structure --- #

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

# --- Helper Functions for PPM --- #

def construct_trie(sequence, D):
    trie = Trie()
    n = len(sequence)
    for i in range(n):
        context = sequence[max(0, i - D):i]
        symbol = sequence[i]
        trie.insert(context, symbol)
    return trie

def get_contexts(training_data, D):
    contexts = set([''])
    N = len(training_data)
    for k in range(1, D + 1):
        contexts.update(training_data[t:t+k] for t in range(N - k + 1))
    return sorted(contexts)

def unique_symbols(training_data):
    return set(training_data)

def count_occurrences(training_data, D):
    contexts = get_contexts(training_data, D)
    counts = {context: {sigma: 0 for sigma in alphabet} for context in contexts}
    N = len(training_data)
    for i in range(1, D + 1):
        for j in range(N - i):
            context = training_data[j:j+i]
            symbol = training_data[j+i]
            counts[context][symbol] += 1
    return counts

def print_probabilities(probabilities):
    for context, symbols in probabilities.items():
        for sigma, prob in symbols.items():
            if prob >= 1:
                raise ValueError("Probability > 1: Please notify the author.")
            if context == "":
                print(f"P({sigma}) = {prob:.4f}")
            else:
                print(f"P({sigma}|{context}) = {prob:.4f}")

# --- Trie Visualization --- #

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

# --- Traversal and Context Management --- #

def traverse_path(trie, path):
    node = trie.root
    counters = []
    for char in path:
        if char in node.children:
            node = node.children[char]
            counters.append((char, node.count))
        else:
            return None
    return counters

def context_children_and_counters(trie, context, symbol, escape):
    node = trie.root
    for char in context:
        if char in node.children:
            node = node.children[char]
        else:
            return (0, 0)

    total = 0
    for child_symbol, child_node in node.children.items():
        if escape and child_symbol == symbol:
            continue
        total += child_node.count

    return (len(node.children), total)

# --- Escape Probability Computation --- #

def escape_prob(trie, context, sigma, training_data):
    temp = context
    counters = traverse_path(trie, temp + sigma)

    if counters and context != "":
        new, total_count = context_children_and_counters(trie, context, sigma, False)
        return counters[-1][1] / (new + total_count)

    if context == "":
        return 1 / len(alphabet)

    new, total_count = context_children_and_counters(trie, context, sigma, True)
    if (new, total_count) == (0, 0):
        return 1 / len(alphabet)

    return (new / (new + total_count)) * escape_prob(trie, temp[1:], sigma, training_data)

# --- Final PPM Computation --- #

def compute_ppm(counts, training_data, D):
    trie = construct_trie(training_data, D)
    probs = counts.copy()

    for context in get_contexts(training_data, D):
        for sigma in alphabet:
            probs[context][sigma] = escape_prob(trie, context, sigma, training_data)
            if probs[context][sigma] == 0:
                probs[context][sigma] = 1 / len(alphabet)

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
