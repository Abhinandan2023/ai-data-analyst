from pprint import pprint

from backend.app.db.connection import SessionLocal
from backend.app.services.sql_executor import SQLExecutor


sql = """
SELECT
    c.id,
    c.name,
    c.email,
    SUM(oi.quantity * oi.unit_price) AS total_spending
FROM customers c
JOIN orders o
    ON c.id = o.customer_id
JOIN order_items oi
    ON o.id = oi.order_id
WHERE o.status = 'completed'
GROUP BY c.id, c.name, c.email
ORDER BY total_spending DESC
LIMIT 1
"""


db = SessionLocal()

try:
    executor = SQLExecutor()

    result = executor.execute(
        db=db,
        sql=sql,
    )

    pprint(result)

finally:
    db.close()