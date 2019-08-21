"""empty message

Revision ID: 53dc9c8f5be4
Revises: 805ec9266db9
Create Date: 2019-08-21 12:29:46.872234

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '53dc9c8f5be4'
down_revision = '805ec9266db9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clients',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('client_name', sa.String(), nullable=True),
    sa.Column('client_id', sa.String(), nullable=True),
    sa.Column('client_secret', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oauth2_roles',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('date_created', sa.TIMESTAMP(), nullable=True),
    sa.Column('date_last_updated', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role'),
    sa.UniqueConstraint('role')
    )
    op.create_table('roles',
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('role_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['oauth2_roles.id'], ),
    sa.PrimaryKeyConstraint('client_id', 'role_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles')
    op.drop_table('oauth2_roles')
    op.drop_table('clients')
    # ### end Alembic commands ###