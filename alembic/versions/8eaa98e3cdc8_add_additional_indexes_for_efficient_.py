"""Add additional indexes for efficient querying

Revision ID: 8eaa98e3cdc8
Revises: 7de024b4d320
Create Date: 2024-07-18 18:00:57.167131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8eaa98e3cdc8'
down_revision: Union[str, None] = '7de024b4d320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_customers_date_created'), 'customers', ['date_created'], unique=False)
    op.create_index(op.f('ix_customers_date_updated'), 'customers', ['date_updated'], unique=False)
    op.create_index('ix_customers_name_code', 'customers', ['name', 'code'], unique=False)
    op.create_index(op.f('ix_orders_amount'), 'orders', ['amount'], unique=False)
    op.create_index(op.f('ix_orders_customer_id'), 'orders', ['customer_id'], unique=False)
    op.create_index('ix_orders_customer_id_time', 'orders', ['customer_id', 'time'], unique=False)
    op.create_index(op.f('ix_orders_date_created'), 'orders', ['date_created'], unique=False)
    op.create_index(op.f('ix_orders_date_updated'), 'orders', ['date_updated'], unique=False)
    op.create_index(op.f('ix_orders_item'), 'orders', ['item'], unique=False)
    op.create_index(op.f('ix_orders_time'), 'orders', ['time'], unique=False)
    op.create_index('ix_orders_time_amount', 'orders', ['time', 'amount'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_orders_time_amount', table_name='orders')
    op.drop_index(op.f('ix_orders_time'), table_name='orders')
    op.drop_index(op.f('ix_orders_item'), table_name='orders')
    op.drop_index(op.f('ix_orders_date_updated'), table_name='orders')
    op.drop_index(op.f('ix_orders_date_created'), table_name='orders')
    op.drop_index('ix_orders_customer_id_time', table_name='orders')
    op.drop_index(op.f('ix_orders_customer_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_amount'), table_name='orders')
    op.drop_index('ix_customers_name_code', table_name='customers')
    op.drop_index(op.f('ix_customers_date_updated'), table_name='customers')
    op.drop_index(op.f('ix_customers_date_created'), table_name='customers')
    # ### end Alembic commands ###
