import json
import threading
import time
import requests
import sseclient

base_url = "http://localhost:16888/"


def set_backend_url(url):
    global base_url
    base_url = url


def get_project_and_task_id(project_name, task_name):
    # Get all projects
    url = base_url + "iscool/v3/projects"
    res = requests.get(url).json()

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


def run_task(project_id, task_id, external_variables, api_key):
    # Send request to execute task
    url = base_url + "iscool/v3/execute/task"
    res = requests.post(url, json={
        "projectID": project_id,
        "taskID": task_id,
        "externalVariables": external_variables
    }, headers={
        "X-API-KEY": api_key
    })

    # Check response
    if not res.ok:
        raise Exception(
            f"Execute task failed! {res.json()['error']['message']}")

    # Return execute id
    return res.json()["executeID"]


def control_task(execute_id, control_code, api_key):
    # Send request to control task
    url = base_url + f"iscool/v3/execute/task/{execute_id}/control"
    res = requests.post(url, json={
        "control": control_code
    }, headers={
        "X-API-KEY": api_key
    })

    # Check response
    if not res.ok:
        raise Exception(
            f"Control task failed! {res.json()['error']['message']}")


def monitor_task_progress(execute_id, api_key):
    # Generate execute task monitor url and SSE headers
    url = base_url + f"iscool/v3/execute/task/{execute_id}/monitor"
    headers = {'Accept': 'text/event-stream', "X-API-KEY": api_key}

    # Send request to monitor task progress
    response = requests.get(url, headers=headers, stream=True)

    # Create SSE client
    client = sseclient.SSEClient(response)

    # Init progress log and failed flag
    progress_log = []
    hasFailed = False

    # Handle SSE timeout
    def handle_sse_timeout():
        # Wait timeout for 10 seconds
        time.sleep(10)

        # if task progress is still empty after timeout
        if len(progress_log) == 0:
            print("SSE timeout!")
            client.close()
    threading.Thread(target=handle_sse_timeout).start()

    # Monitor task progress
    try:
        for event in client.events():
            # Parse event data
            response = json.loads(event.data)

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
        return

    print("Task success!")
