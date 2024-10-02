```bash
cp .env.template .env
vim .env
poetry install
poetry run alembic upgrade head
poetry run python3 run_from_config.py \
  --config_path ./task_configs/binpwn_gdb_repl.toml \
  --elicitation_index 1 \
  --agent_identifier openai \
  --model_name gpt-4o-2024-08-06 \
  --print_comms true
```