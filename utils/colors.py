import colorama


def fore_green(text: str) -> str:
    return str(colorama.Fore.GREEN) + text + str(colorama.Fore.RESET)


def fore_yellow(text: str) -> str:
    return str(colorama.Fore.YELLOW) + text + str(colorama.Fore.RESET)


def fore_light_cyan(text: str) -> str:
    return str(colorama.Fore.LIGHTCYAN_EX) + text + str(colorama.Fore.RESET)


def fore_light_green(text: str) -> str:
    return str(colorama.Fore.LIGHTGREEN_EX) + text + str(colorama.Fore.RESET)


def style_dim(text: str) -> str:
    return str(colorama.Style.DIM) + text + str(colorama.Style.RESET_ALL)


def style_bright(text: str) -> str:
    return str(colorama.Style.BRIGHT) + text + str(colorama.Style.RESET_ALL)
