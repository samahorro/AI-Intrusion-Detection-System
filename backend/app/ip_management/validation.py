
"""IP address validation for AEGIS backend."""

from ipaddress import ip_address


def validate_ip_address(value: str) -> str:
    """
    Validate and normalize an IPv4 or IPv6 address.
    """

    if not isinstance(value, str) or not value:
        raise ValueError("IP address must be a non-empty string.")

    if value != value.strip() or any(
        character.isspace() for character in value
    ):
        raise ValueError("IP address cannot contain whitespace.")

    if "/" in value:
        raise ValueError("CIDR ranges are not supported.")

    try:
        validated_ip = ip_address(value)
        return str(validated_ip)

    except ValueError as exc:
        raise ValueError(
            "Invalid IPv4 or IPv6 address."
        ) from exc
