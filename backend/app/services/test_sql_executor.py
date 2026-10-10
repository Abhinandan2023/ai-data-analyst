from backend.app.db.connection import SessionLocal
from backend.app.services.sql_executor import SQLExecutor


def test_sql_executor_returns_top_customer():
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

        assert len(result) == 1
        assert result[0]["name"] == "Rahul Sharma"
        assert result[0]["total_spending"] == 219000.00

    finally:
        db.close()
def test_sql_executor_returns_monthly_revenue():
    sql = """
    SELECT
        DATE_TRUNC('month', o.order_date) AS revenue_month,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM orders o
    JOIN order_items oi
        ON o.id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY DATE_TRUNC('month', o.order_date)
    ORDER BY revenue_month
    """

    db = SessionLocal()

    try:
        executor = SQLExecutor()
        result = executor.execute(db=db, sql=sql)

        assert len(result) == 2

        assert result[0]["revenue_month"].month == 8
        assert float(result[0]["total_revenue"]) == 263000.00

        assert result[1]["revenue_month"].month == 9
        assert float(result[1]["total_revenue"]) == 177500.00

    finally:
        db.close()


def test_sql_executor_returns_monthly_revenue():
    sql = """
    SELECT
        DATE_TRUNC('month', o.order_date) AS revenue_month,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM orders o
    JOIN order_items oi
        ON o.id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY DATE_TRUNC('month', o.order_date)
    ORDER BY revenue_month
    """

    db = SessionLocal()
    try:
        executor = SQLExecutor()
        result = executor.execute(db, sql)

        assert len(result) == 2
        assert result[0]["total_revenue"] == 263000.00
        assert result[1]["total_revenue"] == 177500.00
    finally:
        db.close()