from pydantic import BaseModel, field_validator
from typing import List, Optional
from enum import Enum

class NotificationCategory(str, Enum):
    urgent = "urgent"
    informational = "informational"
    promotional = "promotional"
    social = "social"

class NotificationAction(str, Enum):
    dismiss = "dismiss"
    snooze = "snooze"
    act_now = "act_now"
    escalate = "escalate"

class Notification(BaseModel):
    id: str
    source: str
    title: str
    body: str
    timestamp: str
    sender: Optional[str] = None

class Observation(BaseModel):
    task_id: str
    task_description: str
    notifications: List[Notification]
    step: int = 0
    max_steps: int = 1

class NotificationLabel(BaseModel):
    notification_id: str
    category: Optional[NotificationCategory] = None
    priority_rank: Optional[int] = None
    action: Optional[NotificationAction] = None
    summary: Optional[str] = None

class Action(BaseModel):
    task_id: str
    labels: List[NotificationLabel]

# 🔥 FINAL FIX HERE
class Reward(BaseModel):
    score: float
    partial_scores: dict = {}
    feedback: str = ""

    @field_validator("score")
    def fix_score(cls, v):
        try:
            v = float(v)
        except:
            return 0.5  # safe fallback

        if v <= 0:
            return 0.0001
        elif v >= 1:
            return 0.9999
        return v

class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict = {}

class State(BaseModel):
    task_id: str
    step: int
    notifications: List[Notification]
    last_score: Optional[float] = None
    done: bool = False