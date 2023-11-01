from regex_validation import is_valid_regex
from preprocessing import preprocess, gen_alphabet
from easygui import multenterbox
from copy import deepcopy
from utils import DEBUG, RegexTree

title = "FLA - Regex to DFA"

# Main function
def main():

    fields = ["Regex", "string"]
    text = "Enter the details to go further"
    output = multenterbox(text, title, fields)
    print (output)
    regex = output[0]
    # regex = 'a(b|c)*a'
    
    # Check if the regex is valid
    if not is_valid_regex(regex):
        exit(0)
    
    # Preprocess regex and generate the alphabet
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
    
    # Test the DFA with a message
    message = output[1]
    print('This is the regex : ' + regex)
    print('This is the alphabet : ' + ''.join(sorted(alphabet)))
    print('This is the automata: \n')
    dfa.write()
    print('\nTesting for : "' + message + '" : ')
    dfa.run(message)

if __name__ == "__main__":
    main()
