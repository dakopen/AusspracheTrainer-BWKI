# AusspracheTrainer
Der AusspracheTrainer analysiert mithilfe von künstlicher Intelligenz die Aussprache eines vor- oder eingegebenen Satzes. Er wurde in Zusammenarbeit mit der [logopädischen Praxis von Tina Hillebrecht](https://logopaedie-hillebrecht.de/ "logopaedie-hillebrecht.de") entwickelt. Als Input nimmt der AussprachteTrainer eine `.wav` Datei mit einer Samplerate von 48 kHz und er gibt in Textform mit farblichen Markierungen das Ergebnis aus.

*Datenschutz: Ihre Audio-Datei wird an Google (über das speech-recognition-package) und IBM (über eine API) übermittelt. Mit der Benutzung der Software erklären Sie sich mit deren DSGVO einverstanden.*
![Output](https://github.com/dakopen/AusspracheTrainer-BWKI/blob/main/main/Example%20Output.png)
## Aufbau des Repositorys
`Schema und Funktionsweise.PDF` &#8594; Bietet einen groben Überblick über die Funktionsweise des AusspracheTrainers, damit die Funktionen der einzelnen Komponenten besser verstanden werden.

`/Training/...` &#8594; Der Code, mit dem wir die KI trainiert haben, bzw. die Audio-Dateien normalisiert und getrimmt haben. Leider finden wir den Code nicht mehr, womit wir den kompletten Commonvoice Datensatz in Lautschrift "übersetzt" haben, allerdings ähnelt die Funktion sehr `/main/IPAclass.py`

`/main/...` &#8594; Das ist der Hauptteil vom Projekt. In diesem Ordner befinden sich alle für den AusspracheTrainer wichtigen Funktionen. Sicher können Sie nicht alle Funktionen begutachten, also haben wir eine kleine Liste zusammengestellt von Funktionen, die wichtig und schön geschrieben/formatiert sind:
* `sequence_matching()` in `/main/Funktionen.py`: Rekursive Funktion, die immer den längsten überschneidenden Abschnitt zweier Strings nimmt und in ein Dictionary sortiert. (Wobei die eigentliche Sortierung von `sort_sequence_dict` in der gleichen Datei übernommen wird)


* `text_zu_IPA()` in `/main/IPAclass.py`: Sie übersetzt einen Satz aus Klartext (deutsches Alphabet) in phonetisches. Auf den ersten Blick ist diese Funktion nicht ganz so schön wie die vorherige, aber sie hat eine wichtiges Feature: Auch wenn die maximale Buchstabenanzahl der Text-zu-Lautschrift API 25 Buchstaben beträgt, kann sie Predictions (die unerwartet länger als 25 Buchstaben sind) trotzdem in Lautschrift übersetzen, indem Sie das Wort splittet und anschließend über die eine ähnliche Funktion wie `sequence_matching()`  zusammenführt. 
 
    *Dies funktioniert allerdings ausschließlich bei Predictions, da wir aus Zeitknappheit bislang die Zuordnung der Lautschrift (IPA) zu Klartext Buchstaben nicht in der Zusammenführungsfunktion integriert haben. Da in der Auswertung die Lautschrift zu Klartext zurückgeformt werden muss, ist die Zuordnung elementar.*


* Die Idee des IPA_dict's (siehe `/main/IPAclass.py`), sodass Wörter nicht erneut abgefragt werden müssen, wenn sie einmal von der API abgefragt wurden. Dieses Vorgehen ersparte besonders beim Umformen der Sätze des Commonvoice Datensatzes unmengen an Zeit. Das IPA_dict wird lokal als Pickle-Datei abgespeichert.

`/Past/...` &#8594; Ähnlich zum Training sind hier frühere Funktionen, die der Vergangenheit angehören. Sie wurden durch effizientere Ersetzt. Die meisten Funktionen gehen hierbei auf das Problem ein, den Targetsatz mit der Prediction sinnvoll zu matchen, damit die richtigen Abschnitte verglichen werden, auch wenn ein Wort zu viel predicted wurde oder in mehrere Wörter aufgeteilt wurde (z.B. e gitarre statt egitarre).

`/Future/...` &#8594; Dieser Part ist womöglich der interessanteste, da Zukunft des AusspracheTrainers erläutert wird bzw. welche Features geplant sind. Das letzte Feature hat es durch die verlängerte Abgabefrist in den fertigen AusspracheTrainer geschafft - die Auswertung kann nun im deutschen Alphabet statt ausschließlich in Lautschrift erfolgen. Das hilft vor allem Laien, die sich nicht mit Lautschrift auskennen.

`/Testaudios 48 kHz/...` &#8594; Falls die eigene Aufnahme von Audios zu aufwendig ist, haben wir exemplarisch drei Audios hochgeladen. Diese sollen einmal eine ziemlich gute Aussprache (`Es war einmal ein Müller, der war arm, aber er hatte eine schöne Tochter.wav`), eine Aussprache mit Sprachfehler (lispeln) (`Die Schnecken hinterlassen eine Schleimspur auf der Straße.wav`) darstellen sowie die Zahl-zu-Wort Funktion demonstrieren (`Ich habe 15 Kinder und sieben Schwestern.wav`). Dennoch empfehlen wir dringlich den AusspracheTrainer selbst auszuprobieren mit eigenen Audios!


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

Downloaden Sie das gesamte Projekt oder nur den `/main` Ordner. Bitte stellen Sie sicher, dass alle Funktionen des main-Ordners sich im selbem Ordner in Ihrer Entwicklungsumgebung befinden.

Mit `pip install -r requirements.txt` installieren Sie bitte alle benötigten Packages. Zusätzlich wird [Pytorch](https://pytorch.org/get-started/locally/) benötigt. Bitte wählen Sie die `(Stable) 1.9.1` Version mit `CUDA 11.1` (sofern Nvidia Grafikkarte vorhanden, sonst `CPU`) für Ihr Betriebssystem aus und kopieren Sie die Command Line, welchen Sie anschließend in Ihrer Entwicklungsumgebung ausführen müssen.

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


### 5. Audios aufnehmen mit einer Samplerate von 48 kHz sowie Bitrate von 768 kBit/s
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
* ein direkter Path (entweder double backslash `"C://Path//Zum//Ordner//AusspracheTrainerKI.pt"` oder mit r `r"C:/Path/Zum/Ordner/AusspracheTrainerKI.pt"`) zur heruntergeladenen KI besteht und 
* eine Audio-Datei mit einer Sample-Rate von 48 kHz im `.wav` Format vorliegt und zusammen mit dem target (=vorgelesenen Satz) in dem Skript eingesetzt wurde,
 
sind Sie bereit.

Ein Wort im Targetsatz darf maximal 25 Buchstaben lang sein, da die externe API nicht mehr Buchstaben erlaubt. In zukünftigen Releases haben wir dies umgangen (wie bereits in der `text_zu_IPA()` Funktion für Predicitons).

Einfach die `AusspracheTrainer.py` Funktion starten. Das Laden des Modells kann je nach Systemvoraussetzungen einige Sekunden (bei CPU länger) in Anspruch nehmen. Etwas länger dauert das Senden und Empfangen der Audio-Datei an Google und IBM. Dies dauert ca. 20 Sekunden.

Das Ergebnis kann je nach Erfahrungsgrad erweitert werden. In der `Auswertung.py`-Datei finden Sie an einigen Stellen kommentierte Bereiche. Zum Beispiel können Sie entscheiden, ob Sie die Endauswertung gerne in Lautschrift oder deutschem Alphabet (Standard) hätten. Außerdem ist der Sigmatismus_score verfügbar, der zeigt, wie oft sie Zischlaute richtig ausgesprochen haben (je kleiner, desto schlechter).

## Output

### Logging-Informationen
Die ersten beiden Zeilen zeigen an, dass der AusspracheTrainer lädt bzw. fertig geladen hat. Während dieser Prozess nur einige Sekunden in Anspruch nehmen sollte, dauert das Senden der Audio-Datei an IMB und Google wesentlich länger. Damit Sie währenddessen wissen, dass sich etwas tut, haben wir das als Logging Information in den Output integriert.

### Klartext-Ergebnisse
Sobald die Ergebnisse von Google und IBM vorliegen, wird der Zielsatz und die beiden Ergebnisse angezeigt. Zusätzlich noch einmal der Pfad zur Audio-Datei, damit Sie noch einmal überprüfen können, ob die richtige Audio-Datei ausgewählt wurde.

### Lautschrift
Die Ergebnisse werden zum Vergleichen (weil unsere KI ausschließlich Lautschrift ausgibt) mit einer API an Gramophone in Lautschrift übersetzt. Die "neuen" Ergebnisse sowie die Prediction unserer AusspracheTrainer IPA-KI sehen Sie nun.

### Targets & Predictions
Nun wird der Targetsatz drei Mal mit der jeweiligen Prediction verglichen. Dies geschieht in folgender Reihenfolge: Google - IBM - AusspracheTrainer IPA-KI. Die Targets werden in dieser Reihenfolge angezeigt, wobei die Farbe Gelb anzeigt, wenn etwas anders verstanden wurde. Das gleiche gilt für die Predictions unten drunter, wobei hier auch die Farbe Rot herangezogen wird für fehlende Abschnitte, oder wenn etwas zu viel ist.

### Auswertung
Zuletzt wird die Auswertung angezeigt. Sie geschieht wieder im deutschen Alphabet. Die Bedeutung der Farben ist die folgende:
* Grün: Perfekte Aussprache, ein grüner Buchstabe/Satzabschnitt hat einen Score von über 0.75, also wurde er von allen KIs richtig erkannt
* Lila: Der Buchstabe/Satzabschnitt wurde von min. einer KI falsch erkannt. Score: 0.5-0.75
* Gelb: Der Buchstabe/Satzabschnitt wurde von mehreren KIs falsch erkannt. Spätestens hier ist der Buchstabe/Satzabschnitt ohne Kontext oft missverständlich. Score: 0.25-0.5
* Rot: Der Buchstabe/Satzabschnitt wurde so gut wie gar nicht erkannt. D.h. die KIs haben die Wörter, in dem er vorkommt anders verstanden. Für Menschen ist er wahrscheinlich - ohne Kontext - genause unverständlich. Score < 0.25

Zu guter Letzt wird - falls ein Sprachfehler (bisher nur Lispeln) vorliegt - dieser angezeigt und der Score mit einer sprachlichen Bewertung ausgegeben.


## Abschließende Überlegungen:
Beim Trainieren unserer KI kamen Frauen- (9%) und Männeranteile (69%) nicht gleichverteilt zur Sprache. Außerdem können Altersunterschiede Einfluss auf eine von der KI falsch verstandene Aussprache haben.

Gleiches gilt, aber im viel kleineren Sinne für die KIs von Google und IBM. Maschinelles Lernen funktioniert anders als menschliche Gehirne - eine unnatürliche und besonders lebhafte und trotzdem richtige Betonung wird von Maschinen oft als Fehler anerkannt. 

**Diese Software ersetzt keinesfalls eine logopädische Fachkraft. Falls ein Verdacht auf Sprachfehler besteht, wenden Sie sich bitte an eine logopädische Praxis in Ihrer Umgebung.**

## Vergleichbare Produkte
### ISi-Speech
[ISi-Speech](https://www.isi-speech.de/) – Individualisierte Spracherkennung in der Rehabilitation für Menschen mit Beeinträchtigung in der Sprechverständlichkeit.

Das logopädische Tool zielt jedoch auf eine andere Zielgruppe ab: "Personen mit stark reduzierter Sprechverständlichkeit infolge einer neurologischen Erkrankung" <sup>[1](https://www.isi-speech.de/entstehung/#:~:text=Als%20Zielgruppe%20werden,m%C3%B6glich%20und%20gew%C3%BCnscht.)</sup> 

Die Zielgruppe des AusspracheTrainers ist hingegen viel breiter gefasst - Muttersprachler (mit und ohne Sprachfehler) sowie nicht-Muttersprachler, jene die komplizierte deutsche Aussprache erlernen möchten.


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
