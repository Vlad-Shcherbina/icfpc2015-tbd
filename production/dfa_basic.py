

def print_state(word, position):
    return word + "_" + str(position) + "_" + word[position - 1]

def calculate_suffix_prefix(word, next_character):
    new_word = word + next_character
    for prefix_length in range(len(new_word) - 1, -1, -1):
        offset = len(new_word) - prefix_length
        if word[0:prefix_length] == new_word[offset:len(new_word)]:
            return prefix_length
    return 0

def start_state(word):
    return "start_" + word

def set_transition(initial_state, character, second_state):
    if initial_state in transitions:
        transitions[initial_state][character] = set([second_state])
    else:
        transitions[initial_state] = {character : set([second_state])}


#print(calculate_suffix_prefix("abcabaaa","x"))
alphabet = ['a','b','c']
words = ["abcabcx", "abx"]
transitions = {}
for word_index in range(0, len(words)):
    word = words[word_index]
    for character_index in range(0, len(word) - 1):
        for character in alphabet:
            next_match = calculate_suffix_prefix(word[:character_index], character)
            if character == word[character_index]:
                next_match = character_index + 1
            set_transition(print_state(word, character_index), character, print_state(word, next_match))
    for character in alphabet:
        if character == word[0]:
            set_transition(print_state(word, len(word)), character, print_state(word, 1))
            set_transition(start_state(word), character, print_state(word, 1))
        else:
            set_transition(print_state(word, len(word)), character, start_state(word))
            set_transition(start_state(word), character, start_state(word))

print transitions
