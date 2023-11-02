from copy import deepcopy
from regex_validation import is_valid_regex
import os

class RegexNode:

    @staticmethod
    def trim_brackets(regex):
        while regex[0] == '(' and regex[-1] == ')' and is_valid_regex(regex[1:-1]):
            regex = regex[1:-1]
        return regex
    
    @staticmethod
    def is_concat(c):
        return c == '(' or RegexNode.is_letter(c)
    
    @staticmethod
    def is_letter(c):
        return c in alphabet

    def __init__(self, regex):
        self.nullable = None
        self.firstpos = []
        self.lastpos = []
        self.item = None
        self.position = None
        self.children = []

        if DEBUG:
            print('Current : '+regex)

        if len(regex) == 1 and self.is_letter(regex):

            self.item = regex

            if use_lambda:
                if self.item == lambda_symbol:
                    self.nullable = True
                else:
                    self.nullable = False
            else:
                self.nullable = False
            return

        kleene = -1
        or_operator = -1
        concatenation = -1
        i = 0


        while i < len(regex):
            if regex[i] == '(':

                bracketing_level = 1

                i+=1
                while bracketing_level != 0 and i < len(regex):
                    if regex[i] == '(':
                        bracketing_level += 1
                    if regex[i] == ')':
                        bracketing_level -= 1
                    i+=1
            else:
                i+=1
            
            if i == len(regex):
                break


            if self.is_concat(regex[i]):
                if concatenation == -1:
                    concatenation = i
                continue

            if regex[i] == '*':
                if kleene == -1:
                    kleene = i
                continue

            if regex[i] == '+':
                if or_operator == -1:
                    or_operator = i
        
        if or_operator != -1:

            self.item = '+'
            self.children.append(RegexNode(self.trim_brackets(regex[:or_operator])))
            self.children.append(RegexNode(self.trim_brackets(regex[(or_operator+1):])))
        elif concatenation != -1:

            self.item = '.'
            self.children.append(RegexNode(self.trim_brackets(regex[:concatenation])))
            self.children.append(RegexNode(self.trim_brackets(regex[concatenation:])))
        elif kleene != -1:

            self.item = '*'
            self.children.append(RegexNode(self.trim_brackets(regex[:kleene])))

    def calc_functions(self, pos, followpos):
        if self.is_letter(self.item):

            self.firstpos = [pos]
            self.lastpos = [pos]
            self.position = pos

            followpos.append([self.item,[]])
            return pos+1
 
        for child in self.children:
            pos = child.calc_functions(pos, followpos)


        if self.item == '.':

            if self.children[0].nullable:
                self.firstpos = sorted(list(set(self.children[0].firstpos + self.children[1].firstpos)))
            else:
                self.firstpos = deepcopy(self.children[0].firstpos)

            if self.children[1].nullable:
                self.lastpos = sorted(list(set(self.children[0].lastpos + self.children[1].lastpos)))
            else:
                self.lastpos = deepcopy(self.children[1].lastpos)

            self.nullable = self.children[0].nullable and self.children[1].nullable

            for i in self.children[0].lastpos:
                for j in self.children[1].firstpos:
                    if j not in followpos[i][1]:
                        followpos[i][1] = sorted(followpos[i][1] + [j])

        elif self.item == '+':

            self.firstpos = sorted(list(set(self.children[0].firstpos + self.children[1].firstpos)))

            self.lastpos = sorted(list(set(self.children[0].lastpos + self.children[1].lastpos)))

            self.nullable = self.children[0].nullable or self.children[1].nullable

        elif self.item == '*':

            self.firstpos = deepcopy(self.children[0].firstpos)

            self.lastpos = deepcopy(self.children[0].lastpos)

            self.nullable = True

            for i in self.children[0].lastpos:
                for j in self.children[0].firstpos:
                    if j not in followpos[i][1]:
                        followpos[i][1] = sorted(followpos[i][1] + [j])

        return pos

    def write_level(self, level):
        print(str(level) + ' ' + self.item, self.firstpos, self.lastpos, self.nullable, '' if self.position == None else self.position)
        for child in self.children:
            child.write_level(level+1)

class RegexTree:

    def __init__(self, regex):
        self.root = RegexNode(regex)
        self.followpos = []
        self.functions()
    
    def write(self):
        self.root.write_level(0)

    def functions(self):
        positions = self.root.calc_functions(0, self.followpos)   
        if DEBUG == True:
            print(self.followpos)
    
    def toDfa(self):

        def contains_hashtag(q):
            for i in q:
                if self.followpos[i][0] == '#':
                    return True
            return False

        M = [] 
        Q = [] 
        V = alphabet - {'#', lambda_symbol if use_lambda else ''} 
        d = [] 
        F = [] 
        q0 = self.root.firstpos

        Q.append(q0)
        if contains_hashtag(q0):
            F.append(Q.index(q0))
        
        while len(Q) - len(M) > 0:

            q = [i for i in Q if i not in M][0]

            d.append({})

            M.append(q)

            for a in V:

                U = []

                for i in q:

                    if self.followpos[i][0] == a:

                        U = U + self.followpos[i][1]
                U = sorted(list(set(U)))

                if len(U) == 0:

                    continue
                if U not in Q:
                    Q.append(U)
                    if contains_hashtag(U):
                        F.append(Q.index(U))
                #d(q,a) = U
                d[Q.index(q)][a] = Q.index(U)
        
        return Dfa(Q,V,d,Q.index(q0),F)

        
class Dfa:

    def __init__(self,Q,V,d,q0,F):
        self.Q = Q
        self.V = V
        self.d = d
        self.q0 = q0
        self.F = F

    def run(self, text):

        if len(set(text) - self.V) != 0:

            print('ERROR characters',(set(text)-self.V),'are not in the automata\'s alphabet')
            exit(0)
        

        q = self.q0
        for i in text:

            if q >= len(self.d):
                print('String NOT accepted, state has no transitions')
                exit(0)
            if i not in self.d[q].keys():
                print('String NOT accepted, state has no transitions with the character')
                exit(0)

            q = self.d[q][i]
        result = ""
        if q in self.F:
            result = "String accepted!"
            print(result)

        else:
            result = "String NOT accepted, stopped in an unfinal state"
            print(result)
        return result


    def write(self):
        if os.path.exists("result.txt"):
            os.remove("result.txt") 
        result = ""
        for i in range(len(self.Q)):
            # print("State "+str(i)+" Transitions: "+str(self.d[i])+str('FINAL STATE' if i in self.F else ''))
            result = result + "State "+str(i)+" Transitions: "+str(self.d[i])+str(' FINAL STATE' if i in self.F else '')+"\n"
        return result
        


def preprocess(regex):
    regex = clean_kleene(regex)
    regex = regex.replace(' ','')
    regex = '(' + regex + ')' + '#'
    while '()' in regex:
        regex = regex.replace('()','')
    return regex

def clean_kleene(regex):
    for i in range(0, len(regex) - 1):
        while i < len(regex) - 1 and regex[i + 1] == regex[i] and regex[i] == '*':
            regex = regex[:i] + regex[i + 1:]
    return regex

def gen_alphabet(regex):
    return set(regex) - set('()+*')

DEBUG = False
use_lambda = False
lambda_symbol = '_'
alphabet = None

regex = '(aa+b)*ab(bb+a)*'

if not is_valid_regex(regex):
    exit(0)

p_regex = preprocess(regex)
alphabet = gen_alphabet(p_regex)
extra = ''
alphabet = alphabet.union(set(extra))