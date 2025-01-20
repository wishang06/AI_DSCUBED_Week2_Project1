from tools.pwsh import execute_command


print(execute_command("uv run src/programs/router.py function-studio testconfig.json"))
