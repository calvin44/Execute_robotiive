import api

project_name = "display"
task_name = "variable"
external_variables = {
    "number": 1,
    "string": "string",
    "boolean": True,
    "array": [1, 2, 3],
    "map": {
        "a": "b"
    }
}
target_url = "http://192.168.1.30:16888/"
api_key = "3d37b7b7-50df-4392-95c9-65a636417757"

if __name__ == "__main__":
    # Set backend URL
    api.set_backend_url(target_url)

    # Get project and task id by project name and task name
    project_id, task_id = api.get_project_and_task_id(project_name, task_name)

    # Run task
    execute_id = api.run_task(project_id, task_id, external_variables, api_key)

    # Control task
    # 1 - Pause, 2 - Continue, 3 - Restart, 4 - Stop
    # api.control_task(execute_id, 1, api_key)

    # Monitor task
    api.monitor_task_progress(execute_id, api_key)
