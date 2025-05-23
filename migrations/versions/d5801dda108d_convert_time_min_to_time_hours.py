"""Convert time_min to time_hours

Revision ID: d5801dda108d
Revises: 206a05314de9
Create Date: 2025-05-23 16:08:20.898077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5801dda108d'
down_revision = '206a05314de9'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column
    op.add_column('jobs', sa.Column('time_hours', sa.Float(), nullable=True))
    
    # Convert existing data from minutes to hours (divide by 60)
    # SQLite doesn't support direct UPDATE with expression, so we do it via SQL
    op.execute("UPDATE jobs SET time_hours = CAST(time_min AS REAL) / 60.0 WHERE time_min IS NOT NULL")
    
    # Drop the old column
    op.drop_column('jobs', 'time_min')


def downgrade():
    # Add the old column back
    op.add_column('jobs', sa.Column('time_min', sa.Integer(), nullable=True))
    
    # Convert existing data from hours to minutes (multiply by 60)
    op.execute("UPDATE jobs SET time_min = CAST(time_hours * 60.0 AS INTEGER) WHERE time_hours IS NOT NULL")
    
    # Drop the new column
    op.drop_column('jobs', 'time_hours')
