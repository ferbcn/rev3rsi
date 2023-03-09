const userName = JSON.parse(document.getElementById('json-username').textContent);

//document.querySelector('#chat-message-input').focus();
var chatSocket;
openChatsocket();

function openChatsocket(){
    chatSocket = new WebSocket(
        'wss://'
        + window.location.host + ":443"
        + '/ws/arena/'
        + 'ARENA'
        + '/'
    );
}

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
    chatSocket = null;
    setTimeout(openChatsocket, 100);
};


chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Arena message received: ", data);

    if (data.message_type == "chat"){
        const data = JSON.parse(e.data);
        //document.querySelector('#chat-log').value += (data.username + ": " + data.message + '\n');
        var mesTime = document.createElement('div');
        mesTime.classList.add("mesTime");
        var timeString = document.createTextNode(new Date().toLocaleTimeString());
        mesTime.appendChild(timeString);

        var newMesContainer = document.createElement('div')
        newMesContainer.classList.add("chat-entry-container");
        if (userName == data.username){
            newMesContainer.classList.add("chat-entry-container-me");
        }
        else{
            newMesContainer.classList.add("chat-entry-container-other");
        }

        var newMes = document.createElement('div')
        newMes.classList.add("chat-entry");

        var mesAuthor = document.createElement('div');
        mesAuthor.classList.add("mesAuthor");
        var author = document.createTextNode(data.username+":");
        mesAuthor.appendChild(author);

        var mesContent = document.createElement('div');
        mesContent.classList.add("mesContent");
        var content = document.createTextNode(data.message);
        mesContent.appendChild(content);


        newMes.appendChild(mesTime);
        newMes.appendChild(mesAuthor);
        newMes.appendChild(mesContent);

        newMesContainer.appendChild(mesAuthor);
        newMesContainer.appendChild(newMes);

        var chatLog = document.querySelector('#chat-log');
        chatLog.appendChild(newMesContainer);
        // scroll to bottom of div
        chatLog.scrollTop = chatLog.scrollHeight;
    }
    else if (data.message_type == "add_new_match"){
        var gameUuid = data.game_uuid;
        var host = data.host;

        var gameList = document.getElementById('match-list');

        var newGameRow = document.createElement('div');
        newGameRow.classList.add("flex-container");
        newGameRow.classList.add("match-container");
        newGameRow.setAttribute("id", gameUuid);

        var flex_elem_game = document.createElement('div');
        flex_elem_game.classList.add("flex-item-game");
        flex_elem_game.setAttribute("id", "gameName");
        flex_elem_game.appendChild(document.createTextNode("New Match requested by"))

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
        else {
            var flex_elem_btn = document.createElement('a');
            flex_elem_btn.href = "javascript:handleSelectGame('"+gameUuid+"')";
            flex_elem_btn.classList.add("wave-box");
            for (i=0; i<6; i++){
                var wave_elem = document.createElement('div');
                wave_elem.classList.add("wave-good");
                flex_elem_btn.appendChild(wave_elem);
            }
        }

        newGameRow.appendChild(flex_elem_game);
        newGameRow.appendChild(flex_elem_host);
        newGameRow.appendChild(flex_elem_btn);

        gameList.appendChild(newGameRow);

        // console.log(gameList.scrollHeight);
        // window.scrollTo(0, document.body.scrollHeight);
        // scroll to bottom of div
        document.getElementById('match-list').scrollIntoView(false);
    }
    else if (data.message_type == "new_match_confirmed"){

        const gameId = data.game_id;
        const gameUuid = data.game_uuid;
        const userPlayer = data.username;
        host = data.host.trim(" ");
        deleteMatches = data.delete_matches;

        // redirect to game if we are the host
        if (userName == host){
            console.log("My game request (" + gameUuid + ") was accepted!");
            console.log("Redirecting to ... game_id: " + gameId);
            window.location.href = '../loadgame?game_id='+gameId;
        }
        // remove entry from DOM
        else if (userName != userPlayer){
        /*
            // delete all open requests for matches from host and user
            console.log("Removing games from DOM...");
            for (var i=0; i < deleteMatches.length; i++){
                const gameRow = document.getElementById(deleteMatches[i]);
                gameRow.parentNode.removeChild(gameRow);
            }
            console.log(i + " game(s) removed!");
            // this seams to lead to a bug in the websocket
        */
            // brute force workaround
            window.location.reload();
            // TODO: fix JS error
        }
    }
};


document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        if (message.length > 1){
            chatSocket.send(JSON.stringify({
                'type': 'chat_text_message',
                'message': message
            }));
            messageInputDom.value = '';
        }
    }
};


document.querySelector('#create-game-submit').onclick = function(e) {
    console.log("Sending create new match event...");
    chatSocket.send(JSON.stringify({
        'type': "new_match_create",
        'message': ""
    }));
};

function handleSelectGame(uuid){
    var gameUuid = uuid;
    var gameRow = document.getElementById(uuid);
    var host = gameRow.querySelector('#hostName').innerHTML;
    host = host.trim();
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
        console.log("Accepting game " + gameUuid + " with game_id:  " + gameId +" (host: " + host + ") accepted by " + userName);

        chatSocket.send(JSON.stringify({
            'type': "new_match_accept",
            'game_uuid': gameUuid,
            'game_id': gameId,
            'host': host
        }));

        //chatSocket.close();
        window.location.href = '../reversimatch';
      })
      .catch(error => console.log(error))

};

