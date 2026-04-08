from models import Action, NotificationCategory, NotificationAction, Reward

def clamp(score):
    return round(min(0.99, max(0.01, float(score))), 4)

def grade_task1(action, ground_truth):
    urgency_tier = {NotificationCategory.urgent: 1, NotificationCategory.informational: 2, NotificationCategory.promotional: 3, NotificationCategory.social: 3}
    total = len(ground_truth)
    if total == 0:
        return Reward(score=clamp(0.01), feedback="No notifications to grade.")
    exact_correct = 0
    partial_correct = 0
    per_item = {}
    for label in action.labels:
        nid = label.notification_id
        if nid not in ground_truth:
            continue
        expected = ground_truth[nid]
        predicted = label.category
        if predicted == expected:
            exact_correct += 1
            per_item[nid] = 0.99
        elif urgency_tier.get(predicted) == urgency_tier.get(expected):
            partial_correct += 1
            per_item[nid] = 0.5
        else:
            per_item[nid] = 0.01
    score = clamp((exact_correct + 0.5 * partial_correct) / total)
    feedback = f"{exact_correct}/{total} exact matches, {partial_correct}/{total} partial."
    return Reward(score=score, partial_scores=per_item, feedback=feedback)

def _kendall_tau(ranking_a, ranking_b):
    pos_a = {item: i for i, item in enumerate(ranking_a)}
    pos_b = {item: i for i, item in enumerate(ranking_b)}
    common = [item for item in ranking_a if item in pos_b]
    if len(common) < 2:
        return 0.5
    concordant = 0
    discordant = 0
    for i in range(len(common)):
        for j in range(i + 1, len(common)):
            a_order = pos_a[common[i]] - pos_a[common[j]]
            b_order = pos_b[common[i]] - pos_b[common[j]]
            if a_order * b_order > 0:
                concordant += 1
            elif a_order * b_order < 0:
                discordant += 1
    total_pairs = len(common) * (len(common) - 1) / 2
    tau = (concordant - discordant) / total_pairs if total_pairs > 0 else 0.0
    return round((tau + 1) / 2, 4)

def grade_task2(action, ground_truth_rank):
    gt_sorted = sorted(ground_truth_rank.items(), key=lambda x: x[1])
    gt_ranking = [item[0] for item in gt_sorted]
    agent_labels = {lbl.notification_id: lbl.priority_rank for lbl in action.labels if lbl.priority_rank is not None}
    if not agent_labels:
        return Reward(score=clamp(0.01), feedback="No priority ranks provided.")
    agent_sorted = sorted(agent_labels.items(), key=lambda x: x[1])
    agent_ranking = [item[0] for item in agent_sorted]
    score = clamp(_kendall_tau(gt_ranking, agent_ranking))
    feedback = f"Kendall-tau rank similarity: {score:.2f}."
    return Reward(score=score, partial_scores={"kendall_tau": score}, feedback=feedback)

def _score_summary(summary):
    if not summary or not summary.strip():
        return 0.01
    length = len(summary.strip())
    if length < 10:
        return 0.3
    if length > 200:
        return 0.6
    return 0.99

def grade_task3(action, ground_truth):
    action_adjacency = {NotificationAction.dismiss: 0, NotificationAction.snooze: 1, NotificationAction.act_now: 2, NotificationAction.escalate: 3}
    total = len(ground_truth)
    if total == 0:
        return Reward(score=clamp(0.01), feedback="No notifications to grade.")
    action_scores = {}
    summary_scores = {}
    escalated_expected = [nid for nid, v in ground_truth.items() if v["needs_summary"]]
    for label in action.labels:
        nid = label.notification_id
        if nid not in ground_truth:
            continue
        expected_action = ground_truth[nid]["action"]
        predicted_action = label.action
        if predicted_action is None:
            action_scores[nid] = 0.01
            continue
        if predicted_action == expected_action:
            action_scores[nid] = 0.99
        else:
            dist = abs(action_adjacency[predicted_action] - action_adjacency[expected_action])
            action_scores[nid] = max(0.01, 0.99 - dist * 0.4)
        if ground_truth[nid]["needs_summary"]:
            summary_scores[nid] = _score_summary(label.summary or "")
    avg_action = sum(action_scores.values()) / total if action_scores else 0.01
    avg_summary = sum(summary_scores.get(nid, 0.01) for nid in escalated_expected) / len(escalated_expected) if escalated_expected else 0.99
    score = clamp(0.7 * avg_action + 0.3 * avg_summary)
    feedback = f"Action accuracy: {avg_action:.2f}, Summary quality: {avg_summary:.2f}. Score: {score:.2f}."
    return Reward(score=score, partial_scores={"action_accuracy": round(avg_action, 4), "summary_quality": round(avg_summary, 4)}, feedback=feedback)

GRADERS = {"task1": grade_task1, "task2": grade_task2, "task3": grade_task3}