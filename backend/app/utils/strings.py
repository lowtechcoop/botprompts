"""
This module is for stateless methods that help with strings and formatting
"""
import decimal
import uuid
from datetime import datetime

from dpn_pyutils.common import get_logger

log = get_logger(__name__)


def dict_to_str(payload: dict) -> str:
    """
    Converts a dictionary to json string
    """
    return str(payload)


def qds_json_serializer(obj, *args, **kwargs) -> dict[str, str] | str:
    """Serialises known types to their string versions"""

    if isinstance(obj, uuid.UUID):
        return str(uuid)

    elif isinstance(obj, datetime):
        return obj.isoformat()

    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    else:
        log.warning(
            "Type '{}' is not JSON serializable for {}".format(type(obj), str(obj))
        )
        raise TypeError(obj)
