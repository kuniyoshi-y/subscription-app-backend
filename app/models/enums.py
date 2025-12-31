import enum

class CategoryType(str, enum.Enum):
    fixed = "fixed"
    subscription = "subscription"
    semi_fixed = "semi_fixed"

class BillingCycle(str, enum.Enum):
    monthly = "monthly"
    yearly = "yearly"
    other = "other"
