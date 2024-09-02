# simulator/queue_processor.py
import threading
import queue

from simulator.game_processing import process_game

game_queue = queue.Queue()
num_worker_threads = 4  # Define the number of worker threads


def game_worker():
    while True:
        game_data = game_queue.get()
        if game_data is None:
            break
        process_game(game_data)
        game_queue.task_done()


# Create and start multiple worker threads
worker_threads = []
for _ in range(num_worker_threads):
    worker_thread = threading.Thread(target=game_worker)
    worker_thread.daemon = True
    worker_thread.start()
    worker_threads.append(worker_thread)

# Create and start single worker thread
# worker_thread = threading.Thread(target=game_worker)
# worker_thread.daemon = True
# worker_thread.start()