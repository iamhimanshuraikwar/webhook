# worker.py
import os
import time
import psycopg2
import resend
import requests # Import the requests library
from dotenv import load_dotenv

# Load environment variables (useful for local testing)
# On Railway, these will be automatically available
load_dotenv()

# Database connection string
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    exit(1)

# Resend API Key (still needed if make.com automation uses it via webhook)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
# We don't exit here if RESEND_API_KEY is not set, as the worker now triggers a webhook
# and the webhook might handle the Resend API key itself.

resend.api_key = RESEND_API_KEY # Keep this line for compatibility, but it might not be used directly by the worker anymore

# Make.com Webhook URL
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")
if not MAKE_WEBHOOK_URL:
    print("Error: MAKE_WEBHOOK_URL environment variable not set.")
    # Exit if webhook URL is not set, as this is now the primary action
    exit(1)

def send_incomplete_plan_email(user_email: str, user_id: str):
    """
    Triggers a webhook to send an email to a user who hasn't selected a plan.
    """
    try:
        # Data to send to the webhook
        payload = {
            "user_id": user_id,
            "user_email": user_email,
            # You can add more data here if needed for your make.com scenario
        }

        # Send POST request to the make.com webhook URL
        response = requests.post(MAKE_WEBHOOK_URL, json=payload)

        # Check if the request was successful
        response.raise_for_status()

        print(f"Webhook triggered successfully for user {user_id} ({user_email}). Status Code: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to trigger webhook for user {user_id} ({user_email}): {e}")
        return False

def process_unprocessed_events():
    """
    Connects to the database, finds unprocessed events, triggers webhook, and updates records.
    """
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Find unprocessed 'no_plan_selected' events
        cur.execute(
            """
            SELECT id, user_id, email
            FROM user_events
            WHERE event_type = 'no_plan_selected' AND processed = FALSE
            ORDER BY created_at ASC
            LIMIT 10 # Process in batches
            """
        )
        events_to_process = cur.fetchall()

        if not events_to_process:
            print("No unprocessed events found.")
            cur.close()
            conn.close()
            return

        print(f"Found {len(events_to_process)} unprocessed events.")

        for event_id, user_id, user_email in events_to_process:
            print(f"Processing event ID {event_id} for user {user_id} ({user_email})")
            email_sent_successfully = send_incomplete_plan_email(user_email, user_id)

            if email_sent_successfully:
                # Update the record to mark as email sent
                cur.execute(
                    """
                    UPDATE user_events
                    SET processed = TRUE
                    WHERE id = %s
                    """,
                    (event_id,)
                )
                conn.commit()
                print(f"Marked event {event_id} as processed=TRUE.")
            else:
                 # Handle case where email sending failed - maybe log or retry later
                 print(f"Email failed to send for event {event_id}. Will not mark as sent.")
                 conn.rollback() # Rollback if update wasn't committed


        cur.close()

    except Exception as e:
        print(f"An error occurred during processing: {e}")
        if conn:
            conn.rollback() # Rollback any pending transaction on error
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Worker started. Checking for events periodically...")
    # Run the processing periodically
    while True:
        process_unprocessed_events()
        # Wait for a specific duration before checking again (e.g., 3600 seconds = 1 hour)
        # Adjust this duration based on how frequently you want to send these emails
        sleep_duration = 3600
        print(f"Sleeping for {sleep_duration} seconds...")
        time.sleep(sleep_duration)
