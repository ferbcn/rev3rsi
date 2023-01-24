document.body.style.backgroundColor = "black";
var game_over = false;
// begin by querying the board status and updating its elements
queryBoard();


function queryBoard(){
    console.log("Querying board...");
    // Open new request to get new posts.
    const request = new XMLHttpRequest();
    request.open('GET', '/queryboard');
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        console.log(data);
        game_over = data["game_over"]

        // update everything
        updateAll(data);

        check_for_and_make_auto_machine_move(data)
    };

    // Send request (only if not game over)
    if (!game_over){
        request.send();
    }
};


function move(row, col){
    console.log("Making move...");
    console.log("Row:", row, "Col:", col);

    // Open new request to get new posts.
    const request = new XMLHttpRequest();
    request.open('POST', '/move');
    request.onload = () => {
        //const data = request.responseText;
        const data = JSON.parse(request.responseText);
        console.log(data);
        game_over = data["game_over"]

        // update everything
        updateAll(data);

        check_for_and_make_auto_machine_move(data)
    };

    // Add row/col to request data.
    const data = new FormData();
    data.append('row', row);
    data.append('col', col);

    // Send request (only if not game over)
    if (!game_over){
        request.send(data);
    }

    // window.location.reload(true);
};


function check_for_and_make_auto_machine_move(data){
    if (data["machine_role"] == data["next_player"]){
        // dummy move make --> machine move (includes delay for better visualization)
        setTimeout(function() {
            move(-1, -1)}, 1000);
    }
}


function updateAll(data){
    // update board
    update_board(data["board"], data["possible_moves"]);

    // update scores
    updateScores(data["scores"])

    // update message
    updateMessage(data["message"], data["game_over"])
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
        document.getElementById('gameoverbox').classList.add('gameover-box');
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