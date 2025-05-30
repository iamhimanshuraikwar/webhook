# FigScreen Email Worker

A background worker service that sends reminder emails to users who have created a FigScreen account but haven't selected a plan yet.

## Features

- Monitors PostgreSQL database for unprocessed user events
- Sends personalized reminder emails via Resend
- Includes special offer (25% off with BETA20 code)
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
   - `RESEND_API_KEY`: Resend API key for sending emails

## Deployment

This service is designed to be deployed on Railway. The `Procfile` and `runtime.txt` are already configured for Railway deployment.

## Environment Variables

- `DATABASE_URL`: Connection string for PostgreSQL database
- `RESEND_API_KEY`: API key for Resend email service

## Database Schema

The service expects a `user_events` table with the following columns:
- `id`: Event ID
- `user_id`: User's unique identifier
- `email`: User's email address
- `event_type`: Type of event (e.g., 'no_plan_selected')
- `email_sent`: Boolean flag indicating if email was sent
- `created_at`: Timestamp of event creation

## Author

Hmanshu Raikwar
Founder of FigScreen 