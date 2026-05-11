from __future__ import annotations

import inspect


def _signature_without(
    signature: inspect.Signature, hidden_params: set[str]
) -> inspect.Signature:
    parameters = [
        parameter
        for name, parameter in signature.parameters.items()
        if name not in hidden_params
    ]
    return signature.replace(parameters=parameters)
