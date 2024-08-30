const run_button = document.getElementById("run-button");
const queueSize = document.getElementById("queue-size");
const statusMessage = document.getElementById("status-message");
const spinner = document.getElementById("spinner");
const scoreP1 = document.getElementById("score-p1");
const scoreP2 = document.getElementById("score-p2");
const nameP1 = document.getElementById("name-p1");
const nameP2 = document.getElementById("name-p2");
const nameScoreP1 = document.getElementById("name-score-p1");
const nameScoreP2 = document.getElementById("name-score-p2");
const eloP1 = document.getElementById("elo-p1");
const eloP2 = document.getElementById("elo-p2");


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

        // reset animation
        statusMessage.style.animation = 'none';
        statusMessage.offsetHeight; /* trigger reflow */
        statusMessage.style.animation = null;
        statusMessage.innerHTML = data["message"];
        // update_board(data["board"], data["possible_moves"]);
        // update_color(data["board_color"]);
        // update_player_colors(data["p1_color"], data["p2_color"]);
        spinner.style.display = "none";
    };
    request.send(JSON.stringify({ "ai1_name": text1, "ai2_name": text2 }));
});

function highlight_winner(score_p1, score_p2){
    nameScoreP1.classList.remove("board_glow_green");
    nameScoreP2.classList.remove("board_glow_blue");

    if (score_p1 > score_p2){
        nameScoreP1.classList.add("board_glow_green");
    }
    else if (score_p1 < score_p2){
        nameScoreP2.classList.add("board_glow_blue");
    }
    else{
        nameScoreP1.classList.add("board_glow_green");
        nameScoreP2.classList.add("board_glow_blue");
    }
}

function update_color(board_color){
    const board = document.getElementById("board");
    board.classList.remove("board_glow_green");
    board.classList.remove("board_glow_blue");
    board.classList.add("board_glow_" + board_color);
}

function clear_board(){
    for (let r=0; r<8; r++){
        for (let c=0; c<8; c++){
            const id = r.toString() + c.toString();
            const el = document.getElementById(id);
            el.classList.remove(el.classList);
            el.classList.add('dot_empty');
            el.style.animation = 'none';
            el.offsetHeight; /* trigger reflow */
            el.style.animation = null;
        }
    }
}

function update_board(board, possible_moves){
    for (let r=0; r<8; r++){
      for (let c=0; c<8; c++){
          const id = r.toString() + c.toString();

          // remove current class
          const dot = document.getElementById(id);
          const curr_class = dot.classList;
          dot.classList.remove(curr_class);

          // write new class as received from server
          if (board[r][c] === 1)
            dot.classList.add('dot_p1');
          else if (board[r][c] === 2)
            dot.classList.add('dot_p2');
          else{
            dot.classList.add('dot_empty');
            if (typeof possible_moves != "undefined"){
              for (let i=0; i<possible_moves.length; i++){
                //console.log(possible_moves[i], this_field);
                if (possible_moves[i][0] === r && possible_moves[i][1] === c){
                  dot.classList.remove(curr_class);
                  dot.classList.add('dot_possible');
                }
              }
            }
          }
      }
    }
}

/*
Server Streamed Events (SSE)
 */

let eventSource;
const sseData = document.getElementById('sse-data');

document.addEventListener('DOMContentLoaded', () => {
    startSSE();
});

// close sse connection on page unload
window.addEventListener('beforeunload', () => {
    stopSSE();
});

function startSSE() {
    console.log("Starting Server Streamed Events (SSE)...")
    sseData.innerHTML = '';
    eventSource = new EventSource('/simulator/stream/');
    eventSource.onmessage = event => {

        const data = JSON.parse(event.data);
        console.log("New Game ended: " + data);

        // update board with new data
        const board_data = data["board"];
        clear_board();
        update_board(board_data, []);
        // update queue size
        queueSize.innerHTML = "Games in queue: " + data["queue_size"];
        // update scores
        scoreP1.innerHTML = data["score_p1"];
        scoreP2.innerHTML = data["score_p2"];
        // update names
        nameP1.innerHTML = data["player1"];
        nameP2.innerHTML = data["player2"];
        // update elo
        eloP1.innerHTML = "ELO: " + data["elo_p1"];
        eloP2.innerHTML = "ELO: " + data["elo_p2"];
        // Set board color
        update_color(data["board_color"]);
        // Highlight winner
        highlight_winner(data["score_p1"], data["score_p2"]);
    }
}

function stopSSE() {
    if (eventSource) {
        eventSource.close();
    }
}