import random
from typing import List

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
    def __init__(self, players: List[Player], deck: Deck, small_blind: int = 25, big_blind: int = 50):
        """Inicjalizuje graczy, talię, blindy i pulę."""
        self.players = players
        self.deck = deck
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.pot = 0
        
    def play_round(self) -> None:
        """Przeprowadza jedną rundę:
           1. Pobiera blindy
           2. Rozdaje karty
           3. Rundę zakładów
           4. Wymianę kart
           5. Showdown i przyznanie puli
        """
        self.collect_blinds()
        self.deck.shuffle()
        self.deck.deal(self.players)
        self.betting_round()

        for player in self.players:
            indices_to_exchange = self.prompt_exchange_cards(player) 
            self.exchange_cards(player, player.hand, indices_to_exchange)

        winner = self.showdown()
        self.award_pot(winner)

    def collect_blinds(self) -> None:
        self.players[0].stack -= self.small_blind
        self.players[1].stack -= self.big_blind
        self.pot += self.small_blind + self.big_blind

    def betting_round(self) -> None:
        current_bet = 0
        for player in list(self.players):
            action = self.prompt_bet(player, current_bet)
            if action == "fold":
                self.players.remove(player)

    
    def prompt_bet(self, player: Player, current_bet: int) -> str:
        """Pobiera akcję od gracza (human lub bot) — check/call/raise/fold."""
        return "check"
    
    def exchange_cards(self, player: Player, hand: List[Card], indices: List[int]) -> List[Card]:
        """Wymienia wskazane karty z ręki gracza, wkłada stare na spód talii."""
        try:
            for idx in indices:
                if not (0 <= idx < len(hand)):
                    raise ValueError("Nieprawidłowy indeks karty do wymiany.")

            if len(self.deck.cards) < len(indices):
                raise RuntimeError("Brak kart do wymiany w talii!")

            for idx in indices:
                old_card = player.change_card(self.deck.cards.pop(), idx)
                self.deck.cards.insert(0, old_card)  

        except Exception as e:
            print(f"Błąd wymiany kart: {e}")

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
        return max(self.players, key=lambda p:sum(ord(card.rank[0]) for card in p.hand))
    
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
        print(f"{player.name}'s hand: {player.cards_to_str()}")
        print(f"{player.name}'s stack: {player.get_stack_amount()}")

    print(f"Pula po rundzie: {game.pot}")
