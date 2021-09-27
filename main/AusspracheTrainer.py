# Warnings ausstellen
import warnings
warnings.filterwarnings("ignore")

import re
import speech_recognition as sr
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import torch
import torch.nn as nn
import torch.utils.data as data
import torch.nn.functional as F
import torchaudio
import gc
from AusspracheTrainerZusatz import TextTransform, SpeechRecognitionModel, MyRecognizeCallback
from IPAclass import *
from Auswertung import auswertung
import itertools

ipa = IPA()

logging.basicConfig(
    level=logging.WARNING)  # Hohes Logging-Level, damit keine unnötigen Benachrichtigungen gezeigt werden
logging.disable(logging.CRITICAL)

text_transform = TextTransform()
train_audio_transforms = nn.Sequential(
    torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_mels=128, normalized=True),
    torchaudio.transforms.FrequencyMasking(freq_mask_param=30),
    torchaudio.transforms.TimeMasking(time_mask_param=100)
)
valid_audio_transforms = torchaudio.transforms.MelSpectrogram()

target = "Eigens gewählter Satz, der gerne geübt werden möchte. Case- und Sonderzeicheninsensitiv!"
path_to_audio = r"C:\Users\USER\OneDrive\Aussprache Trainer\Audiofile.wav"  # Samplerate der wav-Datei = 48kHz !!!


# VOM ZUSÄTZLICH MITABGEGEBENEN TEXTDOKUMENT ENTNEHMEN UND SUBSTITUIEREN
path_to_model = r'D:\AusspracheTrainer\AusspracheTrainerKI.pt'
ibm_authenticator = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ibm_service_url = "https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx"


class Preparation:
    """Hier werden Basis-Funktionen 'deklariert', die im Hauptteil wichtig sind."""
    def __init__(self):
        gc.collect()
        torch.cuda.empty_cache()

    @staticmethod
    def data_processing(data):
        """Dataloader entpacken"""
        spectrograms = []
        for (waveform, sample_rate, _) in data:
            spec = train_audio_transforms(waveform).squeeze(0).transpose(0, 1)
            spectrograms.append(spec)
        spectrograms = nn.utils.rnn.pad_sequence(spectrograms, batch_first=True).unsqueeze(1).transpose(2, 3)
        return spectrograms

    @staticmethod
    def GreedyDecoder(output, blank_label=68, collapse_repeated=True):
        """Zahlen zu Text, da unsere KI mit Zahlen besser als Buchstaben lernt. Daher gibt sie auch nur Zahlen aus."""
        arg_maxes = torch.argmax(output, dim=2)
        decodes = []
        for i, args in enumerate(arg_maxes):
            decode = []
            for j, index in enumerate(args):
                if index != blank_label:
                    if collapse_repeated and j != 0 and index == args[j - 1]:
                        continue
                    decode.append(index.item())
            decodes.append(text_transform.int_to_text(decode))
        return decodes

    @staticmethod
    def target_transform(target):  # Target ist der Zielsatz
        """Targetsatz wird überprüft, ob die Wortlänge eingehalten wurde, außerdem werden Sonderzeichen entfernt"""
        target = ''.join(e for e in target if e.isalnum() or e == " ")
        target = re.sub(" +", " ", target)
        logging.info("Zielsatz gesetzt: %s" % target)
        a = [x for x in target.split() if len(x) > 30]
        if len(a) > 0:
            raise Exception("Es darf kein Wort über dreißig (30) Buchstaben lang sein")
        return target.split(" ")

    @staticmethod
    def test(model, device, test_loader):
        """Test --> wav-Datei wird von unserer AusspracheTrainerKI ausgewertet"""
        logging.info('\nevaluating...')
        predictions = []
        with torch.no_grad():
            for i, _data in enumerate(test_loader):
                spectrograms = _data
                spectrograms = spectrograms.to(device)

                output = model(spectrograms)  # (batch, time, n_class)
                output = F.log_softmax(output, dim=2)
                output = output.transpose(0, 1)  # (time, batch, n_class)

                # Hier wird die Prediction von Zahlen in Buchstaben überführt
                decoded_preds = Preparation.GreedyDecoder(output.transpose(0, 1))

                prediction = re.sub(" +", " ", decoded_preds[0])  # Bei größerer Batch Size als 1 diese Zeile verändern
                predictions.append(prediction.strip().split(" "))
        return predictions

    @staticmethod
    def main():
        """Lädt die AusspracheTrainerKI"""
        global AusspracheKI_preds, test_daten, path_to_model
        print("[1/2] Model lädt...")
        # Nach Vorlage von https://www.assemblyai.com/blog/end-to-end-speech-recognition-pytorch/
        hparams = {
            "n_cnn_layers": 3,
            "n_rnn_layers": 5,
            "rnn_dim": 512,
            "n_class": 69,
            "n_feats": 128,
            "stride": 2,
            "dropout": 0.1,
            "batch_size": 1
        }

        use_cuda = torch.cuda.is_available()
        if use_cuda:
            logging.info("Cuda verfügbar --> GPU")
        else:
            logging.info("Cuda nicht verfügbar --> CPU")
        torch.manual_seed(7)
        device = torch.device("cuda" if use_cuda else "cpu")

        model = SpeechRecognitionModel(
            hparams['n_cnn_layers'], hparams['n_rnn_layers'], hparams['rnn_dim'],
            hparams['n_class'], hparams['n_feats'], hparams['stride'], hparams['dropout']
        ).to(device)
        if not use_cuda:
            checkpoint = torch.load(path_to_model, map_location="cpu")
        else:
            checkpoint = torch.load(path_to_model)

        model.load_state_dict(checkpoint['state_dict'])
        model.eval()
        print("[1/2] Model hat geladen")
        return model, device, use_cuda


myRecognizeCallback = MyRecognizeCallback()


class Hauptteil(Preparation):
    def __init__(self):
        global target, path_to_audio, path_to_model
        super().__init__()
        try:
            self.IPA_dict = ipa.IPA_dict_laden()
        except FileNotFoundError:  # Läuft zum ersten Mal durch
            self.IPA_dict = {}
            logging.info("IPA-Dictionary nicht gefunden. Wahrscheinlich wurde es noch nie gespeichert.")
        model, device, use_cuda = Preparation.main()
        logging.disable()
        target = Preparation.target_transform(target=str(target).lower())

        waveform, samplerate = torchaudio.load(path_to_audio)
        dictionary = {"clientid": "", "path": path_to_audio}

        r"""An dieser Stelle wird ein Dataloader Objekt der Größe 1 erstellt. Diese Funktion haben wir zukunftsbewusst
        nicht umgeschrieben, da das Programm leichter an größere und schnellere Auswertungen skalierbar ist."""
        # Nach dem Abbild torchaudio.datasets.COMMONVOICE(root: Union[str, pathlib.Path], tsv: str = 'train.tsv')
        test_daten = [(waveform, samplerate, dictionary)]
        kwargs = {'num_workers': 0, 'pin_memory': True} if use_cuda else {}
        test_loader = data.DataLoader(dataset=test_daten,
                                      batch_size=1,
                                      shuffle=False,
                                      collate_fn=Preparation.data_processing,
                                      **kwargs)

        print("[2/2] Audio an Google, IBM and AusspracheTrainerKI senden...")
        AusspracheTrainer_IPAKI = Preparation.test(model, device, test_loader)
        AusspracheTrainer_IPAKI = [[i] for i in AusspracheTrainer_IPAKI[0]]  # Gleich formatieren, wie die anderen KIs
        self.Google_IPAKI = []
        self.Google_KI = []
        self.IBM_KI = []
        self.IBM_IPAKI = []
        self.target_IPA = []
        Hauptteil.google_pred(self, path=path_to_audio)
        Hauptteil.send_to_IBM(self, path=path_to_audio,
                              target=target)  # IBM dauert länger als Google, dafür liefert es vielseitigere Ergebnisse
        Hauptteil.target_to_ipa(self, target)
        print("[2/2] Daten wurden empfangen")
        print()

        # [['zo'], ['ɪst'], [ˈtɛkst], [fɔʁmaˈtiːɐ̯t]]
        print(" ".join(self.target), "| TARGET")
        print(" ".join(self.Google_KI), "| Google KI")
        print(" ".join(self.IBM_KI), "| IBM KI")
        print(path_to_audio, "| AUDIO FILE")
        print()
        print(" ".join(self.target_IPA), "| TARGET IPA")
        print(" ".join(self.Google_IPAKI), "| GOOGLE IPA-KI")
        print(" ".join(self.IBM_IPAKI), "| IBM IPA-KI")
        print(" ".join(itertools.chain.from_iterable(AusspracheTrainer_IPAKI)), "| AUSSPRACHETRAINER IPA-KI")
        print()

        auswertung(" ".join(self.target_IPA), [" ".join(self.Google_IPAKI), " ".join(self.IBM_IPAKI),
                                               " ".join(itertools.chain.from_iterable(AusspracheTrainer_IPAKI))])

        # ------------ ENDE ------------ #
        ipa.IPA_dict_speichern(self.IPA_dict)

    def target_to_ipa(self, target):
        """Klartext zu IPA"""
        self.target = target
        for wort in self.target:
            if wort in self.IPA_dict.keys():
                self.target_IPA.append(self.IPA_dict[wort])
            else:
                self.target_IPA.append(ipa.send_to_dwds(wort=wort))
                self.IPA_dict[wort] = self.target_IPA[
                    -1]  # Erweiterung des Dictionary, damit später das gleiche Wort nicht mehr abgefragt werden muss

    def google_pred(self, path):
        r = sr.Recognizer()
        audiofile = sr.AudioFile(path)
        with audiofile as source:
            audio = r.record(source)
            try:
                google_pred = r.recognize_google(audio, language="de-DE")
                # Über die allgemeine API (nicht direkte Anbindung an Google, sondern über speech-recognition) hat man
                # zwar weniger Auswahl und keine explizite Verschlüsselung, dafür umgeht man die
                # kostenlosen 60 Freiminuten pro Monat
            except:
                google_pred = [""]
            if google_pred:
                google_pred = ipa.zahl_zu_text_sortieren(
                    google_pred)  # Zahlen zu Text umformen, da Google sonst Zahlen in der Prediction ausgibt
                # 95 zu fünfundneunzig
                self.Google_KI = google_pred.split()
                for wort in str(google_pred).strip().split():
                    wort = wort.lower()
                    if wort in self.IPA_dict.keys():
                        self.Google_IPAKI.append(self.IPA_dict[wort])
                    else:
                        self.Google_IPAKI.append(ipa.send_to_dwds(wort=wort))
                        self.IPA_dict[wort] = self.Google_IPAKI[-1]
                        # Erweiterung des Dictionary, damit später das gleiche Wort nicht mehr abgefragt werden muss

    def IBM_pred(self):
        """Formatiert erhaltene Daten von IBM (durch send_to_IBM)"""
        data = myRecognizeCallback.data
        transcript = data["results"][0]["alternatives"][0]["transcript"]

        # Andere, hier aufgeführte Daten sind relevant für die Zukunft
        confidence = data["results"][0]["alternatives"][0]["confidence"]
        keywords = data["results"][0]["keywords_result"]
        alternatives = data["results"][0]["alternatives"]
        for wort in str(transcript).strip().split():
            wort = wort.lower()
            self.IBM_KI.append(wort)
            if wort in self.IPA_dict.keys():
                self.IBM_IPAKI.append(self.IPA_dict[wort])
            else:
                self.IBM_IPAKI.append(ipa.send_to_dwds(wort=wort))
                self.IPA_dict[wort] = self.IBM_IPAKI[-1]

    def send_to_IBM(self, path, target):
        global ibm_authenticator, ibm_service_url
        authenticator = IAMAuthenticator(ibm_authenticator)
        speech_to_text = SpeechToTextV1(authenticator=authenticator)
        speech_to_text.set_service_url(ibm_service_url)

        with open(path, 'rb') as audio_file:
            audio_source = AudioSource(audio_file)
            speech_to_text.recognize_using_websocket(
                audio=audio_source,
                content_type='audio/wav',
                recognize_callback=myRecognizeCallback,
                model='de-DE_BroadbandModel',
                keywords=target,
                keywords_threshold=0.2,
                max_alternatives=5
            )
        Hauptteil.IBM_pred(self)


Hauptteil()
