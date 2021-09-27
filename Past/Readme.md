# Der Weg zum AusspracheTrainer
Besonders die Auswertung erwies sich als unheimlich kompliziert. Auf dem Weg dahin haben wir fast alle Funktionen über 10 mal überarbeitet.

## Eine Funktion, die 1000+ Zeilen Code überflüssig machte
Das Hauptproblem lag dabei, die Wörter des Targets mit denen der Prediction zu vergleichen. Allerdings müssen immer die richtigen miteinander verglichen werden, auch wenn Wörter fehlen, zu viel sind, oder sich leicht unterscheiden. Hierfür haben wir mathematische Formeln und komplizierte Funktionen entwickelt (siehe in diesem Projekt), bis wir für ein kleineren Anwendungsfall die perfekte Funktion geschrieben haben. Eine rekursive Sequence-Matching-Funktion, die jedoch anders als angenommen nicht nur kleine Wortteile vergleichen kann, sondern sogar den gesamten Satz. Damit war der Rest überflüssig, allerdings möchten wir Ihnen ihn zur Vollständigkeit halber hier präsentieren.


# Bitte nehmen Sie zur Kenntnis, dass der Code aus Zeitgründen nicht schön formatiert wurde; er dient lediglich für einen groben Überblick übere unsere bisherige Mühen
