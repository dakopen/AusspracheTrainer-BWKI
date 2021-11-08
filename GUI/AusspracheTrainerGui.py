import random
import time
from PIL import Image, ImageDraw
import PySimpleGUI as sg
from base64 import b64encode
import pyaudio
import wave
import io
import threading
from AusspracheTrainerSchnittstelle import aussprache_trainer
import torch
from AusspracheTrainerZusatz import SpeechRecognitionModel
from IPAclass import *
import os
aufnehmen_bool = False
finished = False
path_zur_letzten_aufnahme = ""
path_to_model = r"C:\Users\dakop\OneDrive\AusspracheTrainerKI.pt"


def load_model():
    """Lädt die AusspracheTrainerKI"""
    # global AusspracheKI_preds, test_daten, path_to_model
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


# https://github.com/PySimpleGUI/PySimpleGUI/issues/3412
def round_btn(button_text, fill, text_color, tooltip=None, key=None,
              pad=None, bind_return_key=False, button_width=None, visible=True):
    multi = 5
    btn_w = ((len(button_text) if button_width is None else button_width) * 5 + 20) * multi
    height = 20 * multi
    btn_img = Image.new('RGB', (btn_w, height), (sg.theme_background_color()))
    d = ImageDraw.Draw(btn_img)
    x0 = y0 = 0
    radius = 10 * multi
    d.ellipse((x0, y0, x0 + radius * 2, height), fill=fill)
    d.ellipse((btn_w - radius * 2 - 1, y0, btn_w - 1, height), fill=fill)
    d.rectangle((x0 + radius, y0, btn_w - radius, height), fill=fill)
    data = io.BytesIO()
    btn_img.thumbnail((btn_w // 3, height // 3), resample=Image.LANCZOS)
    btn_img.save(data, format='png', quality=95)
    btn_img = b64encode(data.getvalue())
    return sg.Button(button_text=button_text, image_data=btn_img, button_color=(text_color, text_color),
                     tooltip=tooltip, key=key, pad=pad, enable_events=False, size=(button_width, 1),
                     bind_return_key=bind_return_key, border_width=0, visible=visible)

#http://sebastiandahlgren.se/2014/06/27/running-a-method-as-a-background-thread-in-python/
class AusspracheTrainer_Thread(object):

    def __init__(self, target, path_to_audio, model, device, use_cuda):

        thread = threading.Thread(target=self.run, args=(target, path_to_audio, model, device, use_cuda))  # alternativ hier direkt ausspracheTrainer reinmachen
        thread.daemon = True                            # Daemonize thread
        thread.start()

    def run(self, target, path_to_audio, model, device, use_cuda):
        try:
            aussprache_trainer(target, path_to_audio, model, device, use_cuda)
        except:
            os.environ["overallscore"] = "-1"
            window["fehlermeldung"].update("Google oder IBM haben deinen Satz nicht verstanden")


class Update_Status_Thread(object):
    def __init__(self, window, target, highscores):

        thread = threading.Thread(target=self.run, args=(window, target, highscores))  # alternativ hier direkt ausspracheTrainer reinmachen
        thread.daemon = True                            # Daemonize thread
        thread.start()

    def run(self, window, target, highscores):
        while float(os.environ["overallscore"]) == 0.0:
            pass

        highscore = float(os.environ["overallscore"])
        if float(os.environ["overallscore"]) > 0.0:

            if target in highscores.keys():
                if highscore >= highscores[target]:
                    highscores[target] = highscore
            else:
                highscores[target] = highscore
            with open(r"highscore.pickle", "wb") as highscores_speicherort:
                pickle.dump(highscores, highscores_speicherort)
            window["_highscore_"].update(highscore)
        window["aufnehmen"].update("Weiter üben")
        window["repeat"].update(visible=True)



class Audio_aufnehmen(object):

    def __init__(self):

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        global aufnehmen_bool, target, path_zur_letzten_aufnahme, finished
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, frames_per_buffer=768)
        t_end = time.time() + 20
        frames = []

        # https://stackoverflow.com/questions/24374620/python-loop-to-run-for-certain-amount-of-seconds
        while time.time() < t_end and aufnehmen_bool:
            data = stream.read(768)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        audio.terminate()
        path_zur_letzten_aufnahme = Audio_aufnehmen.naming(self)
        sound_file = wave.open(path_zur_letzten_aufnahme, "wb")
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(48000)
        sound_file.writeframes(b''.join(frames))
        sound_file.close()
        finished = True

    def naming(self):
        index_number = 1
        while True:
            if os.path.isfile("Audios/Aufnahme_%d (%s).wav" % (index_number, "".join([e for e in target if
                                                                               e not in [".", "*", "/", "\\", "[", "]",
                                                                                         "(", ")", "{", "}", "?", "!", "="]]))):
                index_number += 1

            else:
                return "Audios/Aufnahme_%d (%s).wav" % (index_number, "".join([e for e in target if
                                                                               e not in [".", "*", "/", "\\", "[", "]",
                                                                                         "(", ")", "{", "}", "?", "!", "="]]))


def toggle_buttons(window, boolean):
    window["_random_satz_"].update(disabled=boolean)
    window["target"].update(disabled=boolean)
    window["_DROPDOWN_"].update(disabled=boolean)

try:
    with open(r"highscores.pickle", "rb") as highscores_speicherort:
        highscores = pickle.load(highscores_speicherort)
except:
    highscores = {}

sg.theme('SandyBeach')

layout = [
    [sg.Text('AusspracheTrainer')],
    [sg.Text('Satz ausdenken', size=(12, 1)), sg.InputText(key="target", size=(75, 1)), ],
    [sg.Text('ODER', size=(12, 1)), sg.Combo(["/s/ - Satz", "/sch/ - Satz", "/ch1/ - Satz", "zufälligen Satz", "Wettbewerbssatz"], default_value="/s/ - Satz", size=(30, 1), key='_DROPDOWN_'), sg.Button("generieren", key="_random_satz_"), sg.Text(" " * 6), sg.Text('Höchster Score:'), sg.Text('-/-', key="_highscore_")],

    [round_btn("AUFNEHMEN", sg.theme_button_color()[1], sg.theme_button_color()[0], button_width=30, key="aufnehmen"), round_btn("Wiederholen", sg.theme_button_color()[1], sg.theme_button_color()[0], button_width=20, key="repeat", visible=False)], #sg.FileBrowse(file_types=(("Audio Files", "*.wav"), ("All Files", "*.*")), size=(15, 1), key="browse")
    [sg.Text('', key="anweisungen"), sg.Text('', key="fehlermeldung", text_color="red")]
]

window = sg.Window('AusspracheTrainer', layout)
model, device, use_cuda = load_model()
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, '_EXIT_'):
        break
    elif "_CONFIRM_" in event:
        break
    elif "_random_satz_" in event:
        if values["_DROPDOWN_"] == "zufälligen Satz":
            with open("satze.txt", "r", encoding="utf-8-sig") as random_saetze:
                lines = random_saetze.readlines()
                if values["target"] in lines:
                    lines.remove(values["target"])
                window["target"].update(random.choice(lines).strip())

        elif values["_DROPDOWN_"] == "/s/ - Satz":
            s_saetze = ["Susi sagte, dass sie gerne Salat mit Mais isst.", "Morgens isst Susanne gerne Müsli mit Nüssen.", "Auf der Insel scheint die Sonne übermäßig viel.", "Hans isst gerne Bratwurst mit Senf."]
            if values["target"] in s_saetze:
                s_saetze.remove(values["target"])
            window["target"].update(random.choice(s_saetze))

        elif values["_DROPDOWN_"] == "/sch/ - Satz":
            sch_saetze = ["Am Strand bauen die Kinder mit dem Spielzeug und der Schaufel eine Sandburg.", "Die Schnecken hinterlassen eine Schleimspur auf der Straße.", "Auf der Schnellstraße herrscht schneller Straßenverkehr.", "Spreewaldgurken schmecken gut, sind aber im Spreewald am schmackhaftesten."]
            if values["target"] in sch_saetze:
                sch_saetze.remove(values["target"])
            window["target"].update(random.choice(sch_saetze))
        elif values["_DROPDOWN_"] == "/ch1/ - Satz":
            ch1_saetze = ["Die Eichhörnchen sammeln Eicheln für ihren Wintervorrat.", "Ich möchte noch in die Kirche gehen.", "Es ist echt gefährlich sich im Auto nicht anzuschnallen.", "Ein Eichhörnchen ist leichter als ein Elch."]
            if values["target"] in ch1_saetze:
                ch1_saetze.remove(values["target"])
            window["target"].update(random.choice(ch1_saetze))

        elif values["_DROPDOWN_"] == "Wettbewerbssatz":
            window["target"].update("Die Regisseurin meint, die gelbstichige Requisite sei Quatsch mit Soße.")


        if values["target"] in highscores.keys():
            window["_highscore_"].update(highscores[values["target"]])
        else:
            window["_highscore_"].update("-/-")

    elif "aufnehmen" in event:
        if window["aufnehmen"].get_text() == "Nehme auf... ":
            aufnehmen_bool = False
            time.sleep(1)
            print(str(values["target"]), path_zur_letzten_aufnahme)
            aussprache_trainer_thread = AusspracheTrainer_Thread(str(values["target"]), path_zur_letzten_aufnahme, model, device, use_cuda)
            window["aufnehmen"].update("Aufnahme gespeichert ✓")
            window["anweisungen"].update("")
            window.refresh()
            update_status_thread = Update_Status_Thread(window, str(values["target"]), highscores)

        elif window["aufnehmen"].get_text() == "AUFNEHMEN":
            target = values["target"]
            target = str(target)
            if target.strip() != "":
                window["fehlermeldung"].update("")
                toggle_buttons(window, True)
                aufnehmen_bool = True
                aufnehmen = Audio_aufnehmen()
                window["aufnehmen"].update("Nehme auf... ")
                window["repeat"].update(visible=False)
            else:
                window["fehlermeldung"].update("Bitte gib zuerst einen Satz ein!")

        elif window["aufnehmen"].get_text() == "Aufnahme gespeichert ✓":
            pass

        elif window["aufnehmen"].get_text() == "Weiter üben":
            toggle_buttons(window, False)
            window["target"].update("")
            window["_highscore_"].update("-/-")
            window["aufnehmen"].update("AUFNEHMEN")
            window["fehlermeldung"].update("")
            window["repeat"].update(visible=False)


    elif "repeat" in event:
        window["repeat"].update(visible=False)
        aufnehmen_bool = True
        window["fehlermeldung"].update("")
        aufnehmen = Audio_aufnehmen()
        window["aufnehmen"].update("Nehme auf... ")



window.close()
with open(r"highscore.pickle", "wb") as highscores_speicherort:
    pickle.dump(highscores, highscores_speicherort)
