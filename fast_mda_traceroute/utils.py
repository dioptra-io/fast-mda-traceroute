def is_ipv4(addr: str) -> bool:
    """
    >>> is_ipv4("8.8.8.8")
    True
    >>> is_ipv4("::ffff:8.8.8.8")
    True
    >>> is_ipv4("2001:4860:4860::8888")
    False
    """
    return "." in addr
