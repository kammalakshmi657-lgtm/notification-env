import random
from datetime import datetime, timedelta
from models import Notification, NotificationCategory, NotificationAction

NOTIFICATIONS_POOL = [
    {"source": "System", "title": "Server CPU at 98%", "body": "Production server cpu-01 has been at 98% CPU for 10 minutes. Immediate action required.", "sender": "monitoring@ops.com", "category": NotificationCategory.urgent, "action": NotificationAction.act_now, "priority": 1},
    {"source": "SMS", "title": "Message from Mom", "body": "Call me ASAP, it's an emergency regarding Dad.", "sender": "+1-555-0101", "category": NotificationCategory.urgent, "action": NotificationAction.act_now, "priority": 2},
    {"source": "Slack", "title": "CRITICAL: Payment gateway down", "body": "@channel Payment gateway is returning 500 errors. Customers cannot checkout. Need DevOps NOW.", "sender": "alice@company.com", "category": NotificationCategory.urgent, "action": NotificationAction.escalate, "priority": 1},
    {"source": "Calendar", "title": "Meeting starts in 5 minutes", "body": "All-hands meeting with CEO starts in 5 minutes. Join link: meet.company.com/allhands", "sender": "calendar@company.com", "category": NotificationCategory.urgent, "action": NotificationAction.act_now, "priority": 3},
    {"source": "Email", "title": "Security Alert: Unusual login", "body": "We detected a login to your account from an unrecognized device in Lagos, Nigeria.", "sender": "security@bank.com", "category": NotificationCategory.urgent, "action": NotificationAction.escalate, "priority": 2},
    {"source": "Slack", "title": "PR merged: feature/dark-mode", "body": "Bob merged pull request #234 feature/dark-mode into main. Build passing.", "sender": "github-bot@company.com", "category": NotificationCategory.informational, "action": NotificationAction.dismiss, "priority": 8},
    {"source": "System", "title": "Backup completed successfully", "body": "Nightly backup of database completed. 12.4 GB backed up in 4 minutes.", "sender": "backup@ops.com", "category": NotificationCategory.informational, "action": NotificationAction.dismiss, "priority": 9},
    {"source": "Email", "title": "Weekly team report", "body": "Here is your weekly summary: 12 tasks completed, 3 in progress, sprint velocity 42 points.", "sender": "reports@company.com", "category": NotificationCategory.informational, "action": NotificationAction.snooze, "priority": 10},
    {"source": "App", "title": "Your package has shipped", "body": "Order #9823 has shipped via FedEx. Estimated delivery: Thursday.", "sender": "noreply@amazon.com", "category": NotificationCategory.informational, "action": NotificationAction.dismiss, "priority": 11},
    {"source": "Slack", "title": "Standup notes posted", "body": "Today's standup notes are available in #engineering-standup channel.", "sender": "bot@company.com", "category": NotificationCategory.informational, "action": NotificationAction.dismiss, "priority": 12},
    {"source": "Email", "title": "50% off - Today only!", "body": "Flash sale! Get 50% off all premium plans. Use code FLASH50 at checkout. Expires midnight.", "sender": "promo@saasapp.com", "category": NotificationCategory.promotional, "action": NotificationAction.dismiss, "priority": 14},
    {"source": "App", "title": "Your free trial ends in 3 days", "body": "Upgrade to Pro before your trial ends and get 20% off your first year.", "sender": "billing@toolapp.com", "category": NotificationCategory.promotional, "action": NotificationAction.snooze, "priority": 13},
    {"source": "Email", "title": "New features available in v3.0", "body": "We have launched v3.0 with AI-powered features. Click to see what is new.", "sender": "product@service.com", "category": NotificationCategory.promotional, "action": NotificationAction.dismiss, "priority": 15},
    {"source": "App", "title": "John liked your photo", "body": "John Smith and 14 others liked your photo from Saturday.", "sender": "instagram", "category": NotificationCategory.social, "action": NotificationAction.dismiss, "priority": 16},
    {"source": "App", "title": "You have a new follower", "body": "techguru99 started following you on Twitter.", "sender": "twitter", "category": NotificationCategory.social, "action": NotificationAction.dismiss, "priority": 17},
    {"source": "App", "title": "Happy Birthday from LinkedIn", "body": "3 people said happy birthday to you! See their messages.", "sender": "linkedin", "category": NotificationCategory.social, "action": NotificationAction.dismiss, "priority": 18},
    {"source": "SMS", "title": "Group chat: Weekend plans", "body": "Hey are you coming to the game on Saturday?", "sender": "+1-555-0199", "category": NotificationCategory.social, "action": NotificationAction.snooze, "priority": 7},
]

def make_notification(raw, idx, base_time):
    ts = base_time - timedelta(minutes=idx * 3)
    return Notification(id=f"notif_{idx:03d}", source=raw["source"], title=raw["title"], body=raw["body"], timestamp=ts.isoformat(), sender=raw.get("sender"))

def generate_task1_batch(seed=42):
    random.seed(seed)
    pool = NOTIFICATIONS_POOL.copy()
    random.shuffle(pool)
    selected = pool[:8]
    base_time = datetime(2024, 6, 1, 9, 0, 0)
    notifications = [make_notification(n, i, base_time) for i, n in enumerate(selected)]
    ground_truth = {notifications[i].id: selected[i]["category"] for i in range(len(selected))}
    return notifications, ground_truth

def generate_task2_batch(seed=42):
    random.seed(seed)
    pool = NOTIFICATIONS_POOL.copy()
    random.shuffle(pool)
    selected = pool[:15]
    base_time = datetime(2024, 6, 1, 9, 0, 0)
    notifications = [make_notification(n, i, base_time) for i, n in enumerate(selected)]
    id_priority = [(notifications[i].id, selected[i]["priority"]) for i in range(len(selected))]
    id_priority_sorted = sorted(id_priority, key=lambda x: x[1])
    ground_truth_rank = {item[0]: rank + 1 for rank, item in enumerate(id_priority_sorted)}
    return notifications, ground_truth_rank

def generate_task3_batch(seed=42):
    random.seed(seed)
    pool = (NOTIFICATIONS_POOL * 2)[:30]
    random.shuffle(pool)
    base_time = datetime(2024, 6, 1, 9, 0, 0)
    notifications = [make_notification(n, i, base_time) for i, n in enumerate(pool)]
    ground_truth = {notifications[i].id: {"action": pool[i]["action"], "needs_summary": pool[i]["action"] == NotificationAction.escalate} for i in range(len(pool))}
    return notifications, ground_truth
