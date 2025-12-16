import os
import sys
import gspread
from datetime import datetime
from dateutil.relativedelta import relativedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# --- Configuration ---
# NOTE: Set these as Environment Variables in your GCF settings!
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
TARGET_CHANNEL_ID = os.environ.get("TARGET_CHANNEL_ID")
SPREADSHEET_URL = os.environ.get("GOOGLE_SHEET_URL")
SHEET_NAME = os.environ.get("SHEET_NAME")
SPREADSHEET_KEY_FILE = "nlf-college-ministry-rideminder.json" # Name of the file you upload
MAINTAINER = os.environ.get("MAINTAINER")


# --- 1. User Lookup Function ---
def get_user_id_map(client, channel_id):
    """Fetches users in the specified channel and creates a map from Display Name to User ID."""
    try:
        # Get all members of the channel (requires channels:read or groups:read scope)
        channel_members_response = client.conversations_members(channel=channel_id)
        if not channel_members_response["ok"]:
            print("Error fetching channel members")
            return {}

        member_ids = set(channel_members_response["members"])
        print(f"Found {len(member_ids)} members in channel")

        # Get all users (requires users:read scope)
        response = client.users_list()

        if response["ok"]:
            user_map = {}
            for user in response["members"]:
                # Only include users who are in the channel
                if user["id"] in member_ids:
                    # Use a reliable name/email from the sheet for the lookup
                    display_name = user.get("profile", {}).get("real_name") or user.get("name")
                    if display_name:
                        user_map[display_name.lower()] = user["id"]
            return user_map
    except SlackApiError as e:
        print(f"Error fetching users: {e}")
        # In a real app, you would log this error properly
        return {}


# --- 2. Main Cloud Function Entry Point ---
def run_monthly_report(request):
    """
    Main function triggered by Google Cloud Scheduler on the 15th of each month.
    Looks at next month's dates and @mentions all unique people involved.
    """
    print("--- Starting Monthly Ride Reminder ---")

    # Initialize Slack Client
    slack_client = WebClient(token=SLACK_BOT_TOKEN)

    # --- Step A: Calculate Next Month ---
    today = datetime.now()
    next_month = today + relativedelta(months=1)
    target_month = next_month.month
    target_year = next_month.year
    print(f"Looking for dates in {target_month}/{target_year}")

    # --- Step B: Google Sheets Setup ---
    try:
        # Authenticate using the Service Account key file you uploaded
        gc = gspread.service_account(filename=SPREADSHEET_KEY_FILE)

        # Open the spreadsheet by URL
        spreadsheet = gc.open_by_url(SPREADSHEET_URL)
        worksheet = spreadsheet.worksheet(SHEET_NAME)

        # Get all records as a list of dictionaries
        data = worksheet.get_all_records()
    except Exception as e:
        print(f"Error accessing Google Sheet: {e}")
        sys.exit(1)

    # --- Step C: Filter rows for next month and collect unique names ---
    unique_people = set()

    for row in data:
        # Get the date from the row
        date_str = str(row.get('Date', '')).strip()

        if not date_str:
            continue

        # Parse the date (format: M/D/YY)
        try:
            date_obj = datetime.strptime(date_str, "%m/%d/%y")

            # Check if this date is in the target month/year
            if date_obj.month == target_month and date_obj.year == target_year:
                # Collect names from columns: To (1), To (2), From (1), From (2), From (3)
                columns_to_check = ['To (1)', 'To (2)', 'From (1)', 'From (2)', 'From (3)']

                for col in columns_to_check:
                    name = str(row.get(col, '')).strip()
                    if name:  # Only add non-empty names
                        unique_people.add(name)
        except ValueError:
            # Skip rows with invalid date formats
            print(f"Skipping row with invalid date: {date_str}")
            continue

    print(f"Found {len(unique_people)} unique people for next month")

    # --- Step D: User ID Mapping & Build Mentions ---
    user_id_map = get_user_id_map(slack_client, TARGET_CHANNEL_ID)
    mentions = []
    for name in sorted(unique_people):  # Sort for consistent ordering
        # Lookup the User ID (convert to lowercase for robust matching)
        user_id = user_id_map.get(name.lower())

        if user_id:
            mentions.append(f"<@{user_id}>")
        else:
            mentions.append(name)  # If ID not found, just use the name (won't notify)
            print(f"Warning: Could not find Slack ID for name: {name}")

    # Create the alert message
    mentions_text = " ".join(mentions)

    # Format the month/year for the header
    month_year_str = next_month.strftime("%b %Y")  # e.g., "Jan 2026"

    # Build the message
    header_text = f":alarm_clock: {month_year_str} rides"
    body_text = f"<{SPREADSHEET_URL}|College Ministry Volunteer Drivers>. Unavailable? Please find someone to swap with.\n\n{mentions_text}"
    footer_text = f"This message was sent by rideminder. Please contact <@{user_id_map.get(MAINTAINER.lower())}> if I am not working"

    # Fallback text for notifications
    alert_message = f"{month_year_str} rides: {mentions_text}"

    # --- Step E: Post Message to Slack ---
    try:
        slack_client.chat_postMessage(
            channel=TARGET_CHANNEL_ID,
            text=alert_message,  # Same as the actual message, required by Slack API
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": header_text
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": body_text
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": footer_text
                        }
                    ]
                }
            ]
        )
        print("Successfully posted message to Slack.")
        return {"status": "success", "message": "Reminder posted successfully"}, 200

    except SlackApiError as e:
        print(f"Error posting to Slack: {e.response['error']}")
        sys.exit(1)


# To run locally for testing:
if __name__ == "__main__":
    run_monthly_report(None)
