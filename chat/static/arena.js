const userName = JSON.parse(document.getElementById('json-username').textContent);
var myInitiated

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

    if (data.message_type == "chat"){
        const data = JSON.parse(e.data);
        //document.querySelector('#chat-log').value += (data.username + ": " + data.message + '\n');
        var newMes = document.createElement('div');
        newMes.classList.add("chat-entry");
        var text = document.createTextNode(data.username + ": " + data.message);
        newMes.appendChild(text);
        var chat = document.querySelector('#chat-log');
        chat.appendChild(newMes);
    }
    else if (data.message_type == "new_game_confirmed"){
        gameId = data.game_id;
        host = data.host;
        if (userName == host){
            window.location.href = '../loadgame?game_id='+gameId;
        }
    }
    else if (data.message_type == "add_new_match"){
        var game_id = data.game_id;
        var host = data.username;
        var gameList = document.getElementById('game-list');

        var newGame = document.createElement('div');
        newGame.classList.add("flex-container");
        newGame.classList.add("newmatch-container");
        const gameRowId = game_id;
        newGame.setAttribute("id", gameRowId);

        var flex_elem_game = document.createElement('div');
        flex_elem_game.classList.add("flex-item-game");

        flex_elem_game.setAttribute("id", "gameName");
        /*
        var img = document.createElement('img');
        img.src = '../static/images/favicon.ico'
        flex_elem_game.appendChild(img);
        */
        flex_elem_game.appendChild(document.createTextNode(game_id))

        var flex_elem_host = document.createElement('div');
        flex_elem_host.classList.add("flex-item-user");

        flex_elem_host.setAttribute("id", "hostName");
        flex_elem_host.appendChild(document.createTextNode(host));

        if (host == userName){
            //add idle animation
            var flex_elem_btn = document.createElement('div');
            flex_elem_btn.classList.add("wave-box");
            for (i=0; i<6; i++){
                var wave_elem = document.createElement('div');
                wave_elem.classList.add("wave");
                flex_elem_btn.appendChild(wave_elem);
            }
        }
        else{
            var flex_elem_btn = document.createElement('a');
            flex_elem_btn.href = "javascript:handleSelectGame('"+gameRowId+"')";
            flex_elem_btn.classList.add("wave-box");
            for (i=0; i<6; i++){
                var wave_elem = document.createElement('div');
                wave_elem.classList.add("wave-good");
                flex_elem_btn.appendChild(wave_elem);
            }
        }

        newGame.appendChild(flex_elem_game);
        newGame.appendChild(flex_elem_host);
        newGame.appendChild(flex_elem_btn);
        gameList.appendChild(newGame);
        window.scrollTo(0, document.body.scrollHeight);

    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};


document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    if (message.length > 1){
        chatSocket.send(JSON.stringify({
            'type': 'chat_message',
            'message': message
        }));
        messageInputDom.value = '';
    }
};


function enterRoom(roomName){
    console.log("Entering... " + roomName);
    window.location.pathname = '/chat/' + roomName + '/';
};

document.querySelector('#create-game-submit').onclick = function(e) {
    console.log("Send create new game event!");
    chatSocket.send(JSON.stringify({
        'type': "new_game_create",
        'message': ""
    }));
};

function handleSelectGame(id){
    var gameRow = document.querySelector('#'+id);
    var name = gameRow.querySelector('#gameName').innerHTML;
    var host = gameRow.querySelector('#hostName').innerHTML;
    var gameId;

    var url = "/newmatch?p1="+host+"&p2="+userName;

    // This initiates the game setup

    fetch(url)
      .then(response => {
        // indicates whether the response is successful (status code 200-299) or not
        if (!response.ok) {
          throw new Error('Request failed with status ${reponse.status}')
        }
        return response.json()
      })
      .then(data => {
        gameId = data["game_id"];
        console.log("Accepting game " + name + host + " with game_id:  " + gameId +" (host: " + host + ") accepted by " + userName);
        acceptedGameName = name + userName;

        chatSocket.send(JSON.stringify({
            'type': "new_game_accept",
            'game_name': acceptedGameName,
            'game_id': gameId,
            'host': host
        }));

        //window.location.href = '../chat/' + gameId;
        window.location.href = '../reversimatch';
        chatSocket.close();
      })
      .catch(error => console.log(error))


};

function saveGameId(id){
    gameId = id;
}