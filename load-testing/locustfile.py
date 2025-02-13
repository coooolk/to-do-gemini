from locust import HttpUser, task, between
import json
import random

class ToDoAppUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.task_ids = self.fetch_task_ids()
        if not self.task_ids:
            print("Warning: No tasks found initially. Update/Delete tasks will be skipped.")
        self.task_counter = 0

    def fetch_task_ids(self):
        try:
            response = self.client.get("/api/tasks")
            if response.status_code == 200:
                tasks = response.json()
                return [task['_id'] for task in tasks]
            else:
                print(f"Failed to fetch tasks to get IDs. Status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching tasks for IDs: {e}")
            return []

    @task(2)
    def homepage(self):
        self.client.get("/", name="/ (Homepage Load)")

    @task
    def get_categories(self):
        self.client.get("/api/categories", name="/api/categories")

    @task(3)
    def list_tasks(self):
        categories = ["Personal", "Work", "Shopping", "Errands", "Hobbies"]
        category_filter = random.choice(categories) if random.random() < 0.3 else None

        sort_options = ["timeAddedAsc", "timeAddedDesc", "priority", "priorityTimeAdded", None]
        sort_by = random.choice(sort_options)

        params = {}
        if category_filter:
            params["category"] = category_filter
        if sort_by:
            params["sortBy"] = sort_by

        self.client.get("/api/tasks", params=params, name="/api/tasks (list)")

    @task(5)
    def create_task(self):
        categories = ["Personal", "Work", "Shopping", "Errands", "Hobbies"]
        priorities = ["1-High", "2-Medium", "3-Low"]

        task_data = {
            "title": f"Load Test Task - {random.randint(1, 10000)}",
            "category": random.choice(categories),
            "priority": random.choice(priorities),
            "dueDate": None
        }
        response = self.client.post("/api/tasks", json=task_data, name="/api/tasks (create)")

        if response.status_code == 201:  # Check for successful creation (201 Created)
            self.task_counter += 1
            if self.task_counter >= 100:
                self.delete_all_tasks()
                self.task_counter = 0
        else:
            print(f"Task creation failed: {response.status_code} - {response.text}") # Print error details

    def delete_all_tasks(self):
        try:
            response = self.client.delete("/api/tasks/clear", name="/api/tasks/clear (delete all)")
            if response.status_code != 200: # Check for success (200 OK)
                print(f"Failed to clear tasks: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during task clearing: {e}")


    @task(2)
    def update_task_status_priority(self):
        if not self.task_ids:
            return

        task_id_to_update = random.choice(self.task_ids)
        updates = {}
        if random.random() < 0.5:
            updates["completed"] = random.choice([True, False])
        if random.random() < 0.5:
            priorities = ["1-High", "2-Medium", "3-Low"]
            updates["priority"] = random.choice(priorities)

        if updates:
            self.client.put(f"/api/tasks/{task_id_to_update}", json=updates, name="/api/tasks/:id (update)")

    @task(1)
    def delete_task(self):
        if not self.task_ids:
            return

        task_id_to_delete = random.choice(self.task_ids)
        self.client.delete(f"/api/tasks/{task_id_to_delete}", name="/api/tasks/:id (delete)")