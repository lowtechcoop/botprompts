from app.config import get_config
from app.core.auth.errors import InvalidPermission, UserLacksPermission
from app.core.auth.password import PasswordHelper
from app.core.auth.utils import get_user_permissions
from app.core.resources.adapters import AdapterResources
from app.core.sys.users.models import SysUser
from app.core.sys.variables import models, schemas
from app.core.sys.variables.models import SysVariable
from app.database.meta import get_session
from dpn_pyutils.common import get_logger
from fastapi import Depends
from sqlalchemy.orm import Session

log = get_logger(__name__)

config = get_config()


class VariablesLogicManager:
    """
    Defines a class that provides system variable management
    """

    sys_permissions: AdapterResources[models.SysPermission]
    sys_variables: AdapterResources[SysVariable]

    def __init__(self, session: Session) -> None:
        """
        Initializes the variable logic manager
        """

        self.sys_permissions = AdapterResources(
            session=session, table=models.SysPermission
        )
        self.sys_variables = AdapterResources(session=session, table=SysVariable)

        self.password_helper = PasswordHelper()

    async def get_variable(self, variable_name: str, current_user: SysUser | None):
        """
        Gets a variable, ensuring visibility permissions are met
        """

        variable = await self.sys_variables.get_by_name(variable_name)
        if variable is None:
            return None

        if len(variable.permissions) > 0 and current_user is None:
            raise UserLacksPermission("User does not provide credentials")

        if len(variable.permissions) > 0:
            # At least one current_user permission must be present in
            # the variable.permissions list
            user_permissions = get_user_permissions(current_user)
            found_matching_permission = False
            for p in variable.permissions:
                for up in user_permissions:
                    if up.id == p.id:
                        found_matching_permission = True
                        break

                if found_matching_permission:
                    break

            if not found_matching_permission:
                raise UserLacksPermission("Could not find matching permission")

        return variable

    async def create(
        self, create: schemas.VariableCreateSchema
    ) -> models.SysVariable | None:
        """
        Creates a variable with the supplied information
        """

        variable = await self.sys_variables.create(
            create.dict(include={"name", "value"})
        )

        if create.permissions is not None and len(create.permissions) > 0:
            for p in create.permissions:
                perm = await self.sys_permissions.get_by_name(p)
                if perm is None:
                    raise InvalidPermission(
                        f"Permission '{p}' does not exist or could not be found by name"
                    )

                variable.permissions.append(perm)

            variable = await self.sys_variables.apply_and_commit(variable)

    async def update(
        self, variable: models.SysVariable, update: schemas.VariableUpdateSchema
    ) -> models.SysVariable:
        """
        Updates a variable with the supplied information
        """

        if update.value is not None:
            variable = await self.sys_variables.update(
                variable, update.dict(include={"value"})
            )

        if update.permissions is not None:
            update_permission_list = []
            for p in update.permissions:
                perm = await self.sys_permissions.get_by_name(p)
                if perm is None:
                    raise InvalidPermission(
                        f"Permission '{p}' does not exist or could not be found by name"
                    )

                update_permission_list.append(perm)

            variable.permissions = update_permission_list
            variable = await self.sys_variables.apply_and_commit(variable)

        return variable


async def get_variables_manager(session: Session = Depends(get_session)):
    yield VariablesLogicManager(session)
