import requests

# Your GitLab instance URL and Personal Access Token (PAT)
gitlab_url = "https://code.ethicsinfotech.in/"
private_token = ""

# Webhook URL to which issue events will be sent
webhook_url = "https://apidev.gitrepo.ethicstechnology.net/webhook"

# Headers for API requests
headers = {
    "Private-Token": private_token
}

# Step 1: List all projects
projects = []
page = 1
per_page = 100  # Adjust the number of results per page as needed

while True:
    projects_url = f"{gitlab_url}/api/v4/projects?per_page={per_page}&page={page}"
    projects_response = requests.get(projects_url, headers=headers)
    
    if projects_response.status_code != 200:
        break

    current_page_projects = projects_response.json()
    if not current_page_projects:
        break
    
    projects.extend(current_page_projects)
    page += 1


for project in projects:
    project_id = project['id']
    add_webhook_url = f"{gitlab_url}/api/v4/projects/{project_id}/hooks"
    
    webhook_data = {
        "url": webhook_url,
        "issues_events": False,
        "enable_ssl_verification": True
    }
    
    response = requests.post(add_webhook_url, headers=headers, json=webhook_data)
    
    if response.status_code == 201:
        print(f"Successfully added webhook to project {project['name']}")
    else:
        print(f"Failed to add webhook to project {project['name']}")
        print(response.json())
