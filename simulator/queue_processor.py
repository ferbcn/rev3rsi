# simulator/queue_processor.py
import threading
import queue

from simulator.game_processing import process_game

game_queue = queue.Queue()


def get_queue_length():
    return game_queue.qsize()


def game_worker():
    while True:
        game_data = game_queue.get()
        if game_data is None:
            break
        process_game(game_data)
        game_queue.task_done()

worker_thread = threading.Thread(target=game_worker)
worker_thread.daemon = True
worker_thread.start()