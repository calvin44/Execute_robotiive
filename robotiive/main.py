# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=bare-except


from robotiive.api import monitor_execution, set_backend_url, run_task, get_project_and_task_id


def execute_robotiive(project_name, task_name, external_variables):
    try:
        # Set backend URL
        set_backend_url("https://localhost:16888/")

        # Get project and task id by project name and task name
        project_id, task_id = get_project_and_task_id(project_name, task_name)

        # Run task
        execute_id = run_task(project_id, task_id, external_variables)

        # monitor task
        monitor_status = monitor_execution(execute_id=execute_id)

        return monitor_status
    except:
        return {"status": "Failed"}
