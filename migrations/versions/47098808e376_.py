"""empty message

Revision ID: 47098808e376
Revises: None
Create Date: 2017-08-30 23:38:08.917000

"""

# revision identifiers, used by Alembic.
revision = '47098808e376'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tbl_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_category', sa.Integer(), nullable=False),
    sa.Column('name_category', sa.String(length=100), nullable=False),
    sa.Column('createDate', sa.TIMESTAMP(), nullable=False),
    sa.Column('updateDate', sa.TIMESTAMP(), nullable=False),
    sa.Column('isDelete', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tbl_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_item', sa.Integer(), nullable=False),
    sa.Column('name_item', sa.String(length=100), nullable=False),
    sa.Column('createDate', sa.TIMESTAMP(), nullable=False),
    sa.Column('updateDate', sa.TIMESTAMP(), nullable=False),
    sa.Column('isDelete', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tbl_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userid', sa.String(length=250), nullable=False),
    sa.Column('email', sa.String(length=250), nullable=False),
    sa.Column('password', sa.String(length=35), nullable=False),
    sa.Column('firstname', sa.String(length=150), nullable=True),
    sa.Column('lastname', sa.String(length=150), nullable=False),
    sa.Column('birthdate', sa.DATE(), nullable=False),
    sa.Column('registerdate', sa.TIMESTAMP(), nullable=False),
    sa.Column('updateDate', sa.TIMESTAMP(), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.Column('isDelete', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tbl_users')
    op.drop_table('tbl_item')
    op.drop_table('tbl_category')
    ### end Alembic commands ###