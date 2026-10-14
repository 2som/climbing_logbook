# Prompt dla Claude Design: aplikacja webowa Climbing Logbook

Zaprojektuj aplikację webową dla wspinacza do prowadzenia planu treningowego, kalendarza sesji, dziennika przejść skalnych i statystyk. Aplikacja jest frontendem do istniejącego API (FastAPI). Jeden użytkownik, własne dane, bez funkcji społecznościowych.

## Użytkownik i kontekst użycia

Wspinacz amator trenujący wg 12-tygodniowego planu (3 sesje wspinaczkowe + 1 siłownia tygodniowo). Główne użycie: **telefon na ścianie lub siłowni**, spocone ręce, magnezja, przerwy 2-3 minuty między seriami. Drugie użycie: laptop w domu, przegląd planu i statystyk. Projektuj mobile-first, desktop jako rozszerzenie, nie osobny produkt.

Priorytet: wpisanie wyniku serii w 2 dotknięcia. Zero kreatorów, zero modali w modalach.

## Model danych (jak to rozumie użytkownik)

- **Plan treningowy**: nazwa, lista faz. Szablon, można uruchomić wiele razy.
- **Faza**: nazwa, opis, kolejność, długość w tygodniach. Bez dat. Daty wynikają z uruchomienia planu.
- **Aktywny plan**: uruchomienie planu od konkretnej daty. Jeden na użytkownika. Z niego wynika "obecna faza" i "tydzień fazy".
- **Sesja (szablon)**: należy do fazy. Nazwa, typ, szacowany czas, opis, lista ćwiczeń w kolejności.
- **Typ sesji**, 5 stałych: siła/moc, wytrzymałość, projekt, siłownia, luźna.
- **Ćwiczenie w sesji**: nazwa, opis (instrukcja), domyślne serie / powtórzenia / czas, jednostka (kg, sekundy, mm, liczba), etykieta jednostki (np. "dociążenie", "bolt w drugim wejściu", "rundy"), flaga "zbiera wynik". Ćwiczenia rozgrzewkowe nie zbierają wyniku.
- **Biblioteka ćwiczeń**: szablony ćwiczeń użytkownika, źródło wartości domyślnych przy dodawaniu ćwiczenia do sesji.
- **Sesja zaplanowana**: sesja z planu (lub luźna) na konkretny dzień. Pola: ukończona tak/nie, czas trwania w minutach (ręcznie), notatka, odczuwana trudność 0-6. Zawiera listę ćwiczeń z wynikami.
- **Wynik ćwiczenia**: lista serii, każda: powtórzenia + wartość w jednostce ćwiczenia, plus notatka. Domyślne serie z szablonu tylko prefillują formularz, użytkownik dodaje i usuwa serie dowolnie. Tak działa progresja: w następnym tygodniu dopisuje serię lub podnosi wartość.
- **Przejście skalne (ascent)**: tylko skały, bez związku z sesjami. Droga z katalogu (nazwa, rejon, trudność), data, styl (onsight, flash, redpoint, go), komentarz. Skale: francuska dla dróg, Font dla boulderów.

## Ekrany (MVP)

### 1. Dziś / kalendarz (ekran startowy)
- Lista dni, dziś na górze lub wyśrodkowane, 7 dni wstecz i 7 w przód, dalsze ładowanie w obie strony przy przewijaniu.
- Każdy dzień: zaplanowane sesje (nazwa, typ jako kolor lub ikona, czas, status ukończona / nie). Dni puste widoczne, nie ukrywane.
- Nagłówek: obecna faza i tydzień fazy, np. "Faza 2: moc + wytrzymałość, tydzień 2/4".
- Akcja główna: "zaplanuj sesję" → wybór z listy sesji obecnej fazy albo "luźna sesja wewnątrz" / "luźna sesja na zewnątrz", potem data.
- Na sesji: otwórz, przesuń na inny dzień, usuń.

### 2. Sesja (widok wykonania), najważniejszy ekran
- Nagłówek: nazwa, typ, data, szacowany czas, opis sesji (zwijany).
- Lista ćwiczeń w kolejności. Każde: nazwa, krótkie instrukcje (zwijane), domyślne parametry ("5 zwisów x 7s", "4 x 5").
- Ćwiczenie zbierające wynik: tabela serii z polami powtórzenia + wartość (etykieta jednostki z ćwiczenia, np. "dociążenie [kg]", "krawędź [mm]", "rundy"), przycisk "+ seria", usuwanie serii, notatka do ćwiczenia. Wartości z poprzedniego wykonania tego ćwiczenia widoczne obok jako podpowiedź ("ostatnio: 5 x 22 kg").
- Ćwiczenie bez wyniku: tylko odhaczenie.
- Stopka: czas trwania (minuty, ręcznie), odczuwana trudność 0-6, notatka sesji, przycisk "zakończ sesję". Zakończenie nie wymaga wypełnienia wszystkiego.
- Duże pola dotykowe, klawiatura numeryczna, bez auto-save'u w połowie wpisywania liczby, ale zapis po opuszczeniu pola.

### 3. Mój plan
- Aktywny plan: nazwa, data startu, pasek faz z datami i zaznaczeniem obecnej.
- Faza rozwijana → lista sesji → sesja rozwijana → lista ćwiczeń z parametrami. Tylko podgląd + wejście w edycję.
- Akcje: uruchom plan od daty, zakończ aktywny plan, przedłuż obecną fazę (opcja, może być poza MVP, zostaw miejsce).
- Lista pozostałych planów użytkownika (nieaktywnych).

### 4. Edycja planu
- Plan → fazy (nazwa, opis, tygodnie, kolejność przez przeciąganie lub strzałki).
- Faza → sesje (nazwa, typ, czas, opis).
- Sesja → ćwiczenia: dodaj z biblioteki (wyszukiwarka po nazwie, wartości domyślne wchodzą automatycznie) lub nowe, potem nadpisz serie / powtórzenia / czas / opis dla tej sesji. Kolejność przez przeciąganie.
- Kopiuj sesję do innej fazy.

### 5. Biblioteka ćwiczeń
- Lista z wyszukiwarką. Ćwiczenie: nazwa, opis, jednostka, etykieta, domyślne serie / powtórzenia / czas, czy zbiera wynik.
- Formularz dodawania / edycji. Jednostka to wybór z 4 wartości.

### 6. Przejścia skalne
- Lista przejść, filtr: rok / wszystkie, droga / boulder, styl.
- Dodaj przejście: wyszukiwarka drogi z katalogu (nazwa, rejon, trudność) z opcją "dodaj własną", data z szybkimi przyciskami "wczoraj", "ostatnia sobota", "ostatnia niedziela" + date picker, styl, komentarz.

### 7. Statystyki
- Progres w ćwiczeniu: wybór ćwiczenia z biblioteki (tylko zbierające wynik), wykres liniowy: data na X, wartość na Y (max z serii), jednostka z ćwiczenia. Zakres dat.
- Czas na sesjach wg typu: wykres kołowy lub słupkowy, 5 typów, okres: ostatni rok / faza / wszystko.
- Przejścia skalne: poziomy wykres słupkowy, trudność na osi, liczba przejść, osobno drogi i bouldery, filtr rok / wszystko, podział kolorem na styl (bez stylu "go").

## Nawigacja
Dolny pasek na mobile, 5 pozycji: Kalendarz, Sesja (dzisiejsza, jeśli jest), Plan, Przejścia, Statystyki. Biblioteka ćwiczeń dostępna z Planu. Na desktopie pasek boczny.

## Przykładowe dane do makiet (z prawdziwego planu)

Plan "Plan zima 2026/27: CLIMB 5.12", start 26.10.2026. Fazy: Testy (1 tydz.), Faza 1: siła + wytrzymałość ogólna (4), Faza 2: moc + wytrzymałość (4), Faza 3: wytrzymałość siłowa (3), Retest (1).

Tydzień fazy 1:
- Pn: baldy, siła (siła/moc, 120 min): Climbing Movement Prep, On the Wall Mobility 10 min, Contrast Warm Up 2 baldy, One Touch 2 baldy, Perfect Repeat 1 bald x 4, Boulder Mini Project 30 min, Single Session Sends 40 min, Rhythm Cool Down 2 baldy.
- Wt: siłownia (SST) (siłownia, 60 min): Climbing Movement Prep, Hangboard Warm Up, Max Hangs 7/53 (5 zwisów x 7s, dociążenie [kg]), Podciągnięcia z obciążeniem (4 x 5, obciążenie [kg]), Wyciskanie na ławce (3 x 10, ciężar [kg]), Przysiady (3 x 10, ciężar [kg]), Mięśnie antagonistyczne + core 10 min.
- Cz: baldy, wytrzymałość ogólna (wytrzymałość, 90 min): rozgrzewka, Boulder Mini Project 15 min, Spraywall Endurance Circuit (2 rundy), Rhythm Cool Down.
- Sb: liny, wytrzymałość (wytrzymałość, 150 min): rozgrzewka, Route Mini Project (2 próby, bolt [high point]), UDU Project (2 próby, bolt w drugim wejściu), Vert Laps (przejścia), Route Cool Down.

Przykładowy wynik Max Hangs: 5 serii, każda 1 powtórzenie, 20 kg, 20 kg, 20 kg, 22 kg, 22 kg, notatka "ostatnie dwa z zapasem 1s".

Przykładowe przejścia: "Tęcza" 6c+ redpoint, "Krzywa" 6b onsight, boulder "Szpic" 6B flash.

## Ograniczenia i czego nie projektować
- Bez timera w sesji, czas trwania wpisywany ręcznie.
- Bez statusów sesji poza ukończona / nieukończona. Pominięta sesja = usunięcie.
- Bez sekcji w sesji (rozgrzewka / główne / cool down), tylko kolejność.
- Bez współdzielenia planów, bez profili innych użytkowników, bez komentarzy.
- Bez powiadomień, bez integracji z zegarkami.
- Bez wiązania przejść skalnych z sesjami treningowymi.
- Bez konwersji skal trudności.
- Logowanie: e-mail + hasło, jeden ekran, bez rejestracji w MVP.

## Styl
Czytelność w słabym świetle i na małym ekranie ważniejsza niż ozdoby. Wysoki kontrast, duże liczby, typ sesji rozróżnialny kolorem i ikoną jednocześnie. Tryb ciemny domyślny. Język interfejsu polski, nazwy ćwiczeń PCC po angielsku (Max Hangs, Three Strike) jako terminy. Zaproponuj system kolorów dla 5 typów sesji i układ pól serii na ekranie sesji w dwóch wariantach do porównania.
