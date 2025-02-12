from locust import HttpUser, task, between, events
import json
import random

class ToDoAppUser(HttpUser):
    """
    Load test user for the To-Do App API, now with dynamic task ID fetching and task cleanup,
    triggering "delete all tasks" when task count exceeds 100.
    Simulates fetching homepage (frontend), categories, listing tasks,
    creating tasks, updating task status/priority (using fetched IDs),
    and deleting tasks (using fetched IDs), with periodic task deletion,
    conditional "delete all tasks" based on count, and final cleanup.
    """
    wait_time = between(1, 3)  # Simulate users pausing between actions
    all_tasks_deleted_triggered = False # Class-level flag to track if "delete all tasks" has been triggered

    def on_start(self):
        """Fetch initial task IDs and initialize task creation counter when a user starts."""
        self.task_ids = self.fetch_task_ids()
        if not self.task_ids:
            print("Warning: No tasks found initially. Update/Delete tasks will be skipped.")
        self.tasks_created_count = 0 # Initialize counter for tasks created by this user
        self.user_all_tasks_deleted_triggered = False # Instance-level flag for each user

    def fetch_task_ids(self):
        """Helper function to fetch task IDs from the API."""
        try:
            response = self.client.get("/api/tasks")  # Fetch all tasks to get IDs
            if response.status_code == 200:
                tasks = response.json()
                return [task['_id'] for task in tasks]  # Extract IDs
            else:
                print(f"Failed to fetch tasks to get IDs. Status code: {response.status_code}")
                return []  # Return empty list if fetch fails
        except Exception as e:
            print(f"Error fetching tasks for IDs: {e}")
            return []

    def delete_task(self):
        """Helper function to delete a single task (randomly chosen from fetched IDs)."""
        if not self.task_ids:
            print("No task IDs available to delete for periodic deletion.")
            return

        task_id_to_delete = random.choice(self.task_ids)
        try:
            response = self.client.delete(f"/api/tasks/{task_id_to_delete}", name="/api/tasks/:id (periodic delete)")
            if response.status_code == 200:
                print(f"Periodically deleted task with ID: {task_id_to_delete}")
                # After deletion, refresh task IDs to keep them up-to-date
                self.task_ids = self.fetch_task_ids()
            else:
                print(f"Failed to periodically delete task. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error during periodic task deletion: {e}")

    def delete_all_tasks_if_needed(self):
        """Helper function to delete all tasks if count exceeds 100, triggered during test run."""
        if ToDoAppUser.all_tasks_deleted_triggered: # Use class-level flag to check if already triggered
            return  # Do not trigger again if already done

        try:
            response = self.client.delete("/api/tasks/clear", name="/api/tasks/clear (conditional delete)")
            if response.status_code == 200:
                print("Conditional Delete All Tasks triggered - count above 100.")
                ToDoAppUser.all_tasks_deleted_triggered = True # Set class-level flag to prevent re-triggering
            else:
                print(f"Conditional Delete All Tasks failed. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error during conditional delete all tasks: {e}")

    @task(2)  # Give homepage load a bit of priority
    def homepage(self):
        """Fetch the homepage (simulates initial frontend load)."""
        self.client.get("/", name="/ (Homepage Load)")  # Request the root path - adjust if your homepage is at a different path

    @task
    def get_categories(self):
        """Fetch all task categories."""
        self.client.get("/api/categories", name="/api/categories")

    @task(3)  # Give listing tasks a higher priority (relative weight)
    def list_tasks(self):
        """List tasks, optionally with category filter and sorting."""
        # Example with random category filter (you can customize this)
        categories = ["Personal", "Work", "Shopping", "Errands", "Hobbies"]  # Example categories
        category_filter = random.choice(categories) if random.random() < 0.3 else None  # 30% chance of filtering by category

        sort_options = ["timeAddedAsc", "timeAddedDesc", "priority", "priorityTimeAdded", None]
        sort_by = random.choice(sort_options)

        params = {}
        if category_filter:
            params["category"] = category_filter
        if sort_by:
            params["sortBy"] = sort_by

        self.client.get("/api/tasks", params=params, name="/api/tasks (list)")

    @task(5)  # Give task creation highest priority
    def create_task(self):
        """Create a new task, periodically delete one after every 5 creations,
        and trigger "delete all tasks" if total task count exceeds 100."""
        categories = ["Personal", "Work", "Shopping", "Errands", "Hobbies"]  # Example categories
        priorities = ["1-High", "2-Medium", "3-Low"]  # Example priorities

        task_data = {
            "title": f"Load Test Task - {random.randint(1, 10000)}",
            "category": random.choice(categories),
            "priority": random.choice(priorities),
            "dueDate": None  # You can add random due dates if needed, or leave it as null
        }
        self.client.post("/api/tasks", json=task_data, name="/api/tasks (create)")
        self.tasks_created_count += 1 # Increment task creation counter

        if self.tasks_created_count % 5 == 0:  # Check if it's time for periodic delete
            self.delete_task()  # Call the periodic delete task function

        # Check total task count and trigger "delete all tasks" if needed
        task_list_response = self.client.get("/api/tasks")
        if task_list_response.status_code == 200:
            current_task_count = len(task_list_response.json())
            print(f"Current Task Count: {current_task_count}")
            if current_task_count > 100 and not ToDoAppUser.all_tasks_deleted_triggered:
                self.delete_all_tasks_if_needed()  # Trigger "delete all tasks" if count exceeds 100

        else:
            print(f"Failed to fetch task list to check count. Status code: {task_list_response.status_code}")

    @task(2)  # Medium priority for updates
    def update_task_status_priority(self):
        """Update an existing task's completion status and/or priority, using dynamically fetched task IDs."""
        if not self.task_ids:
            return  # Skip if no task IDs available

        task_id_to_update = random.choice(self.task_ids)
        updates = {}
        if random.random() < 0.5:  # 50% chance of updating completion status
            updates["completed"] = random.choice([True, False])
        if random.random() < 0.5:  # 50% chance of updating priority
            priorities = ["1-High", "2-Medium", "3-Low"]
            updates["priority"] = random.choice(priorities)

        if updates:  # Only make the PUT request if there's something to update
            self.client.put(f"/api/tasks/{task_id_to_update}", json=updates, name="/api/tasks/:id (update)")

    @task(1)  # Lowest priority for delete (to avoid accidentally deleting too much data in real tests)
    def delete_single_task_on_demand(self):  # Renamed to avoid confusion with periodic delete
        """Delete a task on demand, using dynamically fetched task IDs."""
        if not self.task_ids:
            return  # Skip delete if no task IDs available

        task_id_to_delete = random.choice(self.task_ids)
        self.client.delete(f"/api/tasks/{task_id_to_delete}", name="/api/tasks/:id (delete on demand)")

def delete_all_tasks_final_cleanup(environment, **kwargs):
    """Deletes all tasks using the /api/tasks/clear endpoint for final cleanup after the test."""
    if ToDoAppUser.all_tasks_deleted_triggered: # Check again before final cleanup to avoid double deletion in some edge cases
        print("Final cleanup: Delete All Tasks already triggered during test run, skipping final cleanup.")
        return

    client = environment.client  # Get a client instance from the environment
    try:
        response = client.delete("/api/tasks/clear", name="/api/tasks/clear (final cleanup)")
        if response.status_code == 200:
            print("Final cleanup: All tasks deleted successfully at the end of the load test.")
        else:
            print(f"Final cleanup: Failed to delete all tasks. Status code: {response.status_code}")
    except Exception as e:
        print(f"Final cleanup: Error deleting all tasks: {e}")

# Register the final cleanup function to be executed when Locust stops
events.locust_stop.add_listener(delete_all_tasks_final_cleanup)