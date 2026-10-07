from sqlalchemy import text
from sqlalchemy.orm import Session


class SQLExecutor:

    def execute(
        self,
        db: Session,
        sql: str,
    ) -> list[dict]:

        result = db.execute(text(sql))

        rows = result.mappings().all()

        return [dict(row) for row in rows]