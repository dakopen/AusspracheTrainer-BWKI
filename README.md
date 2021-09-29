# AusspracheTrainer
Der AusspracheTrainer analysiert mithilfe von künstlicher Intelligenz die Aussprache eines vor- oder eingegebenen Satzes. Er wurde in Zusammenarbeit mit der [logopädischen Praxis von Tina Hillebrecht](https://logopaedie-hillebrecht.de/ "logopaedie-hillebrecht.de") entwickelt. Als Input nimmt der AussprachteTrainer eine `.wav` Datei mit einer Samplerate von 48 kHz und er gibt in Textform mit farblichen Markierungen das Ergebnis aus.

*Datenschutz: Ihre Audio-Datei wird an Google (über das speech-recognition-package) und IBM (über eine API) übermittelt. Mit der Benutzung der Software erklären Sie sich mit deren DSGVO einverstanden.*
![Output](https://github.com/dakopen/AusspracheTrainer/blob/main/main/Example%20Output.png)

## Setup
Das Setup erweist sich leider als etwas kompliziert, aber mit den folgenden Schritten haben Sie den AusspracheTrainer in schnell installiert.

#### Systemvorraussetzungen (geht bestimmt auch mit weniger Computer Capability):
> RAM : A minimum of 16 gb RAM is required. You can also get on with a 8gb ram, but it has it’s [sic!] own complications.

CUDA nur für Nvidia Grafikkarten; Alternativ läuft das Modell sehr gut über CPU
> GPU : CUDA is compatible with almost all the models from 2006 but a minimum of gtx 1050ti, 1060 and above are required.

>SSD or HDD : A SSD with atleast 256gb is required for faster processing.The 128gb SSD falls short of space after the installation of the softwares [sic!].

> Quelle: [medium.datadriveninvestor.com](https://medium.datadriveninvestor.com/installing-pytorch-and-tensorflow-with-cuda-enabled-gpu-f747e6924779)
### 1. Python Installationen
Für unser Projekt benutzen wir `Python 3.8`, der AusspracheTrainer sollte jedoch auf anderen `Python 3` Versionen gleich funktionieren. 

Downloaden Sie das gesamte Projekt oder nur den `/main` Ordner. Bitte stellen Sie sicher, dass alle Funktionen des main-Ordners sich im selbem Ordner befinden.

Mit `pip install -r requirements.txt` installieren Sie bitte alle benötigten Packages. Zusätzlich wird [Pytorch](https://pytorch.org/get-started/locally/) benötigt. Bitte wählen Sie die `(Stable) 1.9.1` Version mit `CUDA 11.1` für Ihr Betriebssystem aus und kopieren Sie die Command Line, welchen Sie anschließend in Ihrer Entwicklungsumgebung ausführen müssen.

### 2. KI herunterladen
Unsere KI umfasst etwas mehr als 500 MB und steht daher nur auf OneDrive zum Herunterladen bereit. Laden Sie mit diesem [Link](https://1drv.ms/u/s!AhrRle8s079TiaRbOrVJ6Gd4HPomqg?e=x1hfEi "AusspracheTrainerKI") das Pytorch Model herunter und setzen Sie den absoluten Path in `AusspracheTrainer.py` (ist die main Funktion, also diejenige, die Sie später auch ausführen sollen) in folgende Zeile als String ein:
```python
path_to_model = r'D:\AusspracheTrainer\AusspracheTrainerKI.pt'  # Herunterladen von https://1drv.ms/u/s!AhrRle8s079TiaRbOrVJ6Gd4HPomqg?e=x1hfEi
```

### 3. API Keys von der Projektabgabe nehmen und einsetzen
In der abgegebenen Textdatei steht der ibm_authenticator-Key und ibm_service_url-Key, die man in die entsprechenden Felder einsetzen muss in `AusspracheTrainer.py`
```python
ibm_authenticator = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ibm_service_url = "https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx"
```
### 4. Einen Satz, den man lernen möchte, sich ausdenken
Entweder entscheidet man sich für einen vorgegebenen Satz, der wahlweise zufällig ausgewählt wird oder einen logopädischen Hintergrund hat, oder man denkt sich selbst einen Satz aus.

Beispielsätze zum Thema pot. Lispeln erkennen finden Sie unter 
`/Future/Logopädin Sigmatimus.docx`. Einfachheitshalber, haben wir pro Kategorie einen Beispielsatz rauskopiert:
* >/s/: Susi sagte, dass sie gerne Salat mit Mais isst.
* >/sch/: Die Schnecken hinterlassen eine Schleimspur auf der Straße.
* >/ch1/: Die Eichhörnchen sammeln Eicheln für ihren Wintervorrat.
* >/.../: Weitere Sprachfehler kommen bald! Siehe `/Future/Readme.md`


### 5. Audios aufnehmen mit einer Samplerate von 48 kHz
Zielformat ist `.wav` mit einer Sample-Rate von 48 kHz. Beide Faktoren sind unermesslich für den AusspracheTrainer.
Für Android schlagen wir Stimmrekorder Plus vor, da man dort eine Sample-Rate von 48 kHz (*nicht voreingestellt!*) und das Zielformat .wav einstellen kann. Vergessen Sie bitte nicht, das Export-Format auf unkomprimiert zu stellen (!), damit auch wirklich eine .wav Datei exportiert wird. 

Herunterladen von:
* [Google Play Store](https://play.google.com/store/apps/details?id=com.coffeebeanventures.easyvoicerecorder&hl=de&gl=US)
* [Apple App Store](https://apps.apple.com/de/app/easy-voice-recorder/id1222784166)
* [Huawei AppGallery](https://appgallery.huawei.com/app/C100099283?sharePrepath=ag&locale=de_DE&source=appshare&subsource=C100099283&shareTo=com.example.android.notepad&shareFrom=appmarket)

### 6. Satz und Audiofile einsetzen
Auch das direkt in `AusspracheTrainer.py` einfach ersetzen:
```python
target = "Eigens gewählter Satz, der gerne geübt werden möchte. Case- und Sonderzeichenunsensibel!"
path_to_audio = r"C:\Users\USER\OneDrive\Aussprache Trainer\Audiofile.wav"  # Sample-Rate der wav-Datei = 48kHz !!!
```

## Benutzung
Die `AusspracheTrainer.py` ist das Herzstück des Trainers. Sie importiert alle Funktionen der anderen Dateien, sodass sie selbst aufgeräumter ist. 

Wenn... 
* Alle Packages inkl. Pytorch über die Command Line installiert,
* beide IBM-Api-Keys eingesetzt, 
* ein direkter Path (entweder double backslash `"C://Path//Zum//Ordner//AusspracheTrainerKI.pt"` oder mit r `r"C:/Path/Zum/Ordner/AusspracheTrainerKI.pt`) zur heruntergeladenen KI besteht und 
* eine Audio-Datei mit einer Sample-Rate von 48 kHz im `.wav` Format vorliegt und zusammen mit dem target (=vorgelesenen Satz) in dem Skript eingesetzt wurde,
 
sind Sie bereit.

Einfach die `AusspracheTrainer.py` Funktion starten. Das Laden des Modells kann je nach Systemvoraussetzungen einige Sekunden (bei CPU länger) in Anspruch nehmen. Etwas länger dauert das Senden und Empfangen der Audio-Datei an Google und IBM. Dies dauert ca. 20 Sekunden.

Das Ergebnis kann je nach Erfahrungsgrad erweitert werden. In der `Auswertung.py`-Datei finden Sie an einigen Stellen kommentierte Bereiche. Zum Beispiel können Sie entscheiden, ob Sie die Endauswertung gerne in Lautschrift oder deutschem Alphabet (Standard) hätten. Außerdem ist der Sigmatismus_score verfügbar, der zeigt, wie oft sie Zischlaute richtig ausgesprochen haben (je kleiner, desto schlechter).

## Kontakt
Daniel Busch - dakopen185@gmail.com

Projektlink: https://github.com/dakopen/AusspracheTrainer/

## Quellenangabe wichtiger Komponenten
### Gramophone
Zum Konvertieren von Klartext in Lautschrift.
>Kay-Michael Würzner & Bryan Jurish. "A hybrid approach to grapheme-phoneme conversion." In Proceedings of the 12th International Conference on Finite State Methods and Natural Language Processing (Düsseldorf, Germany, 22nd - 24th June, 2015), 2015.

> https://kaskade.dwds.de/~kmw/gramophone.py

### AssemblyAi
Für das Grundgerüst der AusspracheTrainer IPA-KI (die auch die Audio-Datei analyisiert, und in unserem Falle direkt Lautschrift ausgibt)
> https://www.assemblyai.com/blog/end-to-end-speech-recognition-pytorch/

### Mozilla Commonvoice Datensatz
Über 700 überprüfte Stunden an `.mp3`-Dateien mit zugehörigem Satz.
> https://commonvoice.mozilla.org/de/datasets (Version 6.1 | de_836h_2020-12-11)
