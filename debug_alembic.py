from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from app.core.config import settings

def check_current_head():
    url = settings.SQLALCHEMY_DATABASE_URI
    engine = create_engine(url)
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    current_rev = context.get_current_revision()
    print(f"Current revision in DB: {current_rev}")
    
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    print(f"Script heads: {script.get_heads()}")
    
    print("Revisions in script directory:")
    for rev in script.walk_revisions():
        print(f"{rev.revision} (down: {rev.down_revision})")

if __name__ == "__main__":
    check_current_head()
