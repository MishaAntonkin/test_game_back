import sqlalchemy as sa
import trafaret as trf

from backend.user.tables import auth_user
from backend.weapon.tables import weapon, user_weapons
from backend.resources import resources
from backend.libs.auth import parse_user_id_from_auth_token
from backend.utils.jrpc import format_jrpc_response
from backend.methods_handler import BaseMethodHandler


class UserInfoMethodHandler(BaseMethodHandler):
    method = 'user.info'

    async def handle(self, message):
        """message"""
        db = resources.db
        user_id = parse_user_id_from_auth_token(message['id'])
        user_query = (
            sa.select([
                auth_user.c.id, auth_user.c.username, auth_user.c.email,
            ])
            .where(auth_user.c.id == user_id)
        )
        user_db_resp = await db.fetch_one(query=user_query)
        weapons_query = (
            sa.select([weapon.c.id, weapon.c.name])
            .select_from(
                weapon.join(
                    user_weapons, weapon.c.id == user_weapons.c.weapon_id,
                )
            )
            .where(user_weapons.c.user_id == user_id)
        )
        users_weapon_db_resp = await db.fetch_all(query=weapons_query)
        weapons = [dict(w) for w in users_weapon_db_resp]
        return format_jrpc_response(
            data=dict(**user_db_resp, weapons=weapons),
            id=message['id'],
        )


UserChangeTrafaret = trf.Dict({
    trf.Key('level', optional=True): trf.Float(gte=1),
    trf.Key('weapons', optional=True): trf.List(trf.Int(gt=0)),
})


class UserChangeMethodHandler(BaseMethodHandler):
    method = 'user.change'

    def get_invalid_message(self, id):
        return format_jrpc_response(
            error={'message': 'invalid params'},
            id=id,
        )

    async def handle(self, message):
        db = resources.db
        user_id = parse_user_id_from_auth_token(message['id'])
        params = message.get('params')
        if not params:
            return self.get_invalid_message(message['id'])
        try:
            UserChangeTrafaret.check(params)
        except trf.DataError:
            return self.get_invalid_message(message['id'])
        weapons_insert_query = user_weapons.insert()
        weapons_insert_values = [
            {"user_id": user_id, "weapon_id": w_id}
            for w_id in message['params']['weapons']
        ]

        await db.execute_many(
            weapons_insert_query, values=weapons_insert_values,
        )

        user_update_query = (
            auth_user.update()
            .where(auth_user.c.id == user_id)
            .values({'level': params['level']})
        )
        await db.execute(user_update_query)

        return format_jrpc_response(data={'status': 'ok'}, id=message['id'])
