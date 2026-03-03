# Python Poker Game (5-Card Draw)

Prosta implementacja klasycznego pokera dobieranego (5-Card Draw) napisaną w języku Python. Gra oferuje graficzny interfejs użytkownika (GUI) oraz możliwość rywalizacji z botami.

## Funkcje
* **Pełna logika układów:** Obsługa wszystkich układów kart – od wysokiej karty po Poker Królewski (Royal Flush).
* **Interfejs Graficzny:** Gra zbudowana w oparciu o bibliotekę `tkinter`, zapewniającą czytelny podgląd kart, stanu graczy i puli.
* **Przeciwnicy AI:** System botów podejmujących decyzje o licytacji oraz wymianie kart na podstawie losowości i dostępnych funduszy.
* **System Licytacji:** Obsługa stawek (Small/Big Blind), sprawdzania (Call), podbijania (Raise) oraz pasowania (Fold).
* **Zarządzanie Sesją:** Automatyczne zapisywanie stanu gry do plików JSON dzięki dedykowanemu menedżerowi sesji.

## Struktura Projektu
* `main.py` – Główny plik uruchomieniowy. Inicjalizuje graczy, silnik gry i uruchamia pętlę interfejsu.
* `GameEngine.py` – Serce aplikacji. Zawiera logikę rund, zarządzanie pulą, sprawdzanie hierarchii kart oraz obsługę błędów (np. `InsufficientFundsError`).
* `gui.py` – Warstwa wizualna. Obsługuje wyświetlanie okien, aktualizację stanu gry w czasie rzeczywistym i interakcję z użytkownikiem.
* `poker.py` – Definicje obiektów: `Card` (karta), `Deck` (talia), `Player` (gracz) oraz `BotPlayer` (logika bota).
* `session_manager.py` – Odpowiada za trwałość danych, zapisując i odczytując stan gry z folderu `data/`.

## Uruchomienie

### Wymagania
* Python 3.x
* Biblioteka `tkinter` 
