from enum import Enum


class IntentType(str, Enum):
    IDENTIFY_TOP_CUSTOMER = "identify_top_customer"
    CALCULATE_TOTAL_REVENUE = "calculate_total_revenue"