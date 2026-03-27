from models import Observation, Action, Reward, StepResult, State
from data import generate_task1_batch, generate_task2_batch, generate_task3_batch
from graders import GRADERS

TASKS = {
    "task1": {"description": "Classify each notification into one of four categories: urgent, informational, promotional, or social. You will receive 8 notifications.", "difficulty": "easy", "max_steps": 1, "generator": generate_task1_batch},
    "task2": {"description": "Rank 15 notifications in order of urgency (1 = most urgent). Assign a unique priority_rank (1-15) to each notification.", "difficulty": "medium", "max_steps": 1, "generator": generate_task2_batch},
    "task3": {"description": "Triage 30 notifications. For each, choose an action: dismiss, snooze, act_now, or escalate. For every escalated notification, also provide a 1-line summary.", "difficulty": "hard", "max_steps": 1, "generator": generate_task3_batch},
}

class NotificationEnv:
    def __init__(self):
        self._task_id = None
        self._notifications = []
        self._ground_truth = {}
        self._step_count = 0
        self._done = False
        self._last_score = None

    def reset(self, task_id="task1", seed=42):
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id: {task_id}. Choose from {list(TASKS.keys())}")
        task = TASKS[task_id]
        notifications, ground_truth = task["generator"](seed=seed)
        self._task_id = task_id
        self._notifications = notifications
        self._ground_truth = ground_truth
        self._step_count = 0
        self._done = False
        self._last_score = None
        return Observation(task_id=task_id, task_description=task["description"], notifications=notifications, step=0, max_steps=task["max_steps"])

    def step(self, action):
        if self._task_id is None:
            raise RuntimeError("Call reset() before step().")
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        grader = GRADERS[self._task_id]
        reward = grader(action, self._ground_truth)
        self._step_count += 1
        self._last_score = reward.score
        self._done = True
        next_obs = Observation(task_id=self._task_id, task_description=TASKS[self._task_id]["description"], notifications=self._notifications, step=self._step_count, max_steps=TASKS[self._task_id]["max_steps"])
        return StepResult(observation=next_obs, reward=reward, done=self._done, info={"task_id": self._task_id, "step": self._step_count})

    def state(self):
        if self._task_id is None:
            return State(task_id="none", step=0, notifications=[], last_score=None, done=False)
        return State(task_id=self._task_id, step=self._step_count, notifications=self._notifications, last_score=self._last_score, done=self._done)
