from fastapi import HTTPException, status


class OrganizationNotFoundException(HTTPException):
    def __init__(self, org_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_name}' not found"
        )


class OrganizationAlreadyExistsException(HTTPException):
    def __init__(self, org_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization '{org_name}' already exists"
        )


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
