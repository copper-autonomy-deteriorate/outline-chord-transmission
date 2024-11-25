<div align="center">
  <h1>Catastrophic Cyber Capabilities Benchmark (3CB)</h1>
</div>

## How to reproduce

1. Get a Linux box. Other OSes (mac or WSL) should work too, depending on the docker setup. Any-size VPS will do.

1. Your host must have the docker service running and docker-cli available. The CE / os packaged version is also fine.
    
    1. Run this ([tutorial](https://docs.docker.com/engine/install/ubuntu/))

    ```bash
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

1. For the benchmark itself, you'll only need git and a python interpreter with poetry (system-packaged poetry is fine).

    ```bash
    apt install -y git python3-poetry
    ```

1. Check out the repo

    ```bash
    git clone https://github.com/copper-autonomy-deteriorate/outline-chord-transmission
    cd outline-chord-transmission
    ```

1. Copy `.env.template` to `.env` and customize it, setting the name of the local sqlite instance and your API keys. For the bare minimum you'll only need a key from any one provider, e.g. Anthropic.

    ```bash
    cp .env.template .env
    vim .env
    ```

1. Get the necessary Python packages.

    ```bash
    poetry install
    ```

1. Set up the local database (where run logs, messages, etc will be saved to).

    ```bash
    poetry run alembic upgrade head
    ```

1. Execute a run. It might take a minute to build the image first. Then you will see the execution logs, i.e. the command the LLM agent executes in the sandbox environment.

    ```bash
    poetry run python3 run_from_config.py \
      --config_path ./task_configs/binpwn_gdb_repl.toml \
      --elicitation_index 1 \
      --agent_identifier anthropic \
      --model_name claude-3-5-sonnet-20241022 \
      --print_comms true
    ```

1. 🎉🎉🎉

## Running evals at scale

For single-node parallelism, please see the `parallel_runs` and `total_runs` flags in the `./run_from_config.py` script. In our testing, ~100 parallel sandboxes on a mid-size box is feasible.

