# Enums for better type safety
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    TRANSFER = "transfer"
    RETURN = "return"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SiteType(str, Enum):
    WAREHOUSE = "warehouse"
    STORE = "store"
    OFFICE = "office"
    OTHER = "other"
