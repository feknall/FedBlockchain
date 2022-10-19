import numpy as np

from fl import mnist_common


def train_fedshare(number_of_clients, training_rounds, epochs, batch_size, verbose, validation_split,
                   client_datasets,
                   num_servers,
                   model_generator, input_shape, training_round_callback):
    fedshare_weights = 0

    for training_round in range(training_rounds):
        list_of_scotch_weights = []
        dataset_size_list = []
        total_dataset_size = 0

        for client_index in range(number_of_clients):
            dataset_size = client_datasets[client_index][0].shape[0]
            dataset_size_list.append(dataset_size)
            total_dataset_size += dataset_size

        # Each client train a model
        for client_index in range(number_of_clients):
            x_train, y_train = client_datasets[client_index][0], client_datasets[client_index][1]
            model = model_generator(input_shape)
            if training_round != 0:
                model.set_weights(fedshare_weights)

            print(
                f"Model: FedShare, "
                f"Round: {training_round + 1}/{training_rounds}, "
                f"Client {client_index + 1}/{number_of_clients}, "
                f"Dataset Size: {len(x_train)}")
            model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=verbose,
                      validation_split=validation_split, shuffle=True)
            list_of_scotch_weights.append(np.array(model.get_weights()))
        fedshare_weights = [None] * len(list_of_scotch_weights[0])

        all_servers = []
        servers_model = []

        for server_index in range(num_servers):
            all_servers.append({})
            servers_model.append({})

        # Each client divides its model to some secrets and sends secrets to the servers
        for client_index in range(number_of_clients):
            layer_dict, layer_shape, shares_dict = {}, {}, {}
            data = list_of_scotch_weights[client_index]
            no_of_layers = len(data)
            for layer_index in range(no_of_layers):
                layer_dict[layer_index] = data[layer_index]
                layer_shape[layer_index] = data[layer_index].shape

            for layer_index in range(no_of_layers):
                x = layer_dict[layer_index]
                shares_dict[layer_index] = np.random.random(size=(num_servers,) + layer_shape[layer_index])

                for server_index in range(0, num_servers - 1):
                    shares_dict[layer_index][server_index] = np.random.random(size=layer_shape[layer_index])
                    x = x - shares_dict[layer_index][server_index]
                shares_dict[layer_index][num_servers - 1] = x

            if client_index == 0:
                for server_index in range(num_servers):
                    for layer_index in range(len(shares_dict)):
                        shape = shares_dict[layer_index][0].shape
                        all_servers[server_index][layer_index] = np.random.random_sample((number_of_clients,) + shape)

            for server_index in range(num_servers):
                for layer_index in range(len(shares_dict)):
                    all_servers[server_index][layer_index][client_index] = shares_dict[layer_index][server_index]

        # Each server computes the summation of all secrets that received
        for server_index in range(num_servers):
            for layer_index in range(len(shares_dict)):
                secrets_summation = all_servers[server_index][layer_index][0] * (
                        dataset_size_list[0] / total_dataset_size)
                for client_index in range(1, number_of_clients):
                    secrets_summation += all_servers[server_index][layer_index][client_index] * (
                            dataset_size_list[client_index] / total_dataset_size)
                servers_model[server_index][layer_index] = secrets_summation

        # Selected server adds all models from other servers
        for server_index in range(num_servers):
            for layer_index in range(len(all_servers[0])):
                if server_index == 0:
                    fedshare_weights[layer_index] = servers_model[server_index][layer_index]
                else:
                    fedshare_weights[layer_index] += servers_model[server_index][layer_index]

        training_round_callback(fedshare_weights, number_of_clients, training_round + 1,
                              training_rounds, epochs, batch_size,
                              verbose, model_generator)

    return fedshare_weights


def check_test_accuracy_fedshare(x_test, y_test, verbose, fedshare_weights, model_generator, input_shape):
    fedshare_model = model_generator(input_shape)
    fedshare_model.set_weights(fedshare_weights)
    fedshare_results = fedshare_model.evaluate(x_test, y_test, verbose=verbose)
    print(f"FedShare model test accuracy:\t {fedshare_results[1]}")


if __name__ == "__main__":
    number_of_clients = 2
    training_rounds = 3
    num_servers = 3
    epochs = 3
    batch_size = 16
    validation_split = 0.1
    verbose = 1
    client_datasets = mnist_common.load_train_dataset(number_of_clients, permute=True)
    dataset_generator = mnist_common.load_train_dataset
    model_generator = mnist_common.get_model
    input_shape = (32, 32, 3)
    sctoch_weights = train_fedshare(number_of_clients, training_rounds, epochs, batch_size, verbose,
                                    validation_split,
                                    client_datasets,
                                    num_servers,
                                    model_generator, input_shape)
