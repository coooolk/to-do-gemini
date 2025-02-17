from locust import HttpUser, task, between, events
import json
import random
import requests
import time  # For time-based cleanup scheduling
from datetime import datetime, timedelta

class ToDoAppUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.task_ids = []
        self.fetch_task_ids()

    def fetch_task_ids(self):
        try:
            response = self.client.get("/api/tasks")
            response.raise_for_status()
            tasks = response.json()
            self.task_ids = [task['_id'] for task in tasks]
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch tasks: {e}")
            self.task_ids = []
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error decoding JSON or accessing keys: {e}")
            self.task_ids = []

    # ... (rest of your existing @task methods)

    @task(1)
    def delete_task(self):  # Keep the individual delete task
        self.fetch_task_ids()
        if self.task_ids:
            task_id_to_delete = random.choice(self.task_ids)
            try:
                self.client.delete(f"/api/tasks/{task_id_to_delete}", name="/api/tasks/:id (delete)")
            except requests.exceptions.RequestException as e:
                print(f"Task deletion failed: {e}")


# Background Cleanup (Integrated into Locust script)

def cleanup_old_tasks(api_url="/api/tasks"):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        tasks = response.json()
        now = datetime.utcnow() # Use UTC for consistency
        for task in tasks:
            try:  # Handle potential missing or malformed createdAt
                created_at_str = task.get('createdAt')
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))  # Parse ISO format, handle Z
                    if now - created_at > timedelta(days=7):  # Delete if older than 7 days
                        delete_url = f"{api_url}/{task['_id']}"
                        delete_response = requests.delete(delete_url)
                        delete_response.raise_for_status()
                        print(f"Deleted task: {task['_id']}, created at: {created_at}")
            except (ValueError, TypeError) as e:
                print(f"Error processing createdAt for task {task.get('_id', 'unknown')}: {e}. Task data: {task}") # Log the task data


    except requests.exceptions.RequestException as e:
        print(f"Error during cleanup: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error during cleanup: {e}")
    except Exception as e:
        print(f"General error during cleanup: {e}")


# Scheduling the cleanup (using a separate thread is crucial)
import threading

def schedule_cleanup(interval_seconds, api_url):
    def run_cleanup():
        while True:
            cleanup_old_tasks(api_url)
            time.sleep(interval_seconds)

    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True) # daemon=True allows the main thread to exit
    cleanup_thread.start()

# Example usage (schedule every 2 hours):
cleanup_interval = 2 * 60 * 60  # 2 hours in seconds
schedule_cleanup(cleanup_interval, "/api/tasks") # Schedule the cleanup


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    print("Locust initialized.")  # No need to trigger cleanup here, it's scheduled.

@events.quitting.add_listener
def on_locust_quit(environment, **_kwargs):
    print("Locust quitting.")