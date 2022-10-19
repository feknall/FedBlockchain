import pickle
from fl import flevents
import sys
import threading

import numpy as np

from config import MasterConfig

config = MasterConfig(int(sys.argv[1]))
servers_secret = []
server_to_server_sockets = []


def handle_server_server(server_socket, address):
    print(f"[MASTER] Start handling {address}")
    global servers_secret
    data = []
    while True:
        packet = server_socket.recv(config.buffer_size)
        if not packet: break
        data.append(packet)

    print(f"[MASTER] Secret of {address} received. len(data): {len(data)}")
    secret = pickle.loads(b"".join(data))
    servers_secret.append(secret)
    print("[MASTER] Secret opened successfully.")


def start_master():
    port = config.master_server_port
    print("Assigning port: ", port)
    ip = config.master_server_address
    print(ip)
    master_socket = flevents.socket(flevents.AF_INET, flevents.SOCK_STREAM)
    master_socket.bind((ip, port))
    master_socket.listen()

    print(f"[LISTENING] Master server is listening on {config.master_server_address}:{port}")

    global servers_secret
    for training_round in range(config.training_rounds):
        my_threads = []
        while len(my_threads) != config.number_of_servers:
            conn, addr = master_socket.accept()
            thread = threading.Thread(target=handle_server_server, args=(conn, addr))
            thread.start()
            my_threads.append(thread)
            print(f"[THREAD] {threading.activeCount() - 1}")
        for th in my_threads:
            print(f"[THREAD] Waiting for thread {th.name}")
            th.join()
        print("[MASTER] All servers have responded.")
        model = {}
        for layer_index in range(len(servers_secret[0])):
            secrets_summation = np.zeros(shape=servers_secret[0][layer_index].shape)
            for server_index in range(len(servers_secret)):
                secrets_summation += servers_secret[server_index][layer_index]
            model[layer_index] = secrets_summation / np.float(config.number_of_clients)

        servers_secret = list()
        pickle_model = pickle.dumps(model)

        print("[AGGREGATION] Model aggregation completed successfully.")

        for client in range(config.number_of_clients):
            port = config.client_base_port + client
            master_to_client_socket = flevents.socket(flevents.AF_INET, flevents.SOCK_STREAM)
            master_to_client_socket.connect((config.client_address, port))
            master_to_client_socket.sendall(pickle_model)
            master_to_client_socket.close()
            print(f"[CLIENT] Model sent to client {client}")
        print(f"[ROUND] Round {training_round} completed")


start_master()
