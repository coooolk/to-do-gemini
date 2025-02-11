from locust import HttpUser, task, between
import json
import random

class ToDoAppUser(HttpUser):
    """
    Load test user for the To-Do App API, now with dynamic task ID fetching.
    Simulates fetching homepage (frontend), categories, listing tasks,
    creating tasks, updating task status/priority (using fetched IDs),
    and deleting tasks (using fetched IDs).
    """
    wait_time = between(1, 3)  # Simulate users pausing between actions

    def on_start(self):
        """Fetch initial task IDs when a user starts."""
        self.task_ids = self.fetch_task_ids()
        if not self.task_ids:
            print("Warning: No tasks found initially. Update/Delete tasks will be skipped.")

    def fetch_task_ids(self):
        """Helper function to fetch task IDs from the API."""
        try:
            response = self.client.get("/api/tasks") # Fetch all tasks to get IDs
            if response.status_code == 200:
                tasks = response.json()
                return [task['_id'] for task in tasks] # Extract IDs
            else:
                print(f"Failed to fetch tasks to get IDs. Status code: {response.status_code}")
                return [] # Return empty list if fetch fails
        except Exception as e:
            print(f"Error fetching tasks for IDs: {e}")
            return []

    @task(2) # Give homepage load a bit of priority
    def homepage(self):
        """Fetch the homepage (simulates initial frontend load)."""
        self.client.get("/", name="/ (Homepage Load)") # Request the root path - adjust if your homepage is at a different path

    @task
    def get_categories(self):
        """Fetch all task categories."""
        self.client.get("/api/categories", name="/api/categories")

    @task(3)  # Give listing tasks a higher priority (relative weight)
    def list_tasks(self):
        """List tasks, optionally with category filter and sorting."""
        # Example with random category filter (you can customize this)
        categories = ["Personal", "Work", "Shopping", "Errands", "Hobbies"] # Example categories
        category_filter = random.choice(categories) if random.random() < 0.3 else None # 30% chance of filtering by category

        sort_options = ["timeAddedAsc", "timeAddedDesc", "priority", "priorityTimeAdded", None]
        sort_by = random.choice(sort_options)

        params = {}
        if category_filter:
            params["category"] = category_filter
        if sort_by:
            params["sortBy"] = sort_by

        self.client.get("/api/tasks", params=params, name="/api/tasks (list)")


    @task(5) # Give task creation highest priority
    def create_task(self):
        """Create a new task."""
        categories = ["Personal", "Work", "Shopping", "Errands", "Hobbies"] # Example categories
        priorities = ["1-High", "2-Medium", "3-Low"] # Example priorities

        task_data = {
            "title": f"Load Test Task - {random.randint(1, 10000)}",
            "category": random.choice(categories),
            "priority": random.choice(priorities),
            "dueDate": None  # You can add random due dates if needed, or leave it as null
        }
        self.client.post("/api/tasks", json=task_data, name="/api/tasks (create)")

    @task(2) # Medium priority for updates
    def update_task_status_priority(self):
        """Update an existing task's completion status and/or priority, using dynamically fetched task IDs."""
        if not self.task_ids:
            return # Skip if no task IDs available

        task_id_to_update = random.choice(self.task_ids)
        updates = {}
        if random.random() < 0.5: # 50% chance of updating completion status
            updates["completed"] = random.choice([True, False])
        if random.random() < 0.5: # 50% chance of updating priority
            priorities = ["1-High", "2-Medium", "3-Low"]
            updates["priority"] = random.choice(priorities)

        if updates: # Only make the PUT request if there's something to update
            self.client.put(f"/api/tasks/{task_id_to_update}", json=updates, name="/api/tasks/:id (update)")


    @task(1) # Lowest priority for delete (to avoid accidentally deleting too much data in real tests)
    def delete_task(self):
        """Delete a task, using dynamically fetched task IDs."""
        if not self.task_ids:
            return # Skip delete if no task IDs available

        task_id_to_delete = random.choice(self.task_ids)
        self.client.delete(f"/api/tasks/{task_id_to_delete}", name="/api/tasks/:id (delete)")