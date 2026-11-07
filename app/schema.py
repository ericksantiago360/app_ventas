"""Agrega columnas nuevas a tablas existentes.

El proyecto no usa Flask-Migrate todavía: db.create_all() crea tablas nuevas
pero no altera las que ya existen. Esta función agrega las columnas que falten
para que una base de datos anterior siga funcionando.
"""
from sqlalchemy import inspect, text


def add_missing_columns(db):
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()
    with db.engine.begin() as conn:
        for table in db.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            current = {c['name'] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in current:
                    continue
                col_type = column.type.compile(dialect=db.engine.dialect)
                ddl = f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {col_type}'
                default = column.default.arg if column.default is not None and column.default.is_scalar else None
                if default is not None:
                    literal = f"'{default}'" if isinstance(default, str) else str(default)
                    ddl += f' DEFAULT {literal}'
                conn.execute(text(ddl))
