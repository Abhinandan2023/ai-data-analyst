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

    CTE_PATTERN = re.compile(
        r"\bWITH\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\(",
        re.IGNORECASE,
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

        cte_columns = self._extract_cte_columns(
            cleaned_sql
        )

        aliases = self._validate_tables(
            cleaned_sql,
            schema,
            cte_columns,
        )

        self._validate_columns(
            cleaned_sql,
            schema,
            aliases,
            cte_columns,
        )

        return cleaned_sql

    def _validate_select_only(self, sql: str) -> None:
        if not re.match(
            r"^(SELECT\b|WITH\b)",
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

    def _extract_cte_columns(
        self,
        sql: str,
    ) -> dict[str, set[str]]:
        """
        Extract columns exposed by CTEs.

        Supports patterns such as:

            o.id AS order_id
            o.customer_id
            SUM(...) AS order_total
        """

        cte_columns = {}

        for match in self.CTE_PATTERN.finditer(sql):
            cte_name = match.group(1).lower()

            start = match.end()
            depth = 1
            position = start

            while position < len(sql) and depth > 0:
                if sql[position] == "(":
                    depth += 1
                elif sql[position] == ")":
                    depth -= 1

                position += 1

            cte_body = sql[start:position - 1]

            columns = set()

            # Capture explicitly aliased expressions:
            #
            # o.id AS order_id
            # SUM(...) AS order_total
            alias_pattern = re.compile(
                r"\bAS\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
                re.IGNORECASE,
            )

            for alias_match in alias_pattern.finditer(
                cte_body
            ):
                columns.add(
                    alias_match.group(1).lower()
                )

            # Capture simple qualified columns without aliases:
            #
            # o.customer_id
            #
            # Only inspect the SELECT portion of the CTE.
            select_match = re.search(
                r"\bSELECT\b(.*?)\bFROM\b",
                cte_body,
                re.IGNORECASE | re.DOTALL,
            )

            if select_match:
                select_clause = select_match.group(1)

                qualified_column_pattern = re.compile(
                    r"\b[a-zA-Z_][a-zA-Z0-9_]*\."
                    r"([a-zA-Z_][a-zA-Z0-9_]*)\b"
                )

                for column_match in qualified_column_pattern.finditer(
                    select_clause
                ):
                    column_name = column_match.group(1).lower()

                    columns.add(column_name)

            cte_columns[cte_name] = columns

        return cte_columns

    def _validate_tables(
        self,
        sql: str,
        schema: dict,
        cte_columns: dict[str, set[str]],
    ) -> dict[str, str]:

        cte_names = set(cte_columns.keys())

        matches = self.TABLE_PATTERN.findall(sql)

        if not matches:
            raise SQLValidationError(
                "No database tables could be identified."
            )

        aliases = {}

        for table_name, alias in matches:

            table_name = table_name.lower()

            # Physical database table OR CTE.
            if (
                table_name not in schema
                and table_name not in cte_names
            ):
                raise SQLValidationError(
                    f"Unknown table referenced: {table_name}"
                )

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
        cte_columns: dict[str, set[str]],
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

            # Validate columns coming from a CTE.
            if actual_table in cte_columns:

                valid_columns = cte_columns[actual_table]

                if column_name not in valid_columns:
                    raise SQLValidationError(
                        f"Unknown column '{column_name}' "
                        f"in CTE '{actual_table}'"
                    )

                continue

            # Validate columns coming from physical tables.
            valid_columns = {
                column["name"].lower()
                for column in schema[actual_table]["columns"]
            }

            if column_name not in valid_columns:
                raise SQLValidationError(
                    f"Unknown column '{column_name}' "
                    f"in table '{actual_table}'"
                )
                