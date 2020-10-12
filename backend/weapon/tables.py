import sqlalchemy as sa
from sqlalchemy.sql import func

from backend.migrations import metadata


weapon = sa.Table(
    'weapon', metadata,
    sa.Column(
        'id',
        sa.BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
    ),
    sa.Column('name', sa.String(75), index=True, unique=True),
    sa.Column('characteristic1', sa.Float(), nullable=True),
    sa.Column('characteristic2', sa.Float(), nullable=True),
    sa.Column(
        'created_at',
        sa.DateTime(timezone=True),
        server_default=func.now()
    ),
    sa.Column(
        'updated_at',
        sa.DateTime(timezone=True),
        onupdate=func.now()
    )
)


user_weapons = sa.Table('user_weapons', metadata,
    sa.Column('user_id', sa.ForeignKey('auth_user.id')),
    sa.Column('weapon_id', sa.ForeignKey('weapon.id'))
)
