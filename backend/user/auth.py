import trafaret as trf

from .tables import auth_user
from backend.libs.password_hasher import (
    create_hashed_password,
    is_password_equals,
)
from backend.libs.auth import create_auth_token
from backend.settings import DEFAULT_LOGIN_TTL
from backend.resources import resources


USER_REGISTER_TRAFARET = trf.Dict({
    trf.Key('username'): trf.String(),
    trf.Key('email'): trf.String(),
    trf.Key('password'): trf.String(),
})


USER_LOGIN_TRAFARET = trf.Dict({
    trf.Key('username'): trf.String(),
    trf.Key('password'): trf.String(),
})


class ValidationError(Exception):
    pass


async def register_user(data) -> str:
    try:
        USER_REGISTER_TRAFARET.check(data)
    except trf.DataError:
        raise ValidationError('wrong data')

    query = auth_user.insert().values({
        'username': data['username'],
        'email': data['email'],
        'password': create_hashed_password(data['password']),
    }).returning(auth_user.c.id)
    result = dict(await resources.db.fetch_one(query=query))
    user_id = result['id']
    return create_auth_token(user_id, DEFAULT_LOGIN_TTL)


async def login_user(data):
    try:
        USER_LOGIN_TRAFARET.check(data)
    except trf.DataError:
        raise ValidationError('wrong data')

    query = (
        auth_user
        .select()
        .where(auth_user.c.username == data['username'])
    )
    result = dict(await resources.db.fetch_one(query=query))
    if not result:
        raise Exception('user not exists')
    if is_password_equals(data['password'], result['password']):
        return create_auth_token(result['id'], DEFAULT_LOGIN_TTL)
    else:
        return
