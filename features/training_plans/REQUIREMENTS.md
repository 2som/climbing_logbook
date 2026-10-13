# Wymagania funkcjonalne API: plany treningowe, kalendarz, ascenty, statystyki

Dokument opisuje zachowanie API bez szczegółów implementacyjnych. Źródła: wstępne wymagania z `api.py` oraz plan treningowy PCC (zima 2026/27) jako przypadek referencyjny, który API musi dać się odwzorować w całości.

## 0. Założenia globalne

- A1. Aplikacja wielo-userowa. Każdy zasób (plan, faza, szablon, ćwiczenie, sesja, ascent, projekt, waga) należy do jednego usera i jest prywatny. Brak współdzielenia planów. Wyjątek: katalog dróg (§5.2) jest wspólny.
- A2. Daty sesji i ascentów to daty kalendarzowe (bez godziny i strefy). Timer sesji operuje na znacznikach czasu.
- A3. Usuwanie zasobów użytych w historii jest miękkie: historia (wykonane sesje, logi, ascenty) nigdy nie traci danych.
- A4. Słowniki stałe (nie edytowalne przez usera): bazowy typ sesji, dyscyplina, typ fazy, typ logowania ćwiczenia, sekcja sesji, status sesji, styl przejścia, skale trudności.
- A5. Jednostki: kg (obciążenie), mm (krawędź), sekundy (zwis, przerwa), minuty (czas trwania), RPE 1-10.

## 1. Słownik pojęć

| Pojęcie | Znaczenie |
|---|---|
| Plan | Nadrzędny kontener: cel, data startu, lista faz. |
| Faza | Odcinek planu z zakresem dat i typem (normalna, deload, testy, performance). |
| Tydzień fazy | Numer tygodnia liczony od daty startu fazy, od 1. |
| Definicja ćwiczenia | Wpis w bibliotece usera: nazwa, opis, kategoria, typ logowania. |
| Szablon sesji | Definicja treningu w fazie: nazwa, bazowy typ, dyscyplina, pozycje ćwiczeń. |
| Pozycja ćwiczenia | Ćwiczenie w szablonie z kolejnością, sekcją i parametrami docelowymi, w tym per tydzień fazy. |
| Sesja zaplanowana | Wystąpienie w kalendarzu na konkretną datę, z zamrożoną kopią pozycji. |
| Wykonanie ćwiczenia | Log pozycji w sesji zaplanowanej: status, serie z wartościami, notatka. |
| Projekt treningowy | Droga lub bald na ścianie, nad którym user pracuje przez wiele sesji. Niezwiązany z ascentami. |
| Droga (katalog) | Wspólny wpis skalny: nazwa, crag, trudność, typ. Tylko dla ascentów. |
| Ascent | Przejście skalne usera. Tylko outdoor. Bez powiązania z sesją ani projektem. |

## 2. Moduł: plany treningowe

### 2.1 Plan

- P1. User tworzy plan: nazwa, opis celu (tekst), opcjonalna data startu.
- P2. Plan bez daty startu jest "szkicem": fazy mają tylko długości w dniach. Aktywacja planu ustawia datę startu i wylicza daty faz sekwencyjnie.
- P3. User ma maksymalnie jeden aktywny plan. Aktywacja drugiego wymaga zakończenia lub dezaktywacji pierwszego.
- P4. Statusy planu: szkic, aktywny, zakończony, anulowany.
- P5. Zakończenie planu: ustawia datę końca, nie rusza sesji w kalendarzu.
- P6. Anulowanie planu: kaskadowo usuwa przyszłe, niewykonane sesje zaplanowane z tego planu. Wykonane, pominięte i luźne sesje zostają. Operacja wymaga jawnego potwierdzenia usera (API zwraca liczbę sesji do usunięcia przed wykonaniem).
- P7. Plan da się skopiować jako nowy szkic wraz z fazami, szablonami i pozycjami.

### 2.2 Faza

- F1. Faza należy do planu: nazwa, typ (normalna, deload, testy, performance), fokus (tekst), data startu, data końca.
- F2. Fazy w jednym planie nie mogą się nakładać. Luki między fazami są dozwolone.
- F3. "Obecna faza" = faza aktywnego planu zawierająca dzisiejszą datę. Gdy dziś wypada w luce lub po ostatniej fazie, API zwraca brak obecnej fazy oraz najbliższą przyszłą fazę.
- F4. Przedłużenie fazy o N dni w dwóch trybach:
  - tylko ta faza: odrzucone, jeśli powstałby konflikt z następną fazą;
  - z przesunięciem: wszystkie kolejne fazy przesuwają się o N dni.
- F5. Przy trybie z przesunięciem API pyta, czy przesunąć również niewykonane sesje zaplanowane w przesuwanych fazach. Wykonane sesje nigdy się nie przesuwają.
- F6. Skrócenie fazy: dozwolone tylko do daty ostatniej wykonanej sesji z tej fazy. Niewykonane sesje poza nowym zakresem: user decyduje (usuń lub zostaw bez fazy).
- F7. Usunięcie fazy z wykonanymi sesjami: zablokowane. Faza bez wykonanych sesji: usuwa też swoje szablony i niewykonane sesje po potwierdzeniu.
- F8. Faza da się skopiować wewnątrz planu (np. deload jako kopia fazy 1 do ręcznej redukcji objętości).
- F9. Deload nie jest flagą modyfikującą inne fazy. To osobna faza z własnymi szablonami.

### 2.3 Definicja ćwiczenia (biblioteka)

- E1. Pola: nazwa, opis (instrukcja wykonania, jak legenda PCC), kategoria (rozgrzewka, drill, główne, cool down, mięśnie antagonistyczne / core), typ logowania, flaga "progres w statystykach".
- E2. Typ logowania określa, jakie pola ma seria przy wykonaniu oraz która metryka jest główna do statystyk:

| Typ | Pola serii | Metryka główna | Kierunek |
|---|---|---|---|
| siłowe | powtórzenia, kg, RPE | kg | więcej = lepiej |
| hangboard | czas zwisu (s), dociążenie kg, krawędź mm, chwyt | kg lub mm (wybór usera w statystyce) | kg więcej, mm mniej |
| test | jedna wartość liczbowa + jednostka | wartość | zależnie od ćwiczenia |
| rundy | liczba rund, przerwa (s), czysto tak/nie | rundy | więcej |
| laps | liczba przejść, numer przejścia odpadnięcia | przejścia | więcej |
| projekt | projekt treningowy, high point (tekst lub liczba), notatka | high point liczbowy | więcej |
| wspin/drill | liczba baldów lub dróg, zakres trudności (tekst) | brak | brak |
| czasowe | minuty | minuty | brak |

- E3. Ćwiczenie typu "test" ma zdefiniowany kierunek (więcej lub mniej = lepiej) i jednostkę na definicji.
- E4. Nazwa ćwiczenia unikalna w bibliotece usera.
- E5. Usunięcie definicji użytej w jakimkolwiek szablonie lub wykonaniu: miękkie, ćwiczenie znika z wyszukiwania, historia zostaje.
- E6. Biblioteka wspólna dla wszystkich planów usera.

### 2.4 Szablon sesji

- S1. Szablon należy do fazy: nazwa, bazowy typ, dyscyplina, szacowany czas (min), opis, opcjonalny preferowany dzień tygodnia, lista pozycji.
- S2. Bazowy typ (stały słownik): siła, moc, wytrzymałość, wytrzymałość siłowa, SST (siłownia), luźna, outdoor, test, regeneracja.
- S3. Dyscyplina (stały słownik): baldy, liny, siłownia, outdoor baldy, outdoor liny, mieszana.
- S4. Warianty tej samej jednostki (np. czwartek: baldy albo liny) to osobne szablony. Zależności między wariantami ("gdy Cz liny, w Sb mini projekt 1 próba") opisuje się tekstem w opisie szablonu.
- S5. Szablon da się skopiować do tej samej lub innej fazy (w tym planie).
- S6. Edycja szablonu nie zmienia już zaplanowanych sesji. Osobna akcja: "zastosuj do przyszłych niewykonanych sesji z tego szablonu", po potwierdzeniu.
- S7. Szablon można dodać do fazy jako nowy lub przez kopię istniejącego z innej fazy (zgodnie z "dodaj sesję do fazy: istniejąca lub utwórz").

### 2.5 Pozycja ćwiczenia w szablonie

- X1. Pola: definicja ćwiczenia, kolejność, sekcja (rozgrzewka, główne, cool down), parametry docelowe domyślne, nadpisania per tydzień fazy, notatka.
- X2. Parametry docelowe to zestaw zależny od typu logowania ćwiczenia (np. siłowe: serie, powtórzenia, RPE; hangboard: liczba zwisów, czas zwisu, przerwa, krawędź; rundy: liczba rund, przerwa; czasowe: minuty).
- X3. Nadpisanie per tydzień: dla tygodnia N fazy osobny zestaw parametrów i osobna notatka. Tygodnie bez nadpisania używają wartości domyślnych.
- X4. Tydzień dla sesji wyliczany z daty sesji względem startu fazy, do której należy szablon. Tydzień poza zdefiniowanym zakresem (przedłużona faza): obowiązuje ostatni zdefiniowany tydzień. Tydzień 0 lub ujemny (sesja zaplanowana przed startem fazy): wartości domyślne.
- X5. Zmiana definicji ćwiczenia (wariant w innym tygodniu, np. Three Strike Newcomers → Repeat Circuit) nie jest wspierana w ramach jednej pozycji. Rozwiązanie: notatka per tydzień. Podmiana definicji per tydzień: v2.
- X6. Ta sama definicja ćwiczenia może wystąpić w szablonie wiele razy (np. Contrast Warm Up w rozgrzewce i Rhythm Cool Down).
- X7. Pozycja typu "projekt" może mieć domyślny projekt treningowy (§2.6), nadpisywalny w sesji.

### 2.6 Projekt treningowy

- T1. Lekka encja usera: nazwa (tekst dowolny, np. "niebieska 6c+ na przewieszeniu"), typ (bald, droga), trudność (tekst), lokalizacja (tekst, np. nazwa ściany), cel (send, UDU, laps, inne), status (aktywny, zrobiony, porzucony), data startu, data zamknięcia, notatka.
- T2. Projekt niezwiązany z katalogiem dróg ani z ascentami.
- T3. Każde wykonanie pozycji typu "projekt" wskazuje jeden projekt treningowy i zapisuje high point (liczba: bolt lub ruch) oraz notatkę. Historia prób projektu = lista takich wykonań.
- T4. API zwraca dla projektu: liczbę sesji, w których był logowany, ostatni high point, wykres high point w czasie.
- T5. Zamknięcie projektu (zrobiony/porzucony) nie usuwa historii. Zamknięty projekt nie pojawia się na liście wyboru w nowych sesjach, ale da się reaktywować.
- T6. Usunięcie projektu z logami: miękkie.

## 3. Moduł: kalendarz i sesje

### 3.1 Widok kalendarza

- K1. Lista dni posortowana po dacie. Domyślne okno: 7 dni wstecz + 7 dni w przód od dziś. Dalsze ładowanie w obie strony przez cursor oparty na dacie.
- K2. Dzień zawiera: sesje zaplanowane (każdy status), ascenty z tego dnia (tylko podgląd, moduł osobny), informację o fazie, w której leży dzień.
- K3. Dni bez wpisów są zwracane jako puste (nie pomijane), żeby lista była ciągła.
- K4. Filtry: tylko sesje z planu, tylko luźne, tylko ukończone, wszystko.
- K5. Wiele sesji tego samego dnia dozwolone, kolejność po czasie utworzenia lub ręcznej kolejności.

### 3.2 Planowanie sesji

- Z1. Źródła sesji: szablon z fazy aktywnego planu, luźna sesja wspinaczkowa wewnątrz, luźna sesja wspinaczkowa na zewnątrz, luźna sesja z własną nazwą i typem.
- Z2. Zaplanowanie z szablonu: data wymagana. Sesja dostaje zamrożoną kopię pozycji z parametrami wyliczonymi dla tygodnia fazy (§X4). Późniejsza edycja szablonu nie wpływa na tę sesję.
- Z3. Planowanie sesji z szablonu fazy A na datę w fazie B lub poza planem: dozwolone, API zwraca ostrzeżenie.
- Z4. Planowanie w przeszłości: dozwolone (wpis po fakcie).
- Z5. Luźna sesja: nazwa, bazowy typ (domyślnie "luźna"), dyscyplina, data, opcjonalnie pozycje ćwiczeń dodane ręcznie z biblioteki.
- Z6. Hurtowe planowanie: "zaplanuj fazę" tworzy sesje dla każdego szablonu z preferowanym dniem tygodnia w każdym tygodniu fazy. Szablony bez dnia tygodnia pomijane. Istniejące sesje tego dnia z tego samego szablonu nie są duplikowane. Operacja zwraca podgląd (liczba sesji) przed wykonaniem.
- Z7. Sesja wie, z jakiego szablonu, fazy i planu pochodzi, nawet gdy szablon zostanie później usunięty.

### 3.3 Cykl życia sesji

- C1. Statusy: zaplanowana, w trakcie, ukończona, częściowo ukończona, pominięta, anulowana.
- C2. Pominięta = świadomie nie zrobiona, zostaje w kalendarzu do statystyk zgodności z planem. Anulowana = usunięta z widoku kalendarza, zachowana w historii.
- C3. Usunięcie sesji: twarde tylko dla sesji bez logów i bez statusu ukończenia. Reszta: anulowanie.
- C4. Ukończenie sesji nie wymaga logów ćwiczeń. Cofnięcie ukończenia dozwolone, logi zostają.
- C5. Przesunięcie sesji na inną datę: dozwolone dla niewykonanych. Parametry docelowe pozycji zostają z oryginalnej daty, osobna opcja "przelicz cele dla nowego tygodnia". Przesunięcie ukończonej sesji w przyszłość: odrzucone. Zmiana daty ukończonej sesji w przeszłość: dozwolone.
- C6. Zamiana szablonu w niewykonanej sesji (np. czwartek baldy → liny): tworzy nową zamrożoną kopię pozycji, poprzednie pozycje bez logów znikają, z logami: zablokowane.
- C7. Duplikacja sesji na inną datę, w tym luźnej.

### 3.4 Widok i edycja sesji

- V1. Sesja zwraca: metadane, status, listę pozycji w kolejności i sekcjach z parametrami docelowymi oraz logami wykonania, czas trwania, oceny, opis.
- V2. Opis sesji: dowolny tekst, zawsze dostępny (w api.py warunkowo, tu: zawsze).
- V3. Oceny po sesji, wszystkie opcjonalne, liczbowe: trudność sesji 0-6, skóra 1-5, palce 1-5, samopoczucie 1-5, sen w godzinach. Uwagi tekstowe osobno.
- V4. Logowanie per pozycja: status (zrobione, pominięte, zmodyfikowane), serie z polami zależnymi od typu logowania (§E2), notatka. Liczba serii w logu może różnić się od docelowej (hangboard -50%).
- V5. Dodanie pozycji ad hoc do sesji (ćwiczenie z biblioteki nieobecne w szablonie) oraz usunięcie pozycji z sesji bez wpływu na szablon.
- V6. Zmiana kolejności pozycji w sesji.

### 3.5 Czas sesji

- D1. Czas trwania w minutach, dwie drogi: timer lub ręczny wpis. Ręczny nadpisuje timer.
- D2. Timer: start, pauza, wznowienie, stop. Start przełącza status na "w trakcie". Stop zapisuje sumę aktywnego czasu.
- D3. Tylko jeden timer aktywny na usera w danym momencie. Start drugiego: odrzucony z informacją o aktywnym.
- D4. Timer aktywny dłużej niż 6 godzin: API zwraca ostrzeżenie, user musi zatwierdzić czas lub wpisać ręcznie.
- D5. Zaplanowany czas (z szablonu) i rzeczywisty przechowywane osobno.

## 4. Moduł: profil

- W1. Waga ciała: lista wpisów data + kg. Jeden wpis na dzień, nadpisywalny.
- W2. Statystyki hangboard mogą prezentować dociążenie jako % masy ciała, biorąc ostatni wpis wagi nie późniejszy niż data sesji. Brak wagi: tylko kg.

## 5. Moduł: ascenty (tylko outdoor)

### 5.1 Ascent

- R1. Pola: droga z katalogu (wymagana), data, styl, komentarz, opcjonalna ocena drogi (gwiazdki 0-3).
- R2. Styl (stały słownik): onsight, flash, redpoint, go. Onsight niedozwolony dla boulderów. "Go" = próba bez przejścia, nie liczy się jako send w statystykach.
- R3. Data nie może być z przyszłości. UI oferuje skróty (wczoraj, ostatnia sobota, ostatnia niedziela), API przyjmuje datę.
- R4. Ten sam user może mieć wiele ascentów tej samej drogi (powtórki, próby). Powtórzony send po wcześniejszym sendzie oznaczany automatycznie flagą "powtórka".
- R5. Ascent bez powiązania z sesją, fazą ani projektem treningowym.
- R6. Edycja i usunięcie ascentu dozwolone zawsze. Usunięcie twarde.
- R7. Lista ascentów usera: filtr typ (droga/bald), rok, styl, crag, sortowanie po dacie lub trudności.

### 5.2 Katalog dróg (wspólny)

- G1. Wpis: nazwa, typ (droga sportowa, bald), trudność w skali typu, crag, sektor (opcjonalny), kraj, źródło (import 8a.nu, własny), autor wpisu własnego.
- G2. Wyszukiwanie po fragmencie nazwy z filtrami: typ, kraj, crag. Wyniki priorytetyzują dopasowanie nazwy, potem crag.
- G3. User może dodać własny wpis, gdy drogi nie ma w katalogu. Wpis własny widoczny dla wszystkich (katalog wspólny), oznaczony jako niezweryfikowany.
- G4. Duplikat (ta sama nazwa, crag i typ, bez względu na wielkość liter) odrzucany, API zwraca istniejący wpis.
- G5. Edycja wpisu własnego: tylko autor, dopóki nikt inny nie zalogował na nim ascentu. Wpisy z importu nieedytowalne przez userów.
- G6. Import z 8a.nu to osobny proces poza API usera. Katalog musi przyjąć aktualizację trudności wpisu bez psucia istniejących ascentów (ascent przechowuje trudność z momentu wpisu).

### 5.3 Skale trudności

- Q1. Drogi: skala francuska (4, 5a ... 9c). Baldy: skala Font (3, 4, 5, 6A, 6A+ ... 9A).
- Q2. Każdy stopień ma wewnętrzną wartość porządkową, osobno dla każdej skali, do sortowania i wykresów. Skale nie są porównywane między sobą.
- Q3. Stopnie spoza słownika odrzucane.

## 6. Moduł: statystyki

- ST1. Progres w ćwiczeniu: wybór definicji ćwiczenia z flagą progresu, zakres dat, agregacja na sesję (max, średnia, suma). Wynik: punkty data + wartość metryki głównej. Dla hangboard dodatkowo wartość jako % masy ciała (§W2) i osobna seria dla krawędzi mm. Dane pochodzą z logów ukończonych i częściowo ukończonych sesji.
- ST2. Czas sesji per bazowy typ: suma minut rzeczywistego czasu trwania ukończonych sesji, grupowana po bazowym typie, okres: ostatnie 12 miesięcy, rok kalendarzowy, faza, all time. Sesje bez czasu pomijane, liczba pominiętych zwracana.
- ST3. Ascenty: liczba sendów per stopień, osobno drogi i baldy, filtr rok lub all time, filtr styl, wykluczony styl "go". Dane do horizontal bar chart: stopień, liczba, podział per styl.
- ST4. Zgodność z planem per faza: liczba sesji zaplanowanych, ukończonych, częściowo, pominiętych.
- ST5. Projekt treningowy: high point w czasie, liczba sesji (§T4).
- ST6. Oceny w czasie: skóra, palce, trudność sesji jako serie czasowe.

## 7. Reguły spójności i walidacje

- RV1. Daty fazy wewnątrz dat planu, gdy plan ma daty.
- RV2. Sesja z szablonu zachowuje odniesienie do fazy; zmiana dat fazy nie zmienia przypisania sesji do fazy.
- RV3. Log serii musi odpowiadać typowi logowania ćwiczenia (pola spoza typu odrzucane).
- RV4. Oceny poza zakresem odrzucane.
- RV5. Pozycja typu projekt bez wskazanego projektu treningowego: log dozwolony z samą notatką, bez high point.
- RV6. Operacje kaskadowe (anulowanie planu, usunięcie fazy, przesunięcie faz, zaplanuj fazę, zastosuj szablon do przyszłych) działają dwuetapowo: podgląd skutków, potem wykonanie z potwierdzeniem.

## 8. Poza zakresem (v2)

- Automatyczne generowanie całego kalendarza przy aktywacji planu (teraz: ręczne "zaplanuj fazę", §Z6).
- Podmiana definicji ćwiczenia per tydzień fazy (§X5).
- Współdzielenie planów i szablonów między userami.
- Załączniki (zdjęcie spraywall circuitu).
- Powiadomienia i przypomnienia o sesjach.
- Konwersja między skalami trudności (V ↔ Font, YDS ↔ francuska).
- Reguły automatycznej modyfikacji (hangboard -50% przy palcach poniżej 3).
- Indoor ascenty i projekty powiązane z katalogiem.
