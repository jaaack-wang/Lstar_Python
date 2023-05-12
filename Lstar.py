'''
- Author: Zhengxiang (Jack) Wang 
- GitHub: https://github.com/jaaack-wang
- Website: https://jaaack-wang.eu.org
- About: Lstar algoirthm with a class method for the
         ObservationTable defined in Angluin (1987).
'''
import sys
import pathlib
# import from local script
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from DFA import DFA
from utils import all_words_of_length

from math import log
from collections import defaultdict


class ObservationTable:
    '''A class method to construct an observation table as 
    characterized by Angluin (1987).
    
    Args (initialization):
        - alphabet (set/list/tuple)): can be str if each char
                    stands for a unique symbol in the alphabet
        - teacher (method): a function that returns True or False
        - max_ce_len (int): maximum len of counterexamples to search. 
                            Defaults to None. 
        - max_ce_searches (int): maximum num of searches for 
                            counterexamples. Defaults to 1e+5.
                
    Methods:
        - .get_table_size(): returns the size of the table
        - .get_num_of_queries(): returns the num of membership queries 
            made excluding those made during the equivalence queries.
        - .make_more_consistent(): identifies an inconsistency (if any) 
                and fix it. A single call of this function does not
                gaurantee that the observation table becomes consistent.
        - .make_more_closed(): identifies an instance where the table is not 
                closed and fix it. A single call of this function does not
                gaurantee that the observation table becomes closed.
        - .to_dfa(): converts a closed and consistent (prerequisite!)
                observation table to a corresponding minimal dfa. The 
                converted dfa is accessible via self.dfa.
        - .find_counterexample(): returns an counterexample if it is found. 
        - .resolve_counterexample(ce): resolves an counterexample (i.e., ce) by
                adding all its prefixes into the observation table. 

    Note: To find a counterexample, the observation table makes membership
    queries exhaustively within a length range of counterexamples, constrained 
    by the preset max_ce_searches.
    '''
    
    def __init__(self, alphabet, teacher, 
                 max_ce_len=None, max_ce_searches=1e+5):
        
        self.A = alphabet
        self.T = teacher
        
        self.dfa = None # proposed dfa. initially None
        self.queried = dict() # to avoid making same queries
        
        self.S = {""}
        self.SdotA = set(alphabet)
        self.E = [""] # this is a list!
        
        self.S_rows = defaultdict(tuple)
        self.SdotA_rows = defaultdict(tuple)
        self._fill_S_rows() # initialze S rows
        self._fill_SdotA_rows() # initialze SdotA rows
        
        self.cur_ce_len = 2 # current counterexample len (at least 2)
        self.max_ce_len = self.__get_max_ce_len(max_ce_searches)
        
        # if the max_ce_len will result in more searches, then
        # use the caculated one to avoid exponentially more searches
        if max_ce_len and max_ce_len < self.max_ce_len:
            self.max_ce_len = max_ce_len
    
    def __get_max_ce_len(self, max_ce_searches):
        '''Returns the max_ce_len based on max_ce_searches. 
        The calculation is the reverse use of the closed form
        for the summation of exp(x) for x in (0, n). Here, the
        max_ce_len must start with 2 as all strs of 1 are quiried.'''
        
        A_size = len(self.A)
        
        if A_size == 1:
            return max_ce_iters
        
        m = max_ce_searches
        a_2_n_plus_1 = (m+1+A_size)*(A_size-1)+1
        max_ce_len = log(a_2_n_plus_1, A_size) - 1
        
        # heuristics: rather search for less  
        # than search for exponentially more
        if max_ce_len >= int(max_ce_len) + 0.8:
            max_ce_len = int(max_ce_len) + 1
        else: 
            max_ce_len = int(max_ce_len)
        return max_ce_len
                
    def get_table_size(self):
        '''Returns the size of the extended observation table, 
        which is # of cells filled with membership answers.'''
        num_prefix = len(self.S) + len(self.SdotA)
        return num_prefix * len(self.E)
    
    def get_num_of_queries(self):
        '''Returns the number of (unique) membership queries made.
        This excludes those made during the equivalence queries.'''
        return len(self.queried)
        
    def _fill_row(self, s, table):
        '''Only fill in unfilled cells in a row'''
        row = table[s]
        E = self.E[len(row):]
        if E:
            row += tuple(self._query(s+e) for e in E)        
            table.update({s: row})
    
    def _query(self, s):
        '''Only ask the teacher the unasked queries.'''
        if s in self.queried:
            return self.queried[s]
        
        answer = self.T(s)
        self.queried[s] = answer
        return answer
    
    def _fill_S_rows(self):
        '''Fill in unfilled cells in S rows'''
        for s in self.S:
            self._fill_row(s, self.S_rows)
    
    def _fill_SdotA_rows(self):
        '''Fill in unfilled cells in SdotA rows'''
        for s in self.SdotA:
            self._fill_row(s, self.SdotA_rows)
    
    def make_more_consistent(self):
        '''Makes the observation table more consistent 
        if it is not and returns True. If the table is 
        (i.e., cannot be more) consistent, returns False.'''
        for s1 in self.S:
            row1 = self.S_rows[s1]
            
            for s2 in self.S:
                row2 = self.S_rows[s2]
                
                if s1 != s2 and row1 == row2:
                    for a in self.A:
                        for e in self.E:
                            ae = a + e
                            q1 = self._query(s1 + ae)
                            q2 = self._query(s2 + ae)
                            if q1 != q2:
                                self.E.append(ae)
                                self._fill_S_rows()
                                self._fill_SdotA_rows()

                                return True
    
    def make_more_closed(self):
        '''Makes the observation table more closed 
        if it is not and returns True. If the table is 
        (i.e., cannot be more) closed, returns False.'''
        
        S_states = set(row for row in self.S_rows.values())
        
        for s, row in self.SdotA_rows.items():
            if row not in S_states:
                self.S.add(s)
                self._fill_row(s, self.S_rows)
                
                self.SdotA.remove(s)
                self.SdotA_rows.pop(s)
                for a in self.A:
                    self.SdotA.add(s+a)
                    self._fill_row(s+a, self.SdotA_rows)
                
                return True
    
    def _make_row_to_state_map(self):
        '''Returns a dictionary that maps every row 
        (i.e., equivalence class) with a unique state.'''
        
        # u"\u03BB" ==> λ
        row_to_state = {self.S_rows[""]: u"\u03BB"}        
        for s in sorted(self.S, key=len)[1:]: # skip init state
            row = self.S_rows[s]
            
            if row not in row_to_state:
                row_to_state[row] = s
        
        return row_to_state
    
    def to_dfa(self):
        '''Returns a minimal and complete dfa converted from the
        observation table, which must be closed and consistent.'''
        
        delta = dict()
        states = set()
        final_states = set()
        row_to_state = self._make_row_to_state_map()
        init_state = row_to_state[self.S_rows[""]]
        
        table = self.S_rows.copy()
        table.update(self.SdotA_rows)
        
        # the slicing [1:] --> to ignore the empty string
        for s in sorted(table.keys(), key=len)[1:]:
            prefix, suffix = s[:-1], s[-1]
            prev_q = row_to_state[table[prefix]]
            cur_q = row_to_state[table[s]]
            
            if prev_q in delta:
                if suffix not in delta[prev_q]:
                    delta[prev_q].update({suffix: cur_q})
                else:
                    msg = "Observation table is not consistent!"
                    assert cur_q == delta[prev_q][suffix], msg
            else:
                delta[prev_q] = {suffix: cur_q}

            states.add(prev_q)
            states.add(cur_q)
            if self.queried[prefix]:
                final_states.add(prev_q)
            if self.queried[s]:
                final_states.add(cur_q)
        
        dfa = DFA(self.A, init_state, final_states, states, delta)
        return dfa
    
    def find_counterexample(self):
        '''Return an counterexample if one is found.'''
        
        dfa = self.to_dfa()
        self.dfa = dfa
        
        while True:
            
            if self.cur_ce_len > self.max_ce_len:
                break
                
            for t in all_words_of_length(self.cur_ce_len, self.A):

                true = self.T(t)
                pred = dfa.recognize(t)
                                
                if pred != true:
                    return t
            
            self.cur_ce_len += 1

    
    def resolve_counterexample(self, ce):
        '''Resolve the counterexample by adding all its
        prefixes into the S rows.'''   
        
        for i in range(len(ce)+1, 0, -1):
            # start from the longest prefix to avoid having
            # same prefixes in the S rows and SdotA rows
            prefix = ce[:i]
            if prefix not in self.S:
                self.S.add(prefix)
                self._fill_row(prefix, self.S_rows)
                
                if prefix in self.SdotA:
                    self.SdotA.remove(prefix)
                    self.SdotA_rows.pop(prefix)
                
                for a in self.A:
                    sa = prefix+a
                    if sa not in self.S:
                        self.SdotA.add(sa)
                        self._fill_row(sa, self.SdotA_rows)
                        
                        
def lstar(alphabet, teacher, max_ce_len=None, max_ce_searches=1e+5):
    '''The Lstar algorithm. Returns the observation table when 
    no counterexample can be found. To get the proposed dfa, use
    table.dfa or table.to_dfa().
    
    Note: the teacher can only answer membership query, as it is
    assumed here that the teacher is a black-box system unknown to
    the learner. The equivalence query is answered by making membership
    queries exhaustively within a finite search space, defined by the
    number of possible strings of a given length over a given alphabet, 
    which should not exceed the preset maximum number of iterations. 
    
    Args:
        - alphabet (set/list/tuple)): can be str if each char
                    stands for a unique symbol in the alphabet
        - teacher (method): a function that returns True or False
        - max_ce_len (int): maximum len of counterexamples to search. 
                            Defaults to None. 
        - max_ce_searches (int): maximum num of searches for 
                            counterexamples. Defaults to 1e+5.

    Note: To find a counterexample, the observation table makes membership
    queries exhaustively within a length range of counterexamples, constrained 
    by the preset max_ce_searches.
    '''
    
    table = ObservationTable(alphabet, teacher, 
                             max_ce_len, max_ce_searches)
    
    while True:
        
        # the observation table must be consistent and closed 
        # at the same time before a counterexample is searched
        while True:

            while table.make_more_consistent():
                pass
        
            if table.make_more_closed():
                continue
            else:
                break
        
        ce = table.find_counterexample()
        
        if ce is None:
            return table
        
        table.resolve_counterexample(ce)
