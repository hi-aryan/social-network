"""Convert rating_workload from integer to enum

Revision ID: convert_workload_enum
Revises: 2b1e6e998022
Create Date: 2025-12-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'convert_workload_enum'
down_revision = '2b1e6e998022'
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type
    workload_enum = sa.Enum('light', 'medium', 'heavy', name='workloadlevel')
    workload_enum.create(op.get_bind(), checkfirst=True)
    
    # Add a temporary column with the new enum type
    op.add_column('post', sa.Column('rating_workload_new', 
                                     sa.Enum('light', 'medium', 'heavy', name='workloadlevel'),
                                     nullable=True))
    
    # Migrate data: 1-2 → 'light', 3 → 'medium', 4-5 → 'heavy'
    op.execute("""
        UPDATE post SET rating_workload_new = 
            CASE 
                WHEN rating_workload <= 2 THEN 'light'::workloadlevel
                WHEN rating_workload = 3 THEN 'medium'::workloadlevel
                ELSE 'heavy'::workloadlevel
            END
    """)
    
    # Drop the old column and rename the new one
    op.drop_column('post', 'rating_workload')
    op.alter_column('post', 'rating_workload_new', new_column_name='rating_workload', nullable=False)


def downgrade():
    # Add a temporary integer column
    op.add_column('post', sa.Column('rating_workload_old', sa.Integer(), nullable=True))
    
    # Convert enum back to integers: 'light' → 1, 'medium' → 3, 'heavy' → 5
    op.execute("""
        UPDATE post SET rating_workload_old = 
            CASE rating_workload::text
                WHEN 'light' THEN 1
                WHEN 'medium' THEN 3
                WHEN 'heavy' THEN 5
            END
    """)
    
    # Drop the enum column and rename the integer column
    op.drop_column('post', 'rating_workload')
    op.alter_column('post', 'rating_workload_old', new_column_name='rating_workload', nullable=False)
    
    # Drop the enum type
    sa.Enum('light', 'medium', 'heavy', name='workloadlevel').drop(op.get_bind(), checkfirst=True)

