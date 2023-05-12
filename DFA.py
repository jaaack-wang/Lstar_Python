'''
- Author: Zhengxiang (Jack) Wang 
- GitHub: https://github.com/jaaack-wang
- Website: https://jaaack-wang.eu.org
- About: A simple DFA class method that can answer the 
        membership of a given string and visualize the dfa.
'''
import json
from collections import defaultdict

try:
    from graphviz import Digraph
except:
    print("\"graphviz\" not installed, which is " \
          "needed if you want to visualize the dfa.")


class DFA:
    '''
    A simple DFA class method that can answer the membership
    of a given string and visualize the dfa.
    
    Args (initialization):
        - alphabet (set/list/tuple)): can be str if each char
                    stands for a unique symbol in the alphabet
        - init_state (str): the initial state
        - final_states (set/list/tuple): final states
        - states (set/list/tuple): all the states
        - delta (dict): the transition table with a nested 
                     dictionary structure: {q: {a: next_q}},
                     where q: the current state, a: the input 
                     symbol, and next_q: the next state. 
                     
    ############################
    Example usage:
    ############################
    
    # initialize a dfa which recognizes even numbers of a and b
    > alphabet = "ab"
    > init_state = "λ"
    > final_states = ["λ"]
    > states = set(["λ", "a", "b", "ab"])
    > delta = {"λ": {"a": "a", "b": "b"}, 
               "a": {"a": "λ", "b": "ab"}, 
               "b": {"a": "ab", "b": "λ"}, 
               "ab": {"a": "b", "b": "a"},}
    > dfa = DFA(alphabet, init_state, final_states, states, delta)
    
    # two basic functions that comes with the DFA class 
    
    > dfa.recognize("ababa") # check the membership of a string 
    > dfa.visualize() # visualize the dfa 
    '''

    def __init__(self, alphabet, init_state, 
                 final_states, states, delta):
        
        self.A = alphabet
        self.q0 = init_state
        self.F = final_states
        self.Q = states
        self.d = delta
    
    def next_state(self, q, a):
        '''The state transition function. Returns the 
        next state given the current state and input 
        symobl, both of which must be known.'''
        
        if not a: # when a is an empty string
            return q
        
        assert q in self.Q, f"Unknown state: {q}"
        assert a in self.A, f"Unknown symbol: {a}"
        return self.d[q][a]
    
    def is_final(self, q):
        return q in self.F
    
    def recognize(self, string=""):
        q = self.q0

        if not string:
            return self.is_final(q)
        
        for sym in string:
            q = self.next_state(q, sym)
        
        return self.is_final(q)
    
    def visualize(self, fname=None, format="pdf"):
        '''Returns a directed graph that visualizes the 
        dfa. To save the graph, specify a file name or path
        with file format specified in the format argment. 
        Possible format: https://graphviz.org/docs/outputs/.
        '''
        graph = Digraph(graph_attr={"rankdir": "LR"}, 
                        edge_attr={"arrowhead": "vee", })
        graph.attr('node', shape='circle')
        graph.node("start ", shape="plain")
        
        Q = sorted(self.Q)
        Q.remove(self.q0)
        Q = [self.q0] + Q
        
        for q in Q:
            graph.node(str(q), q, shape="doublecircle" 
                       if q in self.F else None)
        
        graph.edge("start ", str(self.q0))
        
        for q in Q:
            
            labels_map = defaultdict(list)
            
            for a in self.A:
                next_q = self.d[q][a]
                labels_map[next_q].append(a)
                
            for next_q, labels in labels_map.items():
                graph.edge(str(q), str(next_q), label=", ".join(labels))
        
        if fname:
            graph.render(filename=fname, format=format, cleanup=True)
        return graph
    
    def __len__(self):
        return len(self.d)
    
    def __repr__(self):
        out = "(DFA\n\nAlphabet:{}\n\nInit state: {}\n\n"
        out += "Final states: {}\n\nStates: {}\n\nDelta:\n{}\n)"
        out = out.format(self.A, self.q0, self.F, sorted(self.Q), 
                         json.dumps(self.d, indent=4, ensure_ascii=False))
        return out
