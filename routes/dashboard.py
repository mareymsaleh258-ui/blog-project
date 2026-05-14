from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.user import User
from models.post import Post
from models.comment import Comment
from schemas.base import BaseResponse
from dependencies.db import require_admin
import os, re
from collections import Counter
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def parse_logs():
    log_path = "logs/app.log"
    if not os.path.exists(log_path):
        return [], []

    request_logs = []
    error_logs = []

    with open(log_path, "r") as f:
        for line in f:
            if "status:" in line:
                request_logs.append(line.strip())
            if "| ERROR |" in line or "| WARNING |" in line:
                error_logs.append(line.strip())

    return request_logs, error_logs

@router.get("/stats", response_model=BaseResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    total_users = db.query(User).count()
    total_posts = db.query(Post).count()
    total_comments = db.query(Comment).count()

    request_logs, error_logs = parse_logs()

    # حساب متوسط الـ response time
    durations = []
    status_counter = Counter()
    endpoint_counter = Counter()

    for log in request_logs:
        duration_match = re.search(r"duration: ([\d.]+)ms", log)
        status_match = re.search(r"status: (\d+)", log)
        endpoint_match = re.search(r"(GET|POST|PUT|DELETE) (\S+)", log)

        if duration_match:
            durations.append(float(duration_match.group(1)))
        if status_match:
            status_counter[status_match.group(1)] += 1
        if endpoint_match:
            endpoint_counter[endpoint_match.group(2)] += 1

    avg_response_time = round(sum(durations) / len(durations), 2) if durations else 0
    total_requests = len(request_logs)
    error_count = status_counter.get("500", 0) + status_counter.get("422", 0)
    error_rate = round((error_count / total_requests * 100), 2) if total_requests > 0 else 0

    return BaseResponse(
        success=True,
        message="Dashboard stats",
         data={
            "system_health": "healthy",
            "database": {
                "total_users": total_users,
                "total_posts": total_posts,
                "total_comments": total_comments
            },
            "api_metrics": {
                "total_requests": total_requests,
                "avg_response_time_ms": avg_response_time,
                "error_rate_percent": error_rate,
                "status_code_breakdown": dict(status_counter),
                "top_endpoints": dict(endpoint_counter.most_common(5))
            },
            "recent_errors": error_logs[-5:] if error_logs else []})
        