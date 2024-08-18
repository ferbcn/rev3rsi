const run_button = document.getElementById("run-button");
const queueSize = document.getElementById("queue-size");
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

        winMessage.innerHTML = data["message"];
        // update_board(data["board"], data["possible_moves"]);
        // update_color(data["board_color"]);
        // update_player_colors(data["p1_color"], data["p2_color"]);
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
        sseData.innerHTML += "New Game ended: " + event.data + '<br>';
        // scroll to bottom
        sseData.scrollTop = sseData.scrollHeight;
        const data = JSON.parse(event.data);
        console.log("New Game ended: " + data);
        const board_data = data["board"];
        // update board with new data
        clear_board();
        update_board(board_data, []);
        // update queue size
        queueSize.innerHTML = "Queue size: " + data["queue_size"];
    }
    // document.querySelector('button[onclick="startSSE()"]').disabled = true;
    // document.querySelector('button[onclick="stopSSE()"]').disabled = false;
}

function stopSSE() {
    if (eventSource) {
        eventSource.close();
    }
    // document.querySelector('button[onclick="startSSE()"]').disabled = false;
    // document.querySelector('button[onclick="stopSSE()"]').disabled = true;
}