from backend.app.services.sql_validator import (
    SQLValidationError,
    SQLValidator,
)


validator = SQLValidator()


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

print("Valid query test:")

try:
    result = validator.validate(valid_sql)
    print("PASSED")
    print(result)
except SQLValidationError as e:
    print("FAILED:", e)


unknown_table_sql = """
SELECT *
FROM imaginary_table;
"""

print("\nUnknown table test:")

try:
    validator.validate(unknown_table_sql)
    print("FAILED: unknown table was accepted")
except SQLValidationError as e:
    print("PASSED:", e)


unknown_column_sql = """
SELECT
    c.name,
    c.secret_column
FROM customers c;
"""

print("\nUnknown column test:")

try:
    validator.validate(unknown_column_sql)
    print("FAILED: unknown column was accepted")
except SQLValidationError as e:
    print("PASSED:", e)


dangerous_sql = """
DELETE FROM customers;
"""

print("\nDangerous query test:")

try:
    validator.validate(dangerous_sql)
    print("FAILED: dangerous query was accepted")
except SQLValidationError as e:
    print("PASSED:", e)