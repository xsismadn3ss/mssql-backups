from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence


def execute_command(command: Sequence[str], *, stream_output: bool = True) -> str:
    process = subprocess.Popen(
        list(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    output: list[str] = []
    assert process.stdout is not None

    for line in process.stdout:
        output.append(line)
        if stream_output:
            sys.stdout.write(line)
            sys.stdout.flush()

    return_code = process.wait()
    combined_output = "".join(output)

    if return_code != 0:
        raise subprocess.CalledProcessError(
            return_code,
            list(command),
            output=combined_output,
        )

    return combined_output
