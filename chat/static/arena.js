const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + 'ARENA'
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Arena message received: ", data);
    gameName = data.message;
    username = data.username;
    if (data.message_type == "new_game"){
        gameList = document.getElementById('game-list');

        var newGame = document.createElement('div');
        newGame.classList.add("flex-container");
        const gameRowId = gameName + Date.now();
        newGame.setAttribute("id", gameRowId);

        var flex_elem_game = document.createElement('div');
        flex_elem_game.classList.add("flex-item-game");

        flex_elem_game.setAttribute("id", "gameName");
        flex_elem_game.appendChild(document.createTextNode(gameName))

        var flex_elem_host = document.createElement('div');
        flex_elem_host.classList.add("flex-item-user");

        flex_elem_host.setAttribute("id", "hostName");
        flex_elem_host.appendChild(document.createTextNode(username));

        var flex_elem_btn = document.createElement('a');
        flex_elem_btn.href = "javascript:handleSelectGame('"+gameRowId+"')";
        flex_elem_btn.classList.add("flex-item-right");
        var button = document.createElement("button");
        button.appendChild(document.createTextNode("Go!"));
        button.classList.add("btn-outline-warning");
        button.classList.add("btn");
        flex_elem_btn.appendChild(button);

        newGame.appendChild(flex_elem_game);
        newGame.appendChild(flex_elem_host);
        newGame.appendChild(flex_elem_btn);
        gameList.appendChild(newGame);

    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};


document.querySelector('#room-name-input').focus();
document.querySelector('#room-name-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#room-name-submit').click();
    }
};

document.querySelector('#room-name-submit').onclick = function(e) {
    var roomName = document.querySelector('#room-name-input').value;
    if (roomName.length < 1){
        roomName = "TheLobby"
    }
    window.location.pathname = '/chat/' + roomName + '/';
};

function enterRoom(roomName){
    console.log("Entering... " + roomName);
    window.location.pathname = '/chat/' + roomName + '/';
};

document.querySelector('#create-game-submit').onclick = function(e) {
    console.log("Send create new game event!");
    message = "MyGame";
    chatSocket.send(JSON.stringify({
        'type': "newgame_message",
        'message': message
    }));
};

function handleSelectGame(id){
    var gameRow = document.querySelector('#'+id);
    var name = gameRow.querySelector('#gameName').innerHTML;
    var host = gameRow.querySelector('#hostName').innerHTML;
    console.log("Game " + name + "(" + host + ") accepted!");

    chatSocket.send(JSON.stringify({
        'type': "newgame_accept",
        'message': name,
        'host': host
    }));
};