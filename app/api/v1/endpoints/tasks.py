from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any

from app.api import deps
from app.schemas.user import User
from app.tasks.tasks import (
    refresh_book_data_from_source,
    calculate_book_statistics,
    send_new_book_notification
)

router = APIRouter()

@router.post("/refresh-books")
async def trigger_book_refresh(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_user)
) -> Dict[str, Any]:
    """
    Trigger background task to refresh book data
    """
    # Send task to Celery worker
    task = refresh_book_data_from_source.delay()
    
    return {
        "message": "Book refresh task started",
        "task_id": task.id,
        "status": "processing",
        "task_name": "refresh_book_data"
    }

@router.post("/calculate-statistics")
async def trigger_statistics_calculation(
    current_user: User = Depends(deps.get_current_user)
) -> Dict[str, Any]:
    """
    Trigger background task to calculate book statistics
    """
    task = calculate_book_statistics.delay()
    
    return {
        "message": "Statistics calculation task started",
        "task_id": task.id,
        "status": "processing",
        "task_name": "calculate_statistics"
    }

@router.post("/notify-new-book")
async def trigger_new_book_notification(
    book_title: str,
    book_author: str,
    current_user: User = Depends(deps.get_current_user)
) -> Dict[str, Any]:
    """
    Trigger background task to send new book notification
    """
    task = send_new_book_notification.delay(book_title, book_author)
    
    return {
        "message": "New book notification task started",
        "task_id": task.id,
        "status": "processing",
        "task_name": "send_new_book_notification",
        "book_title": book_title,
        "book_author": book_author
    }

@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(deps.get_current_user)
) -> Dict[str, Any]:
    """
    Check status of a background task
    """
    from app.tasks.celery_app import celery
    
    result = celery.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": result.status,
        "task_name": getattr(result, "name", "Unknown")
    }
    
    if result.ready():
        if result.successful():
            response["result"] = result.result
            response["message"] = "Task completed successfully"
        else:
            response["error"] = str(result.result)
            response["message"] = "Task failed"
    elif result.status == 'PENDING':
        response["message"] = "Task is pending or not found"
    elif result.status == 'STARTED':
        response["message"] = "Task is currently running"
    elif result.status == 'RETRY':
        response["message"] = "Task is being retried"
    elif result.status == 'FAILURE':
        response["message"] = "Task failed"
    
    return response

@router.get("/active-tasks")
async def get_active_tasks(
    current_user: User = Depends(deps.get_current_user)
) -> Dict[str, Any]:
    """
    Get list of active Celery tasks
    """
    from app.tasks.celery_app import celery
    
    inspector = celery.control.inspect()
    
    active_tasks = inspector.active() or {}
    scheduled_tasks = inspector.scheduled() or {}
    reserved_tasks = inspector.reserved() or {}
    
    return {
        "active_tasks": active_tasks,
        "scheduled_tasks": scheduled_tasks,
        "reserved_tasks": reserved_tasks,
        "total_active": sum(len(tasks) for tasks in active_tasks.values()),
        "total_scheduled": sum(len(tasks) for tasks in scheduled_tasks.values()),
        "total_reserved": sum(len(tasks) for tasks in reserved_tasks.values())
    }