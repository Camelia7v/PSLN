import helper
import nltk

left, right = 0, 1

variablesJar = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                "N", "O", "P", "Q", "R", "S", "T", "U", "W", "X", "Y", "Z"]


def isUnitary(rule, variables):
    if rule[left] in variables and rule[right][0] in variables and len(rule[right]) == 1:
        return True
    return False


def isSimple(rule):
    if rule[left] in non_terminals and rule[right][0] in terminals and len(rule[right]) == 1:
        return True
    return False


# Add S0->S rule–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-------–––START
def START(productions, variables):
    variables.append('S0')
    return [('S0', [variables[0]])] + productions


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
def TERM(productions, variables):
    newProductions = []
    # create a dictionary for all base production, like A->a, in the form dic['a'] = 'A'
    dictionary = helper.setupDict(productions, variables, terms=terminals)
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
                        dictionary[term] = variablesJar.pop()
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
def BIN(productions, variables):
    result = []
    for production in productions:
        k = len(production[right])
        if k <= 2:
            result.append(production)
        else:
            newVar = variablesJar.pop(0)
            variables.append(newVar + '1')
            result.append((production[left], [production[right][0]] + [newVar + '1']))
            for i in range(1, k - 2):
                var, var2 = newVar + str(i), newVar + str(i + 1)
                variables.append(var2)
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


def unit_routine(productions, variables):
    unitaries, result = [], []
    for aRule in productions:
        if isUnitary(aRule, variables):
            unitaries.append((aRule[left], aRule[right][0]))
        else:
            result.append(aRule)
    for uni in unitaries:
        for rule in productions:
            if uni[right] == rule[left] and uni[left] != rule[left]:
                result.append((uni[left], rule[right]))

    return result


def UNIT(productions, variables):
    i = 0
    result = unit_routine(productions, variables)
    tmp = unit_routine(result, variables)
    while result != tmp and i < 1000:
        result = unit_routine(tmp, variables)
        tmp = unit_routine(result, variables)
        i += 1
    return result


if __name__ == '__main__':
    grammar_path = 'grammar.txt'
    terminals, non_terminals, rules = helper.loadModel(grammar_path)

    rules = START(rules, variables=non_terminals)
    rules = ELIMINATE_EPSILON(rules)
    rules = TERM(rules, variables=non_terminals)
    rules = BIN(rules, variables=non_terminals)
    rules = DEL(rules)
    rules = UNIT(rules, variables=non_terminals)
    CNF_grammar = helper.prettyForm(rules, terminals)

    print("\nIn the CNF grammar there are ", len(rules), " rules.")
    print("The rules are: ")
    print(CNF_grammar)
    open(f'{grammar_path[:-4]}_output.txt', 'w').write(CNF_grammar)

    # Visualisation
    print("\nPhrase structure tree(s) for 'The flight includes a meal.'")
    grammar = nltk.CFG.fromstring(CNF_grammar)
    sentence = ['the', 'flight', 'include', 'a', 'meal']
    parser = nltk.ChartParser(grammar)
    for tree in parser.parse(sentence):
        print(tree)

    print("\nPhrase structure tree(s) for 'She booked the book on the flight.'")
    grammar = nltk.CFG.fromstring(CNF_grammar)
    sentence = ['she', 'book', 'the', 'book', 'on', 'the', 'flight']
    parser = nltk.ChartParser(grammar)
    for tree in parser.parse(sentence):
        print(tree)
