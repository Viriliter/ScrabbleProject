const PlayerState = {
    UNDEFINED:      0,   // The player has not been initialized yet
    LOBBY_WAITING:  1,   // The player has entered lobby screen but not clicked the ready button yet
    LOBBY_READY:    2,   // After player has clicked the ready button on lobby screen
    WAITING_ORDER:  3,   // Player is waiting to be ordered 
    WAITING:        4,   // Player is waiting for its next turn to play
    PLAYING:        5,   // Player is playing its turn
    WON:            6,   // Player has won the game
    LOST:           7,   // Player has lost the game
};

const PlayerType = {
    UNDEFINED:  0,   // The player type is not been initialized yet
    COMPUTER:   1,   // Computer player type
    HUMAN:      2,   // Human player type
};

class Player {
    playerID = -1;
    playerName = '';
    playerType = PlayerType.UNDEFINED;
    isAdmin = false;
    playerState = PlayerState.UNDEFINED;
    orderLetter = null;
    points = 0;
    rack = null;


    constructor(playerID, playerName) {
        this.playerID = playerID;
        this.playerName = playerName;
        this.rack = [];
    }

    getPlayerID() {
        return this.playerID;
    }

    setPlayerID(playerID) {
        this.playerID = playerID;
    }

    getPlayerName() {
        return this.playerName;
    }

    setPlayerName(playerName) {
        this.playerName = playerName;
    }

    getPlayerType() {
        return this.playerType;
    }

    setPlayerType(playerType) {
        this.playerType = playerType;
    }

    getPlayerState() {
        return this.playerState;
    }

    setPlayerState(playerState) {
        this.playerState = playerState;
    }

    setAdmin() {
        this.isAdmin = true;
    }

    isAdmin() {
        return this.isAdmin;
    }

    getOrderLetter() {
        return this.orderLetter;
    }

    setOrderLetter(letter) {
        this.orderLetter = letter;
    }

    getPoints() {
        return this.points;
    }

    setPoints(points) {
        this.points = points;
    }

    getRack() {
        return this.rack;
    }

    setRack(rack) {
        this.rack = rack;
    }
}
