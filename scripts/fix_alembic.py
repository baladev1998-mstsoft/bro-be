import sys
import os
from sqlalchemy import create_engine, text

# Add the parent directory to sys.path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def fix_alembic_version():
    db_url = settings.SQLALCHEMY_DATABASE_URI_SYNC
    print(f"Connecting to {db_url}")
    engine = create_engine(db_url)
    
    target_revision = '9a502ab17128'
    
    with engine.connect() as connection:
        # Check if table exists
        result = connection.execute(text("SELECT to_regclass('alembic_version')"))
        if result.scalar() is None:
            print("alembic_version table does not exist. Creating it.")
            connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"))
            connection.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{target_revision}')"))
        else:
            print("alembic_version table exists. Updating it.")
            # Check if any row exists
            result = connection.execute(text("SELECT count(*) FROM alembic_version"))
            count = result.scalar()
            if count == 0:
                connection.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{target_revision}')"))
            else:
                connection.execute(text(f"UPDATE alembic_version SET version_num = '{target_revision}'"))
        
        connection.commit()
        print(f"Successfully set alembic version to {target_revision}")

if __name__ == "__main__":
    fix_alembic_version()
