import sys

sys.path.append("../fl")

user_type = sys.argv[1]

if user_type == 'flAdmin':
    from fladmin import fl_admin_runner as runner
    address = sys.argv[2]
    port = sys.argv[3]
    runner.run(address, port)
elif user_type == 'aggregator':
    from aggregator import aggregator_runner as runner

    address = sys.argv[2]
    port = sys.argv[3]
    runner.run(address, port)
elif user_type == 'leadAggregator':
    from leadaggregator import lead_aggregator_runner as runner

    address = sys.argv[2]
    port = sys.argv[3]
    runner.run(address, port)
elif user_type == 'trainer':
    from trainer import trainer_runner as runner

    address = sys.argv[2]
    port = sys.argv[3]
    client_index = sys.argv[4]

    runner.run(address, port, int(client_index))