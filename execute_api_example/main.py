import api

project_name = "GenerateLicense"
task_name = "Main"
external_variables = {
    "StringPassedByExecutor": "/cicd run license_generate -expiredDate -1 -licenseType 0 -productType 4 -uid d0a9dee6-e353-51a1-bf15-5f0934fb904e",
}
target_url = "http://192.168.1.30:16888/"
api_key = "15641be3-c677-4d18-bbb9-81b040840131"

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
