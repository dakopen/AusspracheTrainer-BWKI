
def sort_sequence_dict(sequence_dict, sorted_dict=None):
    """Sortiert ein Dictionary in einem Dictionary. Sofern Key im Dictionary einen kleineren Wwert"""
    global sorting_counter
    # {0: ['apg', 'apg'], 1: {0: ['t', 't'], -1: ['e', 'ɪl']}}
    # {0: ['apg', 'apg'], 1: ['e', 'ɪl'], 2: ['t', 't']}
    if sorted_dict is None:
        sorted_dict = {}
    for key, value in sequence_dict.items():
        if type(value) == dict:
            sorting_counter += 1
            sorted_dict = sort_sequence_dict(value, sorted_dict)
        else:
            sorted_dict[sorting_counter] = value
            sorting_counter += 1
    return sorted_dict


def sequence_matching(target, prediction, minus_i=-1, plus_i=1):
    """
    Matched immer den längsten Überschneidenden Teil des Targets mit der Prediction und ruft sich selbst für
    die übrig gebliebenen Teile auf:
    Bsp.: 'ich habe' und 'ich hatte' werden gematched:
    'ich ha':'ich ha',
    'b':'tt',
    'e':'e'
    """
    # Rekursive Funktion:
    match = SequenceMatcher(None, target, prediction).find_longest_match(0, len(target), 0, len(prediction))
    if match.size == 0:
        return "KEIN MATCH", {0: [target, prediction]}
    pre_match = [target[:match.a], prediction[:match.b]]
    aft_match = [target[match.a + match.size:], prediction[match.b + match.size:]]
    matchings = {0: [target[match.a: match.a + match.size], prediction[match.b: match.b + match.size]]}

    if pre_match[0] != "" and pre_match[1] != "":
        _, matchings[minus_i] = sequence_matching(pre_match[0], pre_match[1], minus_i, plus_i)
        minus_i -= 1
    else:
        if pre_match[0] != "" or pre_match[1] != "":
            matchings[minus_i] = pre_match
            minus_i -= 1
    if aft_match[0] != "" and aft_match[1] != "":
        _, matchings[plus_i] = sequence_matching(aft_match[0], aft_match[1], minus_i, plus_i)
        plus_i += 1
    else:
        if aft_match[0] != "" or aft_match[1] != "":
            matchings[plus_i] = aft_match
            plus_i += 1
    return match, dict(sorted(matchings.items()))
