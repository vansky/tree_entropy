#cat grammar | python calc-entropy.py
# grammar: a pre-trained grammar file (in a form model.CondModel can read)

########################################
#
# Calculates the entropy of a grammar conditioned on a given 'root' category
#
# This permits easy comparison between minimally-paired grammars
#
########################################

import math
import re
import sys
from model import Model, CondModel

########################################
#
# User-defined variables
#
########################################

start_cat = ['V&gN'] # The category/categories that serve as the 'root(s)' of the grammar (all trees are generated from these roots)
NORMALIZE = False # Should the priors be renormalized after each pass?
VERBOSE = False # Should there be output after each breadth-first pass over the grammar?
K_Low = 20 # The lower bound on K (The number of breadth-first passes over the grammar)
K_High = 21 # The upper bound on K (The number of breadth-first passes over the grammer)

########################################
#
# Functions
#
########################################

def normalize(indict):
    tot = 0.0
    for cat in indict:
        tot += indict[cat]
    for cat in indict:
        indict[cat] /= tot

def calc_entropy(K=20):
    global grammar
    global NORMALIZE
    global VERBOSE
    global start_cat
    cat_priors = Model('Prior')
    for cat in start_cat:
      cat_priors[cat] = 1
    normalize(cat_priors)
    for k in range(0,K):
        if VERBOSE:
          sys.stderr.write('Iterating ('+str(k)+'/'+str(K)+'): ')
          sys.stderr.write(str(cat_priors.keys())+'\n')
        tot = 0.0
        if NORMALIZE:
            normalize(cat_priors)
        cat_likes = Model('MarginL') #actually the new prior built from likelihoods
        for parent in cat_priors:
            for child in grammar[parent]:
                cat_likes[child] += grammar[parent][child]*cat_priors[parent]/3.0
        cat_priors = cat_likes.copy()

    # sum over the probability of each category to obtain the overall likelihood of the
    grammar_prob = 0.0
    for cat in cat_priors:
        grammar_prob += cat_priors[cat]
    
    # output the entropy of the grammar
    sys.stderr.write(str(-math.log(grammar_prob))+'\n')
    sys.stdout.write(str(-math.log(grammar_prob))+'\n')


########################################
#
#  Main
#
########################################

sys.stderr.write('Loading grammar\n')

# init grammar
grammar = CondModel('G')

# load grammar
for s in sys.stdin:
    m = re.search('([^ ][^ ]*) -> ([^ ][^ ]*) ([^ ][^ ]*) ([^ ][^ ]*)',s)
    if m is not None:
        # to avoid double-generation of rules, assume a parent has a 2/3 change of generating 2 children and a 1/2 chance of each child ordering
        grammar[m.group(1)][m.group(2)] = float(m.group(4))/3.0
        grammar[m.group(1)][m.group(3)] = float(m.group(4))/3.0
    else:
      m = re.search('([^ ][^ ]*) -> ([^ ][^ ]*) ([^ ][^ ]*)',s)
      if m is not None:
          # to avoid double-generation of rules, assume a parent has a 1/3 chance of generating 1 child
          grammar[m.group(1)][m.group(2)] = float(m.group(3))/3.0

sys.stderr.write('Normalizing grammar\n')
# ensure grammar is normalized
grammar.normalize()

########## iterate!

sys.stderr.write('Using root categories: '+str(start_cat)+'\n')

sys.stderr.write('Iteratively calculating grammar probability\n')

for K in range(K_Low,K_High):
    calc_entropy(K)
