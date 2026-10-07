import re

from backend.app.services.schema_inspector import get_database_schema


class SQLValidationError(ValueError):
    """Raised when generated SQL fails validation."""


class SQLValidator:

    FORBIDDEN_KEYWORDS = {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE",
    }

    TABLE_PATTERN = re.compile(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
        r"(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?",
        re.IGNORECASE,
    )

    COLUMN_PATTERN = re.compile(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b"
    )

    def validate(self, sql: str) -> str:
        if not sql or not sql.strip():
            raise SQLValidationError(
                "SQL query cannot be empty."
            )

        cleaned_sql = sql.strip().rstrip(";").strip()

        self._validate_select_only(cleaned_sql)
        self._validate_forbidden_keywords(cleaned_sql)

        schema = get_database_schema()

        aliases = self._validate_tables(
            cleaned_sql,
            schema,
        )

        self._validate_columns(
            cleaned_sql,
            schema,
            aliases,
        )

        return cleaned_sql

    def _validate_select_only(self, sql: str) -> None:
        if not re.match(
            r"^SELECT\b",
            sql,
            re.IGNORECASE,
        ):
            raise SQLValidationError(
                "Only SELECT queries are allowed."
            )

    def _validate_forbidden_keywords(self, sql: str) -> None:
        if ";" in sql:
            raise SQLValidationError(
                "Multiple SQL statements are not allowed."
            )

        sql_upper = sql.upper()

        for keyword in self.FORBIDDEN_KEYWORDS:
            if re.search(
                rf"\b{keyword}\b",
                sql_upper,
            ):
                raise SQLValidationError(
                    f"Forbidden SQL operation detected: {keyword}"
                )

    def _validate_tables(
        self,
        sql: str,
        schema: dict,
    ) -> dict[str, str]:

        matches = self.TABLE_PATTERN.findall(sql)

        if not matches:
            raise SQLValidationError(
                "No database tables could be identified."
            )

        aliases = {}

        for table_name, alias in matches:

            if table_name.lower() not in schema:
                raise SQLValidationError(
                    f"Unknown table referenced: {table_name}"
                )

            table_name = table_name.lower()

            # SQL keywords should not be interpreted as aliases.
            if alias and alias.upper() not in {
                "ON",
                "WHERE",
                "GROUP",
                "ORDER",
                "LIMIT",
                "INNER",
                "LEFT",
                "RIGHT",
                "FULL",
                "CROSS",
                "JOIN",
            }:
                aliases[alias.lower()] = table_name

            aliases[table_name] = table_name

        return aliases

    def _validate_columns(
        self,
        sql: str,
        schema: dict,
        aliases: dict[str, str],
    ) -> None:

        column_matches = self.COLUMN_PATTERN.findall(sql)

        for table_reference, column_name in column_matches:

            table_reference = table_reference.lower()
            column_name = column_name.lower()

            if table_reference not in aliases:
                raise SQLValidationError(
                    f"Unknown table or alias: {table_reference}"
                )

            actual_table = aliases[table_reference]

            valid_columns = {
                column["name"].lower()
                for column in schema[actual_table]["columns"]
            }

            if column_name not in valid_columns:
                raise SQLValidationError(
                    f"Unknown column '{column_name}' "
                    f"in table '{actual_table}'"
                )