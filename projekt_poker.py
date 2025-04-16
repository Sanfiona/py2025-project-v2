import random

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
