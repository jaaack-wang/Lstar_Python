'''
- Author: Zhengxiang (Jack) Wang 
- GitHub: https://github.com/jaaack-wang
- Website: https://jaaack-wang.eu.org
- About: Utility functions.
'''
import random
import itertools


def all_words_of_length(length, alphabet):
    '''Returns all possible strings given the string 
    length and an alphabet.'''
    return [''.join(list(b)) for b 
            in itertools.product(
                alphabet, repeat=length)]


def debugger(learner, teacher, alphabet, max_test_len=10):
    if learner("") != teacher(""):
        print("Counterexample: empty string")
        return False
    
    for n in range(1, max_test_len+1):        
        for text in all_words_of_length(n, alphabet):
            l_pred = learner(text)
            t_pred = teacher(text)
            
            if l_pred != t_pred:
                print("Counterexample: ", text)
                return False
    
    print("Test passed. Test range: ", (0, max_test_len))
    return True
