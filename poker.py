import random

class Card:
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663'}
       
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        
    def get_value(self):
        return (self.rank, self.suit)
    
    def __str__(self):
        return f"{self.rank}{Card.unicode_dict.get(self.suit, '?')}"

class Deck():
    def __init__(self, *args):
        suits = ['s', 'h', 'd', 'c']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
                
    def __str__(self):
        return ", ".join(str(card) for card in self.cards)
        
    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, players):
        for _ in range(5):  
            for player in players:
                if self.cards:
                    player.take_card(self.cards.pop())

class Player():
    def __init__(self, money, name=""):
        self.__stack_ = money
        self.__name_ = name
        self.__hand_ = []
        self.is_bot = False  # Added this line

    @property
    def name(self):
        return self.__name_
    
    @property
    def stack(self):
        return self.__stack_
    
    @stack.setter
    def stack(self, value):
        self.__stack_ = value

    def set_hand(self, new_hand):
        self.__hand_ = new_hand
        
    def take_card(self, card):
        self.__hand_.append(card)

    def get_stack_amount(self):
        return self.__stack_

    def change_card(self, card, idx):
        if 0 <= idx < len(self.__hand_):
            replaced_card = self.__hand_[idx]
            self.__hand_[idx] = card
            return replaced_card
        raise IndexError("Index out of range")

    def get_player_hand(self):
        return tuple(self.__hand_)

    def cards_to_str(self):
        return ", ".join(str(card) for card in self.__hand_)

    def prompt_bet(self, current_bet: int, min_raise: int, max_raise: int) -> tuple[str, int]:
        print(f"\n{self.name}, twój stack: {self.stack}")
        print(f"Aktualny zakład: {current_bet}")
        print(f"Opcje: fold, call, raise <kwota> (min: {min_raise}, max: {max_raise})")

        while True:
            action_input = input("Twoja decyzja: ").strip().lower()
            
            if action_input == "fold":
                return "fold", 0
                
            elif action_input == "call":
                call_amount = min(current_bet, self.stack)
                if self.stack > 0:
                    print(f"Sprawdzasz za {call_amount}.")
                    return "call", call_amount
                else:
                    print("Nie masz już żetonów! Pasujesz.")
                    return "fold", 0
                
            elif action_input.startswith("raise"):
                try:
                    parts = action_input.split()
                    if len(parts) < 2:
                        print("Nieprawidłowy format (np. 'raise 100')")
                        continue
                    amount = int(parts[1])
                    if amount < min_raise:
                        print(f"Minimalny raise: {min_raise}")
                    elif amount > max_raise:
                        print(f"Możesz podbić maksymalnie do {self.stack} (all-in)!")
                    else:
                        return "raise", amount
                except (IndexError, ValueError):
                    print("Nieprawidłowy format (np. 'raise 100')")
            else:
                print("Nieprawidłowa akcja. Dozwolone: fold, call, raise X")

    def prompt_exchange_cards(self) -> list[int]:
        while True:
            try:
                inp = input(f"{self.name}, wymień karty (indeksy 0-4, oddziel przecinkiem, enter dla braku wymiany): ").strip()
                if not inp:
                    return []
                    
                indices = [int(i.strip()) for i in inp.split(",") if i.strip()]
                
                if any(i < 0 or i > 4 for i in indices):
                    raise ValueError("Indeksy muszą być w zakresie 0-4")
                    
                if len(indices) > 5:
                    raise ValueError("Możesz wymienić maksymalnie 5 kart")
                    
                return indices
                
            except Exception as e:
                print(f"Błąd: {e}. Spróbuj ponownie.")

class BotPlayer(Player):
    def __init__(self, money, name="Bot"):
        super().__init__(money, name)
        self.is_bot = True

    def prompt_bet(self, current_bet: int, min_raise: int, max_raise: int) -> tuple[str, int]:
        print(f"\n{self.name} (Bot), twój stack: {self.stack}")
        print(f"Aktualny zakład: {current_bet}")

        possible_actions = ["fold"]
        
        if self.stack > 0:
            possible_actions.append("call")

        if min_raise <= max_raise:
            possible_actions.append("raise")
        
        chosen_action = random.choice(possible_actions)
        
        if chosen_action == "fold":
            print(f"{self.name} pasuje.")
            return "fold", 0
                
        elif chosen_action == "call":
            call_amount = min(current_bet, self.stack)
            if self.stack > 0:
                print(f"{self.name} sprawdza za {call_amount}.")
                return "call", call_amount
            else:
                print(f"{self.name} nie ma już żetonów i nie może sprawdzić. Pasuje.")
                return "fold", 0
                
        elif chosen_action == "raise":
            raise_amount = random.randint(min_raise, max_raise)
            print(f"{self.name} podbija do {raise_amount}.")
            return "raise", raise_amount

    def prompt_exchange_cards(self) -> list[int]:
        num_cards_to_exchange = random.randint(0, 3)
        if num_cards_to_exchange == 0:
            print(f"{self.name} nie wymienia kart.")
            return []
        else:
            indices = random.sample(range(5), num_cards_to_exchange)
            print(f"{self.name} wymienia karty o indeksach: {indices}.")
            return indices