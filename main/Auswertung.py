import re
from termcolor import colored
from Funktionen import einzelvergleich, bcolors


class Sprachfehler:
    # Laute, die Fehlerhaft werden sind Key; die Values repräsentieren, wonach es sich wahrscheinlich anhört
    SIGMATISMUS = {"ʃ": "f", "s": "f", "ç": "f", "z": "f"}  # Auch als Lispeln bekannt

    # Weitere Sprachfehler einfügen


def char_score_berechnen(target_output, char_scores, target):
    """Errechnet basierend auf den farbigen Markierungen der vorangegangen Kalkulation den Score. Wenn ein Teil
    des Targetsatzes gelb markiert (WARNING) ist - also sich fehlerhaft in der Prediction widerspiegelt - wird dieser
    Buchstabe mit einem geringeren Score versehen. Dieser Buchstabe in den anderen Predictions auch markiert wurde,
    wird der Score immer niedriger."""
    # https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring
    a = ([m.start() for m in re.finditer('\\033\[0m'.encode("utf-8").decode("utf-8"), target_output)])  # ENDC
    b = ([m.start() for m in re.finditer('\\033\[93m'.encode("utf-8").decode("utf-8"), target_output)])  # WARNING
    c = ([m.start() for m in re.finditer('\\033\[92m'.encode("utf-8").decode("utf-8"), target_output)])  # OKGREEN

    char_zuordnung = {}
    char_index_score = 0

    for key in b:
        char_zuordnung[key] = "b"
    for key in c:
        char_zuordnung[key] = "c"

    for i, (key, char) in enumerate(sorted(char_zuordnung.items())):
        start_at = key + 5
        stop_at = a[i]
        chars = target_output[start_at:stop_at]
        if char == "b":
            score = 0.33
        else:  # char == "c":
            score = 0
        for j in range(len(chars)):
            if target[char_index_score] == " " and chars[j] != " ":
                print(colored("CHARINDEXSCORE+1", "blue"), char_index_score, target[char_index_score])
                char_index_score += 1
            char_scores[char_index_score] = char_scores[char_index_score] - score
            char_index_score += 1

    return char_scores


def chars_zu_viel(prediction):
    """Sollten Teile der Prediction rot markiert sein (FAIL) - also überhaupt nicht gematched sein (bzw. überflüssig)
    so wird hier der Score errechnet, der dadurch abgezogen werden muss. Er wird prozentual abgezogen."""
    len_sequence = len(prediction)
    minus_score = 0
    a = ([m.start() for m in re.finditer('\\033\[0m'.encode("utf-8").decode("utf-8"), prediction)])  # ENDC
    b = ([m.start() for m in re.finditer('\\033\[93m'.encode("utf-8").decode("utf-8"), prediction)])  # WARNING
    c = ([m.start() for m in re.finditer('\\033\[92m'.encode("utf-8").decode("utf-8"), prediction)])  # OKGREEN
    d = ([m.start() for m in re.finditer('\\033\[91m'.encode("utf-8").decode("utf-8"), prediction)])  # FAIL

    char_zuordnung = {}

    for key in b:
        char_zuordnung[key] = "b"
    for key in c:
        char_zuordnung[key] = "c"
    for key in d:
        char_zuordnung[key] = "d"
    for i, (key, char) in enumerate(sorted(char_zuordnung.items())):
        if char == "d":
            start_at = key + 5
            stop_at = a[i]
            chars = prediction[start_at:stop_at]
            chars = [i for i in chars if i != "_"]
            score = (len(chars) / len_sequence) / 3  # Da es 3 Predictions gibt, sonst wäre zu viel Minus
            minus_score += score

    return minus_score


def sprachfehler_analysieren(char_scores, target):
    """Analysiert den Satz bzw. die schon kalkulierten Char-Scores auf bestimmte Muster, sodass z.B. ein 'sch', 's'
    'ç' oder 'z' häufiger schlecht ausgesprochen wird. Dies könnte ein Anzeichen für (in disem Fall) Lispeln sein."""
    sigmatismus_anzahl = 0
    sigmatismus_score = 0
    for index, score in char_scores.items():
        if target[index] in Sprachfehler.SIGMATISMUS.keys():
            sigmatismus_anzahl += 1
            sigmatismus_score += score
    return sigmatismus_score / sigmatismus_anzahl  # Durchschnitt ausgeben


def auswertung(target, predictions):
    """Vergleicht den Targetsatz mit den 3 Predictions. Je nach Qualität der Aussprache wird der Satz in folgenden
    Farben wieder ausgegeben:
    Grün (perfekt), Lila (leicht unverständlich), Gelb (unverständlich), Rot (sehr unverständlich)
    Außerdem wird die Aussprache auf Sprachfehler (zurzeit nur Sigmatimus (Lispeln)) überprüft.
    """
    _, target_output, prediction_output = einzelvergleich(target, predictions[0])
    _, target_output2, prediction_output2 = einzelvergleich(target, predictions[1])
    _, target_output3, prediction_output3 = einzelvergleich(target, predictions[2])

    char_scores = {}
    for c, char in enumerate(target):
        char_scores[c] = 1
    char_scores = char_score_berechnen(target_output, char_scores, target)
    char_scores = char_score_berechnen(target_output2, char_scores, target)
    char_scores = char_score_berechnen(target_output3, char_scores, target)

    print(bcolors.BOLD + "Target" + bcolors.ENDC)
    print(target_output)
    print(target_output2)
    print(target_output3)
    print(bcolors.BOLD + "Predictions" + bcolors.ENDC)
    print(prediction_output)
    print(prediction_output2)
    print(prediction_output3)

    # Leerzeichen sollten immer einen Score von 1 haben,
    # da es mehrere Schreibweisen von Wörtern gibt: e gitarre / egitarre; zu hause / zuhause, etc.
    for index in char_scores.keys():
        if target[index] == " ":
            char_scores[index] = 1

    final_output = ""
    for index, score in char_scores.items():
        if score <= 0.1:  # durch Decimalverhalten ohne das Decimal Package wird 0.10 zu 0.09999999999999998
            final_output += bcolors.FAIL
        elif score <= 0.4:
            final_output += bcolors.WARNING
        elif score <= 0.7:
            final_output += bcolors.INACCURACY
        else:
            final_output += bcolors.OKGREEN
        final_output += target[index]
        final_output += bcolors.ENDC

    overall_score = sum(char_scores.values()) / len(char_scores)
    print()
    print(bcolors.BOLD + "Auswertung" + bcolors.ENDC)

    print(final_output)
    overall_score -= (chars_zu_viel(prediction_output) + chars_zu_viel(prediction_output2) + chars_zu_viel(
        prediction_output3))
    sigmatismus = sprachfehler_analysieren(char_scores, target)

    # overall_score * 0.9, da dadurch ein Muster bestätigt wird und nicht zu oft falsch-positiv diese Auswertung kommt.
    if overall_score * 0.9 > sigmatismus and 0.6 <= sigmatismus <= 0.9:
        print(f"{bcolors.WARNING}Überdurchschnittlich ungenaue Aussprache der Zischlaute "
              f"(Lispeln = {list(Sprachfehler.SIGMATISMUS.keys())}). {bcolors.ENDC}")
    elif sigmatismus < 0.6:
        print(f"{bcolors.FAIL}Auffällig ungenaue Aussprache der Zischlaute "
              f"(Lispeln = {list(Sprachfehler.SIGMATISMUS.keys())}).{bcolors.ENDC}")
    # print("Sigmatismus-Score:", sigmatismus), anschalten, wenn man den sigmatismus-score sich angucken möchte

    bewertung_des_scores = "Deine Aussprache ist "
    if overall_score > 0.95:
        print(bewertung_des_scores + "exzellent | Score:", overall_score)
    elif overall_score > 0.90:
        print(bewertung_des_scores + "sehr gut | Score:", overall_score)
    elif overall_score > 0.85:
        print(bewertung_des_scores + "gut | Score:", overall_score)
    elif overall_score > 0.80:
        print(bewertung_des_scores + "verständlich | Score:", overall_score)
    elif overall_score > 0.75:
        print(bewertung_des_scores + "meistens verständlich | Score:", overall_score)
    elif overall_score > 0.70:
        print(bewertung_des_scores + "oft verständlich | Score:", overall_score)
    elif overall_score > 0.65:
        print(bewertung_des_scores + "für andere manchmal unverständlich | Score:", overall_score)
    elif overall_score > 0.60:
        print(bewertung_des_scores + "für andere häufig unverständlich | Score:", overall_score)
    elif overall_score > 0.55:
        print(bewertung_des_scores + "für andere sehr häufig unverständlich | Score:", overall_score)
    elif overall_score > 0.50:
        print(bewertung_des_scores + "für andere schwierig zu verstehen | Score:", overall_score)
    elif overall_score > 0.45:
        print(bewertung_des_scores + "für andere sehr schwierig zu verstehen | Score:", overall_score)
    elif overall_score > 0.30:
        print(bewertung_des_scores + "für andere fast nicht zu verstehen | Score:", overall_score)
    elif overall_score > 0.20:
        print(bewertung_des_scores + "für andere gar nicht zu verstehen | Score:", overall_score)
    else:
        print(bewertung_des_scores + "grundsätzlich unverständlich | Score:", overall_score)

    if overall_score < 0.7:
        print("Wir empfehlen dringend Übungen zur verbesserten Aussprache zu machen.")
    if overall_score < 0.55:
        print("Außerdem könnte eine logopädische Praxis Dir bei diesem Thema behilflich sein.")

