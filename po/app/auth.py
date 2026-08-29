import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException, status

from app.config import settings
from app.db import supabase

_jwks_client = PyJWKClient(settings.supabase_jwks_url)


class AuthedUser:
    def __init__(self, user_id: str, org_id: str, email: str | None = None):
        self.user_id = user_id
        self.org_id = org_id
        self.email = email


def _verify_token(token: str) -> dict:
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience="authenticated",
        )
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )


async def get_current_user(authorization: str = Header(...)) -> AuthedUser:
    """
    Verifies the Supabase-issued JWT sent from the frontend and resolves
    which organization (tenant) this user belongs to, via the `profiles` table.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    payload = _verify_token(token)
    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject")

    profile = (
        supabase.table("profiles")
        .select("org_id")
        .eq("id", user_id)
        .single()
        .execute()
    )

    if not profile.data:
        raise HTTPException(
            status_code=403,
            detail="No organization is linked to this account yet.",
        )

    return AuthedUser(user_id=user_id, org_id=profile.data["org_id"], email=email)
