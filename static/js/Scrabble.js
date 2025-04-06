/** @type {Game} */
let myGame = null;
/** @type {Player} */
let myPlayer = null;
/** @type {number} */
let currentPlayerID = null;
/** @type {Object<string, any>} */
let playersMeta = null;

/** @type {GameState} */
let oldGameState = null;

let selectedTiles = [];
let tileCounter = 0; // Initialize a counter for the tiles

// Create the tile element
function createTile(letter, id=-1, isJoker='false', location='') {
    const tile = document.createElement('div');
    tile.classList.add('tile');
    tile.textContent = letter;  // Only the letter is shown on the tile
    tile.setAttribute('value', letter); // Set value of tile
    tile.setAttribute('location', location); // Set the location attribute
    tile.setAttribute('isJoker', letter === ' ' || isJoker==='true' ? true : false);
    tile.style.position = 'relative';
    
    // If no ID is provided, assign a new one
    if (id === -1) {
        id = tileCounter++;
    }
    tile.setAttribute('tileID', id); // Set the unique identifier attribute

    // Add a span to display the points
    const pointsSpan = document.createElement('span');
    pointsSpan.classList.add('points');
    pointsSpan.textContent = tile.getAttribute('isJoker')=='true' ? 0: letterPoints.get(letter);;
    tile.appendChild(pointsSpan);

    tile.addEventListener('mousedown', mouseDownHandler);
    tile.addEventListener('click', clickHandler);

    return tile;
}

// Mouse event handlers

function mouseDownHandler(event) {
    let tile = event.target;
    if (!tile.classList.contains('tile')) {
        tile = tile.closest('.tile');
    }
    if (tile) {
        tile.classList.add('dragging-tile'); // Add dragging class
        tile.classList.remove('placed-tile'); // Remove placed-tile class

        document.addEventListener('mousemove', mouseMoveHandler);
    }
}

function mouseMoveHandler(event) {
    const tile = document.querySelector('.dragging-tile');
    if (tile) {
        tile.style.position = 'fixed';
        tile.style.left = `${event.pageX+2}px`;
        tile.style.top = `${event.pageY+2}px`;
        tile.style.zIndex = 1000; // Bring the tile to the front
    }
    document.addEventListener('mouseup', mouseUpHandler);
}

function checkBoardZone(target) {
    if (target.classList.contains('transparent-cell')) {
        
        if (target.getAttribute('location')==='') {
            if (target.hasChildNodes()) {
                const child = target.firstChild;
                if (child.classList.contains('dragging-tile')) {
                    return true;
                }
            }
            return false;
        }
        else return true;
    }
    else return false;
}

function mouseUpHandler(event) {
    const tile = document.querySelector('.dragging-tile');

    if (tile) {
        let dropTarget = event.target;

        if (!tile.hasChildNodes()) return;

        let letter = tile.firstChild.textContent; // Only the letter, without any span
        const tileID = tile.getAttribute('tileID');
        const isJoker = tile.getAttribute('isJoker');
        
        if (tileID === null) {
            tileID = tileCounter++;
        }

        if (isJoker==='true') {
            tile.setAttribute('value', ' ');
            letter = ' ';
        }

        const parentNode = tile.parentNode;

        // Check if the drop target is a tile if it is return the tile to the rack
        if (dropTarget.classList.contains('tile') || !checkBoardZone(dropTarget)) {
            console.log('Place is already occupied. Returning tile to rack.');

            // Remove the original tile from the scrabble rack
            if (parentNode.contains(tile)) {
                parentNode.removeChild(tile);
            }

            const returnTile = createTile(letter, tileID, isJoker);  // Create the tile again

            const scrabbleRack = document.getElementById('scrabbleRack');
            scrabbleRack.appendChild(returnTile);

            removeSelectedTile(tileID);
            verifyWord(selectedTiles);

        } else if (checkBoardZone(dropTarget)) {  // Check if the drop target is a valid cell on the game board
            console.log('Tile placed successfully');

            const cellLocation = dropTarget.getAttribute('location').split('_')[1];

            // Create a new tile and add it to the drop target
            const newTile = createTile(letter, tileID, isJoker, cellLocation);
            dropTarget.innerHTML = '';  // Clear the cell
            dropTarget.appendChild(newTile);  // Place the tile on the board
            
            // Remove the original tile from the scrabble rack
            if (parentNode.contains(tile)) parentNode.removeChild(tile);

            newTile.classList.add('placed-tile'); // Add placed-tile class
            // If tile is joker open joker selection dialog, otherwise varify the word.
            if (isJoker==='true') {
                showJokerTileDialog(newTile);
            } else {
                addSelectedTile(letter, tileID, isJoker, cellLocation);
                verifyWord(selectedTiles);
            }
            
        } else if (dropTarget.classList.contains('rack')) {  // Check if the drop target is the scrabble rack
            console.log('Tile placed rack');

            // Create a new tile and add it to the drop target
            const newTile = createTile(letter, tileID, isJoker);
            dropTarget.appendChild(newTile);  // Place the tile on the board
            
            // Remove the original tile from the scrabble rack
            parentNode.removeChild(tile);

            removeSelectedTile(tileID);
            verifyWord(selectedTiles);

        } else {  // If not a valid drop, return the tile to the rack
            console.log('Invalid drop location. Returning tile to rack.');

            // Remove the original tile from the scrabble rack
            if (parentNode.contains(tile)) {
                parentNode.removeChild(tile);
            }

            const returnTile = createTile(letter, tileID, isJoker);  // Create the tile again
            const scrabbleRack = document.getElementById('scrabbleRack');    
            scrabbleRack.appendChild(returnTile);

            removeSelectedTile(tileID);
            verifyWord(selectedTiles);
        }

        tile.classList.remove('dragging-tile'); // Remove dragging-tile class
    }

    document.removeEventListener('mousemove', mouseMoveHandler);
    document.removeEventListener('mouseup', mouseUpHandler);
}

function clickHandler(event) {
    const tile = event.target;
    if (!tile.classList.contains('tile')) {
    }
}

function addSelectedTile(letter, tileID, isJoker, location) {
    const existingTile = selectedTiles.find(t => t.tileID === tileID);
    if (existingTile) {
        // Update the location if the tile is already placed
        existingTile.location = location;
    } else {
        // Add the new tile to the selectedTiles array
        selectedTiles.push({tileID, letter, location, isJoker});
    }
}

function clearSelectedTile() {
    selectedTiles = []
}

function removeSelectedTile(tileID) {
    selectedTiles = selectedTiles.filter(t => t.tileID !== tileID);
}

function verifyWord(tiles) {
    if (!tiles || tiles.length === 0) {
        return;
    }

    console.log('Verifying word...');
    tiles.forEach((letter, tileID, location) => {
        console.log(letter, tileID, location);
    });

    const tilesJson = JSON.stringify(tiles);

    fetch(`${window.location}/verify-word`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: tilesJson
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update the points box with the calculated points
            if (data.points>0) {
                updateTentativePoints(data.points)
            } else {
                updateTentativePoints(0);  // This will clear tentative points
            }
        } else {
            updateTentativePoints(0);  // This will clear tentative points
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
    });
}

function fetchPlayerName(playerID) {
    fetch(`${window.location}/get-player-name`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log(`Player Name: ${data.playerName}`);
            if (data.playerName !== null) {
                myPlayer = new Player(playerID, data.playerName);
            }
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
    });
}

function loadJokerTileSelector(myTile) {
    // Generate tiles for all English letters
    const jokerTilesContainer = document.getElementById('jokerTilesContainer');
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    let selectedJokerTile = null;

    jokerTilesContainer.innerHTML = '';
    
    for (let letter of letters) {
        const tile = document.createElement('div');
        tile.className = 'joker-tile-selector-tile';
        tile.textContent = letter;
        tile.dataset.letter = letter;
        tile.dataset.points = letterPoints.get(letter);
        tile.dataset.isJoker = true;
        tile.dataset.id = myTile.getAttribute('tileID');
        tile.dataset.location = myTile.getAttribute('location');
        
        tile.addEventListener('click', function() {
            if (selectedJokerTile) {
                selectedJokerTile.classList.remove('selected');
                document.querySelectorAll('.joker-tile-selector-tile').forEach(t => t.classList.remove('unselected'));
            } 
            
            if (selectedJokerTile !== this) {
                this.classList.add('joker-tile-selector');
                document.querySelectorAll('.joker-tile-selector-tile').forEach(t => {
                    if (t !== this) t.classList.add('unselected');
                });
                selectedJokerTile = this
            } else {
                selectedJokerTile = null
            }
        });
        
        jokerTilesContainer.appendChild(tile);
    }
    
    // Select button functionality
    document.querySelector('.joker-tile-selector-choose-btn').addEventListener('click', function() {
        if (myTile===null) return;
    
        if (selectedJokerTile!==null) {
            myTile.textContent = selectedJokerTile.dataset.letter;
            myTile.setAttribute('value', selectedJokerTile.dataset.letter);
            myTile.style.position = 'relative'; 

            const pointsSpan = document.createElement('span');
            pointsSpan.classList.add('points');
            pointsSpan.textContent = '0';
            myTile.appendChild(pointsSpan);

            myTile.addEventListener('mousedown', mouseDownHandler);
            myTile.addEventListener('click', clickHandler);

            const dialog = document.getElementById('myJokerDialog');
            dialog.close();
            addSelectedTile(myTile.getAttribute('value'), myTile.getAttribute('tileID') , myTile.getAttribute('isJoker'), myTile.getAttribute('location'));

            verifyWord(selectedTiles);
        } else {
            myTile.textContent = ' ';
            myTile.setAttribute('value', ' ');
            myTile.style.position = 'relative'; 

            const pointsSpan = document.createElement('span');
            pointsSpan.classList.add('points');
            pointsSpan.textContent = '0';
            myTile.appendChild(pointsSpan);

            myTile.removeEventListener('mousedown', mouseDownHandler);
            myTile.removeEventListener('click', clickHandler);

            alert('Please select a letter first');
        }    
    });

}

function loadExchangeLetterSeclector() {
    const scrabbleRack = document.getElementById('scrabbleRack');
    const tilesInRack = scrabbleRack.querySelectorAll('.tile');

    // Generate tiles for all letters available in the rack
    const exchangeLetterContainer = document.getElementById('exchangeLetterContainer');
    let selectedExchangeTile = null;

    exchangeLetterContainer.innerHTML = '';
    
    for (let tileInRack of tilesInRack) {
        const pointSpan = tileInRack.querySelector('.points');
        const letter = tileInRack.getAttribute('value');
        const points = pointSpan ? pointSpan.textContent : '0';
        const isJoker = tileInRack.getAttribute('isJoker');

        const tile = document.createElement('div');
        tile.className = 'exchange-letter-selector-tile';
        tile.textContent = letter;

        tile.dataset.letter = letter;
        tile.dataset.points = points;
        tile.dataset.isJoker = isJoker;
        tile.style.position = 'relative'; 

        tile.addEventListener('click', function() {
            if (selectedExchangeTile) {
                selectedExchangeTile.classList.remove('selected');
                document.querySelectorAll('.exchange-letter-selector-tile').forEach(t => t.classList.remove('unselected'));
            } 
            
            if (selectedExchangeTile !== this) {
                this.classList.add('exchange-letter-selector');
                document.querySelectorAll('.exchange-letter-selector-tile').forEach(t => {
                    if (t !== this) t.classList.add('unselected');
                });
                selectedExchangeTile = this
            } else {
                selectedExchangeTile = null
            }
        });
        
        exchangeLetterContainer.appendChild(tile);
    }
    
    // Close button functionality
    document.querySelector('.exchange-letter-selector-close-btn').addEventListener('click', function() {
        const dialog = document.getElementById('myExchangeDialog');
        dialog.close();
    });

    // Select button functionality
    document.querySelector('.exchange-letter-selector-choose-btn').addEventListener('click', function() {
        if (selectedExchangeTile!==null) {
            const letter = selectedExchangeTile.dataset.letter;
            console.log('letter   :::::: ' + letter);
            const dialog = document.getElementById('myExchangeDialog');
            dialog.close();
            exchangeLetter(letter);
        } else {
            alert('Please select a letter first');
        }    
    });
}

// User actions

function showJokerTileDialog(tile) {
    loadJokerTileSelector(tile)

    dialog = document.getElementById('myJokerDialog');
    dialog.showModal();  // Opens the dialog as a modal
}

function showExchangeLetterDialog() {
    revertTiles();

    loadExchangeLetterSeclector();

    dialog = document.getElementById('myExchangeDialog');
    dialog.showModal();  // Opens the dialog as a modal
}

function showHint() {
    if (myPlayer === null) return;

    if (myPlayer.getPlayerState() !== PlayerState.PLAYING) return;

    

    const lettersJson = JSON.stringify(myPlayer.getRack());

    fetch(`${window.location}/request-hint`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: lettersJson
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Hint: ' + data.hint);
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
    });
}

function requestUpdate() {
    console.log('request update...');
    fetch(`${window.location}/request-update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {})
    .catch(error => {
        console.error('Error:', error);
    });

}

function quitGame() {
    fetch(`${window.location}/quit-game`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'playerID': myPlayer.getPlayerID()})
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
            alert('Cannot quit from the game: ' + data.message);
            return false;
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
        return false;
    });
}

function requestOrder() {
    console.log('request order...');
    fetch(`${window.location}/request-order`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            if (myPlayer !== null) {
                myPlayer.setOrderLetter(data.letter);

                const playerOrderDiv = document.getElementById('playerOrderDiv');
                const rackDiv = document.getElementById('rackDiv');
                const orderTileDiv = document.getElementById('orderTileDiv');

                const tile = createTile(data.letter);
                tile.classList.add('blocked');
                orderTileDiv.appendChild(tile);

                playerOrderDiv.style.visibility = 'collapse';
                rackDiv.style.visibility = 'visible';
                orderTileDiv.style.visibility = 'collapse';
            }
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
    });
}

function requestRack() {
    console.log('request rack...');
    fetch(`${window.location}/request-rack`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            if (myPlayer !== null) {
                updateMyRack(data.rack);
            }
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
    });
}

function exchangeLetter(letter) {
    console.log('exchange tile...');
    fetch(`${window.location}/exchange-letter`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'letter': letter})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            if (myPlayer !== null) {
                requestRack();
            }
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
    });
}

function revertTiles() {
    const scrabbleRack = document.getElementById('scrabbleRack');

    const placedTiles = document.querySelectorAll('.placed-tile');

    placedTiles.forEach(tile => {
        // Remove the tile from the board
        tile.parentElement.removeChild(tile);

        if (tile.getAttribute('isJoker')==='true') {
            tile.textContent = ' ';
            tile.setAttribute('value', ' ');
            tile.style.position = 'relative'; 

            const pointsSpan = document.createElement('span');
            pointsSpan.classList.add('points');
            pointsSpan.textContent = '0';
            tile.appendChild(pointsSpan);
        }

        // Optionally, return the tile to the player's rack
        scrabbleRack.appendChild(tile);

        // Remove the 'placed-tile' class to reset the tile state
        tile.classList.remove('placed-tile');

        updateTentativePoints(0);  // This will clear tentative points
    });

    selectedTiles = [];
}

function shuffleTiles() {
    const scrabbleRack = document.getElementById('scrabbleRack');
    const tiles = Array.from(scrabbleRack.children);

    // Shuffle the tiles array
    for (let i = tiles.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [tiles[i], tiles[j]] = [tiles[j], tiles[i]];
    }
    
    // Clear the scrabbleRack and append the shuffled tiles
    scrabbleRack.innerHTML = '';
    tiles.forEach(tile => scrabbleRack.appendChild(tile));
}

function skipTurn() {
    fetch(`${window.location}/skip-turn`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'gameID': myGame.getGameID(), 'playerID': myPlayer.getPlayerID()})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {

        } else {
            alert('Unknown error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
    });
}

function submitWord(tiles=[]) {
    if (myPlayer === null) return;

    if (myPlayer.getPlayerState() !== PlayerState.PLAYING) return;

    const tilesJson = JSON.stringify(tiles);

    fetch(`${window.location}/submit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: tilesJson
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update the points box with the calculated points
            if (data.points>0) {
                document.getElementById('remainingTiles').textContent = data.points;
                updateTentativePoints(0);  // This will clear tentative points
                clearSelectedTile();
            } else {
                alert('Word verification failed!');
            }
        } else {
            updateTentativePoints(0);  // This will clear tentative points
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Unknown Error:', error);
    });
}

// Frontend updates

function updateTentativePoints(points) {
    if (points === null || points === 0) document.getElementById('tentativePoints').textContent = '';
    else document.getElementById('tentativePoints').textContent = ` (${points})`;
}

function updateCurrentPlayerID(playersMeta_) {
    playersMeta_.forEach((player_, index) => {
        if (player_.PLAYER_STATE === PlayerState.PLAYING) {
            currentPlayerID = player_.PLAYER_ID;
        }
    });
}

function updateLeaderboard(playersMeta_) {
    console.log('leaderboard updating...', playersMeta_);
    if (!playersMeta_ || playersMeta_.length === 0) {
        return;
    }

    const tableLeaderboard = document.getElementById('tableLeaderboard');
    tableLeaderboard.innerHTML = ''; // Clear contents

    const fragment = document.createDocumentFragment();

    playersMeta_.forEach((player_, index) => {
        const playerContainer = document.createElement('div');
        playerContainer.classList.add('player-item');

        if (player_.IS_ADMIN) {
            const adminIndicator = document.createElement('span');
            adminIndicator.style.margin = '10px';
            adminIndicator.style.color = 'yellow';
            adminIndicator.textContent = '★';
            adminIndicator.title = 'Admin';
            playerContainer.appendChild(adminIndicator);
        } else {
            const adminIndicator = document.createElement('span');
            adminIndicator.style.margin = '10px';
            adminIndicator.style.color = 'yellow';
            adminIndicator.textContent = ' ';
            adminIndicator.title = ' ';
            playerContainer.appendChild(adminIndicator);
        }

        const playerName = document.createElement('span');
        playerName.style.margin = '10px';
        playerName.textContent = player_.PLAYER_NAME;
        playerContainer.appendChild(playerName);

        const playerPoint = document.createElement('span');
        playerPoint.style.margin = '10px';
        playerPoint.textContent = player_.PLAYER_POINTS;
        playerContainer.appendChild(playerPoint);

        if (player_.PLAYER_STATE === PlayerState.WAITING) {
            const stateIndicator = document.createElement('span');

            stateIndicator.style.margin = '10px';
            stateIndicator.style.background = 'transparent';
            stateIndicator.style.color = 'var(--text-color)';

            playerContainer.appendChild(stateIndicator);
        } else if (player_.PLAYER_STATE === PlayerState.PLAYING) {
            const stateIndicator = document.createElement('span');
            stateIndicator.innerHTML = " \
                <svg class=\"w-6 h-6 text-gray-800 dark:text-white\" aria-hidden=\"true\" xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 24 24\"> \
                    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z\"/> \
                </svg> \
            "

            stateIndicator.style.margin = '10px';
            stateIndicator.style.background = 'transparent';
            stateIndicator.style.color = 'var(--text-color)';
            stateIndicator.title = 'Waiting player to finish the move';

            playerContainer.appendChild(stateIndicator);
        } else if (player_.PLAYER_STATE === PlayerState.WIN) {

            
        } else if (player_.PLAYER_STATE === PlayerState.LOST) {
            playerName.style.textDecoration = 'line-through';
            playerName.setAttribute('title', 'LOST');
        } else {

        }

        if (myPlayer !== null && myPlayer.getPlayerID() === player_.PLAYER_ID) {
            playerName.style.fontWeight = 'bold';
            playerContainer.style.border = '2px solid white'
        }

        fragment.appendChild(playerContainer);
    });

    tableLeaderboard.appendChild(fragment); // Batch update for performance
}

function updateMyPlayer(playersMeta_) {
    if (!playersMeta_ || playersMeta_.length === 0) {
        return;
    }

    playersMeta_.forEach((player_, index) => {
        if (myPlayer !== null && myPlayer.getPlayerID() === player_.PLAYER_ID) {
            
            requestRack();
            myPlayer.setPlayerState(player_.PLAYER_STATE)
            myPlayer.setPoints(player_.PLAYER_POINTS)

            // Update player control areas according to its state
            const returnLobbyButton = document.getElementById('returnLobbyButton');
            const requestOrderButton = document.getElementById('requestOrderButton');
            const exchangeButton = document.getElementById('exchangeButton');
            const revertButton = document.getElementById('revertButton');
            const hintButton = document.getElementById('hintButton');
            const shuffleButton = document.getElementById('shuffleButton');
            const skipTurnButton = document.getElementById('skipTurnButton');
            const submitButton = document.getElementById('submitButton');

            const scrabbleRack = document.getElementById('scrabbleRack');

            if (myPlayer.getPlayerState() != PlayerState.PLAYING) {
                requestOrderButton.classList.add('blocked');
                exchangeButton.classList.add('blocked');
                revertButton.classList.add('blocked');
                hintButton.classList.add('blocked');
                skipTurnButton.classList.add('blocked');
                scrabbleRack.classList.add('blocked');
                submitButton.classList.add('blocked');
            } else {
                requestOrderButton.classList.remove('blocked');
                exchangeButton.classList.remove('blocked');
                revertButton.classList.remove('blocked');
                hintButton.classList.remove('blocked');
                skipTurnButton.classList.remove('blocked');
                scrabbleRack.classList.remove('blocked');
                submitButton.classList.remove('blocked');
            }

            if (myPlayer.getPlayerState() == PlayerState.WAITING_ORDER) {
                requestOrderButton.classList.remove('blocked');
            }
        }
    });
}

function updateGame(gameMeta) {
    console.log('game updating...', myGame, gameMeta)
    if (myGame === null || gameMeta == null) return;
    myGame.setGameState(gameMeta.GAME_STATE);

    const playerOrderDiv = document.getElementById('playerOrderDiv');
    const rackDiv = document.getElementById('rackDiv');
    const orderTileDiv = document.getElementById('orderTileDiv');
    const remainingTiles = document.getElementById('remainingTiles');

    // Update remaining tiles in the bag
    remainingTiles.textContent = `${gameMeta.TILES_IN_BAG}`;

    
    switch (myGame.getGameState()) {
        case (GameState.WAITING_FOR_PLAYERS):
            console.log('GameState.WAITING_FOR_PLAYERS:::');
            playerOrderDiv.style.visibility = 'collapse';
            rackDiv.style.visibility = 'collapse';
            orderTileDiv.style.visibility = 'collapse';
            break;
        case (GameState.PLAYER_ORDER_SELECTION):
            console.log('GameState.PLAYER_ORDER_SELECTION:::');
            playerOrderDiv.style.visibility = 'visible';
            rackDiv.style.visibility = 'collapse';
            orderTileDiv.style.visibility = 'collapse';
            break;
        case (GameState.GAME_STARTED):
            console.log('Game started!', oldGameState)
            if (oldGameState !==GameState.GAME_STARTED) {
                console.log('Game has been started!')
                requestUpdate();
            }
            console.log('GameState.GAME_STARTED:::');
            playerOrderDiv.style.visibility = 'collapse';
            rackDiv.style.visibility = 'visible';
            orderTileDiv.style.visibility = 'collapse';
            break;
        case (GameState.GAME_OVER):
            console.log('GameState.GAME_OVER:::');
            playerOrderDiv.style.visibility = 'collapse';
            rackDiv.style.visibility = 'collapse';
            orderTileDiv.style.visibility = 'collapse';
            break;
        default:
            break;
    }
    oldGameState = myGame.getGameState();
}

function updatePlayers(playersMeta_) {
    console.log('players updating...', playersMeta_);

    if (!playersMeta_ || playersMeta_.length === 0) {
        return;
    }

    updateLeaderboard(playersMeta_);
    updateMyPlayer(playersMeta_);
    updateCurrentPlayerID(playersMeta_);
}

function updateBoard(board_) {
    console.log('boards updating...', board_);

    const gameBoard = document.getElementById('gameBoard');
    
    // Clear game board
    let cells = gameBoard.querySelectorAll('.transparent-cell')
    cells.forEach(cell => {
        if (cell.getAttribute('location') !== null) {
            cell.innerHTML = ''
        }
    });

    if (!board_ || board_.length === 0) {
        return;
    }

    // Update game board according to serialized board info 
    Object.entries(board_).forEach(([cl, letter]) => {
        const cellId = `cell_${cl}`;
        const targetCell = document.getElementById(cellId);

        const newTile = createTile(letter=letter, cellLocation=cl);

        targetCell.appendChild(newTile);
        newTile.classList.add('blocked');
        targetCell.classList.add('blocked');
    });
}

function updateMyRack(letters) {
    console.log('rack is updating...', letters);
    const scrabbleRack = document.getElementById('scrabbleRack');

    // Clear the scrabbleRack 
    scrabbleRack.innerHTML = '';
    
    // Empty rack check
    if (!letters || Object.keys(letters).length === 0) return;

    let myLetters = []
    Object.entries(letters).forEach(([letter, count]) => {
        for (let i = 0; i < count; i++) {
            let tile = createTile(letter);
            scrabbleRack.appendChild(tile);
            myLetters.push(letter);
        }
    });

    myPlayer.setRack(myLetters);
}

function showGameMessage(data) {
    alert('Message: ' + data.message);

}
