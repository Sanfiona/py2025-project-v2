import random
from typing import List

class Card:
    # słownik symboli unicode
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663'}
       
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
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        self.cards = []
        for suit in self.suits:
            for rank in self.ranks:
                self.cards.append(rank + " of " + suit)
    def __str__(self):
    # TODO: definicja metody, przydatne do wypisywania karty
        return ",".join(self.cards)
        
    def shuffle(self):
    # TODO: definicja metody, tasowanie
       random.shuffle(self.cards) 

    def deal(self, players):
    # TODO: definicja metody, otrzymuje listę graczy i rozdaje im karty wywołując na nich metodę take_card z Player
        hands = {} 
        for pleyer in players: 
          hands[players] = []
        while self.cards:
            for player in players:
                if self.cards:
                    card = self.cards.pop(0)
                    player.take_card(card)
                    hands[players].append(card)
        return hands
          
class Player():

    def __init__(self, money, name=""):
        self.__stack_ = money
        self.__name_ = name
        self.__hand_ = []

    def take_card(self, card):
        self.__hand_.append(card)

    def get_stack_amount(self):
        return self.__stack_

    def change_card(self, card, idx):
    # TODO: przyjmuje nową kartę, wstawia ją za kartę o indeksie idx, zwraca kartę wymienioną
        if 0 <= idx < len(self.__hand_):
            replaced_card = self.__hand_[idx]
            self.__hand_[idx] = card
            return replaced_card
        else:
            raise IndexError("Index out of range")

    def get_player_hand(self):
        return tuple(self.__hand_)

    def cards_to_str(self):
    # TODO: definicja metody, zwraca stringa z kartami gracza
        return ",".join(self.__hand_)

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
        self.exchange_cards()
        winner = self.showdown()
        self.award_pot(winner)

    def collect_blinds(self) -> None:
        self.players[0].stack -= self.small_blind
        self.players[1].stack -= self.big_blind
        self.pot += self.small_blind + self.big_blind

    def betting_round(self) -> None:
        for player in self.players:
            action = self.prompt_bet(player)
            if action == "fold":
                self.players.remove(player)

    
    def prompt_bet(self, player: Player, current_bet: int) -> str:
        """Pobiera akcję od gracza (human lub bot) — check/call/raise/fold."""
        return "check"
    
    def exchange_cards(self, hand: List[Card], indices: List[int]) -> List[Card]:
        """Wymienia wskazane karty z ręki gracza, wkłada stare na spód talii."""
        try:
            if not all(0 <= idx < len(hand) for idx in indices):
                raise ValueError("Indeksy musza byc w zakresie 0-4!")
            
            if len(self.deck.cards) < len(indices):
                raise RuntimeError("Brak wystarczajacej liczby kart w talii!")

            new_cards = [self.deck.cards.pop() for i in indices]

            self.deck.cards.extend(hand[index] for index in indices)

            for index, new_card in zip(indices, new_cards):
                hand[index] = new_card

            return hand  

        except ValueError as ve:
            print(f"Błąd: {ve}")
            return hand 

        except RuntimeError as re:
            print(f"Błąd: {re}")
            return hand  # 
    
    def showdown(self) -> Player:
        """Porównuje układy pozostałych graczy i zwraca zwycięzcę."""
        return max(self.players, key=lambda p:sum(ord(card.rank[0]) for card in p.hand))
    
    def award_pot(self, winner: Player) -> None:
        winner.stack += self.pot
        self.pot = 0