# Training der AusspracheTrainer KI
Hier wird kurz erklärt, wie wir den AusspracheTrainer trainiert haben, welche Quellen und machine learning libraries wir verwendet haben.

## Grundgerüst
Um ein qualitatives Produkt zu entwickeln, haben wir uns am Stand der Technik orientiert. Daher haben wir anstatt eine komplett eigene KI zu schreiben einen bestehenden Code verändert bzw. an unsere Problemstellung angepasst:
[Assembly Ai Speech Recognition Model](https://www.assemblyai.com/blog/end-to-end-speech-recognition-pytorch/ "Building an end-to-end Speech Recognition model in PyTorch")

In der Datei `AusspracheTrainerTraining.py` haben wir unsere Veränderungen durch `# [EDIT START]` bzw. `# [EDIT END]` deutlich gemacht. Ferner lag unsere Arbeit weniger bei der Veränderung des bestehenden Skripts, sondern bei der Vorbereitung der Trainingsdaten.

## Trainingsdaten
Für den AusspracheTrainer verwenden wir den [Mozilla Common Voice Datensatz](https://commonvoice.mozilla.org/de/datasets). Die 777 von der Community überprüften Stunden (in der Version 6.1; de_836h_2020-12-11) filtern wir so, dass ausschließlich Aufnahmen von Muttersprachler*innen übrig bleiben.

### Text
Anschließend muss der zugehörige Satz einer Audio in Lautschrift (IPA) umgeformt werden. Dafür nutzen wir die [DWDS Schnittstelle](https://www.dwds.de/d/api#ipa). Ihre einzige Begrenzung ist zwar, dass Wörter maximal 20 Buchstaben lang sein dürfen, allerdings umgehen wir dies durch intelligentes Splitten und Zusammenfügen eines Wortes. Mehr dazu finden Sie in den Funktionen selbst beschrieben (`IPAclass.py`).

### Audio
Die Audios sind im `.mp3` Format mit einer Sample-Rate von 48 kHz verfügbar. Dieses Format lässt sich leider nicht mit bestehenden Libraries kombinieren, daher haben wir die Audios normalisiert und ins `.wav` Format übertragen. Funktionen dafür finden Sie hier `sound-anpassen.py`. Auch wenn alle Audios auf eine bestimmte Lautstärke normalisiert wurden muss dies nicht mit Trainingsaudios passieren. Also ist eine Installation von ffmpeg nicht zwangsläufig notwendig.

## Hardware und über das Modell
Das Trainieren hat sehr viel Rechenleistung beansprucht. Auf unserer Nvidia 2070 Super haben 10 Epochs ca. 60 Stunden beansprucht. 

Wir haben 2 Modelle trainiert - mit 10 und mit 40 Epochs. Letzteres (welches hier zum Einsatz kommt) erbrachte ca. 15-20% bessere Ergebnisse im Test. Das Modell belegt 556 MB Speicherplatz und hat 23 725 893 Parameter.

Mit mehr Rechenleistung würden wir nicht die Epochs erhöhen, sondern mehr Features in Pytorch erlernen.

### Bitte beachten Sie, dass manche Funktionen ausschließlich dem Zwecke des FUNKTIONierens dienten und sich unsere Programmierkenntnisse über die Zeit stark verbesserten
