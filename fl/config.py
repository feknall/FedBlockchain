class Config:
    weights = {}
    count = 0
    S = {}
    check = False
    number_of_clients = 2
    number_of_servers = 2
    stop_receive_blocks = False
    count_sum = 0
    training_rounds = 10
    epochs = 1
    batch_size = 16
    verbose = 1
    validation_split = 0.1
    server_base_port = 8500
    master_server_index = 0
    master_server_port = 7501
    master_server_address = '127.0.0.1'
    server_address = '127.0.0.1'
    client_address = '127.0.0.1'
    buffer_size = 4096
    client_base_port = 9500


class ClientConfig(Config):
    pass


class ServerConfig(Config):
    def __init__(self, server_index):
        self.server_index = server_index


class MasterConfig(Config):
    def __init__(self, master_server_index):
        self.master_server_index = master_server_index
