tree_entropy
============

Calculates the entropy of a grammar conditioned on a given 'root' category  

This permits easy comparison between minimally-paired grammars

To use
===========

Train the grammars you wish to use and put them in the following format:  
    A -> B = LogProb
    A -> B C = LogProb

Only give one rule per line.