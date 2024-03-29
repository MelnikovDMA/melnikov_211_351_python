"""add visits

Revision ID: f0d454656977
Revises: 62445b2f5a46
Create Date: 2023-06-30 09:21:09.509497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0d454656977'
down_revision = '62445b2f5a46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('visits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], name=op.f('fk_visits_book_id_books')),
    sa.ForeignKeyConstraint(['user_id'], ['books.id'], name=op.f('fk_visits_user_id_books')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_visits'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('visits')
    # ### end Alembic commands ###
