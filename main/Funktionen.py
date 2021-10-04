from IPAclass import *

ipa = IPA()

sorting_counter = 0


# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
class bcolors:
    """Farben für den Output. Wird als Buchstabenfolge an einen String addiert."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INACCURACY = '\033[35m'


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
    # difflib.SequenceMatcher; siehe https://docs.python.org/3/library/difflib.html
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


def einzelvergleich(target, prediction):
    """Vergleicht Targetsatz und Predictionsatz. Die Kernfunktion ist sequence_matching, welche jegliche
    Überschneidung und vergleichbaren Teile matched. Ausgegeben wird eine Fehlerliste (outdated), und mit Farben
    der Targetsatz und Predictionsatz angestrichen, wo Unterschiede sind."""
    fehler_liste = []
    prediction_output = ""
    target_output = ""

    _, matchings = sequence_matching(target, prediction)
    sorted_sequence_dict = sort_sequence_dict(dict(sorted(matchings.items())))

    for value in sorted_sequence_dict.values():
        target_sequence = value[0]
        prediction_sequence = value[1]

        if target_sequence == prediction_sequence:
            target_output += bcolors.OKGREEN + target_sequence + bcolors.ENDC
            prediction_output += bcolors.OKGREEN + prediction_sequence + bcolors.ENDC

        # nicht verwechseln mit target_sequence == "" and prediction_sequence == ""
        elif target_sequence and prediction_sequence == "":
            target_output += bcolors.WARNING + target_sequence + bcolors.ENDC
            prediction_output += bcolors.FAIL + "_" + bcolors.ENDC
            fehler_liste.append((6, [target_sequence, "_"]))

        elif target_sequence == "" and prediction_sequence:
            prediction_output += bcolors.FAIL + prediction_sequence + bcolors.ENDC
            fehler_liste.append((8, ["_", prediction_sequence]))

        else:
            if target_sequence == " ":
                target_output += bcolors.WARNING + target_sequence + bcolors.ENDC
                prediction_output += bcolors.FAIL + prediction_sequence + bcolors.ENDC
                fehler_liste.append((8, ["_", prediction_sequence]))
            elif prediction_sequence == " ":
                target_output += bcolors.WARNING + target_sequence + bcolors.ENDC
                prediction_output += bcolors.FAIL + "_" + bcolors.ENDC
                fehler_liste.append((6, [target_sequence, "_"]))
            else:
                target_output += bcolors.WARNING + target_sequence + bcolors.ENDC
                prediction_output += bcolors.WARNING + prediction_sequence + bcolors.ENDC
                fehler_liste.append((5, [target_sequence, prediction_sequence]))

    return fehler_liste, target_output, prediction_output
