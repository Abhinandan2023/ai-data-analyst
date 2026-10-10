
import re

import sqlglot
from sqlglot import exp

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
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)"
        r"\.([a-zA-Z_][a-zA-Z0-9_]*)\b"
    )

    def validate(self, sql: str) -> str:
        """Validate generated SQL and return the cleaned query."""
        if not sql or not sql.strip():
            raise SQLValidationError("SQL query cannot be empty.")

        cleaned_sql = sql.strip().rstrip(";").strip()

        self._validate_sql_syntax(cleaned_sql)
        self._validate_select_only(cleaned_sql)
        self._validate_forbidden_keywords(cleaned_sql)

        schema = get_database_schema()
        cte_columns = self._extract_cte_columns(cleaned_sql)

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

        self._validate_unqualified_columns(
            cleaned_sql,
            schema,
            cte_columns,
        )

        return cleaned_sql

    def _validate_sql_syntax(self, sql: str) -> None:
        """Check SQL syntax and ensure only one query is present."""
        try:
            statements = sqlglot.parse(sql, read="postgres")

            if len(statements) > 1:
                raise SQLValidationError(
                    "Multiple SQL statements are not allowed."
                )

            if not statements or statements[0] is None:
                raise SQLValidationError("Invalid SQL syntax.")

            statement = statements[0]

            if not isinstance(statement, exp.Query):
                raise SQLValidationError(
                    "Only SELECT queries are allowed."
                )

        except SQLValidationError:
            raise
        except sqlglot.errors.ParseError as exc:
            raise SQLValidationError(
                "Invalid SQL syntax."
            ) from exc

    def _validate_select_only(self, sql: str) -> None:
        """Allow SELECT statements, including statements using CTEs."""
        if not re.match(
            r"^(SELECT\b|WITH\b)",
            sql,
            re.IGNORECASE,
        ):
            raise SQLValidationError(
                "Only SELECT queries are allowed."
            )

    def _validate_forbidden_keywords(self, sql: str) -> None:
        """Reject multiple statements and forbidden SQL operations."""
        if ";" in sql:
            raise SQLValidationError(
                "Multiple SQL statements are not allowed."
            )

        for keyword in self.FORBIDDEN_KEYWORDS:
            if re.search(
                rf"\b{keyword}\b",
                sql,
                re.IGNORECASE,
            ):
                raise SQLValidationError(
                    f"Forbidden SQL operation detected: {keyword}"
                )

    def _extract_cte_columns(
        self,
        sql: str,
    ) -> dict[str, set[str]]:
        """Extract CTE names and their output columns using SQLGlot."""
        cte_columns: dict[str, set[str]] = {}

        try:
            query = sqlglot.parse_one(sql, read="postgres")
        except sqlglot.errors.ParseError as exc:
            raise SQLValidationError(
                "Invalid SQL syntax."
            ) from exc

        for cte in query.find_all(exp.CTE):
            # Get the CTE name directly from its alias.
            alias_node = cte.args.get("alias")

            if alias_node is not None and alias_node.this is not None:
                cte_name = alias_node.this.name.lower()
            else:
                cte_name = cte.alias_or_name.lower()

            cte_query = cte.this

            if isinstance(cte_query, exp.Subquery):
                cte_query = cte_query.this

            if isinstance(cte_query, exp.Select):
                select = cte_query
            else:
                select = cte_query.find(exp.Select)

            columns: set[str] = set()

            if select is not None:
                for projection in select.expressions:
                    if projection.alias:
                        columns.add(projection.alias.lower())
                    elif isinstance(projection, exp.Column):
                        columns.add(projection.name.lower())
                    elif projection.output_name:
                        columns.add(projection.output_name.lower())

            # Support explicitly declared CTE columns:
            # WITH customer_avg (customer_id, avg_value) AS (...)
            if alias_node is not None:
                for identifier in (
                    alias_node.args.get("columns") or []
                ):
                    columns.add(identifier.name.lower())

            cte_columns[cte_name] = columns

        return cte_columns

    def _validate_tables(
        self,
        sql: str,
        schema: dict,
        cte_columns: dict[str, set[str]],
    ) -> dict[str, str]:
        """Validate physical tables and recognize CTE references."""
        cte_names = set(cte_columns.keys())
        matches = self.TABLE_PATTERN.findall(sql)

        if not matches:
            raise SQLValidationError(
                "No database tables could be identified."
            )

        aliases: dict[str, str] = {}

        reserved_words = {
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
            "HAVING",
            "UNION",
            "OFFSET",
            "SET",
            "AS",
            "AND",
            "OR",
        }

        for table_name, alias in matches:
            table_name = table_name.lower()
            alias = alias.lower()

            if (
                table_name not in schema
                and table_name not in cte_names
            ):
                raise SQLValidationError(
                    f"Unknown table referenced: {table_name}"
                )

            if alias and alias.upper() not in reserved_words:
                aliases[alias] = table_name

            aliases[table_name] = table_name

        return aliases

    def _validate_columns(
        self,
        sql: str,
        schema: dict,
        aliases: dict[str, str],
        cte_columns: dict[str, set[str]],
    ) -> None:
        """Validate qualified column references."""
        column_matches = self.COLUMN_PATTERN.findall(sql)

        for table_reference, column_name in column_matches:
            table_reference = table_reference.lower()
            column_name = column_name.lower()

            if table_reference not in aliases:
                raise SQLValidationError(
                    f"Unknown table or alias: {table_reference}"
                )

            actual_table = aliases[table_reference]

            if actual_table in cte_columns:
                valid_columns = cte_columns[actual_table]

                if column_name not in valid_columns:
                    raise SQLValidationError(
                        f"Unknown column '{column_name}' "
                        f"in CTE '{actual_table}'"
                    )

                continue

            valid_columns = {
                column["name"].lower()
                for column in schema[actual_table]["columns"]
            }

            if column_name not in valid_columns:
                raise SQLValidationError(
                    f"Unknown column '{column_name}' "
                    f"in table '{actual_table}'"
                )

    def _validate_unqualified_columns(
        self,
        sql: str,
        schema: dict,
        cte_columns: dict[str, set[str]],
    ) -> None:
        """Validate unqualified columns and allow SELECT aliases."""
        statements = sqlglot.parse(sql, read="postgres")

        if not statements or statements[0] is None:
            raise SQLValidationError("Invalid SQL syntax.")

        query = statements[0]

        for select in query.find_all(exp.Select):
            scope_tables: dict[str, str] = {}

            # Identify tables visible to this SELECT.
            for table in select.find_all(exp.Table):
                table_name = table.name.lower()
                alias = (
                    table.alias.lower()
                    if table.alias
                    else table_name
                )

                if (
                    table_name in schema
                    or table_name in cte_columns
                ):
                    scope_tables[alias] = table_name

            # Aliases such as total_spending in ORDER BY are valid.
            select_aliases = {
                projection.alias.lower()
                for projection in select.expressions
                if projection.alias
            }

            for column in select.find_all(exp.Column):
                if column.table:
                    continue

                name = column.name.lower()

                if name == "*" or name in select_aliases:
                    continue

                matching_tables = []

                for table_name in scope_tables.values():
                    if table_name in schema:
                        valid_columns = {
                            item["name"].lower()
                            for item in schema[table_name]["columns"]
                        }
                    elif table_name in cte_columns:
                        valid_columns = cte_columns[table_name]
                    else:
                        continue

                    if name in valid_columns:
                        matching_tables.append(table_name)

                if not matching_tables:
                    raise SQLValidationError(
                        f"Unknown unqualified column: {name}"
                    )
