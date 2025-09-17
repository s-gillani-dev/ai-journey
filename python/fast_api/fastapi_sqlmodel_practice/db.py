# db.py
"""
Database setup using SQLModel and SQLite.

- Creates a SQLite database file (db.sqlite).
- Initializes the engine for database interaction.
- Provides a session generator to interact with DB.
"""

from sqlmodel import create_engine, SQLModel, Session

# SQLite database URL (creates db.sqlite in project root)
DATABASE_URL = "sqlite:///db.sqlite"

# Create engine (connects SQLModel to SQLite)
engine = create_engine(DATABASE_URL, echo=True)  
# echo=True logs SQL queries to console for debugging

def init_db():
    """
    Initialize the database.
    - Creates all tables defined in SQLModel models (schemas).
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency that provides a database session.
    - Use with 'Depends(get_session)' in FastAPI routes.
    """
    with Session(engine) as session:
        yield session
