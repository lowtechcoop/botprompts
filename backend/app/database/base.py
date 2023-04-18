"""
This module contains the SqlAlchemy declarative base
"""
from dpn_pyutils.common import get_logger
from sqlalchemy import DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import FunctionElement

log = get_logger(__name__)

Base = declarative_base()


class utcnow(FunctionElement):
    type = DateTime()  # type: ignore
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pgsql_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(utcnow, "mssql")
def mssql_utcnow(element, compiler, **kw):
    return "GETUTCDATE()"


@compiles(utcnow, "mysql")
def mysql_utcnow(element, compiler, **kw):
    return "NOW()"
