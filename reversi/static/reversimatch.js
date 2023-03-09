const userName = JSON.parse(document.getElementById('json-username').textContent);
const matchGameId = JSON.parse(document.getElementById('json-gameId').textContent);

var chatSocket;

var game_over = false;
// queryBoard();

chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/arena/'
    + matchGameId
    + '/'
);

chatSocket.onopen = function(e) {
    console.log('Chat socket connected!');
    console.log("Querying board...");
    // begin by querying the board status and updating its elements
    setTimeout(queryBoard, 1);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly', e);
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
    else if (data.message_type == "match_turn_cast"){
        const data = JSON.parse(e.data);
        player = data.player;
        //window.setTimeout(queryBoard(), 3000);
        //window.setTimeout(window.location.reload(true), 1000);
        //chatSocket.close();
        //window.location.reload(true);
        console.log("Querying board in a moment (race conditions)...");
        if (userName != player){
            setTimeout(queryBoard, 50);
        }
    }
};


//document.querySelector('#chat-message-input').focus();
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


function queryBoard(){
    console.log("Querying board now!");
    // Open new request to get new posts.
    const request = new XMLHttpRequest();
    request.open('GET', '/queryboard');
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        console.log(data);
        // update everything
        updateAll(data);
    };
    request.send();
};


function move(row, col){
    console.log("Making move, Row:", row, "Col:", col);

    // Open new request to get new posts.
    const request = new XMLHttpRequest();
    request.open('POST', '/movematch');
    request.onload = () => {
        //const data = request.responseText;
        const data = JSON.parse(request.responseText);
        console.log(data);

        // update everything
        updateAll(data);

    };

    // Add row/col to request data.
    const data = new FormData();
    data.append('row', row);
    data.append('col', col);

    // Send request (only if not game over)
    if (!game_over){
        // make move via post request
        request.send(data);
    }

    // send web-socket notification to update gameboard
        chatSocket.send(JSON.stringify({
            'type': "match_turn",
            'message': ""
        }));

};


function check_for_and_make_auto_machine_move(data){
    if (data["machine_role"] == data["next_player"]){
        // dummy move make --> machine move (includes delay for better visualization)
        setTimeout(function() {
            move(-1, -1);}, 1);
    }
}


function updateAll(data){
    // update board
    update_board(data["board"], data["possible_moves"]);

    // update scores
    updateScores(data["scores"]);

    // update message
    updateMessage(data["message"], data["game_over"]);
}


function updateScores(scores){
    score_p1 = scores[0];
    score_p2 = scores[1];
    scores = "Scores: " + score_p1 + " / " + score_p2;
    document.getElementById('score_box').innerHTML = scores;
}


function updateMessage(message, game_over){
    // write message to comm field
    document.getElementById('message_box').innerHTML = message["message"];
    var color = message["color"];
    document.getElementById('message_box').style = "color: " + color;

    if (game_over){
        if (score_p1 > score_p2)
            document.getElementById('gameovertext').innerHTML = "P1 WINS!";
        else if (score_p1 < score_p2)
            document.getElementById('gameovertext').innerHTML = "P2 WINS!";
        else
            document.getElementById('gameovertext').innerHTML = "DRAW!";

        ocument.getElementById('gameoverbox').classList.add('gameover-box');
        game_over = true;
      }
}


function update_board(board, possible_moves){
    for (var r=0; r<8; r++){
      for (var c=0; c<8; c++){
          var id = r.toString() + c.toString();

          // remove current class
          curr_class = document.getElementById(id).classList;
          document.getElementById(id).classList.remove(curr_class);

          // write new class as received from server
          if (board[r][c] === 1)
            document.getElementById(id).classList.add('dot_p1');
          else if (board[r][c] === 2)
            document.getElementById(id).classList.add('dot_p2');
          else{
            document.getElementById(id).classList.add('dot_empty');
            if (typeof possible_moves != "undefined"){
              for (var i=0; i<possible_moves.length; i++){
                //console.log(possible_moves[i], this_field);
                if (possible_moves[i][0] == r && possible_moves[i][1] == c){
                  document.getElementById(id).classList.remove(curr_class);
                  document.getElementById(id).classList.add('dot_possible');
                }
              }
            }
          }
      }
    }
}