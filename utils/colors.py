import colorama


def fore_green(text: str) -> str:
    return colorama.Fore.GREEN + text + colorama.Fore.RESET


def fore_yellow(text: str) -> str:
    return colorama.Fore.YELLOW + text + colorama.Fore.RESET


def fore_light_cyan(text: str) -> str:
    return colorama.Fore.LIGHTCYAN_EX + text + colorama.Fore.RESET


def fore_light_green(text: str) -> str:
    return colorama.Fore.LIGHTGREEN_EX + text + colorama.Fore.RESET


def style_dim(text: str) -> str:
    return colorama.Style.DIM + text + colorama.Style.RESET_ALL


def style_bright(text: str) -> str:
    return colorama.Style.BRIGHT + text + colorama.Style.RESET_ALL
