# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=global-statement
# pylint: disable=missing-timeout
# pylint: disable=broad-exception-raised
# pylint: disable=bare-except

from json import loads
from threading import Thread
from time import sleep
import requests
import sseclient


BASE_URL = "https://localhost:16888/"


def set_backend_url(url):
    global BASE_URL
    BASE_URL = url


def get_project_and_task_id(project_name, task_name):
    # Get all projects
    url = BASE_URL + "iscool/v3/projects"
    res = requests.get(url+"?start=0&count=100", verify=False).json()

    # Iterate all projects to find project id
    for project in res["data"]:
        if project["name"] != project_name:
            continue
        project_id = project["id"]

        # Iterate all tasks to find task id
        for task in project["tasks"]:
            if task["name"] != task_name:
                continue
            task_id = task["id"]
            return project_id, task_id

    # If project id or task id is not found, raise error
    raise Exception(f"Project name: {project_name} not found!")


def run_task(project_id, task_id, external_variables):
    # Send request to execute task
    url = BASE_URL + "iscool/v3/execute/task"
    res = requests.post(url, json={
        "projectID": project_id,
        "taskID": task_id,
        "externalVariables": external_variables
    }, verify=False)

    # Check response
    if not res.ok:
        raise Exception(f"Execute task failed! {res['message']}")

    # Return execute id
    return res.json()["executeID"]


def monitor_execution(execute_id):
    url = BASE_URL + f"iscool/v3/execute/task/{execute_id}/monitor"
    # Make a GET request to the SSE endpoint
    response = requests.get(url, stream=True, verify=False)

    # Create an SSE client with the response
    client = sseclient.SSEClient(response)

    # Init progress log and failed flag
    progress_log = []
    hasFailed = False
    fail_progress = ""

    # Handle SSE timeout
    def handle_sse_timeout():
        # Wait timeout for 10 seconds
        sleep(10)

        # if task progress is still empty after timeout
        if len(progress_log) == 0:
            print("SSE timeout!")
            client.close()
    Thread(target=handle_sse_timeout).start()

    # Monitor task progress
    try:
        for event in client.events():
            # Parse event data
            response = loads(event.data)

            # Only check action progress
            if response["type"] != 1:  # 1: action progress
                continue

            # Get action progress
            progress = response["progress"]
            progress_log.append(progress)

            # Get result
            result = progress["result"]

            # Check if task failed
            if result == 1:  # 1: failed
                hasFailed = True
                fail_progress = progress

            # Print progress
            print(progress)

            # Deal with stop
            if result == 6:  # 6: stop
                client.close()
    except:
        # To handle: 'NoneType' object has no attribute 'readline'
        # When close SSE client.
        # Actually it's a bug of sseclient, so we just ignore it.
        pass

    # Check if task failed
    if hasFailed:
        print("Task failed!")
        return {
            "status": "Failed",
            "progress": progress_log,
            "failProgress": fail_progress
        }

    return {
        "status": "Success",
        "progress": progress_log
    }
