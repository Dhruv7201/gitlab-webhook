from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from datetime import datetime, timezone
import pytz
from typing import List, Dict
from pydantic import BaseModel
from typing import Any
import requests


router = APIRouter()


class DailyReportRequest(BaseModel):
    project_id: int
    selected_date: str


@router.post("/daily_report", response_model=List[Dict[str, Any]], tags=["reports"])
async def daily_report(
    report_request: DailyReportRequest, conn=Depends(get_connection)
):
    selected_date = datetime.strptime(report_request.selected_date, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59
    )

    # Fetch all issues that match the criteria
    issues_collection = conn["issues"]
    all_issues = list(
        issues_collection.find(
            {
                "project_id": report_request.project_id
                if report_request.project_id != 0
                else {"$exists": True}
            }
        )
    )

    # Fetch users and milestones in a single call
    users_collection = conn["users"]
    milestones_collection = conn["milestones"]

    users_dict = {user["id"]: user["name"] for user in users_collection.find()}
    milestones_dict = {
        milestone["id"]: milestone for milestone in milestones_collection.find()
    }

    report = []
    unique_issues = {}

    # Get the current time in UTC for calculating effort
    now = datetime.now(pytz.utc)

    for issue in all_issues:
        # Check for relevant work entries
        for work in issue.get("work", []):
            if (
                work["label"] in ["Doing", "Testing", "Documentation"]
                and work.get("end_time") is None
            ):
                assigned_to_name = users_dict.get(work["user_id"], "Unknown")

                # Initialize variable for last milestone details
                milestone_details = None

                # Get the last milestone
                milestones = issue.get("milestone", [])
                if milestones:
                    last_milestone = milestones[-1]  # Get the last milestone
                    milestone_id = last_milestone.get("milestone_id")
                    if milestone_id:
                        milestone_details = milestones_dict.get(milestone_id)

                # Ensure start_time is aware, assuming UTC timezone for now
                if isinstance(work["start_time"], datetime):
                    # If work['start_time'] is naive, localize it to UTC
                    if work["start_time"].tzinfo is None:
                        start_time = work["start_time"].replace(tzinfo=pytz.utc)
                    else:
                        start_time = work["start_time"]
                else:
                    if " " in str(work["start_time"]):
                        start_time = (
                            datetime.strptime(work["start_time"], "%Y-%m-%d %H:%M:%S")
                            if work.get("start_time")
                            else now
                        )
                        start_time = start_time.replace(
                            tzinfo=pytz.utc
                        )  # Make it aware by setting UTC timezone
                    if "T" in str(work["start_time"]):
                        start_time = (
                            datetime.fromisoformat(work["start_time"])
                            if work.get("start_time")
                            else now
                        )
                        start_time = start_time.replace(tzinfo=pytz.utc)

                # Now that both `start_time` and `now` are aware, we can subtract them
                time_diff = now - start_time
                effort_hours = time_diff.total_seconds() / 3600  # Convert to hours

                # Build the report entry
                report_entry = {
                    "id": issue["iid"],
                    "issue_id": issue["id"],
                    "issue_url": issue["url"],
                    "name": issue["title"],
                    "assigned_to": assigned_to_name,
                    "milestone": milestone_details["title"]
                    if milestone_details
                    else None,
                    "milestone_start_time": milestone_details["start_date"]
                    if milestone_details
                    else None,
                    "status": work["label"],
                    "start_time": work["start_time"],
                    "due_date": issue.get("due_date"),
                    "efforts": round(effort_hours, 2),  # Rounded to 2 decimal places
                    "comments": "",
                }

                # Check for efforts and comments from comments_efforts collection
                efforts_comments = list(
                    conn["comments_efforts"].find(
                        {
                            "issue_id": issue["iid"],
                            "date": selected_date.date().strftime("%Y-%m-%d"),
                        }
                    )
                )

                if efforts_comments:
                    report_entry["comments"] = efforts_comments[0].get("comments", "")

                # Manage unique issues based on issue_id
                issue_id = report_entry["issue_id"]
                if issue_id not in unique_issues:
                    unique_issues[issue_id] = report_entry
                else:
                    existing_issue = unique_issues[issue_id]
                    milestone_start_time = report_entry["milestone_start_time"]

                    # Keep the latest milestone start time
                    if milestone_start_time and (
                        not existing_issue.get("milestone_start_time")
                        or milestone_start_time > existing_issue["milestone_start_time"]
                    ):
                        unique_issues[issue_id] = report_entry

                    # If milestone start times are equal, check start_time
                    elif milestone_start_time == existing_issue.get(
                        "milestone_start_time"
                    ):
                        start_time = report_entry["start_time"]
                        if start_time and (
                            not existing_issue.get("start_time")
                            or start_time > existing_issue["start_time"]
                        ):
                            unique_issues[issue_id] = report_entry
    # Convert the unique issues dictionary back to a list
    report = list(unique_issues.values())

    # Format due_date
    for issue in report:
        if issue.get("due_date"):
            issue["due_date"] = str(issue["due_date"]).split(" ")[0]

    return report


@router.post("/daily_report_comments", tags=["reports"])
async def daily_report_comments(request: Dict, conn=Depends(get_connection)):
    date_str = request.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    local_tz = pytz.timezone("Asia/Kolkata")

    try:
        local_date = local_tz.localize(
            datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        )
        date_to_store = local_date.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Expected YYYY-MM-DD."
        )

    username = request.get("username")
    data = request.get("data", [])

    comments_efforts_collection = conn["comments_efforts"]

    for item in data:
        if not item.get("comments"):
            continue
        issue_id = item.get("id")
        comment = item.get("comments")
        effort_hours = item.get("efforts", 0)

        existing_comment = comments_efforts_collection.find_one(
            {"issue_id": issue_id, "date": date_to_store, "user_id": username}
        )

        if existing_comment:
            comments_efforts_collection.update_one(
                {"_id": existing_comment["_id"]},
                {"$set": {"comments": comment, "efforts": effort_hours}},
            )
        else:
            comments_efforts_collection.insert_one(
                {
                    "issue_id": issue_id,
                    "date": date_to_store,
                    "user_id": username,
                    "comments": comment,
                    "efforts": effort_hours,
                }
            )

    return {"status": True, "message": "Comments saved successfully"}


# Helper function to convert _id to string in a list of documents
def convert_ids_to_string(documents):
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents


# Fetch data function using asynchronous HTTP requests
async def fetch_data_with_url(url):
    response = requests.get(url)
    return response.json()


@router.get("/get_all_data", tags=["reports"])
async def get_all_data(conn=Depends(get_connection)):
    print(conn)
    collections = {
        "issues": conn["issues"],
        "comments_efforts": conn["comments_efforts"],
        "logins": conn["login"],
        "milestones": conn["milestones"],
        "projects": conn["projects"],
        "users": conn["users"],
    }

    start_time = datetime.now()

    # Asynchronously fetch all collections' data and convert _id to string
    result = {}
    for key, collection in collections.items():
        print(f"Fetching data for {key}...")
        print("Time taken: ", datetime.now() - start_time)
        data = list(collection.find())
        result[key] = convert_ids_to_string(data)

    print(f"Time taken: {datetime.now() - start_time}")
    return result


@router.get("/store_all_data", tags=["reports"])
async def store_all_data(db=Depends(get_connection)):
    url = "https://apidev.gitrepo.ethicstechnology.net/get_all_data"

    data = await fetch_data_with_url(url)
    # Get references to collections
    collections = {
        "issues": db["issues"],
        "comments_efforts": db["comments_efforts"],
        "logins": db["login"],
        "milestones": db["milestones"],
        "projects": db["projects"],
        "users": db["users"],
    }

    # delete existing data
    for key, collection in collections.items():
        collection.delete_many({})

    # Store data in local DB
    for key, collection in collections.items():
        if key in data:  # Check if the key exists in the fetched data
            collection.insert_many(data[key])

    return {"status": True, "message": "Data stored successfully"}
