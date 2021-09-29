import logging
import pickle
import requests
from difflib import SequenceMatcher

class IPA:
    def __init__(self):
        self.IPA_dict = IPA.IPA_dict_laden()

    @staticmethod
    def IPA_dict_laden():
        """Lädt das IPA_dict. Sollte das Programm zum ersten Mal laufen ist es natürlich noch nicht vorhanden."""
        try:
            with open(r"./IPA_dict.pickle", "rb") as IPA_dict_speicherort:
                IPA_dict = pickle.load(IPA_dict_speicherort)
            logging.info("IPA_dict geladen.")
        except:
            IPA_dict = {}
        return IPA_dict

    @staticmethod
    def IPA_dict_speichern(IPA_dict):
        """Speichert das IPA_dict, welches Wörter und IPA beinhaltet, damit jene nicht erneut abgefragt werden."""
        with open(r"./IPA_dict.pickle", "wb") as IPA_dict_speicherort:
            pickle.dump(IPA_dict, IPA_dict_speicherort)
        logging.info("IPA_dict gespeichert.")

    @staticmethod
    def send_to_dwds(wort, retry=0):  # Deprecated
        """Nutzt die API des DWDS, um Wörter in Lautschrift (IPA) zu übertragen. Gelegentlich kommt es zu Netzwerk-
        schwankungen, daher die retry-Funktion."""
        IPA = []
        response = requests.get("https://www.dwds.de/api/ipa/?q=%s" % wort)  # Maximallänge des Wortes = 20 Buchstaben
        if response.status_code == 200:
            responseJson = response.json()
            logging.info(responseJson)
            for x in range(len(responseJson)):
                IPA.append(responseJson[x]["ipa"])
            logging.info("IPA: " + str(IPA))
            return IPA[0]
        else:
            if retry < 5:
                IPA.send_to_dwds(wort=wort, retry=retry+1)
            raise ConnectionError("Keine gültige Antwort")

    @staticmethod
    def send_to_gramophone(wort, retry=0):
        wort = str(wort).lower()  # Großbuchstaben versteht Gramophone nicht
        response = requests.get("https://kaskade.dwds.de/~kmw/gramophone.py?q=%s" % wort)  # Max Länge = 25 Buchstaben
        if response.status_code == 200:
            response = str(response.text)
            response_index_left = response.find("<tr><td>Segmented Transcription</td><td><tt>")
            if response_index_left != -1:
                response_lstrip = response[response_index_left + 44:]
            else:
                response_lstrip = ""

            response_index_right = response_lstrip.find("</tt></td></tr>")
            if response_index_right != -1:
                response = response_lstrip[:response_index_right]
            else:
                response = ""

            if response:
                response_split = response.split()
                ipa_buchstaben = []

                for buchstabenpaar in response_split:
                    try:
                        klartext = buchstabenpaar.split(",")[0]
                        ipa = buchstabenpaar.split(",")[1]
                        ipa_buchstaben.append([klartext, ipa])
                    except:
                        break
            else:
                # Irgendetwas ist schief gelaufen: DEBUGGEN!!
                raise Exception("KEINE GÜLTIGE ANTWORT VON GRAMOPHONE", wort, retry)

            ipa_ganzes_wort = "".join([i[1] for i in ipa_buchstaben])
            return ipa_ganzes_wort, ipa_buchstaben
        else:
            if retry < 5:
                IPA.send_to_gramophone(wort=wort, retry=retry + 1)
            raise ConnectionError("Keine gültige Antwort")

    @staticmethod
    def zahl_zu_text_sortieren(textliste):
        """Überpürft Wort für Wort, ob es sich um eine Zahl handelt. Ist dass der Fall, wird sie in Text umgeformt."""
        # text = Liste
        for i in range(len(textliste)):
            if textliste[i].isnumeric():
                wort = IPA.zahl_zu_text(textliste[i])
                textliste[i] = wort
        return textliste

    @staticmethod
    def zahl_zu_text(eingabe_zahl):  # Für Zahlen von 0-1.000.000
        """Substituiert eine Zahl mit dem alphabetischen Equivalent: 95 zu fünfundneunzig"""
        eingabe_zahl = int(eingabe_zahl)
        if eingabe_zahl == 0:
            return "Null"
        dictionary = {1000000: 'million', 1000: 'tausend', 100: 'hundert', 90: 'neunzig', 80: 'achtzig', 70: 'siebzig',
                      60: 'sechzig',
                      50: 'fünfzig', 40: 'vierzig', 30: 'dreißig', 20: 'zwanzig', 19: 'neunzehn', 18: 'achtzehn',
                      17: 'siebzehn', 16: 'sechzehn', 15: 'fünfzehn', 14: 'vierzehn', 13: 'dreizehn', 12: 'zwölf',
                      11: 'elf', 10: 'zehn', 9: 'neun', 8: 'acht', 7: 'sieben', 6: 'sechs', 5: 'fünf', 4: 'vier',
                      3: 'drei',
                      2: 'zwei', 1: 'ein'}
        zusammenrechnen = {1000000: 0, 1000: 0, 100: 0, 90: 0, 80: 0, 70: 0, 60: 0, 50: 0, 40: 0, 30: 0, 20: 0, 19: 0,
                           18: 0, 17: 0,
                           16: 0, 15: 0, 14: 0, 13: 0, 12: 0, 11: 0, 10: 0, 9: 0, 8: 0, 7: 0, 6: 0, 5: 0, 4: 0, 3: 0,
                           2: 0,
                           1: 0}
        while eingabe_zahl > 0:
            for zahl in dictionary.keys():
                if eingabe_zahl - zahl >= 0:
                    zusammenrechnen[zahl] = 1 + zusammenrechnen[zahl]
                    eingabe_zahl -= zahl
                    break
        wortbruch_liste = []  # Wortbruch im Sinne von Bruchteil des gesamten Wortes
        for key, value in zusammenrechnen.items():
            if value not in dictionary.keys() and value > 1:
                value_for_dict = IPA.zahl_zu_text(value)  # z.B. 102 000, 102 wird erstmal zu hundertundzwei umgeformt
                dictionary[value] = value_for_dict

            if value > 1 or value == 1 and key >= 100:
                wortbruch = str(dictionary[value]) + str(dictionary[key])
                zusammenrechnen[key] = 0
                wortbruch_liste.append(wortbruch)
            elif value == 1:
                wortbruch = str(dictionary[key])
                wortbruch_liste.append(wortbruch)
                zusammenrechnen[key] = 0

        wortbruch_array = []
        if len(wortbruch_liste) > 1:
            for wortbruch in wortbruch_liste:
                appending = True
                for key, value in dictionary.items():
                    if str(wortbruch) == str(value) and int(key) < 10:
                        if not wortbruch_array[-1].endswith(('hundert', 'tausend', 'million')):
                            wortbruch_array.insert(-1, value + "und")
                            appending = False
                            break
                if appending:
                    wortbruch_array.append(wortbruch)
        else:
            wortbruch_array = wortbruch_liste
        x = "".join(str(e) for e in wortbruch_array)
        return x

    def text_zu_IPA(self, textliste, IPA_dict_appenden=True):
        """Wort für Wort von Klartext zur IPA (phonetisches Alphabet)
        Input = ['Liste', 'mit', 'strings'], Output = ['ˈlɪstə', 'mɪt', 'strɪŋs']"""
        IPA_satz = []
        if textliste and type(textliste) is list:
            # Zahlen zu Text umformen, da Google sonst Zahlen in der Prediction ausgibt
            textliste = IPA.zahl_zu_text_sortieren(textliste)
            for wort in textliste:
                if len(wort) > 25:
                    ipa_wort25 = IPA.wort_split25(self, wort)
                    IPA_satz.append(ipa_wort25)
                    continue
                if wort == "":
                    IPA_satz.append("")
                    continue
                if wort in self.IPA_dict.keys():
                    IPA_satz.append(self.IPA_dict[wort][0])
                else:
                    ipawort, zuordnung = IPA.send_to_gramophone(wort=wort)
                    IPA_satz.append(ipawort)
                    # Erweiterung des Dictionary, damit später das gleiche Wort nicht mehr abgefragt werden muss
                    if IPA_dict_appenden:
                        self.IPA_dict[wort] = ipawort, zuordnung
                        IPA.IPA_dict_speichern(self.IPA_dict)
            return IPA_satz
        else:
            raise Exception("Bitte eine Liste eingeben")

    def wort_split25(self, wort):
        """Falls ein Wort länger als 25 Buchstaben ist (Gramophone-API Begrenzung), wird er hier gesplittet und
        anschließend zusammengeführt. Wichtig ist dabei, dass eine Überschneidung (von hier 5) Buchstaben herrscht,
        damit die Wörter wieder korrekt zusammengeführt werden. Denn bei abstrahiert betrachtet:
        SchulE [SPLIT] und SchulERFAHRUNG wird das E, obwohl es alphabetisch der selbe Buchstabe ist,
        unterschiedlich ausgesprochen. Lösung: SchulERFAHR [SPLIT] und ulERFAHRUNG, Das Schul wird vom ersten übernommen
        und das Erfahrung vom zweiten Wort."""
        wortlaenge = len(wort)
        if wortlaenge < 40:
            erster_teil = wort[:25]
            zweiter_teil = wort[-25:]
            teile_zu_ipa, _ = IPA.text_zu_IPA(self, [erster_teil, zweiter_teil], IPA_dict_appenden=False)
            longest_match = IPA.longest_substring(teile_zu_ipa[0], teile_zu_ipa[1])
            return teile_zu_ipa[0][:longest_match.a] + teile_zu_ipa[1][longest_match.b:]
        else:
            raise Exception("Zurzeit sind Wörter mit einer Länge von über vierzig (40) Buchstaben nicht erlaubt. "
                            "Das liegt an einer externen API.")

    # Quelle: https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
    @staticmethod
    def longest_substring(string1, string2):
        """Matched die Überschneidung für wort_split25"""
        match = SequenceMatcher(None, string1, string2).find_longest_match(0, len(string1), 0, len(string2))
        return match
