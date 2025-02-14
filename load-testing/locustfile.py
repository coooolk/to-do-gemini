from locust import HttpUser, task, between, events
import json
import random
import requests  # For background cleanup

class ToDoAppUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.task_ids = []
        self.fetch_task_ids()

    def fetch_task_ids(self):
        try:
            response = self.client.get("/api/tasks")
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            tasks = response.json()
            self.task_ids = [task['_id'] for task in tasks]
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch tasks: {e}")
            self.task_ids = [] # Ensure task_ids is empty in case of error
        except (json.JSONDecodeError, KeyError) as e: # Handle JSON errors
            print(f"Error decoding JSON or accessing keys: {e}")
            self.task_ids = []

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
        try:
            response = self.client.post("/api/tasks", json=task_data, name="/api/tasks (create)")
            response.raise_for_status() # Check for successful creation (201 Created)
            self.fetch_task_ids() # Refresh task_ids after successful creation
        except requests.exceptions.RequestException as e:
            print(f"Task creation failed: {e}")

    @task(2)
    def update_task_status_priority(self):
        self.fetch_task_ids()
        if self.task_ids:
            task_id_to_update = random.choice(self.task_ids)
            updates = {}
            if random.random() < 0.5:
                updates["completed"] = random.choice([True, False])
            if random.random() < 0.5:
                priorities = ["1-High", "2-Medium", "3-Low"]
                updates["priority"] = random.choice(priorities)

            if updates:
                try:
                    self.client.put(f"/api/tasks/{task_id_to_update}", json=updates, name="/api/tasks/:id (update)")
                except requests.exceptions.RequestException as e:
                    print(f"Task update failed: {e}")


    @task(1)
    def delete_task(self):
        self.fetch_task_ids()
        if self.task_ids:
            task_id_to_delete = random.choice(self.task_ids)
            try:
                self.client.delete(f"/api/tasks/{task_id_to_delete}", name="/api/tasks/:id (delete)")
            except requests.exceptions.RequestException as e:
                print(f"Task deletion failed: {e}")



# Background Cleanup (Separate Script: cleanup_tasks.py)

def cleanup_old_tasks(api_url="/api/tasks"):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        tasks = response.json()
        for task in tasks:
            # Example: Delete tasks older than 7 days (Implement your logic here)
            # You'll need to adapt this based on how you store dates.
            # Example (if you have a 'created_at' field):
            # from datetime import datetime, timedelta
            # created_at = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00')) # Adjust format
            # if datetime.now(timezone.utc) - created_at > timedelta(days=7):
            delete_url = f"{api_url}/{task['_id']}"
            delete_response = requests.delete(delete_url)
            delete_response.raise_for_status()
            print(f"Deleted task: {task['_id']}")

    except requests.exceptions.RequestException as e:
        print(f"Error during cleanup: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error during cleanup: {e}")
    except Exception as e:
        print(f"General error during cleanup: {e}")

# Example usage (you would schedule this script):
# cleanup_old_tasks() # Or pass the API URL if needed


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    print("Locust initialized. Triggering background cleanup (if needed).")
    # You could trigger the cleanup script here (if it's not already scheduled)
    # Be very careful about running a blocking operation here.  It could
    # interfere with Locust.  It's generally better to schedule the cleanup
    # separately.


@events.quitting.add_listener
def on_locust_quit(environment, **_kwargs):
    print("Locust quitting.")  # You can add cleanup here if absolutely needed.