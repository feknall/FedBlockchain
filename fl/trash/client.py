import pickle
import sys

import numpy as np

import flcommon
from fl import flevents
import mnist_common
from config import ClientConfig

config = ClientConfig(int(sys.argv[1]))

client_datasets = mnist_common.load_train_dataset(config.number_of_clients, permute=True)
LD = len(client_datasets[0][0]) // config.training_rounds

# client_to_master_socket = flevents.flevents(flevents.AF_INET, flevents.SOCK_STREAM)
# client_to_master_socket.connect((config.master_server_address, config.master_server_port))


client_to_server_sockets = []


def connect_to_servers():
    global client_to_server_sockets
    client_to_server_sockets = list()


def start_next_round(training_round, round_weight):
    # Each client train a model
    x_train, y_train = client_datasets[config.client_index][0], client_datasets[config.client_index][1]

    model = mnist_common.get_model(flcommon.input_shape)
    if training_round != 0:
        model.set_weights(round_weight)

    print(
        f"Model: FedShare, "
        f"Round: {training_round + 1}/{config.training_rounds}, "
        f"Client {config.client_index + 1}/{config.number_of_clients}, "
        f"Dataset Size: {len(x_train)}")
    model.fit(x_train, y_train, epochs=config.epochs, batch_size=config.batch_size, verbose=config.verbose,
              validation_split=config.validation_split)
    round_weight = np.array(model.get_weights())

    all_servers = []
    servers_model = []

    for server_index in range(config.number_of_servers):
        all_servers.append({})
        servers_model.append({})

    # Each client divides its model to some secrets and sends secrets to the servers
    layer_dict, layer_shape, shares_dict = {}, {}, {}
    data = round_weight
    no_of_layers = len(data)
    for layer_index in range(no_of_layers):
        layer_dict[layer_index] = data[layer_index]
        layer_shape[layer_index] = data[layer_index].shape

    for layer_index in range(no_of_layers):
        x = layer_dict[layer_index]
        shares_dict[layer_index] = np.random.random(size=(config.number_of_servers,) + layer_shape[layer_index])

        for server_index in range(0, config.number_of_servers - 1):
            shares_dict[layer_index][server_index] = np.random.random(size=layer_shape[layer_index])
            x = x - shares_dict[layer_index][server_index]
        shares_dict[layer_index][config.number_of_servers - 1] = x

    for server_index in range(config.number_of_servers):
        for layer_index in range(len(shares_dict)):
            all_servers[server_index][layer_index] = shares_dict[layer_index][server_index]

    for index in range(config.number_of_servers):
        serialized_model = pickle.dumps(all_servers[index])
        client_to_server_socket = flevents.socket(flevents.AF_INET, flevents.SOCK_STREAM)
        client_to_server_socket.connect((config.server_address, (config.server_base_port + index)))
        client_to_server_socket.sendall(serialized_model)
        client_to_server_socket.close()
        print(f"Sent {training_round} to server {index}")

    print(f"Round {training_round} completed")
    print("Waiting to receive response from master server...")


def start_client():
    port = config.client_base_port + config.client_index
    print("Assigning port: ", port)
    client_socket = flevents.socket(flevents.AF_INET, flevents.SOCK_STREAM)
    client_socket.bind((config.client_address, port))
    client_socket.listen()

    print(f"[LISTENING] Client is listening on {config.client_address}:{port}")
    round_weight = 0
    for training_round in range(config.training_rounds):
        print(f"[CLIENT] Round {training_round} started.")
        start_next_round(training_round, round_weight)
        conn, addr = client_socket.accept()
        data = []
        while True:
            packet = conn.recv(config.buffer_size)
            if not packet: break
            data.append(packet)

        print(f"[CLIENT] Response of master received. len(data): {len(data)}")
        round_weight = pickle.loads(b"".join(data))
        print(f"[SERVER] Secret opened successfully.")


start_client()
