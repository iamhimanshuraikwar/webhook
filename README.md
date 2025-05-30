# FigScreen Email Worker

A background worker service that monitors for users who have created a FigScreen account but haven't selected a plan yet and triggers a webhook to handle further automation.

## Features

- Monitors PostgreSQL database for unprocessed user events
- Triggers a configurable webhook with user data
- Runs as a background service on Railway
- Processes events in batches to prevent overload

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `MAKE_WEBHOOK_URL`: The URL of the make.com webhook to trigger
   - `RESEND_API_KEY`: Resend API key (may be needed by your webhook automation)

## Deployment

This service is designed to be deployed on Railway. The `Procfile` and `runtime.txt` are already configured for Railway deployment.

## Environment Variables

- `DATABASE_URL`: Connection string for PostgreSQL database
- `MAKE_WEBHOOK_URL`: The URL of the make.com webhook to trigger
- `RESEND_API_KEY`: API key for Resend email service (optional, depending on webhook implementation)

## Database Schema

The service expects a `user_events` table with the following columns:
- `id`: Event ID
- `user_id`: User's unique identifier
- `email`: User's email address
- `event_type`: Type of event (e.g., 'no_plan_selected')
- `processed`: Boolean flag indicating if the event has been processed (webhook triggered)
- `created_at`: Timestamp of event creation

## Author

Hmanshu Raikwar
Founder of Figscreen 