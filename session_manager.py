import os
import json
class SessionManager:
    def __init__(self, data_dir: str = 'data', config_file: str = "config.json"):
        """Inicjalizuje katalog, w którym przechowywane będą pliki sesji."""
        self.data_dir = data_dir
        self.config_file = config_file
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)


    def save_session(self, session: dict) -> None:
        """Zapisuje stan gry i historię zakończonych rozdań do pliku."""
        game_id = session.get("game_id", "unknown")
        file_name = os.path.join(self.data_dir, f"session_{game_id}.json")
        try:
            with open(file_name, 'w') as file:
                json.dump(session, file, indent=4)
            print(f"Sesja gry {game_id} została zapisana do pliku {file_name}")
        except Exception as e:
            print(f"Nie udalo sie zapisac: {e}")


    def load_session(self, game_id: str) -> dict:
        """Ładuje sesję gry z pliku i zwraca strukturę pozwalającą na kontynuację rozgrywki."""
        file_name = os.path.join(self.data_dir, f"session_{game_id}.json")
        try:
            with open(file_name, 'r') as file:
                session = json.load(file)
            print(f"Sesja gry {game_id} zostala wczytana")
            return session
        except FileNotFoundError:
            print(f"Plik sesji {game_id} nie istnieje")
            return {}
        except json.JSONDecodeError:
            print(f"Błąd podczas dekodowania pliku sesji gry {game_id}.")
            return {}
        except Exception as e:
            print(f"Nie udało się wczytać sesji: {e}")
            return {}