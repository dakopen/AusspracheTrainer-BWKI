# Der Weg zum AusspracheTrainer
Besonders die Auswertung erwies sich als unheimlich kompliziert. Auf dem Weg dahin haben wir fast alle Funktionen mehrmals überarbeitet.

## Sequence Matcher ersetzt über 1000 Zeilen Code
Das Hauptproblem lag dabei, die Wörter des Targets mit denen der Prediction zu vergleichen. Allerdings müssen immer die richtigen miteinander verglichen werden, auch wenn Wörter fehlen, zu viel sind, oder sich leicht unterscheiden. Hierfür haben wir mathematische Formeln und komplizierte Funktionen entwickelt (siehe in diesem Projekt), bis wir für ein kleineren Anwendungsfall die perfekte Funktion geschrieben haben. Eine rekursive Sequence-Matching-Funktion, die jedoch anders als angenommen nicht nur kleine Wortteile vergleichen kann, sondern sogar den gesamten Satz (siehe `Sequence-matcher.py`). Damit war der Rest überflüssig, allerdings möchten wir Ihnen ihn zur Vollständigkeit halber hier präsentieren.


### Similarity Metrics:
Diese Funktion war der Kern der mathematischen Funktionen: Er gab mehrere Zahlen aus, jene etwas über die Ähnlichkeit von zwei Strings aussagten. Die Zahlen wurden später mit einer weiteren, komplizierten Funktion zusammengerechnet.

### Auswertungsfunktion2:
Wie man dem Namen entnehmen kann, war dies der zweite Anlauf auf das gleiche, in der Einleitung beschriebene Problem zu bewältigen. Der Code funktionierte zwar recht stabil, wird nun aber um weiten verbessert, indem er durch die perfekte Funktion substituiert wurde. 

### AuswertungAlsFunktion:
Diese Funktion wurde auch überflüssig. Teile davon sind in die jetzige Auswertung eingeflossen.


### Bitte nehmen Sie zur Kenntnis, dass der Code aus Zeitgründen nicht schön formatiert wurde; er dient lediglich für einen groben Überblick übere unsere bisherige Mühen

