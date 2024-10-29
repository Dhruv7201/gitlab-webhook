# GitLab Webhook Event Capture

## Overview

This project implements a webhook to capture events from GitLab and store relevant data in a MongoDB database. The application is built using FastAPI for the backend and React with TypeScript for the frontend. The main focus is on capturing events related to issues, users, projects, logins, and milestones.

## Features

- **Webhook Integration**: Listen to GitLab events and process them in real-time.
- **Data Storage**: Store captured events in MongoDB across multiple collections:
  - **Issues Collection**: Tracks changes related to issues, including labels, assignees, and child tasks.
  - **Users Collection**: Captures user-related data.
  - **Projects Collection**: Stores project details.
  - **Logins Collection**: User login and passwords are stored here
  - **Milestones Collection**: Manages milestone changes.
- **Cron Job for Linked Issues**: Planned feature to track linked issues periodically (implementation not yet set).

## Technologies Used

- **Backend**: FastAPI
- **Frontend**: React with TypeScript
- **Database**: MongoDB

## Installation

### Prerequisites

- Python 3.10+
- Node.js 20.18.0
- MongoDB instance

### Backend Setup

1. Clone the repository:

   ```bash
   git clone https://code.ethicsinfotech.in/ethics-projects/ethics-python/ethics-gitlab-reports
   cd gitlab-webhook-event-capture/backend
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables for your MongoDB connection in a `.env` file.

5. Run the backend server:
   ```bash
   python3 run.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd ../frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the frontend application:
   ```bash
   npm run dev
   ```

## Webhook Configuration

To set up the GitLab webhook:

1. Go to your GitLab project settings.
2. Navigate to the "Webhooks" section.
3. Enter the URL for your FastAPI webhook endpoint (e.g., `https://apidev.gitrepo.ethicstechnology.net/webhook`).
4. Select the events you want to capture (e.g., Issues events).
5. Click "Add Webhook".

## Data Models

### Issues Collection

- **Important Fields**:
  - `work`: Array of labels assigned to the issue.
  - `assignees`: Array of user IDs assigned to the issue.
  - `milestone`: Current milestone associated with the issue.
  - `child_task`: Array of child tasks linked to the issue.

## Future Work

- Implement the cron job to periodically check and track linked issues.
- Enhance frontend UI for better user experience.

