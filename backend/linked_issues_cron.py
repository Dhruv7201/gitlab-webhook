import requests
from datetime import datetime, timedelta, timezone
from app.db import get_connection

# GitLab URL and token
gitlab_url = "https://code.ethicsinfotech.in"
private_token = "glpat-cnaauXhTzMEhsHSNw9DY"

headers = {"Private-Token": private_token}

# Calculate the time 6 hours ago in UTC
six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=6)
updated_after = six_hours_ago.isoformat()

# Initialize variables
issues = []
page = 1
per_page = 100

# Database connection
db = next(get_connection())
issues_collection = db["issues"]

# Loop through all projects
project_page = 1

while True:
    projects_url = f"{gitlab_url}/api/v4/projects?per_page={per_page}&page={project_page}&last_activity_after={updated_after}"
    projects_response = requests.get(projects_url, headers=headers)

    # Check for response status and errors
    if projects_response.status_code != 200:
        print(f"Error fetching projects: {projects_response.status_code}")
        break

    projects = projects_response.json()
    if not projects:
        break

    # Loop through each project
    for project in projects:
        project_id = project["id"]
        project_url = project["web_url"]
        # Loop to fetch all issues updated in the last 6 hours for the current project
        issue_page = 1

        while True:
            issues_url = f"{gitlab_url}/api/v4/projects/{project_id}/issues?per_page={per_page}&page={issue_page}&updated_after={updated_after}"
            issues_response = requests.get(issues_url, headers=headers)

            # Check for response status and errors
            if issues_response.status_code != 200:
                print(
                    f"Error fetching issues for project {project_id}: {issues_response.status_code}"
                )
                break

            current_page_issues = issues_response.json()
            if not current_page_issues:
                break

            issues.extend(current_page_issues)
            issue_page += 1

            # Process each issue
            for issue in current_page_issues:
                issue_id = issue["iid"]

                # Get notes for the issue to find linked issues
                notes_url = (
                    f"{gitlab_url}/api/v4/projects/{project_id}/issues/{issue_id}/notes"
                )
                notes_response = requests.get(notes_url, headers=headers)
                notes = notes_response.json()

                for note in notes:
                    if "body" in note:
                        if "marked this issue as related to" in note["body"]:
                            linked_issue_id = (
                                note["body"]
                                .split("marked this issue as related to")[1]
                                .strip()
                                .replace("#", "")
                            )
                            linked_issue_id = (
                                linked_issue_id.split("\n")[0].strip().replace(" ", "")
                            )
                            linked_issue_id = int(linked_issue_id)

                            db_issue = issues_collection.find_one(
                                {"iid": issue_id, "project_id": project_id}
                            )
                            if db_issue:
                                linked_issues = db_issue.get("linked_issues", [])
                                if linked_issue_id not in linked_issues:
                                    linked_issues.append(linked_issue_id)
                                    issues_collection.update_one(
                                        {"iid": issue_id, "project_id": project_id},
                                        {"$set": {"linked_issues": linked_issues}},
                                    )
                                    print(
                                        f"Linked issue {linked_issue_id} to issue {issue_id}"
                                    )
                                else:
                                    pass
                            else:
                                pass

    project_page += 1
