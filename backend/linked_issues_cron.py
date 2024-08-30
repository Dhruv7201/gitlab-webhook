import requests
from datetime import datetime, timedelta, timezone
from app.db import get_connection

# GitLab URL and token
gitlab_url = "https://code.ethicsinfotech.in"
private_token = ""

headers = {
    "Private-Token": private_token
}

# Calculate the time 6 hours ago in UTC
six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=6)
updated_after = six_hours_ago.isoformat()

# Initialize variables
issues = []
page = 1
per_page = 100


# data base
db = next(get_connection())
issues_collection = db['issues']

# Loop to fetch all issues updated in the last 6 hours
while True:
    issues_url = f"{gitlab_url}/api/v4/issues?per_page={per_page}&page={page}&updated_after={updated_after}"
    issues_response = requests.get(issues_url, headers=headers)

    # Check for response status and errors
    if issues_response.status_code != 200:
        print(f"Error: {issues_response.status_code}")
        break
    if "error" in issues_response.json():
        print(issues_response.json())
        break

    # Parse response
    current_page_issues = issues_response.json()
    if not current_page_issues:
        break

    issues.extend(current_page_issues)
    page += 1

# Print issue titles
for issue in issues:
    # loop through the issues and get linked issues from the notes
    issue_id = issue['iid']
    notes_url = f"{gitlab_url}/api/v4/projects/{issue['project_id']}/issues/{issue_id}/notes"
    notes_response = requests.get(notes_url, headers=headers)
    notes = notes_response.json()
    for note in notes:
        if 'body' in note:
            if 'marked this issue as related to' in note['body']:
                linked_issue_id = note['body'].split('marked this issue as related to')[1].strip().replace('#', '')
                linked_issue_id = int(linked_issue_id)
                db_issue = issues_collection.find_one({'iid': issue_id})
                if db_issue:
                    linked_issues = db_issue.get('linked_issues', [])
                    if linked_issue_id not in linked_issues:
                        linked_issues.append(linked_issue_id)
                        issues_collection.update_one({'iid': issue_id}, {'$set': {'linked_issues': linked_issues}})
                    else:
                        print(f"Error: Issue {linked_issue_id} already linked to issue {issue_id}")
                else:
                    print(f"Error: Issue {issue_id} not found in the database")
            
