from dataclasses import dataclass

@dataclass(frozen=True)
class LogConfig:
    SYSTEM: str = "SYSTEM"
    SECURITY: str = "SECURITY"
    WORKER: str = "WORKER"

LOG_TYPES = LogConfig()