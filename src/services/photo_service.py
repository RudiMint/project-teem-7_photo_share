from fastapi import Request, Depends, HTTPException, status

from src.database.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        """
        Create an instance of RoleAccess.

        :param allowed_roles: List[Role]: The list of roles allowed to access the resource.
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self, request: Request, user: User = Depends(auth_service.get_current_user)
    ):
        """
        Check if the user has the required role to access the resource.

        :param request: Request: The incoming request.
        :param user: User: Current authenticated user dependency.
        :raises HTTPException 403: If the user does not have the required role.
        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            )
