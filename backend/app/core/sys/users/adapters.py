from typing import List

from app.core.resources.adapters import AdapterResources
from app.core.sys.users import models
from app.database.adapters import AdapterCRUD
from dpn_pyutils.common import get_logger
from sqlalchemy import select

log = get_logger(__name__)


class SysUsersAdapter(AdapterResources[models.SysUser]):
    """
    Additional SysUser database methods
    """

    async def get_by_email(self, email: str) -> models.SysUser | None:
        """
        Gets a user by email
        """
        stmt = select(self.table).where(self.table.email == email)  # type: ignore

        return self.session.execute(stmt).unique().scalar_one_or_none()


class SysUserTokensAdapter(AdapterCRUD[models.SysUserToken]):
    """
    SysUserToken database methods
    """

    async def get_by_token(
        self, token: str, token_type: str | None = None
    ) -> models.SysUserToken | None:
        """
        Gets a user token by token string
        """

        stmt = select(self.table).where(self.table.token == token)  # type: ignore

        if token_type is not None:
            stmt = stmt.where(self.table.token_type == token_type)

        return self.session.execute(stmt).unique().scalar_one_or_none()

    async def get_user_tokens(
        self, user: models.SysUser, token_type: str | None
    ) -> List[models.SysUserToken] | None:
        """
        Gets all the tokens for a specific user, optionally filtering by a specific token type
        """

        stmt = select(self.table).where(self.table.user_id == user.id)

        if token_type is not None:
            stmt = stmt.where(self.table.token_type == token_type)

        return [r for r in self.session.execute(stmt).all()]  # type: ignore
