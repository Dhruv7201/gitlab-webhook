import requests
import re
import json
import dateutil.parser


class GitlabTask:
    def __init__(self, gitlab_task_iid, gitlab_project_id):
        self.gitlab_task_iid = gitlab_task_iid
        self.gitlab_project_id = gitlab_project_id

    def convert_git_time(self, total_days):
        years = total_days // 2600
        months = (total_days % 2600) // 160
        weeks = ((total_days % 2600) % 160) // 40
        days = (((total_days % 2600) % 160) % 40) // 8
        hours = ((((total_days % 2600) % 160) % 40) % 8) // 60
        mins = ((((total_days % 2600) % 160) % 40) % 8) % 60
        time_spent = ""
        if years:
            time_spent += str(years) + "y"
        if months:
            time_spent += str(months) + "mo"
        if weeks:
            time_spent += str(weeks) + "w"
        if days:
            time_spent += str(days) + "d"
        if hours:
            time_spent += str(hours) + "h"
        if mins:
            time_spent += str(mins) + "m"
        return time_spent

    def get_issue_notes(self, gitlab_updated_at=None):
        GITLAB_DOMAIN = "https://code.ethicsinfotech.in"
        ACCESS_TOKEN = "glpat-cnaauXhTzMEhsHSNw9DY"
        headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}
        params = {"updated_after": gitlab_updated_at}
        if self.gitlab_task_iid:
            api_url_note = f"{GITLAB_DOMAIN}/api/v4/projects/{self.gitlab_project_id}/issues/{self.gitlab_task_iid}/notes"
        else:
            pass
        try:
            if gitlab_updated_at:
                response = requests.get(api_url_note, headers=headers, params=params)
            else:
                response = requests.get(api_url_note, headers=headers)
            print("\n ===Responce====", response)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Do something with the response here
                # For example, you can print the response content
                notes = response.json()
                added_data_dict = {}
                deleted_data_dict = {}
                deleted_data_list = []
                for note in sorted(notes, key=lambda x: x["id"]):
                    if note.get("system"):
                        time_pattern = re.search(
                            "^(add|subtract)ed (.*) of time spent at(.*)$",
                            note.get("body"),
                        )
                        not_time_spent_at_pattern = re.search(
                            "^(add|subtract)ed (.*) of time spent$", note.get("body")
                        )
                        delete_time_from_pattern = re.search(
                            "^(delet)ed (.*) of spent time from(.*)$", note.get("body")
                        )
                        delete_time_pattern = re.search(
                            "^(delet)ed (.*) of time spent at(.*)$", note.get("body")
                        )
                        if (
                            time_pattern
                            and str(note.get("author").get("id"))
                            + str(note.get("noteable_id"))
                            + str(note.get("noteable_iid"))
                            + "/"
                            + str(time_pattern.group(2))
                            + "/"
                            + str(time_pattern.group(3))
                            not in added_data_dict
                        ):
                            added_data_dict.update(
                                {
                                    str(note.get("author").get("id"))
                                    + str(note.get("noteable_id"))
                                    + str(note.get("noteable_iid"))
                                    + "/"
                                    + str(time_pattern.group(2))
                                    + "/"
                                    + str(time_pattern.group(3)): note
                                }
                            )
                        elif (
                            not_time_spent_at_pattern
                            and str(note.get("author").get("id"))
                            + str(note.get("noteable_id"))
                            + str(note.get("noteable_iid"))
                            + "/"
                            + str(not_time_spent_at_pattern.group(2))
                            + "/"
                            + str(note.get("updated_at"))
                            not in added_data_dict
                        ):
                            added_data_dict.update(
                                {
                                    str(note.get("author").get("id"))
                                    + str(note.get("noteable_id"))
                                    + str(note.get("noteable_iid"))
                                    + "/"
                                    + str(not_time_spent_at_pattern.group(2))
                                    + "/"
                                    + str(note.get("updated_at")): note
                                }
                            )
                        elif (
                            delete_time_pattern
                            and str(note.get("author").get("id"))
                            + str(note.get("noteable_id"))
                            + str(note.get("noteable_iid"))
                            + "/"
                            + str(delete_time_pattern.group(2))
                            + "/"
                            + str(delete_time_pattern.group(3))
                            not in deleted_data_dict
                        ):
                            deleted_data_dict.update(
                                {
                                    str(note.get("author").get("id"))
                                    + str(note.get("noteable_id"))
                                    + str(note.get("noteable_iid"))
                                    + "/"
                                    + str(delete_time_pattern.group(2))
                                    + "/"
                                    + str(delete_time_pattern.group(3)): note
                                }
                            )
                        elif (
                            delete_time_from_pattern
                            and str(note.get("author").get("id"))
                            + str(note.get("noteable_id"))
                            + str(note.get("noteable_iid"))
                            + "/"
                            + str(delete_time_from_pattern.group(2))
                            + "/"
                            + str(delete_time_from_pattern.group(3))
                            not in deleted_data_dict
                        ):
                            deleted_data_dict.update(
                                {
                                    str(note.get("author").get("id"))
                                    + str(note.get("noteable_id"))
                                    + str(note.get("noteable_iid"))
                                    + "/"
                                    + str(delete_time_from_pattern.group(2))
                                    + "/"
                                    + str(delete_time_from_pattern.group(3)): note
                                }
                            )
                        else:
                            print(f"Note: {note.get('body')}")

                        if not time_pattern:
                            time_pattern = re.search(
                                "^(delet)ed (.*) of spent time from(.*)$",
                                note.get("body"),
                            )
                            if (
                                time_pattern
                                and str(note.get("author").get("id"))
                                + str(note.get("noteable_id"))
                                + str(note.get("noteable_iid"))
                                + "/"
                                + str(time_pattern.group(2)).replace("-", "")
                                + "/"
                                + str(time_pattern.group(3))
                                not in deleted_data_dict
                            ):
                                deleted_data_dict.update(
                                    {
                                        str(note.get("author").get("id"))
                                        + str(note.get("noteable_id"))
                                        + str(note.get("noteable_iid"))
                                        + "/"
                                        + str(time_pattern.group(2)).replace("-", "")
                                        + "/"
                                        + str(time_pattern.group(3)): note
                                    }
                                )
                            if time_pattern:
                                for key, val in deleted_data_dict.items():
                                    if key in added_data_dict:
                                        deleted_data_list.append(
                                            added_data_dict.get(key).get("id")
                                        )
                                        added_data_dict.pop(key)
                for key, val in added_data_dict.items():
                    time_pattern = re.search(
                        "^(add|subtract)ed (.*) of time spent at(.*)$", val.get("body")
                    )
                    not_time_spent_at_pattern = re.search(
                        "^(add|subtract)ed (.*) of time spent$", val.get("body")
                    )
                    if time_pattern:
                        minus: bool = False
                        if time_pattern.group(1) == "subtract":
                            minus = True
                        time_spent = time_pattern.group(2)
                        total_days: float = 0
                        years = re.search("([0-9.]+)y", time_spent)
                        months = re.search("([0-9.]+)mo", time_spent)
                        weeks = re.search("([0-9.]+)w", time_spent)
                        days = re.search("([0-9.]+)d", time_spent)
                        hours = re.search("([0-9.]+)h", time_spent)
                        mins = re.search("([0-9.]+)m(?:i)?", time_spent)
                        if months:
                            mo = (
                                float(months.group(1)) * 160 * 2600
                            )  # month is four weeks of five days
                            # mo = float(months.group(1)) * 4 * 5  # month is four weeks of five days
                            if minus:
                                mo = -mo
                            total_days += mo
                        if weeks:
                            w = float(weeks.group(1)) * 40 * 3600  # week is five days
                            # w = float(weeks.group(1)) * 5  # week is five days
                            if minus:
                                w = -w
                            total_days += w
                        if days:
                            d = float(days.group(1)) * 8 * 3600
                            # d = float(days.group(1))
                            if minus:
                                d = -d
                            total_days += d
                        if hours:
                            h = float(hours.group(1)) * 60 * 60  # day of 8 hours
                            # h = float(hours.group(1)) / 8  # day of 8 hours
                            if minus:
                                h = -h
                            total_days += h
                        if mins:
                            m = float(mins.group(1)) * 60
                            # m = float(mins.group(1)) / 8 / 60
                            if minus:
                                m = -m
                            total_days += m
                        total_days = self.convert_git_time(abs(total_days))
                        date_spent = re.search(
                            "(\d{4}-\d{2}-\d{2})", time_pattern.group(3)
                        ).group(1)

                    elif not_time_spent_at_pattern:
                        minus: bool = False
                        if not_time_spent_at_pattern.group(1) == "subtract":
                            minus = True
                        time_spent = not_time_spent_at_pattern.group(2)
                        total_days: float = 0
                        years = re.search("([0-9.]+)y", time_spent)
                        months = re.search("([0-9.]+)mo", time_spent)
                        weeks = re.search("([0-9.]+)w", time_spent)
                        days = re.search("([0-9.]+)d", time_spent)
                        hours = re.search("([0-9.]+)h", time_spent)
                        mins = re.search("([0-9.]+)m(?:i)?", time_spent)
                        if months:
                            mo = float(months.group(1)) * 160 * 2600
                            if minus:
                                mo = -mo
                            total_days += mo
                        if weeks:
                            w = float(weeks.group(1)) * 40 * 3600
                            if minus:
                                w = -w
                            total_days += w
                        if days:
                            d = float(days.group(1)) * 8 * 3600
                            if minus:
                                d = -d
                            total_days += d
                        if hours:
                            h = float(hours.group(1)) * 60 * 60
                            if minus:
                                h = -h
                            total_days += h
                        if mins:
                            m = float(mins.group(1)) * 60
                            if minus:
                                m = -m
                            total_days += m
                        total_days = self.convert_git_time(abs(total_days))
                        date_spent: str = (
                            dateutil.parser.isoparse(val.get("updated_at"))
                            .date()
                            .isoformat()
                        )
            for key, _ in deleted_data_dict.items():
                if "T" in key:
                    # split key with t and remove last element
                    key = key.split("T")[0]

            print(f"Deleted Data: {json.dumps(deleted_data_dict, indent=4)}")
            print(f"Added Data: {json.dumps(added_data_dict, indent=4)}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    gitlab_task = GitlabTask(1, 834)
    gitlab_task.get_issue_notes()
