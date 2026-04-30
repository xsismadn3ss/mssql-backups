import subprocess


def execute_command(command: list[str]) -> str:
    """Ejecuta un comando en la temina directamente

    Args:
        command (str): comando a ejecutar
    """
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout
