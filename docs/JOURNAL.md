---
title: "rideminder"
summary: "Automated monthly Slack reminders for ride volunteers"
tech_stack:
  - Python
  - Slack API
  - Google Sheets API
  - GitHub Actions
repo_url: "https://github.com/dotjasonhwang/rideminder"
date: "2025-12-16"
status: "complete"
---

# rideminder

## Problem Statement

College ministry volunteers coordinate monthly ride schedules via a Google Sheet. This bot automatically notifies all assigned drivers for the upcoming month on the 15th via Slack, eliminating manual reminders to reduce last minute changes due to forgotten schedules.

## Tech Stack

- Language: Python 3.11+
- Infrastructure: GitHub Actions (monthly cron)
- APIs/Services: Slack API, Google Sheets API
- Key Libraries: gspread, slack-sdk, python-dateutil

## Architecture

- Trigger: GitHub Actions cron (15th monthly at 9 AM UTC)
  - Data: Read Google Sheet for next month's dates
    - Parse rows, extract unique names from driver columns (B-F)
  - Users: Fetch Slack channel members
    - Map sheet names → Slack user IDs (lowercase matching)
  - Message: Build formatted Slack message
    - Header with month/year + @mentions + swap instructions + sheet link
  - Post: Send to target channel with Block Kit formatting

## Challenges

- Straight forward slack app, no technical challenges, aside from learning how slack apps work, utilized Gemini.
- At one point I remember thinking that Google Cloud Functions was recommended due to the integration with GSheets API, but realized that doesn't make sense and is not true, and GitHub Actions was lighter weight option.

## Key Decisions

- GitHub Actions over Google Cloud Functions - Simpler, free, better visibility
- Channel-scoped user lookup - Only fetch users in target channel
- Environment-driven config - SHEET_NAME and MAINTAINER as env vars for flexibility

## What I Learned

- Learned how to deploy a Slack app to GitHub Actions
- Slack retains inactive user information

## Future Improvements

- For the use case, no future improvements are necessary.

## Misc Notes

- Slack bot needs: `users:read`, `chat:write`, `channels:read` scopes
- Bot must be invited to channel before posting
- Service account needs Viewer access to Google Sheet
