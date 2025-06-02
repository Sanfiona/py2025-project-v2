import tkinter as tk
from tkinter import messagebox

class PokerGUI:
    def __init__(self, master, game_engine):
        self.master = master
        self.game_engine = game_engine
        master.title("Poker Game")
        master.geometry("800x600")

        self._player_action_var = tk.Variable()
        self._exchange_cards_var = tk.Variable()

        self.game_state_label = tk.Label(master, text="Welcome to Poker!", font=("Arial", 16))
        self.game_state_label.pack(pady=10)

        self.player_info_frames = {}
        for player in self.game_engine.players:
            frame = tk.LabelFrame(master, text=f"{player.name} (Stack: {player.stack})", padx=10, pady=10)
            frame.pack(pady=5, fill="x", padx=20)
            self.player_info_frames[player.name] = {
                "frame": frame,
                "hand_label": tk.Label(frame, text="Hand: "),
                "stack_label": tk.Label(frame, text=f"Stack: {player.stack}")
            }
            self.player_info_frames[player.name]["hand_label"].pack(side=tk.LEFT)
            self.player_info_frames[player.name]["stack_label"].pack(side=tk.RIGHT)

        self.pot_label = tk.Label(master, text=f"Pot: {self.game_engine.pot}", font=("Arial", 14))
        self.pot_label.pack(pady=5)
        
        self.current_bet_label = tk.Label(master, text=f"Current Bet: {self.game_engine.current_bet}", font=("Arial", 14))
        self.current_bet_label.pack(pady=5)

        self.action_frame = tk.Frame(master)
        self.action_frame.pack(pady=20)

        self.fold_button = tk.Button(self.action_frame, text="Fold", command=lambda: self.process_player_action("fold"))
        self.fold_button.pack(side=tk.LEFT, padx=5)

        self.call_button = tk.Button(self.action_frame, text="Call", command=lambda: self.process_player_action("call"))
        self.call_button.pack(side=tk.LEFT, padx=5)

        self.raise_button = tk.Button(self.action_frame, text="Raise", command=lambda: self.process_player_action("raise", self.raise_entry.get()))
        self.raise_button.pack(side=tk.LEFT, padx=5)
        
        self.raise_entry = tk.Entry(self.action_frame, width=10)
        self.raise_entry.pack(side=tk.LEFT, padx=5)
        self.raise_entry.bind("<Return>", lambda event: self.process_player_action("raise", self.raise_entry.get()))
        
        self.exchange_cards_frame = tk.Frame(master)
        self.exchange_cards_frame.pack(pady=10)
        self.exchange_labels = []
        self.exchange_vars = []
        for i in range(5):
            var = tk.IntVar()
            cb = tk.Checkbutton(self.exchange_cards_frame, text=f"Card {i+1}", variable=var)
            cb.pack(side=tk.LEFT, padx=2)
            self.exchange_labels.append(cb)
            self.exchange_vars.append(var)
        self.exchange_button = tk.Button(self.exchange_cards_frame, text="Exchange Selected", command=self.process_exchange)
        self.exchange_button.pack(side=tk.LEFT, padx=5)

        self.next_round_button = tk.Button(master, text="Next Round", command=self.start_next_round)
        self.next_round_button.pack(pady=10)
        
        self.update_gui_state()
        self.disable_action_buttons()
        self.disable_exchange_elements()
        self.next_round_button.config(state=tk.NORMAL)


    def update_gui_state(self, message=""):
        self.game_state_label.config(text=message)
        self.pot_label.config(text=f"Pot: {self.game_engine.pot}")
        self.current_bet_label.config(text=f"Current Bet: {self.game_engine.current_bet}")

        for player in self.game_engine.players:
            info_frame = self.player_info_frames[player.name]
            info_frame["stack_label"].config(text=f"Stack: {player.stack}")
            if not player.is_bot:
                 info_frame["hand_label"].config(text=f"Hand: {player.cards_to_str()}")
            else:
                 info_frame["hand_label"].config(text="Hand: [Hidden]")

        self.master.update_idletasks()

    def disable_action_buttons(self):
        self.fold_button.config(state=tk.DISABLED)
        self.call_button.config(state=tk.DISABLED)
        self.raise_button.config(state=tk.DISABLED)
        self.raise_entry.config(state=tk.DISABLED)

    def enable_action_buttons(self):
        self.fold_button.config(state=tk.NORMAL)
        self.call_button.config(state=tk.NORMAL)
        self.raise_button.config(state=tk.NORMAL)
        self.raise_entry.config(state=tk.NORMAL)

    def disable_exchange_elements(self):
        for cb in self.exchange_labels:
            cb.config(state=tk.DISABLED)
        self.exchange_button.config(state=tk.DISABLED)

    def enable_exchange_elements(self):
        for i, cb in enumerate(self.exchange_labels):
            cb.config(text=f"{self.game_engine.players[0].get_player_hand()[i]}", state=tk.NORMAL)
        self.exchange_button.config(state=tk.NORMAL)
        
    def show_raise_input(self):
        pass

    def get_player_bet_input(self, current_table_bet: int, min_raise_total: int, max_raise_total: int) -> tuple[str, int]:
        player = self.game_engine.players[0] # Human player
        amount_to_call = current_table_bet - player.bet_for_current_round
        
        self.enable_action_buttons()
        self.call_button.config(text=f"Call ({min(amount_to_call, player.stack)})")
        
        self.game_state_label.config(text=f"{player.name}, it's your turn. Your stack: {player.stack}. Current Bet: {current_table_bet}. Your contribution this round: {player.bet_for_current_round}.")
        self.master.wait_variable(self._player_action_var)
        action, amount = self._player_action_var.get()
        return action, amount

    def process_player_action(self, action_type, amount_str=None):
        player = self.game_engine.players[0]

        if action_type == "fold":
            self._player_action_var.set(("fold", 0))
        elif action_type == "call":
            amount_to_call = self.game_engine.current_bet - player.bet_for_current_round
            call_amount = min(amount_to_call, player.stack)
            self._player_action_var.set(("call", player.bet_for_current_round + call_amount)) # Return total amount
        elif action_type == "raise":
            try:
                requested_raise_total = int(amount_str) # This is the total bet amount
                
                min_raise_total = self.game_engine.current_bet + self.game_engine.big_blind
                max_raise_total = player.stack + player.bet_for_current_round

                if requested_raise_total < min_raise_total:
                    messagebox.showerror("Invalid Raise", f"Minimum raise is to {min_raise_total}")
                    return
                elif requested_raise_total > max_raise_total:
                    messagebox.showerror("Invalid Raise", f"You can bet a maximum of {max_raise_total} (all-in)!")
                    return
                
                self._player_action_var.set(("raise", requested_raise_total))
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for raise.")
                return
        self.disable_action_buttons()

    def get_player_exchange_input(self):
        self.enable_exchange_elements()
        self.game_state_label.config(text=f"{self.game_engine.players[0].name}, select cards to exchange.")
        for i, card_obj in enumerate(self.game_engine.players[0].get_player_hand()):
            self.exchange_labels[i].config(text=str(card_obj))
        self.master.wait_variable(self._exchange_cards_var)
        indices = self._exchange_cards_var.get()
        self.disable_exchange_elements()
        return indices

    def process_exchange(self):
        selected_indices = [i for i, var in enumerate(self.exchange_vars) if var.get() == 1]
        self._exchange_cards_var.set(selected_indices)
        for var in self.exchange_vars:
            var.set(0)

    def start_next_round(self):
        self.next_round_button.config(state=tk.DISABLED)
        
        for player in self.game_engine.players:
            if not player.is_bot:
                player.prompt_bet = self.prompt_human_bet
                player.prompt_exchange_cards = self.prompt_human_exchange_cards
        
        self.game_engine.play_round()
        self.update_gui_state("Round Over!")
        self.next_round_button.config(state=tk.NORMAL)


    def prompt_human_bet(self, current_table_bet: int, min_raise_total: int, max_raise_total: int) -> tuple[str, int]:
        self._player_action_var = tk.Variable()
        player = self.game_engine.players[0]
        amount_to_call = current_table_bet - player.bet_for_current_round
        
        self.current_bet_label.config(text=f"Current Bet: {current_table_bet}")
        self.update_gui_state(f"{player.name}, your stack: {player.stack}. Your contribution this round: {player.bet_for_current_round}.")
        self.update_gui_state(f"Opcje: fold, call ({min(amount_to_call, player.stack)}), raise <kwota> (min total bet: {min_raise_total}, max total bet (all-in): {max_raise_total})")
        
        self.enable_action_buttons()
        self.call_button.config(text=f"Call ({min(amount_to_call, player.stack)})")
        
        self.master.wait_variable(self._player_action_var)
        action, amount = self._player_action_var.get()
        return action, int(amount)

    def prompt_human_exchange_cards(self) -> list[int]:
        self._exchange_cards_var = tk.Variable()
        self.update_gui_state(f"{self.game_engine.players[0].name}, select cards to exchange.")
        self.enable_exchange_elements()
        self.master.wait_variable(self._exchange_cards_var)
        indices = self._exchange_cards_var.get()
        self.disable_exchange_elements()
        return indices