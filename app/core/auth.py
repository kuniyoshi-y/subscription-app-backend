"""Cognito JWT検証モジュール

API Gatewayで1次検証済みのトークンをFastAPI側でも検証する（二重チェック）。
"""

import urllib.request
import json
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode

from app.core.config import settings

security = HTTPBearer()


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    """CognitoのJWKS（公開鍵セット）を取得してキャッシュする"""
    url = (
        f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com"
        f"/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    )
    with urllib.request.urlopen(url) as res:
        return json.loads(res.read())


def verify_token(token: str) -> dict:
    """JWTトークンを検証してクレーム（payload）を返す"""
    jwks = _get_jwks()

    try:
        # トークンのヘッダーからkidを取得
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

    # kidに対応する公開鍵を探す
    key = next(
        (k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]),
        None,
    )
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Public key not found",
        )

    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.COGNITO_CLIENT_ID,
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
        )

    return claims


def get_current_user_sub(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """JWTを検証してCognitoのsubを返す"""
    claims = verify_token(credentials.credentials)
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="sub claim not found",
        )
    return sub


def get_current_claims(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """JWTを検証してclaimsを全て返す（email等の取得に使う）"""
    return verify_token(credentials.credentials)
