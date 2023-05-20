from typing import Callable, Type

from app.core.resources.adapters import AdapterResources
from app.core.resources.models import BRR
from app.database.meta import get_session
from dpn_pyutils.common import get_logger
from fastapi import Depends
from sqlalchemy.orm import Session

log = get_logger(__name__)


def get_adapter(record: Type[BRR]) -> Callable[[Session], AdapterResources[BRR]]:
    """
    Callable that creates a generic database adapter for the Resource models
    """

    def get_adapter_repository(session: Session = Depends(get_session)):
        return AdapterResources(session=session, table=record)

    return get_adapter_repository
