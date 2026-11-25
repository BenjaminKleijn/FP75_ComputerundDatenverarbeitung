**ACHTUNG**
für bessere chi2 Werte ist es unbedingt notwendig, die Datenpunkte an den Frequenzvielfachen von 50 Hz (Netzfrequenz) aus dem Fit und der chi Summe rauszunehmen. Das implementiert man in meiner Plot Class iguess irgendwie indem man erstmal einen Fit mit allem macht, dann die Bereiche berechnet, bei denen die Abweichung der experimentellen Amplitude zu fit sehr hoch ist, und checkt, ob das um eine Vielfachese der Netzfrequenz liegt, dann die Punkte rausnimmt und den Fit mit dieser Maske nochmal macht. Oder man plottet sich die Daten und schaut per Hand die Ausreißer an und schließt sie dann händisch aus.


**Überblick**:\
Auswertung_TeX = TeX Ordner mit finaler pdf für VS Code (wir haben in overleaf gearbeitet und das ding wurde zu groß)\
Code,Daten,Plots = der lab python code; alle Messdaten, die mit `Plot_class.jpynb` geplotted wurden. In dem Notebook ist eine sehr lange Einleitung geschrieben, wie ihr die Plot_class auch benutzen könnt. Hoffentlich brint es euch was.\
Powerpoint = unsere Vortragsdatei, ist ganz gut als Überblick über die Ergebnisse des Versuch i guess

**Wie die TeX Datei funktioniert**:\
dieses Mal ist Auswertung_TeX/main.tex die einzige Datei 
