import time
import random
from locust import HttpUser, TaskSet, between, task
from bson import ObjectId  # For generating valid ObjectIds


class TaskSetLoad(TaskSet):

    @task(3)  # Higher weight for getting tasks
    def get_tasks(self):
        # Test with and without category filtering and sorting
        category = random.choice(["Work", "Personal", "Shopping", "General", None]) # Randomly pick a category or none.
        sort_by = random.choice(["timeAddedAsc", "timeAddedDesc", "priority", "priorityTimeAdded", None])

        url = "/api/tasks"
        params = {}
        if category:
            params["category"] = category
        if sort_by:
            params["sortBy"] = sort_by

        self.client.get(url, params=params, name="/api/tasks")

    @task(20) # Lower weight for creating tasks
    def create_task(self):
        task_data = {
            "title": f"Task {time.time()}", # Unique title
            "category": random.choice(["Work", "Personal", "Shopping", "General"]),
            "priority": random.choice(["1-High", "2-Medium", "3-Low"]),
            "dueDate": "2024-03-15" # Example due date format
        }
        self.client.post("/api/tasks", json=task_data, name="/api/tasks")

    @task(1)  # Lower weight for updating tasks
    def update_task(self):
        # First, get a task ID.  This is a bit more complex.
        res = self.client.get("/api/tasks")
        if res.status_code == 200 and res.json():
            tasks = res.json()
            task_to_update = random.choice(tasks) # Pick a random task to update
            task_id = task_to_update["_id"]

            updates = {
                "completed": not task_to_update["completed"], # Toggle completion status
                "priority": random.choice(["1-High", "2-Medium", "3-Low"]) # Change priority
            }
            self.client.put(f"/api/tasks/{task_id}", json=updates, name="/api/tasks/[id]")


    @task(3)
    def get_categories(self):
        self.client.get("/api/categories", name="/api/categories")

    @task(1)  # Lower weight for clearing all tasks
    def clear_all_tasks(self):
       self.client.delete("/api/tasks/clear", name="/api/tasks/clear")


class WebsiteUser(HttpUser):
    # No host defined here!  This is the key change.
    wait_time = between(1, 3)
    tasks = [TaskSetLoad]