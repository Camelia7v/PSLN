import helper
import nltk

left, right = 0, 1

alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "W", "X", "Y", "Z"]


def isUnitary(rule, non_terminals):
    if rule[left] in non_terminals and rule[right][0] in non_terminals and len(rule[right]) == 1:
        return True
    return False


def isSimple(rule):
    if rule[left] in non_terminals and rule[right][0] in terminals and len(rule[right]) == 1:
        return True
    return False


# Add S0->S rule–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-------–––START
def START(productions, probabilities, non_terminals):
    non_terminals.append('S0')
    probabilities.reverse()
    probabilities.append('1.0')
    probabilities.reverse()
    return [('S0', [non_terminals[0]])] + productions


# Remove rules containing null, like A->ε, without changing the expressiveness of the grammar--------ELIMINATE_EPSILON
def ELIMINATE_EPSILON(productions):
    for production in productions:
        if production[left] in non_terminals and len(production[right]) == 1:
            if production[right][0] == "ε" or production[right][0] == "epsilon" or production[right][0] == "Îµ":
                non_terminal = production[left]
                productions.remove(production)
                for rule in productions:
                    for index, value in enumerate(rule[right]):
                        if value == non_terminal:
                            right_side = rule[right][:index] + rule[right][index + 1:]
                            if not right_side:
                                right_side.append("epsilon")
                                productions.append((rule[left], right_side))
                            else:
                                productions.append((rule[left], right_side))
    return productions


# Remove rules containing both terms and variables, like A->Bc, replacing by A->BZ and Z->c–––––––––––------------TERM
def TERM(productions, non_terminals):
    newProductions = []
    # create a dictionary for all base production, like A->a, in the form dic['a'] = 'A'
    dictionary = helper.setupDict(productions, non_terminals, terms=terminals)
    for production in productions:
        # check if the production is simple
        if isSimple(production):
            # in that case there is nothing to change
            newProductions.append(production)
        else:
            for term in terminals:
                for index, value in enumerate(production[right]):
                    if term == value and term not in dictionary:
                        # it's created a new production variable->term and added to it
                        dictionary[term] = alphabet.pop()
                        # Variables set it's updated adding new variable
                        non_terminals.append(dictionary[term])
                        newProductions.append((dictionary[term], [term]))
                        production[right][index] = dictionary[term]
                    elif term == value:
                        production[right][index] = dictionary[term]
            newProductions.append((production[left], production[right]))

    # merge created set and the introduced rules
    return newProductions


# Eliminate non unitary rules––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––------––BIN
def BIN(productions, probabilities, non_terminals):
    result = []
    for production in productions:
        k = len(production[right])
        if k <= 2:
            result.append(production)
        else:
            newVar = alphabet.pop(0)
            non_terminals.append(newVar + '1')
            result.append((production[left], [production[right][0]] + [newVar + '1']))
            probabilities.insert(productions.index(production) + 1, '1.0')
            for i in range(1, k - 2):
                var, var2 = newVar + str(i), newVar + str(i + 1)
                non_terminals.append(var2)
                result.append((var, [production[right][i], var2]))
            result.append((newVar + str(k - 2), production[right][k - 2:k]))
    return result


# Delete non terminal rules–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-------––DEL
def DEL(productions):
    newSet = []
    # seekAndDestroy throw back in:
    #        – outlaws all left side of productions such that right side is equal to the outlaw
    #        – productions the productions without outlaws
    outlaws, productions = helper.seekAndDestroy(target='e', productions=productions)
    # add new reformulation of old rules
    for outlaw in outlaws:
        # consider every production: old + new resulting important when more than one outlaws are in the same prod.
        for production in productions + [e for e in newSet if e not in productions]:
            # if outlaw is present on the right side of a rule
            if outlaw in production[right]:
                # the rule is rewritten in all combination of it, rewriting "e" rather than outlaw
                # this cycle prevents to insert duplicate rules
                newSet = newSet + [e for e in helper.rewrite(outlaw, production) if e not in newSet]

    # add unchanged rules and return
    return newSet + ([productions[i] for i in range(len(productions))
                      if productions[i] not in newSet])


def unit_routine(productions, probabilities, non_terminals):
    unitaries, result, unitary_probabilities = [], [], []
    new_probabilities = probabilities.copy()
    i = 0
    for aRule in productions:
        if isUnitary(aRule, non_terminals):
            unitaries.append((aRule[left], aRule[right][0]))
            unitary_probabilities.append(probabilities[productions.index(aRule)])
            del new_probabilities[productions.index(aRule) - i]
            i = i + 1
        else:
            result.append(aRule)
    for uni in unitaries:
        for rule in productions:
            if uni[right] == rule[left] and uni[left] != rule[left]:
                result.append((uni[left], rule[right]))
                sum = float(unitary_probabilities[unitaries.index(uni)]) * float(probabilities[productions.index(rule)])
                new_probabilities.append(str(format(sum, ".3f")))
    return result, new_probabilities


def UNIT(productions, probabilities, non_terminals):
    i = 0
    result, new_probabilities = unit_routine(productions, probabilities, non_terminals)
    tmp, tmp_probabilities = unit_routine(result, new_probabilities, non_terminals)
    while result != tmp and i < 1000:
        result, new_probabilities = unit_routine(tmp, tmp_probabilities, non_terminals)
        tmp, tmp_probabilities = unit_routine(result, new_probabilities, non_terminals)
        i += 1
    return result, new_probabilities


def calculate_probability(tree, rules, probabilities, j):
    if j == 1:
        for i in range(len(rules)):
            if tree[0] in rules[i][1] and tree.label() in rules[i][0]:
                return float(probabilities[i])
    else:
        for i in range(len(rules)):
            if tree[0].label() in rules[i][1] and tree.label() in rules[i][0]:
                return float(probabilities[i])


def separate_tree(tree, rules, probabilities, sentence_probability):
    lhs = tree[0]
    rhs = tree[1]
    rhsvalue, lhsvalue = 1, 1
    if len(lhs) == 1:
        sentence_probability = sentence_probability * calculate_probability(lhs, rules, probabilities, 1)
    else:
        lhsvalue = separate_tree(lhs, rules, probabilities, 1)
    if len(rhs) == 1:
        sentence_probability = sentence_probability * calculate_probability(rhs, rules, probabilities, 1)
    else:
        rhsvalue = separate_tree(rhs, rules, probabilities, 1)
    sentence_probability = sentence_probability * calculate_probability(tree, rules, probabilities,
                                                                        2) * lhsvalue * rhsvalue
    return sentence_probability


if __name__ == '__main__':
    grammar_path = 'grammar.txt'
    terminals, non_terminals, rules, probabilities = helper.loadModel(grammar_path)

    rules = START(rules, probabilities, non_terminals)
    rules = ELIMINATE_EPSILON(rules)
    rules = TERM(rules, non_terminals)
    rules = BIN(rules, probabilities, non_terminals)
    rules = DEL(rules)
    rules, probabilities = UNIT(rules, probabilities, non_terminals)
    CNF_grammar, CNF_grammar_P = helper.prettyForm(rules, probabilities, terminals)

    print("\nIn the CNF grammar there are ", len(rules), " rules and ", len(probabilities), " probabilities.")
    print("The rules are: ")
    print(CNF_grammar)
    print("The probabilities are: ")
    print(CNF_grammar_P)
    open(f'{grammar_path[:-4]}_output.txt', 'w').write(CNF_grammar + CNF_grammar_P)

    # Visualisation
    print("\nPhrase structure tree(s) for 'The flight includes a meal.'")
    grammar = nltk.CFG.fromstring(CNF_grammar)
    sentence = ['the', 'flight', 'include', 'a', 'meal']
    parser = nltk.ChartParser(grammar)
    for tree in parser.parse(sentence):
        sentence_probability = 1.0
        value = 0
        if len(tree) > 1:
            value = separate_tree(tree, rules, probabilities, sentence_probability)
        print(tree)
        print("The probability of the tree is: " + str(value) + ".\n")
        # 0.000031104

    print("\nPhrase structure tree(s) for 'She booked the book on the flight.'")
    grammar = nltk.CFG.fromstring(CNF_grammar)
    sentence = ['she', 'book', 'the', 'book', 'on', 'the', 'flight']
    parser = nltk.ChartParser(grammar)
    for tree in parser.parse(sentence):
        sentence_probability = 1.0
        value = 0
        if len(tree) > 1:
            value = separate_tree(tree, rules, probabilities, sentence_probability)
        print(tree)
        print("The probability of the tree is: " + str(value) + ".\n")
