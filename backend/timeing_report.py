import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


BASE_URL = "https://code.ethicsinfotech.in/api/graphql"
ACCESS_TOKEN = os.getenv("GITLAB_KEY")
ISSUE_ID = "gid://gitlab/Issue/12911"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

query = """
query issueTimeTrackingReport($id: IssueID!) {
  issuable: issue(id: $id) {
    id
    title
    timelogs {
      nodes {
        id
        timeSpent
        user {
          id
          name
        }
        spentAt
        note {
          body
        }
        summary
      }
    }
  }
}
"""

def fetch_timelogs(issue_id):
    payload = {
        "operationName": "issueTimeTrackingReport",
        "variables": {"id": issue_id},
        "query": query
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)
    response_data = response.json()

    if "data" in response_data and "issuable" in response_data["data"]:
        return response_data["data"]["issuable"]["timelogs"]["nodes"]
    else:
        raise Exception(f"Error fetching timelogs: {response_data}")

def format_timelogs(timelogs):
    report = []
    total_time_spent = 0

    for log in timelogs:
        spent_at = datetime.strptime(log["spentAt"], "%Y-%m-%dT%H:%M:%S%z").strftime("%d %b %Y")
        time_spent_hours = log["timeSpent"] / 3600
        total_time_spent += time_spent_hours
        report.append({
            "Date": spent_at,
            "Time Spent": f"{time_spent_hours}h",
            "User": log["user"]["name"],
            "Summary": log["summary"] or ""
        })

    report.append({
        "Date": "",
        "Time Spent": f"{total_time_spent}h",
        "User": "",
        "Summary": ""
    })

    return report


if __name__ == "__main__":
    try:
        timelogs = fetch_timelogs(ISSUE_ID)
        report = format_timelogs(timelogs)
        print("Report fetched successfully!")
        print(report)
    except Exception as e:
        print(f"Error: {e}")
