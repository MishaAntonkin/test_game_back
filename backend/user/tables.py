import sqlalchemy as sa
from sqlalchemy.sql import func

from backend.migrations import metadata


auth_user = sa.Table(
    'auth_user', metadata,
    sa.Column(
        'id',
        sa.BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
    ),
    sa.Column('email', sa.String(75), nullable=True),
    sa.Column('username', sa.String(75), index=True, unique=True),
    sa.Column('password', sa.String()),
    sa.Column('level', sa.Float(), default=1),
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
