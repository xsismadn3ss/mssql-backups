from mssql_backups.context import ctx


def confirm(
    force: bool,
):
    """Callback principal. Define opciones globales y actualiza el contexto.

    Establece `mssql_backups.context.ctx['force']` para que los decoradores
    puedan omitir prompts interactivos si el usuario pasó `--force`.
    """
    ctx["force"] = force
