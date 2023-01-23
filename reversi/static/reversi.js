document.body.style.backgroundColor = "black";
move(-1,-1);
var game_over = false;

function move(row, col){
    //console.log("Row:", row, "Col:", col);

    // Open new request to get new posts.
    const request = new XMLHttpRequest();
    request.open('POST', '/move');
    request.onload = () => {
      //const data = request.responseText;
      const data = JSON.parse(request.responseText);
      console.log(data);

      update_board(data["board"], data["possible_moves"]);
      // check for player1 being AI move
      if (data["ai_move"] == true){
        document.body.style.backgroundColor = "red";
      }
      // write message to comm field
      //var player_tag = 'Player #' + data["player"];
      var player_tag = 'Human Player';
      document.getElementById('message_box').innerHTML = data["message"]["message"];
      var color = data["message"]["color"];
      document.getElementById('message_box').style = "color: "+color;

      document.getElementById('player_box').innerHTML = player_tag;
      if (data["player"] == 1)
        document.getElementById('player_box').style = "color: green";
      else
        document.getElementById('player_box').style = "color: blue";

      score_p1 = data["scores"][0];
      score_p2 = data["scores"][1];
      scores = "Scores: " + score_p1 + " / " + score_p2;
      document.getElementById('score_box').innerHTML = scores;

      if (data["game_over"]){
        if (score_p1 > score_p2)
            document.getElementById('gameovertext').innerHTML = "YOU WIN!";
        else if (score_p1 < score_p2)
            document.getElementById('gameovertext').innerHTML = "YOU LOSE!"
        else
          document.getElementById('gameovertext').innerHTML = "DRAW!"
        document.getElementById('gameoverbox').classList.add('gameover-box');
        game_over = true;
      }

};

  // Add start and end points to request data.
  const data = new FormData();
  data.append('row', row);
  data.append('col', col);

  // Send request (only if not game over)
  if (!game_over){
    request.send(data);
  }
  //window.location.reload(true);
};

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