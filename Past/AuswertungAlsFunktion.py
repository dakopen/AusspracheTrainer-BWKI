from SimilarityMetrics import *
from IPAclass import *
from Auswertungsfunktionen2 import *

ipa = IPA()

def auswertung(target, prediction):
    def strip_verarbeitung(liste):
        liste = str(liste).lower().replace("[", "").replace("]", "").replace(",", "").replace("'", "")
        return liste

    if "[" in target:
        target = strip_verarbeitung(target).split()
    else:
        target = str(target).lower().split()
    if "[" in prediction:
        prediction = strip_verarbeitung(prediction).split()
    else:
        prediction = str(prediction).lower().split()
    matches, targets_matches_replaced, predictions_matches_replaced = find_matches(targets=target, predictions=prediction)

    matches_and_nonmatches = sort_matched_and_unmatched(targets_matches_replaced=targets_matches_replaced,
                                                        predictions_matches_replaced=predictions_matches_replaced)

    klartext_matches = {}
    for i, (key, value) in enumerate(matches_and_nonmatches.items()):
        """Füllt ein Dictionary mit Klartextwerten. 
        Key = incremating number, Value = (["wort"], ["wort"])"""

        # Key sollte enumeration entsprechen, kann sich aber in Zukunft evtl ändern
        klartexte = get_dict_item_at(dict=matches_and_nonmatches, dict_index=i,
                                     targets_matches_replaced=targets_matches_replaced,
                                     predictions_matches_replaced=predictions_matches_replaced, target=target,
                                     prediction=prediction)

        klartext_matches[key] = (klartexte[0], klartexte[1])  # ['ich'], ['ich']
    inserted_values_for_key = 0
    for i, (match_nonmatch_key, value) in enumerate(matches_and_nonmatches.items()):
        print(colored(klartext_matches, "green"), match_nonmatch_key, "KEY")
        current_target, current_prediction = klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key)]
        #print(colored((current_target, current_prediction), "yellow"))
        next_previous_scores = {-1: 0, +1: 0}  # previous = -1, next = +1
        #print(colored((current_target, current_prediction), "green"))

        # Zwei Fälle
        # 1. bei der Prediction ist es zu viel und man muss es mergen
        # 2. beim Target ist das Wort zu viel und man muss die Prediction splitten
        # 3. bei Target und Prediction sind mehrere Wörter nicht gematcht und man muss sie splitten und/oder mergen

        # 1
        if current_target == [""]:
            current_target, current_prediction = current_target[-1], current_prediction[-1]
            if i > 0:
                next_previous_scores = get_score_pn(match_nonmatch_key=str(int(match_nonmatch_key)+inserted_values_for_key),
                                                    index_position_changer=-1,
                                                    klartext_matches=klartext_matches,
                                                    next_previous_scores=next_previous_scores,
                                                    current_prediction=current_prediction)

            if len(matches_and_nonmatches) > i + 1:
                next_previous_scores = get_score_pn(match_nonmatch_key=str(int(match_nonmatch_key)+inserted_values_for_key),
                                                    index_position_changer=1,
                                                    klartext_matches=klartext_matches,
                                                    next_previous_scores=next_previous_scores,
                                                    current_prediction=current_prediction)

            # zuerst das nächste testen, da es in der Realität wahrscheinlicher ist

            if next_previous_scores[1] > next_previous_scores[-1] and next_previous_scores[
                1] > 0.07:  # -1 *nicht* verwechseln mit letztem Listeneintrag. Das ist ein Dictionary
                # MERGE NEXT AND CURRENT
                klartext_matches = merge(match_nonmatch_key=str(int(match_nonmatch_key)+inserted_values_for_key), index_position_changer=1,
                                         klartext_matches=klartext_matches, current_prediction=current_prediction)

            elif next_previous_scores[1] < next_previous_scores[-1] and next_previous_scores[-1] > 0.07:
                # MERGE PREVIOUS AND CURRENT
                klartext_matches = merge(match_nonmatch_key=str(int(match_nonmatch_key)+inserted_values_for_key), index_position_changer=-1,
                                         klartext_matches=klartext_matches, current_prediction=current_prediction)

        if len(current_target) == 1 and current_prediction == [""]:
            # TODO schöner / effizienter aufschreiben
            # z.B. e gitarre
            next_previous_scores = {-1: [0], +1: [0]}  # previous = -1, next = +1

            if len(klartext_matches) > int(match_nonmatch_key) + inserted_values_for_key + 1:
                next_target, next_prediction = klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key + 1)]
                current_score_before = gesamtscore(vergleich(current_target[0], current_prediction[0]))
                prediction_split = split(target=current_target, prediction=next_prediction)
                current_score_after = gesamtscore(vergleich(current_target[0], prediction_split[0]))
                new_score_before = gesamtscore(vergleich(next_target[0], next_prediction[0]))
                new_score_after = gesamtscore(vergleich(next_target[0], str(
                    klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key + 1)][1][0])[
                                                                     len(prediction_split[0]):]))

                if new_score_after * 2 + current_score_after > new_score_before * 2 + current_score_before:  # * 2, um dem besondere Bedeutung zuzuweisen
                    next_previous_scores[+1] = [new_score_after * 2 + current_score_after, next_target, [
                        str(klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key + 1)][1][0])[
                        len(prediction_split[0]):]], prediction_split]

            if int(match_nonmatch_key) + inserted_values_for_key + 1 > 1:
                previous_target, previous_prediction = klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key - 1)]

                current_score_before = gesamtscore(vergleich(current_target[0], current_prediction[0]))
                prediction_split = split(target=current_target, prediction=previous_prediction)
                current_score_after = gesamtscore(vergleich(current_target[0], prediction_split[0]))
                new_score_before = gesamtscore(vergleich(previous_target[0], previous_prediction[0]))
                new_score_after = gesamtscore(vergleich(previous_target[0], str(
                    klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key - 1)][1][0])[
                                                                         :-len(prediction_split[0])]))
                if new_score_after * 2 + current_score_after > new_score_before * 2 + current_score_before:  # * 2, um dem besondere Bedeutung zuzuweisen
                    next_previous_scores[-1] = [new_score_after * 2 + current_score_after, previous_target, [str(klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key - 1)][1][0])[:-len(prediction_split[0])]], prediction_split]

            if next_previous_scores[1][0] > next_previous_scores[-1][0]:
                klartext_matches, inserted_values = split_neu_matchen(target=current_target,
                                                                      prediction=next_previous_scores[1][-1],
                                                                      klartext_matches=klartext_matches,
                                                                      match_nonmatch_key=str(int(match_nonmatch_key)+inserted_values_for_key))

                inserted_values_for_key += inserted_values
                klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key + 1)] = (
                next_previous_scores[1][1], next_previous_scores[1][-2])

            elif next_previous_scores[1][0] < next_previous_scores[-1][0]:
                klartext_matches, inserted_values = split_neu_matchen(target=current_target,
                                                                      prediction=next_previous_scores[-1][-1],
                                                                      klartext_matches=klartext_matches,
                                                                      match_nonmatch_key=str(int(match_nonmatch_key)+inserted_values_for_key))

                inserted_values_for_key += inserted_values
                klartext_matches[str(int(match_nonmatch_key) + inserted_values_for_key - 1)] = (next_previous_scores[-1][1], next_previous_scores[-1][-2])


        # 2
        elif len(current_target) > 1 and len(current_prediction) == 1:
            # SPLIT

            prediction_split = split(current_target, current_prediction)
            if current_prediction[0] not in prediction_split:  # Es wurde wirklich etwas gesplittet
                print(colored(prediction_split, "yellow"))
                klartext_matches, inserted_values = split_neu_matchen(target=current_target, prediction=prediction_split,
                                                                      klartext_matches=klartext_matches,
                                                                      match_nonmatch_key=str(int(match_nonmatch_key)+inserted_values_for_key))
                inserted_values_for_key += inserted_values
        elif len(current_target) == 1 and len(current_prediction) > 1:
            # MERGE
            prediction_merged, unmatched_prediction = merge_prediction(target=current_target, prediction=current_prediction)
            dictionary_fuer_einschub = {}
            prediction_merged_is_in_dict = False
            if "---" not in unmatched_prediction:
                continue
            for einschub_key, unmatched_predictionword in enumerate(unmatched_prediction):
                if unmatched_predictionword == "---" and not prediction_merged_is_in_dict:
                    target_einschub_value = current_target
                    unmatched_predictionword = prediction_merged
                    prediction_merged_is_in_dict = True  # sonst hat man mehrere ersetzte Predictions durch merge
                elif unmatched_predictionword == "---" and prediction_merged_is_in_dict:
                    continue
                else:
                    target_einschub_value = [""]

                dictionary_fuer_einschub[einschub_key] = (target_einschub_value, [unmatched_predictionword])

            klartext_matches[str(int(match_nonmatch_key)+inserted_values_for_key)] = dictionary_fuer_einschub
            klartext_matches, inserted_values = dictionary_einschub(klartext_matches)
            inserted_values_for_key += inserted_values

        elif len(current_target) > 1 and len(current_prediction) > 1:
            continue  # Kein Problem, der Sequence Matcher regelt den Rest
            ''' # ANDERSWEITIGE ZUORDNUNG
            dictionary_fuer_einschub = {}
            unmatched_before = 0
            last_unmatched_prediction = []
            unmatched_pred_before = []
            last_einschub_key = 0
            plus_einschub_key = 0
            current_prediction_matched = current_prediction.copy()
            for einschub_key, targetwort in enumerate(current_target):
                prediction_merged, unmatched_prediction = merge_prediction(target=[targetwort],
                                                                           prediction=current_prediction)

                unmatched_pred_before = words_before_merge(unmatched_prediction=unmatched_prediction)
                current_prediction_matched = mark_index_as_matched(current_prediction_matched, unmatched_prediction)
                if any(i for i in current_prediction_matched[:get_last_index_after_merge(current_prediction_matched)] if i != "---"):
                    dictionary_fuer_einschub[einschub_key+plus_einschub_key] = ([""], [j for j in current_prediction_matched if j != "---"])
                    print(dictionary_fuer_einschub)
                    plus_einschub_key += 1

                    current_prediction_matched[:get_last_index_after_merge(current_prediction_matched)] = ["---"]*get_last_index_after_merge(current_prediction_matched)
                dictionary_fuer_einschub[einschub_key+plus_einschub_key] = ([targetwort], [prediction_merged])
                last_unmatched_prediction = unmatched_prediction
                print(colored(dictionary_fuer_einschub, "red"))
                print(current_prediction_matched)
                print(colored(unmatched_pred_before, "yellow"))
            if get_last_index_after_merge(current_prediction_matched) != len(current_prediction_matched):
                dictionary_fuer_einschub[len(current_target)+plus_einschub_key+1] = ([""], current_prediction_matched[get_last_index_after_merge(current_prediction_matched)+1:])


            dictionary_fuer_einschub = add_before_and_after_merge_the_rest(list_with_rest=current_prediction_matched,
                                                                           dictionary_fuer_einschub=dictionary_fuer_einschub)

            klartext_matches[str(int(match_nonmatch_key)+inserted_values_for_key)] = dictionary_fuer_einschub
            klartext_matches, inserted_values = dictionary_einschub(klartext_matches)
            inserted_values_for_key += inserted_values'''
        #print(colored(klartext_matches, "red"))
    print(colored(klartext_matches, "red"))
    print(colored(klartext_matches, "blue"))

    klartext_matches = unsqueeze_multiple_values(klartext_matches)
    print(colored(klartext_matches, "blue"))
    #klartext_matches = rectify_mismatches(klartext_matches)  # Diese Funktion bildet leider keinen Mehrwert
    klartext_matches = remove_empty_values(klartext_matches)
    klartext_matches = reorganize_keys(klartext_matches)
    print("-----" * 3)
    print(colored(klartext_matches, "blue"))
    klartext_matches = get_empty_dict_values(klartext_matches)
    print(colored(klartext_matches, "blue"))
    klartext_matches = remove_empty_values(klartext_matches)
    klartext_matches = reorganize_keys(klartext_matches)
    print(colored(klartext_matches, "yellow"))
    prediction_output_merged = ""
    target_output_merged = ""
    fehler_liste = []
    for i, (target, prediction) in klartext_matches.items():
        #target = ipa.text_zu_IPA(target)
        #prediction = ipa.text_zu_IPA(prediction)
        fehler, target_output, prediction_output = einzelvergleich(target, prediction)
        prediction_output_merged += " " + prediction_output
        target_output_merged += " " + target_output
        fehler_liste.append(fehler)
    target_output_merged = re.sub(' +', ' ', target_output_merged)
    prediction_output_merged = re.sub(' +', ' ', prediction_output_merged)

    return klartext_matches, target_output_merged.strip(), prediction_output_merged.strip(), fehler_liste
#auswertung(str(['eːs', 'vaːɐ̯', 'ˈaɪ̯nmaːl', 'aɪ̯n', 'ˈmʏlɐ', 'ˈdeːɐ̯', 'vaːɐ̯', 'aʁm', 'ˈaːbɐ', 'eːɐ̯', 'ˈhatə', 'ˈaɪ̯nə', 'ˈʃøːnə', 'ˈtɔχtɐ']), str([['eːs'], ['vaːɐ̯'], ['ˈaɪ̯nmaːl'], ['ˈaɪ̯nən'], ['ˈmʏlɐ'], ['ˈdeːɐ̯'], ['vaːɐ̯'], ['aʁm'], ['ˈaːbɐ'], ['eːɐ̯'], ['ˈhatə'], ['ˈaɪ̯nəs'], ['ˈʃøːnə'], ['ˈtɔχtɐ']]))
#auswertung(str(['eːs', 'vaːɐ̯', 'ˈaɪ̯nmaːl', 'aɪ̯n', 'ˈmʏlɐ', 'ˈdeːɐ̯', 'vaːɐ̯', 'aʁm', 'ˈaːbɐtn', 'eːɐ̯', 'ˈhatə', 'ˈaɪ̯nə', 'ˈʃøːnə', 'ˈtɔχtɐ']), str(['eːs', 'vaːɐ̯', 'ˈaɪ̯nmaːl', 'aɪ̯n', 'ˈmʏlɐ', 'ˈdeːɐ̯', 'ˈvaːɐ̯ˌhaːbn̩', 'ˈaːbɐm', 'ˈhatə', 'ˈaɪ̯nə', 'ˈʃøːnə', 'ˈtɔχtɐ']))
#auswertung("tm", "odn")