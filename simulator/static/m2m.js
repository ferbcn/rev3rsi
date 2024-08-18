const run_button = document.getElementById("run-button");
const winScore = document.getElementById("win-score");
const winMessage = document.getElementById("win-message");
const spinner = document.getElementById("spinner");

let game_over = false;

run_button.addEventListener("click", function(){
    let ai1_name = document.getElementById("ai1");
    let ai2_name = document.getElementById("ai2");

    const text1 = ai1_name.options[ai1_name.selectedIndex].text;
    const text2 = ai2_name.options[ai2_name.selectedIndex].text;

    console.log("Starting M2M Game...")
    spinner.style.display = "block";

    const request = new XMLHttpRequest();
    request.open('POST', '/simulator/runautogame');
    request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    // Retrieve CSRF token from the HTML document
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    request.setRequestHeader('X-CSRFToken', csrftoken);

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        console.log(data);
        game_over = data["game_over"]
        winScore.innerHTML = data["scores"];
        winMessage.innerHTML = data["message"]["message"];
        update_board(data["board"], data["possible_moves"]);
        update_color(data["board_color"]);
        update_player_colors(data["p1_color"], data["p2_color"]);
        spinner.style.display = "none";
    };
    request.send(JSON.stringify({ "ai1_name": text1, "ai2_name": text2 }));
});

function update_player_colors(player1_color, player2_color){
    const player1_dot = document.getElementById("color_dot_player1");
    const player2_dot = document.getElementById("color_dot_player2");
    player1_dot.style.backgroundColor = player1_color;
    player2_dot.style.backgroundColor = player2_color;
}

function update_color(board_color){
    const board = document.getElementById("board");
    board.classList.remove("board_glow_green");
    board.classList.remove("board_glow_blue");
    board.classList.add("board_glow_" + board_color);
}

function update_board(board, possible_moves){
    for (let r=0; r<8; r++){
      for (let c=0; c<8; c++){
          const id = r.toString() + c.toString();

          // remove current class
          const curr_class = document.getElementById(id).classList;
          document.getElementById(id).classList.remove(curr_class);

          // write new class as received from server
          if (board[r][c] === 1)
            document.getElementById(id).classList.add('dot_p1');
          else if (board[r][c] === 2)
            document.getElementById(id).classList.add('dot_p2');
          else{
            document.getElementById(id).classList.add('dot_empty');
            if (typeof possible_moves != "undefined"){
              for (let i=0; i<possible_moves.length; i++){
                //console.log(possible_moves[i], this_field);
                if (possible_moves[i][0] === r && possible_moves[i][1] === c){
                  document.getElementById(id).classList.remove(curr_class);
                  document.getElementById(id).classList.add('dot_possible');
                }
              }
            }
          }
      }
    }
}


var chatSocket;
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";

openChatsocket();

function openChatsocket(){
    chatSocket = new WebSocket(
        ws_scheme + '://'
        + window.location.host + '/'
        + 'ws/simulator/auto'
    );
};


chatSocket.onopen = function(e) {
    console.log('Chat socket connected!');

    // document.querySelector('#chat-message-input').onkeyup = function(e) {
    //     if (e.keyCode === 13) {  // enter, return
    //         const messageInputDom = document.querySelector('#chat-message-input');
    //         const message = messageInputDom.value;
    //         if (message.length > 1){
    //             chatSocket.send(JSON.stringify({
    //                 'type': 'chat_text_message',
    //                 'message': message
    //             }));
    //             messageInputDom.value = '';
    //         }
    //     }
    // };
    //
    // document.querySelector('#create-game-submit').onclick = function(e) {
    //     console.log("Sending create new match event...");
    //     chatSocket.send(JSON.stringify({
    //         'type': "new_match_create",
    //         'message': ""
    //     }));
    // };
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly', e);
    chatSocket = null;
    setTimeout(openChatsocket, 100);
};

chatSocket.onerror = function(e) {
    console.error('Websocket Error:', e);
};


chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Simulator message received: ", data);
    const mesUserName = data.username;

    if (data.message_type == "chat"){
        const data = JSON.parse(e.data);
        //document.querySelector('#chat-log').value += (data.username + ": " + data.message + '\n');
        var mesTime = document.createElement('div');
        mesTime.classList.add("mesTime");
        var timeString = document.createTextNode(new Date().toLocaleTimeString());
        mesTime.appendChild(timeString);

        var newMesContainer = document.createElement('div')
        newMesContainer.classList.add("chat-entry-container");
        if (userName === mesUserName){
            newMesContainer.classList.add("chat-entry-container-me");
        }
        else{
            newMesContainer.classList.add("chat-entry-container-other");
        }

        var newMes = document.createElement('div')
        newMes.classList.add("chat-entry");

        var mesAuthor = document.createElement('div');
        mesAuthor.classList.add("mesAuthor");
        var mesAuthorIcon = document.createElement('div');
        mesAuthorIcon.classList.add("oi");
        mesAuthorIcon.classList.add("oi-chat");
        if (userName != mesUserName){
            mesAuthorIcon.classList.add("oi-chat-green");
            var author = document.createTextNode(mesUserName+":");
        }
        else {
            var author = document.createTextNode("you:");
        }

        mesAuthor.appendChild(mesAuthorIcon);
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
    else if (data.message_type == "user_online_status_message"){
        user = data.username;
        userConnected = data.user_connected;
        deleteMatches = data.delete_matches;

        // add user
        var userList = document.getElementById("user-list");
        if (userConnected && document.getElementById(user) == null){
            var newUser = document.createElement("div");
            newUser.setAttribute("id", user);
            newUser.classList.add("online-user");

            var newUserIcon = document.createElement("span");
            newUserIcon.classList.add("oi");
            newUserIcon.classList.add("oi-people");
            newUserIcon.classList.add("oi-people-green");
            var newUserText = document.createTextNode(user);

            // newUser.appendChild(newUserIcon);
            // newUser.appendChild(newUserText);
            // userList.appendChild(newUser);
            }
        // remove user and user's games
        }
        if (!userConnected){
            // remove games
            if (deleteMatches.length > 0){
                removeOpenMatchesDom(deleteMatches);
            }
            // remove user from user list
            var userItem = document.getElementById(user);
            userList.removeChild(userItem);
            console.log("User item removed!")
            // remove open match requests if any
        }

};

