"""empty message

Revision ID: build_and_release_artifacts_
Revises: remove_tag_from_release_
Create Date: 2021-12-20 14:14:11.894267

"""

# revision identifiers, used by Alembic.
revision = 'build_and_release_artifacts_'
down_revision = 'remove_tag_from_release_'

from alembic import op
import sqlalchemy as sa


from alembic import context


def upgrade():
    upgrades_pre()
    schema_upgrades()
    upgrades_post()


def downgrade():
    downgrades_pre()
    schema_downgrades()
    downgrades_post()


def upgrades_pre():
    """Add any optional data prep pre migrations here!"""
    pass


def schema_upgrades():
    """schema upgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('build_artifact',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('build_id', sa.String(), nullable=False),
    sa.Column('input_repo_id', sa.String(), nullable=False),
    sa.Column('output_repo_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('upload_path', sa.String(), nullable=False),
    sa.Column('data', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['input_repo_id'], ['repo.id'], onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['output_repo_id'], ['repo.id'], onupdate='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('release_artifact',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('release_id', sa.String(), nullable=False),
    sa.Column('input_repo_id', sa.String(), nullable=False),
    sa.Column('output_repo_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('upload_path', sa.String(), nullable=False),
    sa.Column('data', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['input_repo_id'], ['repo.id'], onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['output_repo_id'], ['repo.id'], onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['release_id'], ['release.id'], onupdate='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def upgrades_post():
    """Add any optional data prep post migrations here!"""
    pass


def downgrades_pre():
    """Add any optional data prep pre migrations here!"""
    pass


def schema_downgrades():
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('release_artifact')
    op.drop_table('build_artifact')
    # ### end Alembic commands ###


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass