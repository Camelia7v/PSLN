import itertools

left, right = 0, 1


def loadModel(modelPath):
    file = open(modelPath).read()
    terminals = (file.split("Non-Terminals:\n")[0].replace("Terminals:\n", "").replace("\n", ""))
    non_terminals = (file.split("Non-Terminals:\n")[1].split("Productions:\n")[0].replace("Non-Terminals:\n", "")
                     .replace("\n", ""))
    productions = (file.split("Productions:\n")[1].split("Probabilities:\n")[0])
    probabilities = (file.split("Probabilities:\n")[1])
    return cleanAlphabet(terminals), cleanAlphabet(non_terminals), cleanProduction(productions), cleanAlphabet(
        probabilities)


# Make production easy to work with
def cleanProduction(expression):
    result = []
    # remove spaces and explode on ";"
    rawRules = expression.replace('\n', '').split(';')

    for rule in rawRules:
        # Explode every rule on "->" and make a couple
        leftSide = rule.split(' -> ')[0].replace(' ', '')
        rightTerms = rule.split(' -> ')[1].split(' | ')
        for term in rightTerms:
            result.append((leftSide, term.split(' ')))
    return result


def cleanAlphabet(expression):
    return expression.replace('  ', ' ').split(' ')


def seekAndDestroy(target, productions):
    trash, erased = [], []
    for production in productions:
        if target in production[right] and len(production[right]) == 1:
            trash.append(production[left])
        else:
            erased.append(production)

    return trash, erased


def setupDict(productions, variables, terms):
    result = {}
    for production in productions:
        if production[left] in variables and production[right][0] in terms and len(production[right]) == 1:
            result[production[right][0]] = production[left]
    return result


def rewrite(target, production):
    result = []
    # get positions corresponding to the occurrences of target in production right side
    # positions = [m.start() for m in re.finditer(target, production[right])]
    positions = [i for i, x in enumerate(production[right]) if x == target]
    # for all found targets in production
    for i in range(len(positions) + 1):
        # for all combinations of all possible length phrases of targets
        for element in list(itertools.combinations(positions, i)):
            # Example: if positions is [1 4 6]
            # now i've got: [] [1] [4] [6] [1 4] [1 6] [4 6] [1 4 6]
            # erase position corresponding to the target in production right side
            tadan = [production[right][i] for i in range(len(production[right])) if i not in element]
            if tadan:
                result.append((production[left], tadan))
    return result


def prettyForm(rules, probabilities, terminals):
    dictionary = {}
    dictionary_P = {}
    for rule in rules:
        if rule[left] in dictionary:
            dictionary[rule[left]] += ' | ' + ' '.join(rule[right])
            dictionary_P[rule[left] + '_P'] += ' | ' + ''.join(probabilities[rules.index(rule)])
        else:
            dictionary[rule[left]] = ' '.join(rule[right])
            dictionary_P[rule[left] + '_P'] = ''.join(probabilities[rules.index(rule)])
    result = ""
    result_P = ""
    for key in dictionary:
        right_side = dictionary[key].split(" | ")
        right_side_str = ""
        for i in range(len(right_side)):
            if right_side[i] in terminals:
                right_side[i] = f"'{right_side[i]}'"
            if i == len(right_side) - 1:
                right_side_str += right_side[i]
            else:
                right_side_str += right_side[i] + " | "
        result += key + " -> " + right_side_str + "\n"

    for key in dictionary_P:
        right_side = dictionary_P[key].split(" | ")
        right_side_str = ""
        for i in range(len(right_side)):
            if right_side[i] in terminals:
                right_side[i] = f"'{right_side[i]}'"
            if i == len(right_side) - 1:
                right_side_str += right_side[i]
            else:
                right_side_str += right_side[i] + " | "
        result_P += key + " -> " + right_side_str + "\n"
    return result, result_P
