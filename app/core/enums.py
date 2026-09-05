from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEREGISTERED = "deregistered"


class Environment(str, Enum):
    DEV = "dev"
    TEST = "test"
    QA = "qa"
    PPD = "ppd"
    PROD = "prod"