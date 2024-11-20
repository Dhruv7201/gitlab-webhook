import requests
from dateutil import parser
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

group_id = "490"
access_token = os.getenv("GITLAB_KEY")
headers = {"Authorization": f"Bearer {access_token}"}
base_url = "https://code.ethicsinfotech.in/api/v4"
per_page = 100


def get_projects_in_group(group_id):
    url = f"{base_url}/groups/{group_id}/projects"
    projects = []
    page = 1

    while True:
        response = requests.get(
            url, headers=headers, params={"page": page, "per_page": per_page}
        )
        projects_page = response.json()
        if not projects_page:
            break
        projects.extend(projects_page)
        page += 1

    return projects


def get_subgroups(group_id):
    url = f"{base_url}/groups/{group_id}/subgroups"
    subgroups = []
    page = 1

    while True:
        response = requests.get(
            url, headers=headers, params={"page": page, "per_page": per_page}
        )
        subgroups_page = response.json()
        if not subgroups_page:
            break
        subgroups.extend(subgroups_page)
        page += 1

    return subgroups


def get_all_projects(group_id, path=""):
    projects = []
    current_path = path

    projects_in_group = get_projects_in_group(group_id)
    for project in projects_in_group:
        project["full_path"] = (
            current_path + "/" + project["name"] if current_path else project["name"]
        )
        projects.append(project)

    subgroups = get_subgroups(group_id)
    for subgroup in subgroups:
        subgroup_path = (
            f'{current_path}/{subgroup["name"]}' if current_path else subgroup["name"]
        )
        projects.extend(get_all_projects(subgroup["id"], subgroup_path))

    return projects


def get_issues_with_label(project_id, label):
    url = f"{base_url}/projects/{project_id}/issues"
    issues = []
    page = 1

    while True:
        response = requests.get(
            url,
            headers=headers,
            params={
                "labels": label,
                "state": "all",
                "page": page,
                "per_page": per_page,
            },
        )
        issues_page = response.json()
        if not issues_page:
            break
        issues.extend(issues_page)
        page += 1

    return issues


def filter_issues_by_month(issues, month, year):
    filtered_issues = []
    for issue in issues:
        created_at = parser.isoparse(issue["created_at"])
        if created_at.month == month and created_at.year == year:
            filtered_issues.append(issue)
    return filtered_issues


def get_user_from_log_with_label(project_id, issue_id, label):
    url = f"{base_url}/projects/{project_id}/issues/{issue_id}/notes"
    notes = []
    page = 1

    while True:
        response = requests.get(
            url, headers=headers, params={"page": page, "per_page": per_page}
        )
        notes_page = response.json()
        if not notes_page:
            break
        notes.extend(notes_page)
        page += 1

    return notes


def get_time_tracking_info(issue_id, project_id):
    url = f"{base_url}/projects/{project_id}/issues/{issue_id}"
    response = requests.get(url, headers=headers)
    issue_data = response.json()
    print(issue_data)
    time_tracking = issue_data.get("time_stats", {})
    return time_tracking.get("total_time_spent", 0)


def main():
    counter = 0
    data = []
    projects = get_all_projects(group_id)
    processed_issues = set()  # Track processed issue IDs to avoid duplicates

    for project in projects:
        issues = get_issues_with_label(project["id"], "L3-Support")
        july_issues = filter_issues_by_month(issues, 7, 2024)

        for issue in july_issues:
            if issue["id"] in processed_issues:
                continue  # Skip already processed issues
            track = "Mayur Prajapati"

            notes = get_user_from_log_with_label(project["id"], issue["iid"], "Doing")
            for note in notes:
                if note["author"]["name"] == track:
                    processed_issues.add(issue["id"])  # Mark issue as processed
                    counter += 1
                    time_tracking = get_time_tracking_info(issue["iid"], project["id"])
                    if time_tracking > 60:
                        if time_tracking > 3600:
                            time_tracking = f"{time_tracking // 3600}h {time_tracking % 3600 // 60}m"
                        else:
                            time_tracking = f"{time_tracking // 60}m"

                    data.append(
                        {
                            "Created Date": issue["created_at"],
                            "Issue Title": issue["title"],
                            "Issue ID": issue["iid"],
                            "Label": "L3-Support",
                            "Project Name": project["full_path"],
                            "Time Tracking": time_tracking,
                        }
                    )

                    break  # Exit the note loop once the issue is processed

    df = pd.DataFrame(data)
    df.to_csv("issues_report_july_2024.csv", index=False)


if __name__ == "__main__":
    main()
