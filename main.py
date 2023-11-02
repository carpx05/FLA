from regex_validation import is_valid_regex
from preprocessing import preprocess, gen_alphabet
from easygui import multenterbox, textbox
from copy import deepcopy
from utils import DEBUG, RegexTree

title = "FLA - Regex to DFA"

# Main function
def main():

    fields = ["Regex", "string"]
    text = "Enter the details to go further"
    output = multenterbox(text, title, fields)
    regex = output[0]
    # regex = 'a(b+c)*a'
    
    if not is_valid_regex(regex):
        exit(0)
    
    p_regex = preprocess(regex)
    alphabet = gen_alphabet(p_regex)
    # add optional letters that don't appear in the expression
    extra = ''
    alphabet = alphabet.union(set(extra))
    
    # Construct the RegexTree and DFA
    tree = RegexTree(p_regex)
    if DEBUG:
        tree.write()
    dfa = tree.toDfa()
    
    String = output[1]
    print('This is the regex : ' + regex)
    print('This is the alphabet : ' + ''.join(sorted(alphabet)))
    print('This is the automata: \n')
    transition_text = dfa.write()

    print('\nTesting for : "' + String + '" : ')
    result_text = dfa.run(String)
    transition_text = transition_text +"\n" + result_text
    print(transition_text)
            
    result = textbox("result:", title, transition_text)

if __name__ == "__main__":
    main()
