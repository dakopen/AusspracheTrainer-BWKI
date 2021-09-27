import math
from SimilarityMetrics import *
from termcolor import colored
import re
import copy
from IPAclass import *
import itertools

ipa = IPA()


# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def gesamtscore(vergleich_output_scores):
    if vergleich_output_scores[2] == 0:
        return 1
    # 0: Similar, 1: Jaro distance, 2: Levenshtein Distance, 3: Länge
    score = (vergleich_output_scores[0] ** math.sqrt(2)) * (vergleich_output_scores[1] ** math.sqrt(2)) * (
        ((vergleich_output_scores[3] - vergleich_output_scores[2]) / (vergleich_output_scores[3]) ** math.sqrt(2)))  #
    return score


def last_match(match_liste):
    """Sucht eine Liste nach dem Keywort "---", und gibt den letzten Index aus, bei dem das Wort damit aufhört"""
    match_liste.reverse()  # von hinten anfangen zu suchen, da letzter Index ausgegeben werden soll
    for x in range(len(match_liste)):
        if match_liste[x].endswith("---"):
            match_liste.reverse()  # richtig rum sortieren
            return len(match_liste) - x - 1
    # Falls kein Match gefunden wurde
    match_liste.reverse()
    return -1


def is_matched(s):
    """True, wenn "---" im Wort ist."""
    return "---" in s


def count_nicht_zugeorndet(match_liste, endpunkt):
    """Gibt die Anzahl an nicht zugeordneten Elementen in einer Liste bis zum Endpunkt an."""
    nicht_zugeordnet = 0
    for x in range(endpunkt):
        if not match_liste[x] or not match_liste[x][0].isdigit():
            nicht_zugeordnet += 1
    return nicht_zugeordnet


def find_matches(targets, predictions):
    """Sucht zugehörige Wörter in zwei Listen, die sich nur leicht unterscheiden.
    Gibt ein Dictionary mit den Matches als Indexe aus, sowie zwei weitere Listen mit den Matches ersetzt
    an den jeweiligen Stellen."""
    # targets = ['wir', 'sehen', 'oft'], predictions = ['wir', 'sehe', 'oft']
    targets_matches_replaced = targets.copy()  # List
    predictions_matches_replaced = predictions.copy()  # List
    matches = {}  # Dictionary
    last_prediction_matched = 0
    for i, targetword in enumerate(targets):
        # i = 0, targetword = 'wir'
        max_matching_score = 0  # Int
        corresponding_prediction_to_max_score = None  # String
        exaktes_match = False  # Bool
        for j, predictionword in enumerate(predictions_matches_replaced):  # Note the difference in the List
            # j = 0, predictionword = 'wir'
            counter_nicht_zugeordnet_prediction = count_nicht_zugeorndet(predictions_matches_replaced, j)
            counter_nicht_zugeordnet_target = count_nicht_zugeorndet(targets_matches_replaced, i)

            # Int, gibt an, wie viele Wörter nicht zugeorndet werden konnten
            counter_nicht_zugeordnet = max(counter_nicht_zugeordnet_prediction, counter_nicht_zugeordnet_target)
            # Schon zugeordnet oder liegt zu weit hinten im Satz vom Targetindex ausgehend
            # DEBUG print(f"i:{i}, j:{j}, counter:{counter_nicht_zugeordnet}, target:{targetword}, predwort:{predictionword}")
            # DEBUG print(predictions_matches_replaced, targets_matches_replaced, last_prediction_matched)
            if predictionword.endswith("---") or i - j > counter_nicht_zugeordnet or last_prediction_matched > j:
                continue

            # Zu weit vorne im Satz vom Targetwortindex ausgehend, 3 Wörter weiter vorne sollte ausreichen, sonst liegt der Fehler wo anders
            if j - i > 1 + counter_nicht_zugeordnet or j - i > 3:
                break

            score = gesamtscore(vergleich(targetword, predictionword))  # Int von 0 - 1, gibt die Ähnlichkeit an
            if score == 1:  # exaktes Match
                exaktes_match = True
                targetword_index = i
                predictionword_index = j

                targets_matches_replaced[targetword_index] = str(i) + "---"  # 0---
                predictions_matches_replaced[predictionword_index] = str(i) + "---"  # 0---
                matches[str(targetword_index)] = predictionword_index  # {targetindex: predictionindex}
                last_prediction_matched = predictionword_index
                break
            elif score > max_matching_score:
                max_matching_score = score
                predictionword_index = j

        if not exaktes_match:  # Score 0 < score < 1
            if max_matching_score >= 0.14:  # Lässt gerade so einen Fehler zu, bei zwei Buchstabenwörter
                targetword_index = i
                targets_matches_replaced[targetword_index] = str(i) + "---"
                predictions_matches_replaced[predictionword_index] = str(i) + "---"
                last_prediction_matched = predictionword_index
    return matches, targets_matches_replaced, predictions_matches_replaced


def sort_matched_and_unmatched(targets_matches_replaced, predictions_matches_replaced):
    """Gibt ein Dictionary aus, in welchem die Matches und Klartext-Wörter als Value stehen.
    Key = incrementing number; Value = Tuple, bestehend aus zwei Listen (Targets + Preds)"""
    targets_del = targets_matches_replaced.copy()  # List
    predictions_del = predictions_matches_replaced.copy()  # List

    # Dictionary, beinhaltet entweder Zahlen von Target- und Predictionindex oder unmatched Wörter
    matches_and_nonmatches = {}
    dictionary_key = 0

    zugeordnete_predictions = []
    zugeordnete_targets = []
    for targetwort in targets_del:
        # targetwort = '0---'
        if is_matched(targetwort):
            match_nummer = targetwort.replace("---", "")  # Gibt nur die Nummer aus, vor "---"
            for predictionwort in predictions_del:
                if match_nummer == predictionwort.replace("---", ""):
                    if len(zugeordnete_predictions) + len(zugeordnete_targets) == 0:  # beide Listen sind leer
                        zugeordnete_targets, zugeordnete_predictions = [match_nummer], [match_nummer]
                    else:
                        # Falls Targetwort kein Match ist und/oder es nicht einem Pred zugeordnet wird,
                        # zum Dict hinzufügen
                        matches_and_nonmatches[str(dictionary_key)] = (zugeordnete_targets, zugeordnete_predictions)
                        dictionary_key += 1  # incrementing the dictionary_key
                        zugeordnete_targets, zugeordnete_predictions = [match_nummer], [match_nummer]

                    # Damit wird die Liste nicht doppelt durchsucht
                    predictions_del = predictions_del[predictions_del.index(predictionwort) + 1:]
                    matches_and_nonmatches[str(dictionary_key)] = (zugeordnete_targets, zugeordnete_predictions)
                    dictionary_key += 1  # incrementing the dictionary_key
                    zugeordnete_targets, zugeordnete_predictions = [], []
                    break

                zugeordnete_predictions.append(predictionwort)

        else:
            zugeordnete_targets.append(targetwort)

    # Falls das Letzte Targetwort nicht zugeorndet wurde, da "ELSE" durchgelaufen ist
    if len(zugeordnete_predictions) == 0:
        zugeordnete_predictions = predictions_del

    # Dem Dictionary hinzufügen
    if len(zugeordnete_targets) + len(zugeordnete_predictions) != 0:
        matches_and_nonmatches[str(dictionary_key)] = (zugeordnete_targets, zugeordnete_predictions)

    # matches_and_nonmatches = {'0': (['0'], ['0']), '1': (['oft'], []),
    # '2': (['2'], ['2']), '3': (['fotostrecken'], ['foto', 'strecken'])}
    return matches_and_nonmatches


def get_klartext(match, matches_replaced, original_list):
    """Sucht den Klartext des Matches in der Originalen-Klartext-Liste."""
    index = matches_replaced.index((match + "---"))
    return original_list[index]


def get_dict_item_at(dict, dict_index, targets_matches_replaced, predictions_matches_replaced, target, prediction):
    """Gibt den Klartext eines Dictionary Wertes aus. Dadurch werden die Zahlen der Zuordnung wieder zu Klartext umgeformt."""

    # Tuple an Stelle des gefragten Indexes
    values_at_index = list(dict.values())[dict_index]  # Tuple mit Listen: (['2'], ['2'])
    get_klartext_parameters = {0: ["", targets_matches_replaced, target],
                               1: ["", predictions_matches_replaced, prediction]}
    klartexte_at_index = []
    for i, value in enumerate(values_at_index):
        if len(value) == 1 and value[0].isdigit():
            get_klartext_parameters[i][0] = value[0]
            klartext = [get_klartext(*get_klartext_parameters[i])]
        else:
            if len(value) != 0:
                klartext = value
            else:
                klartext = [""]

        klartexte_at_index.append(klartext)
    return klartexte_at_index


def get_empty_dict_values(dictionary):
    """7: ([''], ['ˈʃmʊsl̩təɐ̯eːɐ']), 8: ([''], ['ɛntˈlɪçhɪˈnan']), 9: (['ˈʃmʊnʦl̩tə'], ['']), 10: (['eːɐ̯'], ['']), 11: (['ɪn'], ['']), 12: (['sɪç'], ['']), 13: (['hɪˈnaɪ̯n'], [''])
    zu 7: (['ˈʃmʊnʦl̩tə', 'eːɐ̯', 'ɪn', 'sɪç', 'hɪˈnaɪ̯n'], ['ˈʃmʊsl̩təɐ̯eːɐ', 'ɛntˈlɪçhɪˈnan'])
    ==> Wenn aufeinanderfolgend mehrere Values bei den Targets und/oder Predictions leer sind, werden sie gemerged"""
    empty_values = {}
    # 0 = Only Target
    # 1 = Only Pred
    dict_speicher = dictionary.copy()
    for key, value in dictionary.items():
        if value[0] == [""]:
            empty_values[key] = 1
        if value[1] == [""]:
            empty_values[key] = 0
    zusammen_targets, zusammen_preds = [], []

    if len(empty_values) > 1:
        last_key = list(empty_values.keys())[0] - 1
        #print(last_key)
        for key, value in empty_values.items():
            if abs(key - last_key) == 1:  # aufeinanderfolgend
                if value == 0:
                    zusammen_targets.append(key)
                else:  # value = 1
                    zusammen_preds.append(key)
            elif zusammen_targets and zusammen_preds:
                for key in zusammen_targets:
                    dictionary[key] = ([""], [""])
                for key in zusammen_preds:
                    dictionary[key] = ([""], [""])
                dictionary_anfang = min(zusammen_targets[0], zusammen_preds[0])
                dictionary[dictionary_anfang] = (
                    [dict_speicher[key][0][0] for key in zusammen_targets],
                    [dict_speicher[key][1][0] for key in zusammen_preds])
                dictionary = get_empty_dict_values(dictionary)  # Nochmal aufrufen, da sich die Indexe verschieben

                zusammen_targets, zusammen_preds = [], []
            else:
                zusammen_targets, zusammen_preds = [], []
                if value == 0:
                    zusammen_targets.append(key)
                else:  # value = 1
                    zusammen_preds.append(key)
            last_key = key
        if zusammen_targets and zusammen_preds:
            for key in zusammen_targets:
                dictionary[key] = ([""], [""])
            for key in zusammen_preds:
                dictionary[key] = ([""], [""])
            dictionary_anfang = min(zusammen_targets[0], zusammen_preds[0])
            dictionary[dictionary_anfang] = (
                [dict_speicher[key][0][0] for key in zusammen_targets],
                [dict_speicher[key][1][0] for key in zusammen_preds])

    return dictionary


def get_score_pn(match_nonmatch_key, index_position_changer, klartext_matches, next_previous_scores,
                 current_prediction):
    """Testet den Score, wenn das Wort ans nächste oder vorherige Wort, das jetzige addiert wird """
    # pn = previous_next
    pn_target, pn_prediction = klartext_matches[str(int(match_nonmatch_key) + index_position_changer)]
    if index_position_changer == -1:
        pn_target, pn_prediction = pn_target[-1], pn_prediction[-1]
    else:  # index_position_changer == 1:
        pn_target, pn_prediction = pn_target[0], pn_prediction[0]

    pn_score_old = gesamtscore(vergleich(pn_target, pn_prediction))
    if pn_score_old != 1:
        if index_position_changer == -1:
            pn_prediction += current_prediction
        else:
            pn_prediction = current_prediction + pn_prediction
        pn_score_new = gesamtscore(vergleich(pn_target, pn_prediction))
        if pn_score_new > pn_score_old:
            next_previous_scores[index_position_changer] = pn_score_new
            # MERGE PN AND CURRENT
    return next_previous_scores


def merge(match_nonmatch_key, index_position_changer, klartext_matches, current_prediction):
    """Führt zwei Wörter zusammen und lässt an der Stelle, wo das Wort vorher war einen leeren String."""
    unchanged_target, merge_prediction = klartext_matches[str(int(match_nonmatch_key) + index_position_changer)]
    if index_position_changer == -1:
        unchanged_target, merge_prediction = unchanged_target[-1], merge_prediction[-1]
        merge_prediction += current_prediction
    else:  # index_position_changer == 1:
        unchanged_target, merge_prediction = unchanged_target[0], merge_prediction[0]
        merge_prediction = current_prediction + merge_prediction

    klartext_matches[str(int(match_nonmatch_key) + index_position_changer)] = ([unchanged_target], [merge_prediction])
    klartext_matches[match_nonmatch_key] = ([""], [""])

    return klartext_matches


def split(target, prediction):
    """Das Target ist eine Liste aus mehreren, auseinander geschriebenen Wörtern, während diese bei der Prediction zusammen geschrieben wurden.
    Input: current_target = ["fahrrad", "ständer"], current_prediction = ["fahrradständer"]
    Output: ["fahrrad", "ständer"]"""
    prediction = prediction[0]  # List zu String
    start_und_end_indexe = []
    for i, targetwort in enumerate(target):
        if start_und_end_indexe:
            start_und_end_index = [start_und_end_indexe[-1][-1], start_und_end_indexe[-1][-1] + len(targetwort)]
        else:
            start_und_end_index = [0, len(prediction)]
        max_score = 0.05  # Sorgt dafür, dass wenn es sich nur ganz leicht ähnelt, es nicht als Wort erkannt wird
        if i == 0:  # das erste Wort muss mit dem ersten Buchstaben der Prediction beginnen
            for endindex in range(1,
                                  len(prediction) + 1):  # Endindex fängt bei 1 an und hört bei 1 auf, da er exklusiv funktioniert
                cropped_prediction = prediction[:endindex]
                score = gesamtscore(vergleich(targetwort, cropped_prediction))
                if score >= max_score:
                    max_score = score
                    start_und_end_index = [0, endindex]
            start_und_end_indexe.append(start_und_end_index)

        elif i == len(targetwort):  # das letzte Wort muss mit dem letzten Buchstaben der Prediction aufhören
            for startindex in range(len(prediction)):
                cropped_prediction = prediction[startindex:]
                score = gesamtscore(vergleich(targetwort, cropped_prediction))
                if score >= max_score:
                    max_score = score
                    start_und_end_index = [startindex, len(targetwort)]
            start_und_end_indexe.append(start_und_end_index)

        else:  # alle anderen Wörter
            for startindex in range(len(prediction)):
                for endindex in range(1,
                                      len(prediction) + 1):  # Endindex fängt bei 1 an und hört bei 1 auf, da er exklusiv funktioniert
                    cropped_prediction = prediction[startindex:endindex]
                    score = gesamtscore(vergleich(targetwort, cropped_prediction))
                    if score >= max_score:  # TODO: Einfügen, dass wenn es sich nur ganz leicht ähnelt, es nicht reingenommen wird
                        max_score = score
                        start_und_end_index = [startindex, endindex]
            start_und_end_indexe.append(start_und_end_index)
    start_und_end_indexe[0][0] = 0
    start_und_end_indexe[-1][-1] = len(prediction)

    split_prediction = ueberschneidungen_loesen(target=target, prediction=prediction,
                                                start_und_end_indexe=start_und_end_indexe)
    if len(start_und_end_indexe) == 2:
        if gesamtscore(vergleich(target[0], prediction[start_und_end_indexe[0][0]:start_und_end_indexe[0][1]])) * gesamtscore(vergleich(target[0], prediction[start_und_end_indexe[1][0]:start_und_end_indexe[1][1]])) < gesamtscore(vergleich(" ".join(target), " ".join(prediction)))**2:
            split_prediction = [prediction]
    return split_prediction


def ueberschneidungen_loesen(target, prediction, start_und_end_indexe):
    """Sollte es zu Überschneidung kommen innerhalb der start_und_end_indexe, oder Buchstaben ausgelassen
    wird es hier überprüft und gelöst. Es wird eine Liste mit korrekt gesplitteten prediction ausgegeben."""

    endindex = -1  # damit am Anfang Startindex von 0 in jedem Fall größer ist
    last_index0 = None  # wird ausschließlich später deklariert und nur dann verwendet, aber sonst markiert die IDE das als pot. Fehler
    split_prediction = []
    for i, index in enumerate(start_und_end_indexe):
        # i = enumerator, für das Callen von vorherigen Elementen

        # Wenn der Index des nächsten Wortes im letzten Wort anfängt oder ein Buchstabe dazwischen ausgelassen wurde
        if index[0] <= endindex or index[0] - endindex > 1 and endindex != -1:
            score_index0_last = gesamtscore(vergleich(target[i - 1], prediction[index[0]:index[1]]))
            score_endindex_last = gesamtscore(vergleich(target[i - 1], prediction[endindex:index[1]]))

            score_index0_current = gesamtscore(vergleich(target[i], prediction[index[0]:index[1]]))
            score_endindex_current = gesamtscore(vergleich(target[i], prediction[endindex:index[1]]))

            if score_index0_last + score_index0_current >= score_endindex_last + score_endindex_current:
                split_prediction[-1] = prediction[last_index0:index[
                    0]]  # Änderung des letzten Elements der Liste, da nun der Endindex ein anderer ist
                split_prediction.append(prediction[index[0]:index[1]])
            else:
                split_prediction.append(prediction[endindex:index[1]])

        else:
            endindex = index[1]
            last_index0 = index[0]
            split_prediction.append(prediction[index[0]:index[1]])  #

    return split_prediction


def split_neu_matchen(target, prediction, klartext_matches, match_nonmatch_key):
    """Matcht nach einem Split von Wörtern diese neu, und setzt sie direkt ins Dictionary ein."""

    matches, targets_matches_replaced, predictions_matches_replaced = find_matches(targets=target,
                                                                                   predictions=prediction)
    matches_and_nonmatches = sort_matched_and_unmatched(targets_matches_replaced=targets_matches_replaced,
                                                        predictions_matches_replaced=predictions_matches_replaced)
    klartext_matches_split = {}
    for i, (key, value) in enumerate(matches_and_nonmatches.items()):
        klartexte = get_dict_item_at(dict=matches_and_nonmatches, dict_index=i,
                                     targets_matches_replaced=targets_matches_replaced,
                                     predictions_matches_replaced=predictions_matches_replaced, target=target,
                                     prediction=prediction)

        klartext_matches_split[key] = (klartexte[0], klartexte[1])

    klartext_matches[match_nonmatch_key] = klartext_matches_split
    dictionary_mit_einschub, inserted_values = dictionary_einschub(klartext_matches)
    return dictionary_mit_einschub, inserted_values


def dictionary_einschub(dictionary):
    """Durchsucht ein Dictionary nach Typ Dictionary Values und schiebt
     die Values des gefundenen Dictionaries an dieser Stelle ein."""
    inserted_values = 0
    dictionary_mit_einschub = {}
    # Key ist durchgängig, nicht verwechseln mit .items()
    for key, value in enumerate(dictionary.values()):
        if type(value) == dict:
            for value_in_sub_dict in value.values():
                if max(len(liste[0]) for liste in value_in_sub_dict) != 0:  # Filter empty lists
                    dictionary_mit_einschub[str(int(key) + inserted_values)] = value_in_sub_dict
                    inserted_values += 1
            inserted_values -= 1  # da nun auch ein "normaler" Dictionary Key ersetzt wird
        else:
            dictionary_mit_einschub[str(int(key) + inserted_values)] = value
    return dictionary_mit_einschub, inserted_values


def merge_prediction(target, prediction):
    # len(target) = 1, len(prediction) > 1

    target = target[0]  # List zu String
    max_score = 0.05
    indexe_und_pred = []
    unmatched_prediction = prediction
    for start_index in range(len(prediction)):
        for end_index in range(1, len(prediction)):  # siehe split
            prediction_merged = "".join(prediction[start_index:end_index + 1])
            score = gesamtscore(vergleich(target, prediction_merged))
            if score >= max_score:
                max_score = score
                indexe_und_pred = [start_index, end_index, prediction_merged]
    prediction_merged = ""
    if indexe_und_pred:
        prediction_merged = indexe_und_pred[-1]
        # ["---"]*(indexe_und_pred[1]+1-indexe_und_pred[0]), falls man die alte Wortanzahl haben möchte
        unmatched_prediction = prediction[:indexe_und_pred[0]] + ["---"] * (
                indexe_und_pred[1] + 1 - indexe_und_pred[0]) + prediction[indexe_und_pred[1] + 1:]

    return prediction_merged, unmatched_prediction


def rectify_mismatches(dictionary):
    """Falls ein Wort 1:1 gematcht wurde, aber nicht zusammenpasst, wird es hiermit aufgeteilt."""
    for key, value in dictionary.items():
        inserted_values_for_key = 0
        target, prediction = dictionary[str(int(key) + inserted_values_for_key)]
        if len(target) == 1 and len(prediction) == 1:
            score = gesamtscore(vergleich(target[0], prediction[0]))
            if score < 0.07:
                dictionary[key] = {0: (target, [""]), 1: ([""], prediction)}
                dictionary, inserted_values = dictionary_einschub(dictionary)
                inserted_values_for_key += inserted_values
    return dictionary


def words_before_merge(unmatched_prediction):
    """Überprüft, ob ein Wort gemerged wurde (ersetzt durch "---") und schaut, ob Wörter davor waren"""
    # unmatched_prediction = list
    try:
        index_of_match = unmatched_prediction.index("---")
    except:
        index_of_match = 0
    if index_of_match > 0:  # 1 oder größer, d.h. nicht an erster Stelle steht
        return unmatched_prediction[:index_of_match]
    return []


def get_last_index_after_merge(unmatched_prediction):
    unmatched_prediction.reverse()
    try:
        index = unmatched_prediction.index("---")
        unmatched_prediction.reverse()
        return len(unmatched_prediction) - index - 1
    except:
        unmatched_prediction.reverse()
        return len(unmatched_prediction)


def unsqueeze_multiple_values(dictionary):
    """Wenn mehrere Values einem leeren Gegenvalue zugeorndet wurden, werden sie hier vereinzelt."""
    for key, value in dictionary.items():
        dictionary_fuer_einschub = {}
        add_to_key = 0
        if value[0] == [""] and len(value[1]) > 1:
            for predictionword in value[1]:
                dictionary_fuer_einschub[str(int(key) + add_to_key)] = ([""], [predictionword])
                add_to_key += 1
            dictionary[key] = dictionary_fuer_einschub

        elif len(value[0]) > 1 and value[1] == [""]:
            for targetword in value[0]:
                dictionary_fuer_einschub[str(int(key) + add_to_key)] = ([targetword], [""])
                add_to_key += 1
            dictionary[key] = dictionary_fuer_einschub
    dictionary, inserted_values = dictionary_einschub(dictionary)
    return dictionary


def remove_empty_values(dictionary):
    """Leere Dictionary Einträge werden hier entfernt."""
    dictionary = {k: v for k, v in dictionary.items() if
                  v[0] != [""] and v[0] != ["---"] or v[1] != [""] and v[1] != ["---"]}
    return dictionary


def reorganize_keys(dictionary):
    """Sortiert die Values neu. Keys sind jetzt Typ Integer."""
    organized_dict = {}
    for new_key, value in enumerate(dictionary.values()):
        organized_dict[new_key] = value
    return organized_dict


def mark_index_as_matched(unmatched_list, list_with_matches):
    for i in range(len(list_with_matches)):
        if list_with_matches[i] == "---":
            unmatched_list[i] = "---"
    return unmatched_list


def add_before_and_after_merge_the_rest(list_with_rest, dictionary_fuer_einschub):
    first_occurence = last_match(list_with_rest) - 1
    list_with_rest.reverse()
    last_occurence = last_match(list_with_rest) - 1
    list_with_rest.reverse()
    add_before = list_with_rest[:first_occurence]
    add_after = list_with_rest[len(list_with_rest) - last_occurence:]
    if last_match(list_with_rest) == -1:  # Kein Match
        add_before = list_with_rest
        add_after = []
    if add_before:
        einschub_in_einschub = {0: ([""], add_before), 1: dictionary_fuer_einschub[0]}
        dictionary_fuer_einschub[0] = einschub_in_einschub
        dictionary_fuer_einschub, _ = dictionary_einschub(dictionary_fuer_einschub)
    if add_after:
        dictionary_fuer_einschub[len(dictionary_fuer_einschub)] = ([""], add_after)
    return dictionary_fuer_einschub


def betonungszeichen_entfernen(ipa):
    anzahl_betonungszeichen = 0
    indexe_betonungszeichen = []
    # TODO HOMOGRAPH
    ipa_ohne_betonungszeichen = ""
    for i, buchstabe in enumerate(ipa):
        if buchstabe not in ["’", "'", "ˌ", "´", "`", "‘", "’", "‛", "′", "ʻ", "ˈ"]:
            ipa_ohne_betonungszeichen += buchstabe

        else:
            indexe_betonungszeichen.append(i)
            anzahl_betonungszeichen += 1

    return ipa_ohne_betonungszeichen, anzahl_betonungszeichen, indexe_betonungszeichen


def langer_vokal(ipa):
    anzahl_langer_vokale = 0
    indexe_lange_vokale = []
    ipa_ohne_lange_vokale = ""
    for i, buchstabe in enumerate(ipa):
        if buchstabe != "ː":
            ipa_ohne_lange_vokale += buchstabe
        else:
            indexe_lange_vokale.append(i)
            anzahl_langer_vokale += 1

    return ipa_ohne_lange_vokale, anzahl_langer_vokale, indexe_lange_vokale


def check_suffix(target, prediction):
    fehler_liste = []
    matching_sequence = ipa.longest_substring(target, prediction)
    # Endungsvergleich
    targetwort_endung = target[matching_sequence.a + matching_sequence.size:]
    predictionwort_endung = prediction[matching_sequence.b + matching_sequence.size:]
    if targetwort_endung and not predictionwort_endung:
        # Nur Target hat einen Suffix
        fehler_liste.append((4, [targetwort_endung, predictionwort_endung, matching_sequence]))
    if not targetwort_endung and predictionwort_endung:
        # Nur Prediction hat einen Suffix
        pass


def check_prefix(target, prediction):
    fehler_liste = []
    matching_sequence = ipa.longest_substring(target, prediction)
    # Anfangsvergleich
    targetwort_anfang = target[:matching_sequence.a]
    predictionwort_anfang = prediction[:matching_sequence.b]

    if targetwort_anfang and not predictionwort_anfang:
        # Nur Prediction hat keinen Prefix

        fehler_liste.append((3, [targetwort_anfang, predictionwort_anfang, matching_sequence]))
    elif not targetwort_anfang and predictionwort_anfang:
        # Nur Prediction hat keinen Prefix
        fehler_liste.append((3, [targetwort_anfang, predictionwort_anfang, matching_sequence]))



# An die fehler_liste als TUPLE, (FEHLER, optional=weitere Infos)
def remove_ipa_special_characters(wort):
    # Häufigsten Zusatzbuchstaben werden entfernt, da diese zu kleinlich sind um einen Mehrwert zu bieten
    wort_ohne_special_characters = ""
    for buchstabe in wort:
        if buchstabe not in [c for c in "ˈˌːˑ̆|‖x͡yx͡.̋˥́˦̄˧̀˨̏˩̌̂ꜜꜛ↗↘̥̬ʰʲʷ̹̜̟̩̯̈̽˞̰̃ˠˁ"]:
            wort_ohne_special_characters += buchstabe
    return wort_ohne_special_characters


#  ˈˌːˑ̆|‖x    ͡ yx ͡ .̋˥́˦̄˧̀˨̏˩̌̂ꜜꜛ↗↘̥̬ʰʲʷ̹̜̟̩̯̈̽˞̰̃ˠˁ
# Wichtiger ist der zweite Value (x/8)
similarity_values_konsonanten = {"p": (1 / 8, 1 / 22), "b": (1 / 8, 2 / 22), "t": (1 / 8, 5 / 22), "d": (1 / 8, 8 / 22),
                                 "ʈ": (1 / 8, 11 / 22), "ɖ": (1 / 8, 12 / 22), "c": (1 / 8, 13 / 22),
                                 "ɟ": (1 / 8, 14 / 22),
                                 "k": (1 / 8, 15 / 22), "g": (1 / 8, 16 / 22), "ɢ": (1 / 8, 18 / 22),
                                 "ɡ": (1 / 8, 17 / 22),  # vorher nicht vorhanden
                                 "ʔ": (1 / 8, 21 / 22),
                                 "m": (2 / 8, 2 / 22), "ɱ": (2 / 8, 4 / 22), "n": (2 / 8, 8 / 22),
                                 "ɳ": (2 / 8, 12 / 22),
                                 "ɲ": (2 / 8, 14 / 22), "ŋ": (2 / 8, 16 / 22), "ɴ": (2 / 8, 18 / 22),
                                 "ʙ": (3 / 8, 2 / 22), "ʦ": (4.5 / 8, 7 / 22),  # vorher nicht vorhanden
                                 "ʧ": (5 / 8, 8.5 / 22),  # vorher nicht vorhanden
                                 "ʤ": (5 / 8, 7.5 / 22),  # vorher nicht vorhanden
                                 "r": (3 / 8, 8 / 22), "ʀ": (3 / 8, 18 / 22), "ⱱ": (4 / 8, 4 / 22),
                                 "ɾ": (4 / 8, 8 / 22),
                                 "ɽ": (4 / 8, 12 / 22), "ɸ": (5 / 8, 1 / 22), "β": (5 / 8, 2 / 22),
                                 "f": (5 / 8, 3 / 22), "w": (5 / 8, 4.5 / 22),  # vorher nicht vorhanden
                                 "v": (5 / 8, 4 / 22), "θ": (5 / 8, 5 / 22), "ð": (5 / 8, 6 / 22), "s": (5 / 8, 7 / 22),
                                 "z": (5 / 8, 8 / 22), "ʃ": (5 / 8, 9 / 22), "ʒ": (5 / 8, 10 / 22),
                                 "ʂ": (5 / 8, 11 / 22),
                                 "ʐ": (5 / 8, 12 / 22), "ç": (5 / 8, 13 / 22), "ʝ": (5 / 8, 14 / 22),
                                 "x": (5 / 8, 15 / 22),
                                 "ɣ": (5 / 8, 16 / 22), "χ": (5 / 8, 17 / 22), "ʁ": (5 / 8, 18 / 22),
                                 "ħ": (5 / 8, 19 / 22),
                                 "ʕ": (5 / 8, 20 / 22), "ɂ": (5 / 8, 20.5 / 22),  # vorher nicht vorhanden
                                 "h": (5 / 8, 21 / 22), "ɦ": (5 / 8, 22 / 22),
                                 "ɬ": (6 / 8, 5 / 22),
                                 "ɮ": (6 / 8, 8 / 22), "ʋ": (7 / 8, 4 / 22), "ɹ": (7 / 8, 8 / 22),
                                 "ɻ": (7 / 8, 12 / 22),
                                 "j": (7 / 8, 14 / 22), "ɰ": (7 / 8, 16 / 22), "l": (8 / 8, 8 / 22),
                                 "ɭ": (8 / 8, 12 / 22),
                                 "ʎ": (8 / 8, 14 / 22), "ʟ": (8 / 8, 16 / 22)}

# Wird nicht verwendet, da fast kein Buchstabe hiervon vorkommt.
'''similarity_values_pulmonic = {
                             # UNGEMATCHTE BUCHSTABEN, EIGENS AUSGEDACHTE WERTE VERWENDET:
                             "ts": (7/21, 1/5), "dz": (8/21, 1/5), "t̠ʃ": (9/21, 1/5), "d̠ʒ": (10/21, 1/5), "ʈʂ": (11/21, 1/5),
                             "ɖʐ": (12/21, 1/5), "tɕ": (13/21, 1/5), "dʑ": (14/21, 1/5), "pɸ": (1/21, 2/5),
"bβ": (2/21, 2/5), "p̪f": (3/21, 2/5), "b̪v": (4/21, 2/5), "t̪θ": (5/21, 2/5), "d̪ð": (6/21, 2/5), "tɹ̊": (7/21, 2/5), "dɹ": (8/21, 2/5), "tɹ̊": (9/21, 2/5), "dɹ": (10/21, 2/5), cç (13/21, 2/5), ɟʝ (14/21, 2/5), kx (15/21, 2/5), ɡɣ (16/21, 2/5), qχ (17/21, 2/5), ɢʁ (18/21, 2/5), ʡʢ (20/21, 2/5), ʔh (21/21, 2/5)
                             }'''
# Wichtiger ist der zweite Value (x/8)
similarity_values_vokale = {"i": (1 / 3, 2 / 8), "y": (1 / 3, 2 / 8), "ɨ": (2 / 3, 2 / 8), "ʉ": (2 / 3, 2 / 8),
                            "ɯ": (3 / 3, 2 / 8),
                            "u": (3 / 3, 2 / 8), "ɪ": (2 / 6, 3 / 8), "ʏ": (2 / 6, 3 / 8), "ʊ": (5 / 6, 3 / 8),
                            "e": (1 / 3, 4 / 8),
                            "ø": (1 / 3, 4 / 8), "ɘ": (2 / 3, 4 / 8), "ɵ": (2 / 3, 4 / 8), "ɤ": (3 / 3, 4 / 8),
                            "o": (3 / 3, 4 / 8), "õ": (1.5 / 3, 5 / 8),  # Hinzugefügt, aber ähnlich
                            "e̞": (1 / 3, 5 / 8), "ø̞": (1 / 3, 5 / 8), "ə": (2 / 3, 5 / 8), "ɤ̞": (3 / 3, 5 / 8),
                            "o̞": (3 / 3, 5 / 8),
                            "ɛ": (1 / 3, 6 / 8), "œ": (1 / 3, 6 / 8), "ɜ": (2 / 3, 6 / 8), "ɞ": (2 / 3, 6 / 8),
                            "ʌ": (3 / 3, 6 / 8),
                            "ɔ": (3 / 3, 6 / 8), "æ": (1 / 3, 7 / 8), "ɐ": (2 / 3, 7 / 8), "a": (1 / 3, 8 / 8),
                            "ɶ": (1 / 3, 8 / 8), "ã": (1.5 / 3, 7 / 8),  # Hinzugefügt, aber ähnlich
                            "ä": (2 / 3, 8 / 8), "ɑ": (3 / 3, 8 / 8), "ɒ": (3 / 3, 8 / 8)}

ipa_sonderzeichen = ["ː", "’", "'", "ˌ", "´", "`", "‘", "’", "‛", "′", "ʻ", "ˈ", "̩ ", "̩", "̯ "]


def character_auswertung(matches, target_matches_replaced, prediction_matches_replaced, imperfect_matches):
    # Nimmt als Input den Output von character_matching
    if target_matches_replaced == prediction_matches_replaced:
        return 0

    for target_index, prediction_index in matches.items():
        # target_index = str, prediction_index = int
        if str(target_index) == str(prediction_index):
            pass
        # elif target_index


def measure_char_distance(targetchar, predictionchar):
    # Je NIEDRIGER der Score, desto BESSER
    if targetchar in similarity_values_vokale.keys():
        # Ist Vokal
        if predictionchar in similarity_values_vokale.keys():
            target_value = similarity_values_vokale[targetchar]
            prediction_value = similarity_values_vokale[predictionchar]
            score = abs(target_value[0] - prediction_value[0]) + abs(target_value[1] - prediction_value[1]) * 3
            return score
        elif predictionchar in similarity_values_konsonanten.keys() or predictionchar in ipa_sonderzeichen:
            return 4  # Weit über höchstem Score
        else:
            print(targetchar, "|", predictionchar, "ACHTUNG, UNGEMATCHTER BUCHSTABE; WEDER KONSONANT NOCH VOKAL")

    elif targetchar in similarity_values_konsonanten.keys():
        # Ist Konsonant
        if predictionchar in similarity_values_konsonanten.keys():
            target_value = similarity_values_konsonanten[targetchar]
            prediction_value = similarity_values_konsonanten[predictionchar]
            score = abs(target_value[0] - prediction_value[0]) * 3 + abs(target_value[1] - prediction_value[1])
            return score
        elif predictionchar in similarity_values_vokale.keys() or predictionchar in ipa_sonderzeichen:
            return 4
        else:
            print(targetchar, "|", predictionchar, "ACHTUNG, UNGEMATCHTER BUCHSTABE; WEDER KONSONANT NOCH VOKAL")
    elif targetchar in ipa_sonderzeichen:
        if predictionchar in ipa_sonderzeichen:
            if targetchar == predictionchar:
                return 0
            else:
                return 2
    else:
        print(targetchar, "Target, ACHTUNG, UNGEMATCHTER BUCHSTABE; WEDER KONSONANT NOCH VOKAL")
    return 4

sorting_counter = 0
def sort_sequence_dict(sequence_dict, sorted_dict=None):
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


# TODO Hier Character für Character wie oben die matching function vergleichen, aber mit Twist:
# Buchstaben, die sich ähnlich klingen, sollen höhere Similarity Werte erhalten. Dadurch wird das besser
# gematched und Fehler zusätzlich auch direkt erkannt.
# http://www.lehrerasm.it/fileadmin/user_upload/Wortarten/aehnlich_klingende_konsonanten_01.pdf
# https://de.wikipedia.org/wiki/Phonem
# https://en.wikipedia.org/wiki/International_Phonetic_Alphabet
# Hier die Spalte und Zeile nehmen, wenn es dort in der gleichen Reihe noch etwas gibt, dann höherer Score
# Wenn näher dran, dann höhere Score, wenn weiter weg dann geringerer Score
def character_matching(target, prediction):
    global similarity_values_konsonanten, similarity_values_vokale
    target = [i for i in target]  # List
    prediction = [i for i in prediction]  # List
    target_matches_replaced = target.copy()  # List
    prediction_matches_replaced = prediction.copy()  # List
    matches = {}
    last_prediction_matched = 0
    imperfect_matches = {}

    # Damit die IDE nicht gelb markiert. Wird hier oben NICHT verwendet, sondern später definiert
    predictionchar_index = None

    for t_index, target_char in enumerate(target):
        max_matching_score = 4  # Int
        exaktes_match = False
        for p_index, pred_char in enumerate(prediction_matches_replaced):
            counter_nicht_zugeordnet_prediction = count_nicht_zugeorndet(prediction_matches_replaced, p_index)
            counter_nicht_zugeordnet_target = count_nicht_zugeorndet(target_matches_replaced, t_index)
            counter_nicht_zugeordnet = max(counter_nicht_zugeordnet_prediction, counter_nicht_zugeordnet_target)
            if pred_char.endswith(
                    "---") or t_index - p_index > counter_nicht_zugeordnet or last_prediction_matched > p_index:
                continue

            if p_index - t_index > 1 + counter_nicht_zugeordnet:
                break
            score = measure_char_distance(targetchar=target_char, predictionchar=pred_char)
            if score == 0:  # exaktes Match
                exaktes_match = True
                targetchar_index = t_index
                predictionchar_index = p_index

                target_matches_replaced[targetchar_index] = str(t_index) + "---"  # 0---
                prediction_matches_replaced[predictionchar_index] = str(t_index) + "---"  # 0---
                matches[str(targetchar_index)] = predictionchar_index  # {targetindex: predictionindex}
                last_prediction_matched = predictionchar_index
                break
            elif score < max_matching_score:  # KLEINER ALS, da umgekehrt
                max_matching_score = score
                predictionchar_index = p_index

        if not exaktes_match:
            if max_matching_score <= 3:
                targetchar_index = t_index
                target_matches_replaced[targetchar_index] = str(t_index) + "---"
                prediction_matches_replaced[predictionchar_index] = str(t_index) + "---"
                last_prediction_matched = predictionchar_index
                imperfect_matches[(str(t_index) + "---")] = (
                    max_matching_score, target[targetchar_index], prediction[predictionchar_index])
    return matches, target_matches_replaced, prediction_matches_replaced, imperfect_matches
    # TODO: Es wird nicht immer der richtige Character gematched, da direkt der mit dem niedrigsten Wert genommen wird,
    #  auch wenn später noch besser passende kommen. Allerdings ist dies viel zu viel Kleinarbeit, das auf die
    #  Schnelle zu regeln, da es nur geringe Auswirkungen auf das Gesamtergebnis hat.

def sonderzeichen_analyse(anzahl_target, anzahl_prediction, indexe_target, indexe_prediction, fehler_liste,
                          fehlernummer):
    if anzahl_target > anzahl_prediction:
        # Target hat mehr Betonungszeichen
        fehler_liste.append((fehlernummer, [1, indexe_target, indexe_prediction]))
    elif anzahl_target == anzahl_prediction:
        for index_target, index_pred in zip(indexe_target, indexe_prediction):
            if abs(index_target - index_pred) > 1:
                fehler_liste.append((fehlernummer, [2, index_target, index_pred]))
    elif anzahl_target < anzahl_prediction:
        fehler_liste.append((fehlernummer, [3, indexe_target, indexe_prediction]))
    return fehler_liste


def get_unique_key_for_dict(dictionary):
    i = 0
    while True:
        if i in dictionary.keys():
            i += 1
        else:
            return i


def einzelvergleich(target, prediction):
    fehler_liste = []
    if len(target) == 1 and len(prediction) > 1:
        prediction = ["".join(prediction)]

    if len(target) > 1 and len(prediction) > 1:
        # Kommt hoffentlich nicht vor, für denn fall der Fälle wird es eben grob gematched, aber eigentlich
        fehler_liste.append((-1, [target, prediction]))
        prediction = [" ".join(prediction)]
        target = [" ".join(target)]

    if len(target) > 1 and len(prediction) == 1:
        # Sollte nicht passieren, tuts aber trotzdem:
        target = [" ".join(target)]

    #print(target, prediction)
    target, prediction = target[0], prediction[0]
    #print(target, prediction)
    if target == prediction:
        print("TARGET:", bcolors.OKGREEN + target + bcolors.ENDC)
        print("PREDICTION:", bcolors.OKGREEN + prediction + bcolors.ENDC)
        return [(0,)], bcolors.OKGREEN + target + bcolors.ENDC,  bcolors.OKGREEN + prediction + bcolors.ENDC

    elif prediction == "":
        print("TARGET:", bcolors.WARNING + target + bcolors.ENDC)
        print("PREDICTION:", bcolors.FAIL + str("___ "*len(target.split())).strip() + bcolors.ENDC)
        return [(1,)], bcolors.WARNING + target + bcolors.ENDC, bcolors.FAIL + str("___ "*len(target.split())).strip() + bcolors.ENDC

    elif target == "":
        print("TARGET:")
        print("PREDICTION:", bcolors.FAIL + prediction + bcolors.ENDC)
        return [(2,)], "", bcolors.FAIL + prediction + bcolors.ENDC

    # Vorbereitung für die jeweils andere Analyse: Lange Vokale entfernen, um verbesserte Betonungszeichenanalyse durchzuführen
    target_ohne_langer_vokal, _, _ = langer_vokal(target)
    prediction_ohne_langer_vokal, _, _ = langer_vokal(prediction)

    target_ohne_betonung, _, _ = betonungszeichen_entfernen(target)
    prediction_ohne_betonung, _, _ = betonungszeichen_entfernen(prediction)

    # Betonungsanalyse:
    _, anzahl_betonungszeichen_target, betonungszeichen_indexe_target = betonungszeichen_entfernen(
        target_ohne_langer_vokal)
    _, anzahl_betonungszeichen_prediction, betonungszeichen_indexe_prediction = betonungszeichen_entfernen(
        prediction_ohne_langer_vokal)

    fehler_liste = sonderzeichen_analyse(anzahl_target=anzahl_betonungszeichen_target,
                                         anzahl_prediction=anzahl_betonungszeichen_prediction,
                                         indexe_target=betonungszeichen_indexe_target,
                                         indexe_prediction=betonungszeichen_indexe_prediction,
                                         fehler_liste=fehler_liste, fehlernummer=7)

    # Langervokalanalyse
    target_ohne_vokale_und_betonung, anzahl_lange_vokale_target, lange_vokale_indexe_target = langer_vokal(
        target_ohne_betonung)
    prediction_ohne_vokale_und_betonung, anzahl_lange_vokale_prediction, lange_vokale_indexe_prediction = langer_vokal(
        prediction_ohne_betonung)
    fehler_liste = sonderzeichen_analyse(anzahl_target=anzahl_lange_vokale_target,
                                         anzahl_prediction=anzahl_lange_vokale_prediction,
                                         indexe_target=lange_vokale_indexe_target,
                                         indexe_prediction=lange_vokale_indexe_prediction, fehler_liste=fehler_liste,
                                         fehlernummer=11)

    target_ohne_vokale_und_betonung = remove_ipa_special_characters(target_ohne_vokale_und_betonung)
    prediction_ohne_vokale_und_betonung = remove_ipa_special_characters(prediction_ohne_vokale_und_betonung)

    # _, matchings = sequence_matching(target_ohne_vokale_und_betonung, prediction_ohne_vokale_und_betonung)
    #print(colored((target, prediction), "yellow"))
    _, matchings = sequence_matching(target, prediction)
    #print(matchings)
    sorted_sequence_dict = sort_sequence_dict(dict(sorted(matchings.items())))
    prediction_output = ""
    target_output = ""
    #print(sorted_sequence_dict)
    for value in sorted_sequence_dict.values():
        target_sequence = value[0]
        prediction_sequence = value[1]

        if target_sequence == prediction_sequence:
            target_output += bcolors.OKGREEN + target_sequence + bcolors.ENDC
            prediction_output += bcolors.OKGREEN + prediction_sequence + bcolors.ENDC
        elif target_sequence and prediction_sequence == "":
            target_output += bcolors.WARNING + target_sequence + bcolors.ENDC
            prediction_output += bcolors.UNDERLINE + bcolors.FAIL + " " + bcolors.ENDC
            fehler_liste.append((6, [target_sequence, "_"]))

        elif target_sequence == "" and prediction_sequence:
            prediction_output += bcolors.FAIL + prediction_sequence + bcolors.ENDC
            fehler_liste.append((8, ["_", prediction_sequence]))

        else:
            target_output += bcolors.WARNING + target_sequence + bcolors.ENDC
            prediction_output += bcolors.WARNING + prediction_sequence + bcolors.ENDC
            fehler_liste.append((5, [target_sequence, prediction_sequence]))

    print("TARGET:", target_output)
    print("PREDICTION:", prediction_output, fehler_liste)

    return fehler_liste, target_output, prediction_output


# Fehlerliste Zahlen sind durcheinander, !!!ES TRETEN FAST IMMER MEHRERE FEHLER AUF EINMAL AUF, DA ÜBERSCHNEIDUNG!!!:
# 0 = Kein Fehler
# 1 = Wort nicht von der KI erkannt (Wort bei Target, keins bei der Prediction)
# 2 = Wort zuviel von der KI erkannt (Wort bei der Prediction, keins bei dem Target)
# 3 = Fehler am ANFANG
# 4 = Fehler am ENDE
# 5 = Generelle undeutliche Aussprache (nicht näher spezifiziert)
# 6 = Fehlende Buchstaben oder Sonderzeichen (nicht näher spezifiziert)
# 7 = Betonungszeichen FEHLER
# 8 = Buchstaben oder Sonderzeichen zu viel
# 9 = Falscher Konsonant
# HÄUFIG!!! : \/
# 10 = Erst Wort zu viel erkannt, dann nicht nicht erkannt --> Nicht gematcht, da zu unterschiedlich
# HÄUFIG!!! : /\
# 11 = Langer Vokal FEHLER



# TODO: Dictionarykeys aus Zahlen als Integer umformen überall
