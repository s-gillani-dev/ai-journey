# 📘 FastAPI + Alembic + SQLModel Guide

This guide explains how database migrations are handled in a **FastAPI** application using **Alembic** with **SQLModel**.

---

## 🔹 High-Level Flow
```
models.py → alembic revision --autogenerate → migration file → alembic upgrade → db.sqlite
```

---

## 🔹 Why Alembic?
- `SQLModel` (built on SQLAlchemy) can create tables with `SQLModel.metadata.create_all()`, but:
  - It **does not handle schema changes** (adding/removing fields).
  - Without Alembic, you’d need to drop/recreate tables manually.
- **Alembic** adds **versioned migrations** so schema changes are tracked and applied safely.

---

## 🔹 Setup Flow

### 1. Initialize Alembic
Run once in your project root:
```bash
alembic init migrations
```
This creates a `migrations/` folder with configs.

---

### 2. Configure `env.py`
In `migrations/env.py`, tell Alembic where your DB is and expose models:

```python
from pathlib import Path
from models import SQLModel

DB_PATH = str((Path().parent / 'db.sqlite').resolve())
config.set_main_option("sqlalchemy.url", f"sqlite:///{DB_PATH}")

# Point Alembic to SQLModel metadata (your models)
target_metadata = SQLModel.metadata
```

---

### 3. Update Template (`script.py.mako`)
By default, Alembic-generated files don’t import `sqlmodel`.  
Fix by editing `migrations/script.py.mako`:

```python
from alembic import op
import sqlalchemy as sa
import sqlmodel   # 👈 add this
${imports if imports else ""}
```

Now, every new migration automatically imports `sqlmodel`.

---

### 4. Create Initial Migration
Autogenerate migration from your models:
```bash
alembic revision --autogenerate -m "initial migration"
```

This creates a migration under `migrations/versions/`.  
Inside, you’ll see `op.create_table(...)` commands based on your models.

---

### 5. Apply Migration
Run migrations to update your DB schema:
```bash
alembic upgrade head
```

Now your `db.sqlite` contains all tables (`Band`, `Album`, etc.).
```