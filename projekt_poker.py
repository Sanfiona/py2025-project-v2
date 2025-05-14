import random
from typing import List
from collections import Counter
import datetime

class InsufficientFundsError(Exception):
    """Wyjątek rzucany, gdy gracz nie ma wystarczających środków."""
    pass

class Card:
    # słownik symboli unicode
    unicode_dict = {'Hearts': '\u2665', 'Diamonds': '\u2666', 'Clubs': '\u2663', 'Spades': '\u2660'}
       
    def __init__(self, rank, suit):
    # TODO: definicja konstruktora, ma ustawiać pola rangi i koloru.
        self.rank = rank
        self.suit = suit
        
    def get_value(self):
    # TODO: definicja metody (ma zwracać kartę w takiej reprezentacji, jak dotychczas, tzn. krotka)
        return (self.rank, self.suit)
    
    def __str__(self):
    # TODO: definicja metody, przydatne do wypisywania karty
        return f"{self.rank}{Card.unicode_dict.get(self.suit, '?')}"

class Deck():
    
    def __init__(self, *args):
    # TODO: definicja metody, ma tworzyć niepotasowaną talię (jak na poprzednich lab)
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = []
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(rank, suit))
    def __str__(self):
    # TODO: definicja metody, przydatne do wypisywania karty
        return ", ".join(str(card) for card in self.cards)
        
    def shuffle(self):
    # TODO: definicja metody, tasowanie
       random.shuffle(self.cards) 

    def deal(self, players):
    # TODO: definicja metody, otrzymuje listę graczy i rozdaje im karty wywołując na nich metodę take_card z Player
       for _ in range(5):  
        for player in players:
            if self.cards:
                player.take_card(self.cards.pop())
          
class Player():

    def __init__(self, money, name=""):
        self.stack = money
        self.name = name
        self.hand = []

    def take_card(self, card):
        self.hand.append(card)

    def get_stack_amount(self):
        return self.stack

    def change_card(self, card, idx):
    # TODO: przyjmuje nową kartę, wstawia ją za kartę o indeksie idx, zwraca kartę wymienioną
        if 0 <= idx < len(self.hand):
            replaced_card = self.hand[idx]
            self.hand[idx] = card
            return replaced_card
        else:
            raise IndexError("Index out of range")

    def get_player_hand(self):
        return tuple(self.hand)

    def cards_to_str(self):
    # TODO: definicja metody, zwraca stringa z kartami gracza
        return ", ".join(str(card) for card in self.hand)

class GameEngine:
    def __init__(self, players: List[Player], deck: Deck, small_blind: int = 25, big_blind: int = 50, session_manager = SessionManager):
        """Inicjalizuje graczy, talię, blindy i pulę."""
        self.players = players
        self.deck = deck
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.pot = 0
        self.session_manager = session_manager
        self.game_id = str(datetime.now().timestamp())
        
    def play_round(self) -> None:
        """Przeprowadza jedną rundę:
           1. Pobiera blindy
           2. Rozdaje karty
           3. Rundę zakładów
           4. Wymianę kart
           5. Showdown i przyznanie puli
        """
        self.collect_blinds()
        self.deck = Deck()
        self.deck.shuffle()
        self.deck.deal(self.players)

        for player in self.players:
            print(f"{player.name}, Twoje karty: {player.cards_to_str()}")
        self.betting_round()

        for player in self.players:
            indices_to_exchange = self.prompt_exchange_cards(player) 
            self.exchange_cards(player, player.hand, indices_to_exchange)

        winner = self.showdown()  
        winnings = self.pot
        if winner:
            self.award_pot(winner)
            print(f"{winner.name} wygrał {winnings} żetonów!")
        else:
            print("Brak zwycięzcy w tej rundzie.")
        
        session_data = self.generate_session_data()
        self.session_manager.save_session(session_data, self.game_id)

    def generate_session_data(self):
        """Generuje dane sesji do zapisania."""
        session_data = {
            "players": [player.get_player_hand() for player in self.players],
            "pot": self.pot,
            "blinds": {"small_blind": self.small_blind, "big_blind": self.big_blind},
            "history": []  # Możesz dodać historię zakończonych rozdań
        }
        return session_data

    def collect_blinds(self) -> None:
        self.players[0].stack -= self.small_blind
        self.players[1].stack -= self.big_blind
        self.pot += self.small_blind + self.big_blind

    def betting_round(self) -> None:
        current_bet = 0
        for player in list(self.players):
            action, amount = self.prompt_bet(player, current_bet)

            if action == "fold":
                print(f"{player.name} pasuje.")
                self.players.remove(player)
            elif action == "call":
                if player.get_stack_amount() >= current_bet:
                    player.stack -= current_bet
                    self.pot += current_bet
                    print(f"{player.name} sprawdza za {current_bet} żetonów.")
                else:
                    raise InsufficientFundsError(f"{player.name} nie ma wystarczjąco środków")
            elif action == "raise":
                current_bet = amount
                player.stack -= amount
                self.pot += amount
                print(f"{player.name} podbija do {amount} żetonów.")
    
    def prompt_bet(self, player: Player, current_bet: int) -> tuple[str, int]:
        """Pobiera akcję gracza — fold, call, raise."""
        print(f"{player.name}, masz {player.get_stack_amount()} w stacku.")
        print(f"Minimalny zakład do wyrównania: {current_bet}")
        print("Dostępne opcje: fold, call, raise X")

        while True:
            action = input("Twoja decyzja: ").strip().lower()

            if action == "fold":
                return "fold", 0
            
            elif action == "call":
                if player.get_stack_amount() >= current_bet:
                    return "call", current_bet
                else:
                    print("Nie masz wystarczających funduszy na call!")   
            
            elif action.startswith("raise"):
                try:
                    amount = int(action.split()[1])
                    if amount <= current_bet:
                        print(f"Raise musi być większy niż aktualny zakład ({current_bet}).")
                        continue

                    if amount > player.get_stack_amount():
                        print("Nie masz wystarczających funduszy!")
                        
                    else:
                        return "raise", amount  
                except ValueError:
                    print("Podaj prawidłową kwotę raise")       
            else:
                print("Nieprawidłowa akcja, spróbuj ponownie.")
                

    def exchange_cards(self, player: Player, hand: List[Card], indices: List[int]) -> List[Card]:
        """Wymienia wskazane karty z ręki gracza, wkłada stare na spód talii."""
        for idx in indices:
            if not (0 <= idx < len(hand)):
                raise ValueError("Nieprawidłowy indeks karty do wymiany.")

        if len(self.deck.cards) < len(indices):
            raise RuntimeError("Brak kart do wymiany w talii!")

        for idx in indices:
            old_card = player.change_card(self.deck.cards.pop(), idx)
            self.deck.cards.insert(0, old_card)  


    def prompt_exchange_cards(self, player: Player) -> List[int]:
        """Prosi gracza o wybór kart do wymiany (indeksy)."""
        while True:
            try:
                print(f"{player.name}, Twoje karty: {player.cards_to_str()}")
                inp = input("Wybierz indeksy kart do wymiany (od indeksu 0 i oddzielone przecinkami): ").strip()
                if not inp:
                    return []

                indices = [int(i.strip()) for i in inp.split(',') if i.strip()]

                for idx in indices:
                    if not (0 <= idx < len(player.hand)):
                        raise ValueError(f"Nieprawidłowy indeks: {idx}")
                return indices
            except Exception as e:
                print(f"Błąd: {e}")
                print("Spróbuj ponownie.")
                
    def showdown(self) -> Player:
        """Porównuje układy pozostałych graczy i zwraca zwycięzcę."""
        best_player = self.players[0]
        best_rank = self.hand_rank(best_player.hand)
        hand_ranking = ['High Card', 'One Pair', 'Two Pair', 'Three of a Kind', 'Straight',
                    'Flush', 'Full House', 'Four of a Kind', 'Straight Flush']
    
        for player in self.players[1:]: 
            rank = self.hand_rank(player.hand)
            if hand_ranking.index(rank) > hand_ranking.index(best_rank):
                best_player = player
                best_rank = rank

        return best_player
    def hand_rank(self, hand: List[Card]) -> str:
        """Ocena układu ręki w pokerze."""
        ranks = [card.rank for card in hand]
        suits = [card.suit for card in hand]

        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)

        is_straight = self.is_straight(ranks)

        is_flush = len(suit_counts) == 1

        if is_straight and is_flush:
            return 'Straight Flush'
        if 4 in rank_counts.values():
            return 'Four of a Kind'
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            return 'Full House'
        if is_flush:
            return 'Flush'
        if is_straight:
            return 'Straight'
        if 3 in rank_counts.values():
            return 'Three of a Kind'
        if list(rank_counts.values()).count(2) == 2:
            return 'Two Pair'
        if 2 in rank_counts.values():
            return 'One Pair'
        return 'High Card'

    def is_straight(self, ranks: List[str]) -> bool:
        """Sprawdza, czy karty są w stricie."""
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                    'J': 11, 'Q': 12, 'K': 13, 'A': 14}

        rank_ints = sorted([rank_values[rank] for rank in ranks])

        return rank_ints == list(range(rank_ints[0], rank_ints[0] + 5))
    
    def award_pot(self, winner: Player) -> None:
        winner.stack += self.pot
        self.pot = 0
if __name__ == "__main__":
    deck = Deck()

    player1 = Player(1000, "Anna")
    player2 = Player(1000, "Jan")
    players = [player1, player2]

    game = GameEngine(players, deck)

    game.play_round()

    for player in players:
        print(f"{player.name} stack: {player.get_stack_amount()}")