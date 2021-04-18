def set_destructive(payload: dict) -> dict:
    """CUP packet rewrites client config from scratch"""
    payload.update(FORCE=True)
    return payload