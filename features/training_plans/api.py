"""
plan treningowy dzieli się na fazy, sesje i ćwiczenia
tworzenie planu treningowego:
1. utwórz fazę
2. dodaj sesję do fazy (istniejąca lub utwórz)
3. dodaj ćwiczenie do fazy (istniejące lub utwórz)

mój plan treningowy:
 -> obecna faza (default)
 -> widok z podziałami na fazy i możliwymi ćwiczeniami
 -> opcja przedłużenia fazy
 -> anulowanie treningu (kaskada na zaplanowane sesje z planu treningowego - zapytanie do usera)

Kalendarz

Widok kalendarza - na dobrą sprawę to zwykła lista z podziałem na dni z offsetem - 7 dni + 7 dni + infinite load z curor based pagination

dostępne akcje:
 -> zaplanuj sesje
 -> usuń sesje
 -> edytuj sesje / widok sesji:
   - sesja wyświetla wszystkie ćwiczenia zawarte w sesji
   - jeśli sesja daje możliwość dodania opisu - dodaj możliwość opisu
   - odznacz sesje jako ukończoną
   - możliwość oznaczenia poziomu trudności sesji od (0-6?)
   - jeśli ćwiczenie sesji dodaje możliwość wprowadzenia obciążenia - możliwość dodania obciążenie per serie ćwiczenia
   - monitorowanie czas sesji, może być timer w apce, może być wpisywane z palca przez usera

możliwe sesje do zaplanowania:
sesje z planu trenigowego + luźna sesja wspinaczkowa wewnątrz, luźna sesja wspinaczkowa na zewnątrz


Dodanie ascentów (tak jak w 8a.nu):
możliwośc dodania drogi sportowej lub bouldera do historii
formularz musi zawierać: 
1. wybór daty z domyślnymi przyciskami: yesterday, last sunday, last saturday i date picker
2. nazwa drogi
3. trudność drogi,
4. styl przejścia (flash, onsight, redpoint, go)
5. ewentualny komentarz

Najlepiej żeby drogi / boulder możnaby wyszukiwać więc przydałoby się zescrapować 8a.nu (AI TASK)



Statystyki
1. możliwość wyświetlania progresu w ćwiczeniach. Realnie będzie to tylko hangboard i ćwiczenia na siłowni.
 np. wybieram ćwiczenia: podciąganie z obciążeniem to pokazuje mi się wykres z datami gdzie wartoscia na wykresie będzie obciążenie
2. wykres kołowy z ostatniego roku który pokazuje ile czasu łącznie spędziłem na sesjach + inna sesja = inny kolor. Myślę, że przy intesywnym planie treningowym jest dużo różnych sesji więc wykres się rozwodni. Dobrze będzie pomyśleć o czym w rodzaju bazowy typ np. siła, wytrzymałość itd.
3. wykres ze wszystkim ascentami. Filtry po roku lub all_time. Wykres typu Horizontal Bar Chart.
"""