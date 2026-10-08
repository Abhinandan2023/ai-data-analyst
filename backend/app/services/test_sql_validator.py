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