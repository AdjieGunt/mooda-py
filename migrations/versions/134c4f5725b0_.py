"""empty message

Revision ID: 134c4f5725b0
Revises: 1d548af42928
Create Date: 2017-08-31 00:14:57.674000

"""

# revision identifiers, used by Alembic.
revision = '134c4f5725b0'
down_revision = '1d548af42928'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tbl_item', sa.Column('id_category', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tbl_item', 'tbl_category', ['id_category'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tbl_item', type_='foreignkey')
    op.drop_column('tbl_item', 'id_category')
    ### end Alembic commands ###
