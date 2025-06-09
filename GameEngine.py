from typing import List
from collections import Counter
from datetime import datetime
from session_manager import SessionManager
from poker import Player, Deck, Card

class InsufficientFundsError(Exception):
    pass

class GameEngine:
    def __init__(self, players: List[Player], deck: Deck, 
                 small_blind: int = 25, big_blind: int = 50, gui=None):
        self.players = players
        self.deck = deck
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.pot = 0
        self.game_id = str(datetime.now().timestamp())
        self.session_manager = SessionManager()
        self.current_bet = 0
        self.gui = gui
        
    def set_gui(self, gui):
        self.gui = gui

    def play_round(self) -> None:
        if self.gui:
            self.gui.update_gui_state("Starting new round!")
        print(f"\n=== Rozpoczynamy nową rundę gry! ===")
        
        for player in self.players:
            player.set_hand([])
            player.is_all_in = False
        self.deck = Deck()
        self.deck.shuffle()
        
        self.collect_blinds()
        self.deck.deal(self.players)

        if self.gui:
            self.gui.update_gui_state("Initial cards dealt.")
        print("\n--- Początkowe karty ---")
        for player in self.players:
            print(f"{player.name}: {player.cards_to_str()}")
        
        players_in_hand = self.betting_round()
        
        if not players_in_hand:
            message = "All players folded! Pot carries over to next round."
            if self.gui: self.gui.update_gui_state(message)
            print(message)
            return
            
        if len(players_in_hand) == 1:
            winner = players_in_hand[0]
            winner.stack += self.pot
            message = f"{winner.name} wygrywa {self.pot} żetonów (wszyscy inni spasowali)!"
            if self.gui: self.gui.update_gui_state(message)
            print(message)
            self.pot = 0
            return
        
        if self.gui: self.gui.update_gui_state("Exchanging cards...")
        print("\n--- Wymiana kart ---")
        for player in players_in_hand:
            if not player.is_bot:
                print(f"\n{player.name}, Twoje karty: {player.cards_to_str()}")
                indices = self.gui.get_player_exchange_input()
            else:
                indices = player.prompt_exchange_cards() 
            
            if indices:
                new_hand = self.exchange_cards(player, indices)
                player.set_hand(new_hand)
                print(f"Nowe karty: {player.cards_to_str()}")
        
        if self.gui: self.gui.update_gui_state("Final hands revealed.")
        print("\n--- Ostateczne karty ---")
        for player in players_in_hand:
            print(f"{player.name}: {player.cards_to_str()}")
        
        winners = self.showdown(players_in_hand)
        if winners:
            winnings, remainder = divmod(self.pot, len(winners))
            for i, winner in enumerate(winners):
                amount = winnings + (1 if i < remainder else 0)
                winner.stack += amount
                hand_rank_name = self.hand_rank(winner.get_player_hand())[1]
                message = f"\n{winner.name} wygrywa {amount} żetonów z układem: {hand_rank_name}!"
                if self.gui: self.gui.update_gui_state(message)
                print(message)
        else:
            message = "\nBrak zwycięzcy w tej rundzie!"
            if self.gui: self.gui.update_gui_state(message)
            print(message)
        
        self.pot = 0
        
        session_data = self.generate_session_data()
        self.session_manager.save_session(session_data)
        if self.gui: self.gui.update_gui_state(f"Game session {self.game_id} saved.")
        print(f"Sesja gry {self.game_id} została zapisana.")
        self.gui.update_gui_state("Round finished. Click 'Next Round' to play again.")
        self.gui.update_gui_state()

    def generate_session_data(self):
        return {
            "game_id": self.game_id,
            "timestamp": datetime.now().isoformat(),
            "players": [
                {"id": i, "name": p.name, "stack": p.stack}
                for i, p in enumerate(self.players)
            ],
            "hands": {
                str(i): [str(card) for card in p.get_player_hand()]
                for i, p in enumerate(self.players)
            },
            "pot": self.pot,
            "deck": [str(card) for card in self.deck.cards],
            "blinds": {"small_blind": self.small_blind, "big_blind": self.big_blind},
            "bets": [],
        }

    def collect_blinds(self) -> None:
        if self.gui: self.gui.update_gui_state("Collecting blinds...")
        print(f"\n--- Pobieranie blindów ---")
        
        if self.players[0].stack < self.small_blind:
            print(f"{self.players[0].name} doesn't have enough for small blind, going all-in.")
            self.pot += self.players[0].stack
            self.players[0].stack = 0
            self.players[0].is_all_in = True
        else:
            self.players[0].stack -= self.small_blind
            self.pot += self.small_blind
        self.players[0].bet_for_current_round = self.small_blind
        print(f"{self.players[0].name} płaci small blind: {self.small_blind}")

        if len(self.players) > 1:
            if self.players[1].stack < self.big_blind:
                print(f"{self.players[1].name} doesn't have enough for big blind, going all-in.")
                self.pot += self.players[1].stack
                self.players[1].stack = 0
                self.players[1].is_all_in = True
            else:
                self.players[1].stack -= self.big_blind
                self.pot += self.big_blind
            self.players[1].bet_for_current_round = self.big_blind
            print(f"{self.players[1].name} płaci big blind: {self.big_blind}")
        else:
            print("Not enough players for big blind.")
        
        self.current_bet = self.big_blind
        if self.gui: self.gui.update_gui_state()

    def betting_round(self) -> List[Player]:
        if self.gui: self.gui.update_gui_state("Starting betting round...")
        print(f"\n--- Runda zakładów ---")
        
        active_players_in_round = [p for p in self.players if p.stack > 0 or p.is_all_in]
        
        for player in active_players_in_round:
            player.bet_for_current_round = 0
            player.has_acted_this_cycle = False

        if len(self.players) > 0:
            self.players[0].bet_for_current_round = self.small_blind
        if len(self.players) > 1:
            self.players[1].bet_for_current_round = self.big_blind
            self.current_bet = self.big_blind
        elif len(self.players) == 1:
            self.current_bet = self.small_blind

        players_to_act_in_cycle = list(active_players_in_round) 
        last_raiser = None 

        while True:
            players_currently_acting = list(players_to_act_in_cycle)
            players_to_act_in_cycle = []

            if not players_currently_acting:
                break

            for player in players_currently_acting:
                if player not in active_players_in_round or player.stack == 0 and not player.is_all_in:
                    continue

                if player.is_all_in and player.bet_for_current_round < self.current_bet:
                    player.has_acted_this_cycle = True
                    continue

                if player.bet_for_current_round >= self.current_bet and player != last_raiser:
                    player.has_acted_this_cycle = True
                    continue
                
                amount_to_match = self.current_bet - player.bet_for_current_round
                
                min_raise_total = self.current_bet + self.big_blind 
                max_raise_total = player.stack + player.bet_for_current_round 

                if self.gui and not player.is_bot:
                    action, total_bet_amount = self.gui.get_player_bet_input(
                        self.current_bet, min_raise_total, max_raise_total
                    )
                else:
                    action, total_bet_amount = player.prompt_bet(
                        self.current_bet, min_raise_total, max_raise_total
                    )
                
                actual_bet_amount_for_this_action = total_bet_amount - player.bet_for_current_round

                if action == "fold":
                    if self.gui: self.gui.update_gui_state(f"{player.name} folds.")
                    if player in active_players_in_round:
                        active_players_in_round.remove(player)
                    player.has_acted_this_cycle = True
                elif action == "call":
                    payment = min(amount_to_match, player.stack)
                    player.stack -= payment
                    self.pot += payment
                    player.bet_for_current_round += payment
                    if player.stack == 0:
                        player.is_all_in = True
                        if self.gui: self.gui.update_gui_state(f"{player.name} calls {payment} and goes all-in.")
                    else:
                        if self.gui: self.gui.update_gui_state(f"{player.name} calls {payment}.")
                    player.has_acted_this_cycle = True
                elif action == "raise":
                    if total_bet_amount <= self.current_bet:
                        player.has_acted_this_cycle = False 
                        players_to_act_in_cycle.append(player) 
                        continue

                    if actual_bet_amount_for_this_action > player.stack:
                        total_bet_amount = player.stack + player.bet_for_current_round
                        actual_bet_amount_for_this_action = player.stack

                    payment = actual_bet_amount_for_this_action
                    player.stack -= payment
                    self.pot += payment
                    player.bet_for_current_round += payment
                    self.current_bet = player.bet_for_current_round

                    if player.stack == 0:
                        player.is_all_in = True
                        if self.gui: self.gui.update_gui_state(f"{player.name} raises to {total_bet_amount} and goes all-in.")
                    else:
                        if self.gui: self.gui.update_gui_state(f"{player.name} raises to {total_bet_amount}.")
                    
                    last_raiser = player
                    player.has_acted_this_cycle = True

                    for p in active_players_in_round:
                        if p != player and p.bet_for_current_round < self.current_bet and not p.is_all_in:
                            p.has_acted_this_cycle = False
                            players_to_act_in_cycle.append(p)
                        elif p.bet_for_current_round == self.current_bet and p.is_all_in: 
                            p.has_acted_this_cycle = True
                    break 

                if not player.has_acted_this_cycle:
                    players_to_act_in_cycle.append(player)

                if self.gui: self.gui.update_gui_state()

            # Only one player left
            if len(active_players_in_round) <= 1:
                break
            
            # All remaining players have matched the current bet or are all-in for less
            all_matched_or_all_in = True
            for p in active_players_in_round:
                if p.bet_for_current_round < self.current_bet and not p.is_all_in:
                    all_matched_or_all_in = False
                    break
            
            if all_matched_or_all_in and not players_to_act_in_cycle: 
                break
        
        return active_players_in_round


    def exchange_cards(self, player: Player, indices: List[int]) -> List[Card]:
        new_hand = list(player.get_player_hand())
        indices = sorted(set(indices), reverse=True)  
        
        for idx in indices:
            if 0 <= idx < len(new_hand):
                old_card = new_hand[idx]
                if self.deck.cards:
                    new_hand[idx] = self.deck.cards.pop()
                    self.deck.cards.append(old_card)
                else:
                    print(f"Brak kart w talii do wymiany dla {player.name}!")
                    break
            else:
                print(f"Nieprawidłowy indeks karty: {idx} dla {player.name}. Pomijam.")
        
        return new_hand

    def showdown(self, active_players: List[Player]) -> List[Player]:
        if self.gui: self.gui.update_gui_state("Showdown!")
        print("\n--- Showdown ---")
        
        player_ranks_detailed = []
        for player in active_players:
            hand = player.get_player_hand()
            rank_tuple = self.hand_rank(hand)
            player_ranks_detailed.append((rank_tuple, player))
            message = f"{player.name}: {player.cards_to_str()} - {rank_tuple[1]}"
            if self.gui: self.gui.update_gui_state(message)
            print(message)
        
        if not player_ranks_detailed:
            return []

        sortable_player_ranks = []
        for rank_tuple, player in player_ranks_detailed:
            rank_category_index = rank_tuple[0]
            tie_breaking_values = rank_tuple[2:]
            
            sort_key = (rank_category_index,) + tuple(-val for val in tie_breaking_values)
            sortable_player_ranks.append((sort_key, player))

        sortable_player_ranks.sort(key=lambda x: x[0])
        
        best_hand_key = sortable_player_ranks[0][0]
        winners = [player for sort_key, player in sortable_player_ranks if sort_key == best_hand_key]
        
        if len(winners) > 1:
            message = "\nTie between players:"
            if self.gui: self.gui.update_gui_state(message)
            print(message)
            for winner in winners:
                message = f"  - {winner.name}"
                if self.gui: self.gui.update_gui_state(message)
                print(message)
        
        return winners

    def get_card_value(self, rank: str) -> int:
        rank_values = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9,
                       '10':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        return rank_values.get(rank, 0)

    def hand_rank(self, hand: List[Card]) -> tuple:
        if not hand or len(hand) != 5:
            return (9, 'Invalid Hand')

        ranks = [card.rank for card in hand]
        suits = [card.suit for card in hand]
        
        rank_values_raw = [self.get_card_value(r) for r in ranks]
        rank_values_sorted = sorted(rank_values_raw, reverse=True)
        
        rank_counts = Counter(rank_values_raw)
        suit_counts = Counter(suits)
        
        is_flush = len(suit_counts) == 1
        is_straight = self.is_straight(ranks)

        hand_rankings_names = ['Straight Flush', 'Four of a Kind', 'Full House', 'Flush',
                                'Straight', 'Three of a Kind', 'Two Pair', 'One Pair', 'High Card']
        
        if is_straight and is_flush:
            return (hand_rankings_names.index('Straight Flush'), 'Straight Flush', rank_values_sorted[0])

        if 4 in rank_counts.values():
            quad_rank = [r for r, count in rank_counts.items() if count == 4][0]
            kicker = [r for r, count in rank_counts.items() if count == 1][0]
            return (hand_rankings_names.index('Four of a Kind'), 'Four of a Kind', quad_rank, kicker)

        if sorted(rank_counts.values()) == [2, 3]:
            trips_rank = [r for r, count in rank_counts.items() if count == 3][0]
            pair_rank = [r for r, count in rank_counts.items() if count == 2][0]
            return (hand_rankings_names.index('Full House'), 'Full House', trips_rank, pair_rank)

        if is_flush:
            return (hand_rankings_names.index('Flush'), 'Flush', *rank_values_sorted)

        if is_straight:
            return (hand_rankings_names.index('Straight'), 'Straight', rank_values_sorted[0])

        if 3 in rank_counts.values():
            trips_rank = [r for r, count in rank_counts.items() if count == 3][0]
            kickers = sorted([r for r, count in rank_counts.items() if count == 1 and r != trips_rank], reverse=True)
            return (hand_rankings_names.index('Three of a Kind'), 'Three of a Kind', trips_rank, *kickers)

        if list(rank_counts.values()).count(2) == 2:
            pairs = sorted([r for r, count in rank_counts.items() if count == 2], reverse=True)
            kicker = [r for r, count in rank_counts.items() if count == 1][0]
            return (hand_rankings_names.index('Two Pair'), 'Two Pair', pairs[0], pairs[1], kicker)

        if 2 in rank_counts.values():
            pair_rank = [r for r, count in rank_counts.items() if count == 2][0]
            kickers = sorted([r for r, count in rank_counts.items() if count == 1 and r != pair_rank], reverse=True)
            return (hand_rankings_names.index('One Pair'), 'One Pair', pair_rank, *kickers)

        return (hand_rankings_names.index('High Card'), 'High Card', *rank_values_sorted)

    def is_straight(self, ranks: List[str]) -> bool:
        rank_values = sorted(list(set(self.get_card_value(r) for r in ranks)))
        
        if len(rank_values) < 5:
            return False

        if set(rank_values) == {14, 2, 3, 4, 5}:
            return True
            
        for i in range(len(rank_values) - 4):
            if rank_values[i+4] - rank_values[i] == 4:
                return True
        return False