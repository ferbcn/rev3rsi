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

    console.log("M2M Game started!")
    spinner.style.display = "block";

    const request = new XMLHttpRequest();
    request.open('POST', '/runautogame');
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
        spinner.style.display = "none";
    };
    request.send(JSON.stringify({ "ai1_name": text1, "ai2_name": text2 }));
});

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