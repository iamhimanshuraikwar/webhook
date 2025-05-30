# worker.py
import os
import time
import psycopg2
from resend import Resend
from dotenv import load_dotenv

# Load environment variables (useful for local testing)
# On Railway, these will be automatically available
load_dotenv()

# Database connection string
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    exit(1)

# Resend API Key
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
if not RESEND_API_KEY:
    print("Error: RESEND_API_KEY environment variable not set.")
    exit(1)

resend = Resend(api_key=RESEND_API_KEY)

def send_incomplete_plan_email(user_email: str, user_id: str):
    """
    Sends an email to a user who hasn't selected a plan.
    """
    try:
        result = resend.emails.send(
            {
                "from": "FigScreen <no-reply@figscreen.com>",
                "to": user_email,
                "subject": "Complete Your Figscreen Setup",
                "html": f"""
                    <p>Hi there,</p>
                    <p>We noticed you created an account with Figscreen but haven't selected a plan yet.</p>
                    <p>Complete your setup to start using all the features!</p>
                    <p>As a special offer, you can get 25% off any paid plan using the code: <strong>BETA20</strong></p>
                    <p><a href="https://app.figscreen.com/dashboard">Choose Your Plan</a></p>
                    <p>If you have any questions, feel free to reach out.</p>
                    <p>Best regards,<br>Hmanshu Raikwar<br>Founder of Figscreen</p>
                """
            }
        )
        print(f"Email sent successfully to {user_email}: {result['id']}")
        return True
    except Exception as e:
        print(f"Failed to send email to {user_email}: {e}")
        return False

def process_unprocessed_events():
    """
    Connects to the database, finds unprocessed events, sends emails, and updates records.
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
            WHERE event_type = 'no_plan_selected' AND email_sent = FALSE
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
                    SET email_sent = TRUE
                    WHERE id = %s
                    """,
                    (event_id,)
                )
                conn.commit()
                print(f"Marked event {event_id} as email_sent=TRUE.")
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
