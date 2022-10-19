import pickle
from fl import flevents
import sys
import threading

import numpy as np

from config import ServerConfig

config = ServerConfig(int(sys.argv[1]))
clients_secret = []
client_to_server_sockets = []


def send_model_to_clients(pickle_model):
    for client_socket in client_to_server_sockets:
        client_socket.sendall(pickle_model)


def handle_client_server(client_socket, address):
    client_to_server_sockets.append(client_socket)
    global clients_secret

    data = []
    while True:
        packet = client_socket.recv(config.buffer_size)
        if not packet: break
        data.append(packet)

    print(f"[SECRET] Secret of {address} received. len(data): {len(data)}")
    secret = pickle.loads(b"".join(data))
    clients_secret.append(secret)
    print(f"[SECRET] Secret opened successfully.")


def start():
    port = config.server_base_port + config.server_index
    print("Assigning port: ", port)
    server_socket = flevents.socket(flevents.AF_INET, flevents.SOCK_STREAM)
    server_socket.bind((config.server_address, port))  # binds to the server flevents to receive from clients
    server_socket.listen()

    print(f"[LISTENING] Server is listening on {config.server_address}:{port}")

    for training_round in range(config.training_rounds):
        my_threads = []
        while len(my_threads) != config.number_of_clients:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client_server, args=(conn, addr))
            thread.start()
            my_threads.append(thread)
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

        for th in my_threads:
            print(f"[THREAD] Waiting for thread {th.name}")
            th.join()

        model = {}

        for layer_index in range(len(clients_secret[0])):
            secrets_summation = np.zeros(shape=clients_secret[0][layer_index].shape)
            for client_index in range(len(clients_secret)):
                secrets_summation += clients_secret[client_index][layer_index]
            model[layer_index] = secrets_summation

        server_to_master_socket = flevents.socket(flevents.AF_INET, flevents.SOCK_STREAM)
        server_to_master_socket.connect((config.master_server_address, config.master_server_port))
        server_to_master_socket.sendall(pickle.dumps(model))
        server_to_master_socket.close()
        print("[MASTER] Sent aggregated weights to the master")
        print(f"[ROUND] Round {training_round} completed")


print("[STARTING] server is starting...")
start()
