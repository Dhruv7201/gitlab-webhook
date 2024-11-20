from typing import Dict
from fastapi import APIRouter, Depends
from app.db import get_connection
from datetime import datetime

router = APIRouter()


@router.post("/get_issues_by_filter", tags=["filter"])
async def get_issues_by_filter(request: Dict, conn=Depends(get_connection)):
    try:
        project_id = request["project_id"]
        filter = request["filter"]
        users_collection = conn["users"]

        issue_list = [
            {"$unwind": "$work"},
        ]

        if project_id != 0:
            issue_list.append({"$match": {"work.project_id": project_id}})
        if filter != "":
            issue_list.append({"$match": {"work.label": filter}})
        issue_list.extend(
            [
                {"$sort": {"work.start_time": -1, "work.end_time": -1}},
                {
                    "$group": {
                        "_id": "$work.issue_id",
                        "work": {"$first": "$work"},
                        "user": {"$first": "$name"},
                    }
                },
                {
                    "$lookup": {
                        "from": "issues",
                        "localField": "work.issue_id",
                        "foreignField": "id",
                        "as": "result",
                    }
                },
                {"$unwind": "$result"},
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "result.author_id",
                        "foreignField": "id",
                        "as": "creator",
                    }
                },
                {"$unwind": "$creator"},
                {"$match": {"work.end_time": None}},
                {
                    "$project": {
                        "_id": 0,
                        "label": "$work.label",
                        "creator_name": "$creator.name",
                        "name": "$user",
                        "duration": "$work.duration",
                        "issue_name": "$result.title",
                        "url": "$result.url",
                        "created_at": "$result.created_at",
                        "creator_username": "$creator.username",
                        "last_update": {
                            "$cond": {
                                "if": {"$ne": ["$work.end_time", None]},
                                "then": "$work.end_time",
                                "else": "$work.start_time",
                            }
                        },
                    }
                },
            ]
        )

        issues_list = list(users_collection.aggregate(issue_list))
        curr_time = datetime.now()

        for issue in issues_list:
            if issue["duration"] is None:
                issue["duration"] = (curr_time - issue["last_update"]).total_seconds()
            issue["last_update"] = (curr_time - issue["last_update"]).total_seconds()
            issue["created_at"] = (curr_time - issue["created_at"]).total_seconds()

        return {
            "status": True,
            "data": issues_list,
            "message": "Issues fetched successfully",
        }
    except Exception as e:
        return {"status": False, "data": [], "message": str(e)}


@router.post("/get_onhold", tags=["filter"])
async def get_onhold(request: Dict, conn=Depends(get_connection)):
    try:
        project_id = request.get("project_id", 0)
        issues_collection = conn["issues"]

        issue_list = []

        if project_id != 0:
            issue_list.append({"$match": {"project_id": project_id}})

        issue_list.extend(
            [
                {
                    "$match": {
                        "work": {"$elemMatch": {"label": "OnHold", "end_time": None}}
                    }
                },
                {
                    "$lookup": {
                        "from": "projects",
                        "localField": "project_id",
                        "foreignField": "id",
                        "as": "project_details",
                    }
                },
                {"$unwind": "$project_details"},
                {
                    "$project": {
                        "_id": 0,
                        "id": 1,
                        "title": 1,
                        "on_hold_since": {
                            "$map": {
                                "input": {
                                    "$filter": {
                                        "input": "$work",
                                        "as": "workItem",
                                        "cond": {
                                            "$and": [
                                                {"$eq": ["$$workItem.label", "OnHold"]},
                                                {"$eq": ["$$workItem.end_time", None]},
                                            ]
                                        },
                                    }
                                },
                                "as": "onHoldWork",
                                "in": "$$onHoldWork.start_time",
                            }
                        },
                        "OnHold": 1,
                        "sub_group": 1,
                        "project_name": "$project_details.name",
                        "project_url": "$project_details.web_url",
                        "issue_url": "$url",
                        "subgroup_name": "$project_details.subgroup_name",
                    }
                },
            ]
        )

        issues_list = list(issues_collection.aggregate(issue_list))

        for issue in issues_list:
            issue["on_hold_since"] = issue["on_hold_since"][0]
            issue["on_hold_since"] = (
                datetime.now() - issue["on_hold_since"]
            ).total_seconds()
            issue["on_hold_since"] = issue["on_hold_since"] / (24 * 3600)
            issue["on_hold_since"] = round(issue["on_hold_since"], 2)
            issue["on_hold_since"] = f"{issue['on_hold_since']} Days"

        return {
            "status": True,
            "data": issues_list,
            "message": "Issues fetched successfully",
        }

    except Exception as e:
        return {"status": False, "data": [], "message": str(e)}
