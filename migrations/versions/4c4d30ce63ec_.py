"""empty message

Revision ID: 4c4d30ce63ec
Revises: 48a34fbbe398
Create Date: 2017-09-08 19:07:21.163000

"""

# revision identifiers, used by Alembic.
revision = '4c4d30ce63ec'
down_revision = '48a34fbbe398'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tbl_category', 'createDate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('tbl_category', 'updateDate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('tbl_item', 'createDate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('tbl_item', 'updateDate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tbl_item', 'updateDate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('tbl_item', 'createDate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('tbl_category', 'updateDate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('tbl_category', 'createDate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    ### end Alembic commands ###