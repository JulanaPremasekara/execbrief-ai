from alembic import op
from execbrief.infrastructure.database.models.metrics import metadata
revision="0001_metrics"
down_revision=None
branch_labels=None
depends_on=None
def upgrade():
    metadata.create_all(op.get_bind())
def downgrade():
    raise RuntimeError("Destructive downgrade requires an explicit reviewed migration")

