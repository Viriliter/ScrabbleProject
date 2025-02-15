const GameState = {
    UNDEFINED:               0,  // Initial state
    WAITING_FOR_PLAYERS:     1,  // Waiting for players to join the game
    PLAYER_ORDER_SELECTION:  2,  // Players are selecting the order of play
    GAME_STARTED:            3,  // Game has started
    GAME_OVER:               4   // Game is over
}

class Game {
    gameID = '';
    players = [];
    gameState = GameState.UNDEFINED;

    constructor(gameID) {
        this.gameID = gameID;
        this.players = [];
    }

    getGameID() {
        return this.gameID;
    }

    getGameState() {
        return this.gameState;
    }

    setGameState(state) {
        this.gameState = state;
    }

    addPlayers(player) {
        this.players.push(player);
    }
}
