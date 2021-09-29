# Die Zukunft des AusspracheTrainers
Für die Zukunft ist viel geplant, welches wir leider bis zum Abgabetermin noch nicht fertigstellen können. Es befindet sich zurzeit in der Planungs- oder sogar schon Testphase.

## Mehr Sprachfehler
Durch die Zusammenarbeit mit der [logopädischen Praxis von Tina Hillebrecht](https://logopaedie-hillebrecht.de/) werden wir mit Sicherheit in Zukunft mehr Sprachfehler erfassen können. Aus Zeitgründen haben wir bisher nur den Sigmatismus im Programm.

---> `Fehlerhafte Aussprachen (Dyslalien).xlsx`
---> `Logopädin Sigmatimus.docx`

## Laut-Ähnlichkeit einbeziehen
Manche Laute klingen sehr ähnlich. Zum Beispiel "m" und "n" oder "d" und "t". Solche kann man ohne Kontext viel schwerer von einander unterscheiden und sollten dementsprechend eine andere Gewichtung bekommen. Je näher alle Zahlen im Tuple neben dem Buchstaben in der Excel-Datei sind, desto ähnlicher sind sie. Ist die Spalte (zweite Zahl) im Tuple wichtiger.

---> `IPA Konsonanten Mapping.xlsx`

## Homographe
Das gleiche Wort im deutschen Alphabet kann eine unterschiedliche Aussprache haben. Bekannte Beispiele davon sind "umfahren" (einen Umweg um etwas fahren vs. durch etwas fahren) oder "modern" (verwesen vs. neuzeitlich). Die API des DWDS macht dies möglich: [IPA von "modern"](https://www.dwds.de/api/ipa/?q=modern), allerdings muss die Auswertung dafür noch geschrieben werden, sodass das richtige der beiden Wörter ausgewählt wird; basierend auf dem zugehörigen Wort der AusspracheTrainer KI, welche die einzige ist, jene direkt IPA ausgibt. Da Homographe nur selten auftreten, wird dieses Feature erst in zukünftigen Versionen erscheinen.

## Direkte Einbindung des Gramophone Source Codes **EDIT** 
Die Lautschrift der Schnittschnelle des DWDS wird von der Open-Source Software [Gramophone](https://kaskade.dwds.de/gramophone/) bereitgestellt. Eine direkte Anbindung an solche würde folgenden Vorteil bieten:
__Nachvollziehbarkeit, welcher Buchstabe des deutschen Alphabets zu welchem der Lautschrift gehören__

Dadurch kann die Auswertung auch im deutschen Alphabet ausgegeben werden, sodass Nutzer*innen, die nicht mit der Lautschrift bewandert sind, das Ergebnis trotzdem schnell und sicher verstehen. Dieses Feature können sie [hier](https://kaskade.dwds.de/~kmw/gramophone.py?q=modern#:~:text=Segmented%20Transcription,n%2Cn%20%3A%2013.095) sich angucken, beim Beispielwort "modern".  *Auf der Anwendungswebseite ist nur eine mögliche Aussprache des Homographs zu sehen.*
