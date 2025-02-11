# Easy Load Test for Your To-Do App - Including Frontend (Initial Load) - Now with Dynamic Task IDs!

This folder helps you load test your To-Do app, including simulating the initial loading of the frontend and then testing the backend API. It now **dynamically fetches task IDs** for update and delete operations, making the test more realistic! It's still very easy to run - just provide your app's web address!

## Files Included

*   **`locustfile.py`**:  Defines the load test. **You DO NOT need to change this file to get started.**  It now fetches task IDs dynamically and uses them for updates and deletes.
*   **`README.md`**: This file (the one you are reading) with instructions.

## Before You Begin

1.  **Make sure your ENTIRE To-Do App (Frontend and Backend) is running.**  It needs to be accessible at a web address (URL). This URL should be the address where you access the To-Do app in your web browser.
2.  **Install Locust:** If you haven't yet, open your command line and type:
    ```bash
    pip install locust
    ```

## Running the Load Test - Just 3 Steps!

1.  **Open your command line:** Go to the folder with `locustfile.py` and `README.md`.

2.  **Run the Locust command:** Type the command below, **replacing `http://your-todo-app-url` with the web address you use to access your To-Do app in a browser.**  This should be the *frontend* URL.

    ```bash
    locust -f locustfile.py --host=http://your-todo-app-url
    ```
    **Example:** If you access your To-Do app in the browser at `http://my-todo-app.example.com`, use:
    ```bash
    locust -f locustfile.py --host=[http://my-todo-app.example.com](http://my-todo-app.example.com)
    ```
    Or, if it's on your computer at `http://localhost:3000` (if your frontend runs on port 3000, for example):
     ```bash
    locust -f locustfile.py --host=http://localhost:3000
    ```

3.  **Open Locust in your browser:**  Locust will give you a web address (usually `http://localhost:8089`). Open this in your browser.

4.  **Start Testing in the Locust Web UI:**
    *   **"Number of users to simulate":**  Enter the number of users. Start small (like 10 or 50).
    *   **"Ramp up rate":**  Enter the rate to increase users (e.g., 1 user per second).
    *   Click **"Start swarming"**.

5.  **Watch the Results!**  Locust will show you how your app performs.

## Understanding This "Whole App" Test (Important!)

*   **Simulating Initial Frontend Load:** This test includes a step where Locust requests the main page (`/`).
*   **Dynamic Task IDs for Update/Delete:**  The test now **fetches real task IDs** from your API at the start of each simulated user session and uses these IDs for updating and deleting tasks. This makes the test more realistic.
*   **Still Primarily Backend API Load Test:**  The test STILL mainly focuses on load testing the backend API.  Locust is making direct API calls.
*   **Not Full Browser Simulation:** Locust is *not* a full browser simulator.

## For a More Complete "Whole App" Picture (Advanced - Optional for Now)

(Same as before -  manual frontend monitoring or dedicated frontend performance tools for a truly complete picture).

## What to do Next

*   **Run this updated test** and monitor the results in Locust.
*   **Also, manually load your To-Do app frontend in a browser** while the Locust test is running and use browser developer tools (Network tab).
*   **Analyze the combined results** (Locust API metrics and browser frontend performance).
*   **Customize `locustfile.py` later** for even more advanced scenarios if needed.

**Key Changes in `locustfile.py`:**

*   **`on_start()` method:**  Now fetches task IDs when each user starts.
*   **`fetch_task_ids()` helper function:** Handles fetching task IDs from `/api/tasks`.
*   **`update_task_status_priority()` and `delete_task()`:** Now use `random.choice(self.task_ids)` to select a task ID for update/delete operations, if task IDs are available. They also include checks to skip if no task IDs were fetched initially.

With these changes, the load tests are now more robust and realistic because they are working with actual task data from your API, rather than hardcoded placeholders. Let me know how this updated version works for you!