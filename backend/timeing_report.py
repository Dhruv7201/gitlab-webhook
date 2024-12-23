import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import re

load_dotenv()

# URL of the API
api_url = "https://code.ethicsinfotech.in/api/v4/projects/834/issues/1/notes"
now = datetime.now()
end_time = now.strftime("%Y-%m-%dT%H:%M:%S")
start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%S")
print(f"Fetching data from {start_time} to {end_time}")


# Function to fetch and filter the data by time
def fetch_and_format_data(api_url, start_time, end_time):
    headers = {"PRIVATE-TOKEN": os.getenv("GITLAB_KEY")}

    # Send a GET request to the API to get all notes
    response = requests.get(api_url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

    # Parse the JSON response
    data = response.json()

    # List to hold the formatted data
    formatted_data = []

    for note in data:
        # Extract the created_at timestamp and check if it falls within the last 15 minutes
        created_at = datetime.strptime(note["created_at"], "%Y-%m-%dT%H:%M:%S.%f+05:30")

        # Filter notes based on time (if the note was created within the last 15 minutes)
        if created_at >= datetime.strptime(
            start_time, "%Y-%m-%dT%H:%M:%S"
        ) and created_at <= datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S"):
            # Extracting relevant fields
            body = note["body"]

            # Check if the body contains a "spent at" date and extract it
            spent_at_match = re.search(r"at (\d{4}-\d{2}-\d{2})", body)
            if spent_at_match:
                # Extract the date from the "spent at" part
                formatted_date = spent_at_match.group(1)
                # Remove the "spent at" and keep only the time spent
                time_spent = body.split(" at ")[0].replace("added ", "")
                # Format to dd MMM YYYY
                formatted_date = datetime.strptime(formatted_date, "%Y-%m-%d").strftime(
                    "%d %b %Y"
                )
            else:
                # If no "spent at" date, use the created_at timestamp
                formatted_date = created_at.strftime("%d %b %Y")
                time_spent = body.replace("added ", "")  # Clean up the "added" word

            # Extract user name and user_id
            user = note["author"]["name"]
            user_id = note["author"]["id"]

            # Get the user email from the user ID
            user_url = f"https://code.ethicsinfotech.in/api/v4/users/{user_id}"
            user_response = requests.get(user_url, headers=headers)
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_email = user_data.get("email", "N/A")
            else:
                user_email = "N/A"

            summary = note.get("description", body[:50])

            # Append formatted data to the list
            formatted_data.append(
                {
                    "Date": formatted_date,
                    "Time Spent": time_spent,
                    "Email": user_email,
                    "User": user,
                    "Summary": summary,
                }
            )

    return formatted_data


# Call the function and get the formatted data
formatted_data = fetch_and_format_data(api_url, start_time, end_time)

# Print the formatted data
for entry in formatted_data:
    print(entry)
