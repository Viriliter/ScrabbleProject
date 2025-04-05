
class PlayerType:
    UNDEFINED = "UNDEFINED"
    COMPUTER = "COMPUTER"
    HUMAN = "HUMAN"

class PlayerPrivileges:
    UNDEFINED = 0   # N/A
    ADMIN = 1       # ADMIN is the player who creates the game
    PLAYER = 2      # PLAYER is ordinary 
    REFEREE = 3     # REFEREE does not join the game just watches players' action

class PlayerState:
    UNDEFINED       = 0   # The player has not been initialized yet
    LOBBY_WAITING   = 1   # The player has entered lobby screen but not clicked the ready button yet
    LOBBY_READY     = 2   # After player has clicked the ready button on lobby screen
    WAITING_ORDER   = 3   # Player is entered the game but waiting to be ordered 
    WAITING         = 4   # Player is waiting for its next turn to play
    PLAYING         = 5   # Player is playing its turn
    WON             = 6   # Player has won the game
    LOST            = 7   # Player has lost the game

    @staticmethod
    def to_string(state: int) -> str:
        state_map = {
            PlayerState.UNDEFINED: "UNDEFINED",
            PlayerState.LOBBY_WAITING: "LOBBY_WAITING",
            PlayerState.LOBBY_READY: "LOBBY_READY",
            PlayerState.WAITING_ORDER: "WAITING_ORDER",
            PlayerState.WAITING: "WAITING",
            PlayerState.PLAYING: "PLAYING",
            PlayerState.WON: "WON",
            PlayerState.LOST: "LOST"
        }
        return state_map.get(state, "UNKNOWN_STATE")  # Handle unexpected values

class PlayerStrategy:
    UNDEFINED   = 0   # Undefined policy
    GREEDY      = 1   # The greedy policy
    BALANCED    = 2   # The balanced game strategy

    @staticmethod
    def to_string(state: int) -> str:
        state_map = {
            PlayerStrategy.UNDEFINED: "UNDEFINED",
            PlayerStrategy.GREEDY: "GREEDY",
            PlayerStrategy.BALANCED: "BALANCED",
        }
        return state_map.get(state, "UNKNOWN_STATE")  # Handle unexpected values
class GameState:
    UNDEFINED               = 0  # Initial state
    WAITING_FOR_PLAYERS     = 1  # Waiting for players to join the game
    PLAYER_ORDER_SELECTION  = 2  # Players are selecting the order of play
    GAME_STARTED            = 3  # Game has started
    GAME_OVER               = 4  # Game is over

    @staticmethod
    def to_string(state: int) -> str:
        state_map = {
            GameState.UNDEFINED: "UNDEFINED",
            GameState.WAITING_FOR_PLAYERS: "WAITING_FOR_PLAYERS",
            GameState.PLAYER_ORDER_SELECTION: "PLAYER_ORDER_SELECTION",
            GameState.GAME_STARTED: "GAME_STARTED",
            GameState.GAME_OVER: "GAME_OVER",
        }
        return state_map.get(state, "UNKNOWN_STATE")  # Handle unexpected values