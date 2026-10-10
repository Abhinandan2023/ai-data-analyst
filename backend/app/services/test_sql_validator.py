import pytest

from backend.app.services.sql_validator import (
    SQLValidationError,
    SQLValidator,
)


validator = SQLValidator()


def test_valid_sql_is_accepted():
    valid_sql = """
    SELECT
        c.name,
        SUM(oi.quantity * oi.unit_price) AS total_spending
    FROM customers c
    JOIN orders o
        ON o.customer_id = c.id
    JOIN order_items oi
        ON oi.order_id = o.id
    GROUP BY c.name
    ORDER BY total_spending DESC
    LIMIT 1;
    """

    result = validator.validate(valid_sql)

    assert result
    assert result.upper().startswith("SELECT")


def test_unknown_table_is_rejected():
    unknown_table_sql = """
    SELECT *
    FROM imaginary_table;
    """

    with pytest.raises(
        SQLValidationError,
        match="Unknown table referenced: imaginary_table",
    ):
        validator.validate(unknown_table_sql)


def test_unknown_column_is_rejected():
    unknown_column_sql = """
    SELECT
        c.name,
        c.secret_column
    FROM customers c;
    """

    with pytest.raises(
        SQLValidationError,
        match="Unknown column 'secret_column' in table 'customers'",
    ):
        validator.validate(unknown_column_sql)


def test_dangerous_sql_is_rejected():
    dangerous_sql = """
    DELETE FROM customers;
    """

    with pytest.raises(
        SQLValidationError,
        match="Only SELECT queries are allowed",
    ):
        validator.validate(dangerous_sql)

def test_cte_select_sql_is_accepted():
    validator = SQLValidator()

    sql = """
    WITH order_totals AS (
        SELECT
            o.id AS order_id,
            o.customer_id,
            SUM(oi.quantity * oi.unit_price) AS order_total
        FROM orders o
        JOIN order_items oi
            ON o.id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY o.id, o.customer_id
    )
    SELECT
        c.id,
        c.name,
        AVG(ot.order_total) AS average_order_value
    FROM customers c
    JOIN order_totals ot
        ON c.id = ot.customer_id
    GROUP BY c.id, c.name
    ORDER BY average_order_value DESC
    LIMIT 1;
    """

    result = validator.validate(sql)

    assert result.startswith("WITH")
    assert "SELECT" in result.upper()
    assert "AVG" in result.upper()

def test_empty_sql_is_rejected():
    with pytest.raises(
        SQLValidationError,
        match="SQL query cannot be empty",
    ):
        validator.validate("")


def test_multiple_sql_statements_are_rejected():
    sql = """
    SELECT c.id FROM customers c;
    DELETE FROM customers
    """

    with pytest.raises(
        SQLValidationError,
        match="Multiple SQL statements are not allowed",
    ):
        validator.validate(sql)

def test_unknown_unqualified_column_is_rejected():
    sql = """
    SELECT nonexistent_column
    FROM customers;
    """

    with pytest.raises(SQLValidationError):
        validator.validate(sql)