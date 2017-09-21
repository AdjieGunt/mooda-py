"""empty message

Revision ID: 2d3a7f133159
Revises: 15a46f3383a6
Create Date: 2017-09-15 17:58:22.050000

"""

# revision identifiers, used by Alembic.
revision = '2d3a7f133159'
down_revision = '15a46f3383a6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tbl_interested', sa.Column('id_item', sa.Integer(), nullable=True))
    op.add_column('tbl_interested', sa.Column('userid', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tbl_interested', 'tbl_item', ['id_item'], ['id'])
    op.create_foreign_key(None, 'tbl_interested', 'tbl_users', ['userid'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tbl_interested', type_='foreignkey')
    op.drop_constraint(None, 'tbl_interested', type_='foreignkey')
    op.drop_column('tbl_interested', 'userid')
    op.drop_column('tbl_interested', 'id_item')
    ### end Alembic commands ###