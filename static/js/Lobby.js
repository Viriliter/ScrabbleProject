let myGame = null
let myPlayer = null
let playersMeta = null;

function openSettings() {
}

function openAbout() {
}

function navigateToNewGameStack() {
    document.getElementById('selectionStackItem').style.visibility = 'hidden';
    document.getElementById('newGameStackItem').style.visibility = 'visible';
    document.getElementById('joinLobbyStackItem').style.visibility = 'hidden';
    document.getElementById('lobbyStackItem').style.visibility = 'hidden';
}

function navigateToJoinLobbyStack() {
    document.getElementById('selectionStackItem').style.visibility = 'hidden';
    document.getElementById('newGameStackItem').style.visibility = 'hidden';
    document.getElementById('joinLobbyStackItem').style.visibility = 'visible';
    document.getElementById('lobbyStackItem').style.visibility = 'hidden';
}

function navigateToLobbyStack() {
    document.getElementById('selectionStackItem').style.visibility = 'hidden';
    document.getElementById('newGameStackItem').style.visibility = 'hidden';
    document.getElementById('joinLobbyStackItem').style.visibility = 'hidden';
    document.getElementById('lobbyStackItem').style.visibility = 'visible';
}

function updateLobby(playersMeta_) {
    console.log('lobby updating...', playersMeta_);

    if (!playersMeta_ || playersMeta_.length === 0) {
        return;
    }

    const lobbyPlayerList = document.getElementById('lobbyPlayerList');
    lobbyPlayerList.innerHTML = ''; // Clear contents

    const fragment = document.createDocumentFragment();

    playersMeta_.forEach((player_, index) => {
        const playerContainer = document.createElement('div');
        playerContainer.classList.add('container-lobby');

        const playerIndex = document.createElement('span');
        playerIndex.style.margin = '10px';
        playerIndex.textContent = `${index + 1}`;

        const playerName = document.createElement('span');
        playerName.style.margin = '10px';
        playerName.textContent = player_.PLAYER_NAME ? player_.PLAYER_NAME : 'Waiting Player to Join';

        playerContainer.appendChild(playerIndex);
        playerContainer.appendChild(playerName);

        console.log(player_.PLAYER_STATE);

        if (player_.IS_ADMIN) {
            const adminIndicator = document.createElement('span');
            adminIndicator.style.margin = '10px';
            adminIndicator.style.color = 'yellow';
            adminIndicator.textContent = '★';
            adminIndicator.title = 'Admin';
            playerContainer.appendChild(adminIndicator);
        }

        if (player_.PLAYER_STATE == PlayerState.LOBBY_READY) {
            const readyIndicator = document.createElement('span');
            readyIndicator.style.margin = '10px';
            readyIndicator.style.background = 'var(--cell-color)';
            readyIndicator.style.color = 'var(--text-color)';
            readyIndicator.textContent = 'READY';
            playerContainer.appendChild(readyIndicator);
        }

        fragment.appendChild(playerContainer);
    });

    lobbyPlayerList.appendChild(fragment); // Batch update for performance
}

function collectPlayerTypes() {
        const playerTypes = [];
        const playerTypeIds = ['dropdownPlayerType1', 'dropdownPlayerType2', 'dropdownPlayerType3', 'dropdownPlayerType4'];

        playerTypeIds.forEach(id => {
            const playerTypeElement = document.getElementById(id);
            if (playerTypeElement && playerTypeElement.textContent.trim() !== 'EMPTY') {
                playerTypes.push(playerTypeElement.textContent.trim());
            }
        });

        return playerTypes;
}

function createNewGame() {
    
    const playerTypes = collectPlayerTypes();
    const playerName = document.getElementById('inputPlayerName').value;

    if (playerTypes.length <= 1) {
        alert('Minimum number of player should be 2!');
        return;
    }

    if (playerTypes[0] === 'HUMAN' && playerName === '') {
        alert('Enter a Username');
        return;
    }

    const playerTypesJson = JSON.stringify(playerTypes);

    fetch('/create-new-game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: playerTypesJson
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data.status === 'success') {
            if (myGame !== null) {
                alert('Cannot create a new game again!')
                return false;
            }

            myGame = new Game(data.gameID);
            myPlayer = new Player(data.playerID, '');
            myPlayer.setPlayerType(playerTypes[0]=='HUMAN'? PlayerType.HUMAN: PlayerType.COMPUTER)
            if (data.isAdmin) myPlayer.setAdmin();

            document.getElementById('gameIDSpan').textContent = myGame.getGameID();
            document.getElementById('gameIDHeader').style.visibility = 'visible';
            
            playersMeta = data.playersMeta;
            updateLobby(playersMeta)

            if (myPlayer.getPlayerType() == PlayerType.HUMAN) {
                myPlayer.setPlayerName(playerName);
                setPlayerName(myGame.getGameID(), myPlayer.getPlayerID(), myPlayer.getPlayerName());   
                navigateToLobbyStack();
            } else if (myPlayer.getPlayerType() == PlayerType.COMPUTER) {
                enterGame();
            }
            
            return true;
        } else {
            alert('Unknown error: ' + data.message);
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        return false;
    });
}

function setPlayerName(gameID, playerID, playerUsername) {
    fetch('/set-player-name', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body:  JSON.stringify({ "gameID": gameID, "playerID": playerID, "playerName": playerUsername })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            myPlayer.setPlayerName(data.playerUsername)
        } else {
            alert('Unknown error: ' + data.message);
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        return false;
    });
}

function joinGame() {
    in_gameID = document.getElementById('inputGameID').value;
    in_playerName = document.getElementById('inputJoinPlayerName').value;   

    if (in_gameID == '') {
        alert('Enter a Game ID');
        return;
    }

    if (in_playerName == '') {
        alert('Enter a Username');
        return;
    }

    fetch('/join-game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body:  JSON.stringify({ "gameID": in_gameID, "playerType": "HUMAN"})
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response from server:', data);
        if (data.status === 'success') {
            const baseUrl = window.location.origin;
            if (myGame !== null) {
                alert('Cannot join the game!')
                return false;
            }

            myGame = new Game(data.gameID);
            myPlayer = new Player(data.playerID, '')

            document.getElementById('gameIDSpan').textContent = myGame.getGameID();
            document.getElementById('gameIDHeader').style.visibility = 'visible';

            playersMeta = data.playersMeta;
            updateLobby(playersMeta)

            myPlayer.setPlayerName(in_playerName);
            setPlayerName(myGame.getGameID(), myPlayer.getPlayerID(), myPlayer.getPlayerName());

            navigateToLobbyStack();
            return true;
        } else {
            alert('Unknown error: ' + data.message);
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        return false;
    });
}

function enterGame() {
    fetch('/enter-game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'gameID': myGame.getGameID(), 'playerID': myPlayer.getPlayerID()})
    })
    .then(response => {
        if (response.redirected) {
            // Handle redirection
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        // Handle the response data
        if (data && data.status !== 'success') {
            alert('Cannot enter the game: ' + data.message);
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        return false;
    });
}
