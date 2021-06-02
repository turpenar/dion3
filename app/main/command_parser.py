
import pathlib as pathlib

from app.main import mixins, config


# importing all prepositions and prepositional phrases

verbs = config.verbs
prepositions = config.prepositions
articles = config.articles
determiners = config.determiners
nouns = config.nouns
adjectives = config.adjectives

objects = mixins.objects
items = mixins.items
npcs = mixins.npcs
enemies = mixins.enemies

for category in objects:
    for object in objects[category]:
        nouns.extend(objects[category][object]['handle'])
        adjectives.extend(objects[category][object]['adjectives'])

for category in items:
    for item in items[category]:
        nouns.extend(items[category][item]['handle'])
        adjectives.extend(items[category][item]['adjectives'])

for npc in npcs:
    nouns.extend(npcs[npc]['handle'])
    adjectives.extend(npcs[npc]['adjectives'])

for enemy in enemies:
    nouns.extend(enemies[enemy]['handle'])
    adjectives.extend(enemies[enemy]['adjectives'])

def find_index(input_list, list_of_matches):
    return [i for i, item in enumerate(input_list) if item in list_of_matches]

def parser(input):
    input = input.lower()
    tokens = input.split()
    tokens = [x for x in tokens if x not in articles]

    relevant_verbs = set(tokens).intersection(verbs)
    relevant_nouns = set(tokens).intersection(nouns)
    relevant_adjectives = set(tokens).intersection(adjectives)
    relevant_prepositions = set(tokens).intersection(prepositions)
    relevant_determiners = set(tokens).intersection(determiners)
    relevant_numbers = [int(token) for token in tokens if token.isdigit()]

    verb_index = find_index(tokens, relevant_verbs)
    noun_index = find_index(tokens, relevant_nouns)
    adjective_index = find_index(tokens, relevant_adjectives)
    preposition_index = find_index(tokens, relevant_prepositions)
    determiner_index = find_index(tokens, relevant_determiners)
    numbers = relevant_numbers

    kwargs = {}

    if len(verb_index) == 0:
        kwargs['action_verb'] = tokens[0]
    if len(verb_index) == 1:
        kwargs['action_verb'] = tokens[verb_index[0]]
        kwargs['subject_verb'] = None
    if len(verb_index) > 1:
        kwargs['action_verb'] = tokens[verb_index[0]]
        kwargs['subject_verb'] = tokens[verb_index[1]]
    if len(noun_index) == 0:
        kwargs['direct_object'] = None
        kwargs['indirect_object'] = None
    elif len(noun_index) == 1:
        if len(preposition_index) > 0:
                kwargs['direct_object'] = None
                kwargs['indirect_object'] = [tokens[noun_index[0]]]
        else:
            kwargs['direct_object'] = [tokens[noun_index[0]]]
            kwargs['indirect_object'] = None
    else:
        kwargs['direct_object'] = [tokens[noun_index[0]]] or None
        kwargs['indirect_object'] = [tokens[noun_index[1]]] or None

    if len(preposition_index) < 1:
        kwargs['preposition'] = None
    elif len(preposition_index) == 1:
        kwargs['preposition'] = [tokens[preposition_index[0]]] or None
    if len(adjective_index) < 1:
        kwargs['adjective_1'] = None
    elif len(adjective_index) == 1:
        kwargs['adjective_1'] = [tokens[adjective_index[0]]] or None
    elif len(adjective_index) == 2:
        kwargs['adjective_1'] = [tokens[adjective_index[0]]] or None
        kwargs['adjective_2'] = [tokens[adjective_index[1]]] or None
    if len(numbers) == 0:
        kwargs['number_1'] = None
    elif len(numbers) == 1:
        print("code goes here")
        kwargs['number_1'] = [numbers[0]] 
        
    return kwargs

