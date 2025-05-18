# SETUP https://cloud.google.com/pubsub/docs/overview

# AI: This script sets up Google Cloud Pub/Sub for Gmail notifications.
# AI: It creates a topic and a subscription, and grants Gmail permission to publish.
# AI: You will need to replace placeholders like YOUR_PROJECT_ID, YOUR_TOPIC_ID, etc.
# AI: if you choose not to use the interactive prompts.

# AI: Prerequisites:
# AI: 1. Google Cloud SDK (gcloud) installed and authenticated.
# AI:    Run 'gcloud auth login' and 'gcloud auth application-default login'.
# AI: 2. Gmail API enabled for your project (you mentioned it's already enabled).
# AI: 3. Pub/Sub API enabled for your project. If not, run:
# AI:    gcloud services enable pubsub.googleapis.com --project=YOUR_PROJECT_ID
# AI:    (Replace YOUR_PROJECT_ID with your actual project ID)

echo "This script will guide you through setting up Pub/Sub for Gmail API notifications."

# AI: Function to check if a service is enabled
check_service_enabled() {
  local service_name="$1"
  local project_id="$2"
  local enabled
  enabled=$(gcloud services list --project="$project_id" --filter="config.name:$service_name" --format="value(state)" 2>/dev/null)
  if [ "$enabled" = "ENABLED" ]; then
    return 0 # True
  else
    return 1 # False
  fi
}

echo "---------------------------------------------------------------------"
echo "Step 1: Configure Project and Service Account"
echo "---------------------------------------------------------------------"

# AI: Get Project ID
current_project=$(gcloud config get-value project 2>/dev/null)
if [ -z "$current_project" ]; then
  echo "No default Google Cloud Project ID is set."
  read -r -p "Please enter your Google Cloud Project ID: " YOUR_PROJECT_ID
else
  read -r -p "Enter your Google Cloud Project ID or press Enter to use '$current_project': " user_input_project_id
  if [ -z "$user_input_project_id" ]; then
    YOUR_PROJECT_ID=$current_project
  else
    YOUR_PROJECT_ID=$user_input_project_id
  fi
fi
gcloud config set project "$YOUR_PROJECT_ID"
echo "Using Project ID: $YOUR_PROJECT_ID"

# AI: Enable Pub/Sub API if not already enabled
PUBSUB_API="pubsub.googleapis.com"
echo "Checking if Pub/Sub API ($PUBSUB_API) is enabled for project $YOUR_PROJECT_ID..."
if check_service_enabled "$PUBSUB_API" "$YOUR_PROJECT_ID"; then
  echo "Pub/Sub API is already enabled."
else
  echo "Pub/Sub API is not enabled. Enabling it now..."
  gcloud services enable "$PUBSUB_API" --project="$YOUR_PROJECT_ID"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to enable Pub/Sub API. Please enable it manually in the Google Cloud Console and re-run the script."
    exit 1
  fi
  echo "Pub/Sub API enabled successfully."
fi

# AI: Gmail API (user stated it's enabled, good to double check)
GMAIL_API="gmail.googleapis.com"
echo "Checking if Gmail API ($GMAIL_API) is enabled for project $YOUR_PROJECT_ID..."
if check_service_enabled "$GMAIL_API" "$YOUR_PROJECT_ID"; then
  echo "Gmail API is already enabled."
else
  echo "Warning: Gmail API is not enabled. You stated it was, but please ensure it is enabled in the Google Cloud Console for the script to work."
  # AI: Optionally, exit here or try to enable it. For now, just warn.
  # gcloud services enable $GMAIL_API --project=$YOUR_PROJECT_ID
fi


echo "---------------------------------------------------------------------"
echo "Step 2: Define Pub/Sub Resource Names"
echo "---------------------------------------------------------------------"
read -r -p "Enter a name for your Pub/Sub Topic (e.g., gmail-notifications): " YOUR_TOPIC_ID
read -r -p "Enter a name for your Pub/Sub Subscription (e.g., gmail-subscriber): " YOUR_SUBSCRIPTION_ID

echo "---------------------------------------------------------------------"
echo "Step 3: Create Pub/Sub Topic"
echo "---------------------------------------------------------------------"
echo "Creating Pub/Sub topic '$YOUR_TOPIC_ID' in project '$YOUR_PROJECT_ID'..."
if gcloud pubsub topics describe "$YOUR_TOPIC_ID" --project="$YOUR_PROJECT_ID" >/dev/null 2>&1; then
  echo "Topic '$YOUR_TOPIC_ID' already exists."
else
  gcloud pubsub topics create "$YOUR_TOPIC_ID" \
      --project="$YOUR_PROJECT_ID"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to create Pub/Sub topic. Please check permissions and configuration."
    exit 1
  fi
  echo "Pub/Sub topic '$YOUR_TOPIC_ID' created successfully."
fi

echo "---------------------------------------------------------------------"
echo "Step 4: Create Pub/Sub Subscription"
echo "---------------------------------------------------------------------"
echo "Creating Pub/Sub subscription '$YOUR_SUBSCRIPTION_ID' for topic '$YOUR_TOPIC_ID'..."
if gcloud pubsub subscriptions describe "$YOUR_SUBSCRIPTION_ID" --project="$YOUR_PROJECT_ID" >/dev/null 2>&1; then
  echo "Subscription '$YOUR_SUBSCRIPTION_ID' already exists."
else
  gcloud pubsub subscriptions create "$YOUR_SUBSCRIPTION_ID" \
      --topic="$YOUR_TOPIC_ID" \
      --project="$YOUR_PROJECT_ID" \
      --ack-deadline=60 # AI: Default is 10s. 60s gives more time for processing. Adjust as needed.
  if [ $? -ne 0 ]; then
    echo "Error: Failed to create Pub/Sub subscription."
    exit 1
  fi
  echo "Pub/Sub subscription '$YOUR_SUBSCRIPTION_ID' created successfully."
fi

echo "---------------------------------------------------------------------"
echo "Step 5: Grant Gmail Service Account Permission"
echo "---------------------------------------------------------------------"
# AI: The service account for Gmail push notifications.
GMAIL_PUSH_SERVICE_ACCOUNT="service-${YOUR_PROJECT_NUMBER}@gcp-sa-gmail.iam.gserviceaccount.com"
# AI: Fallback, more general one sometimes cited, though project-specific is better if known
# GMAIL_PUSH_SERVICE_ACCOUNT_LEGACY="gmail-api-push@system.gserviceaccount.com"

# AI: To get PROJECT_NUMBER
echo "Fetching project number for $YOUR_PROJECT_ID..."
YOUR_PROJECT_NUMBER=$(gcloud projects describe "$YOUR_PROJECT_ID" --format="value(projectNumber)")
if [ -z "$YOUR_PROJECT_NUMBER" ]; then
  echo "Error: Could not retrieve project number for $YOUR_PROJECT_ID. Using legacy Gmail service account."
  GMAIL_SERVICE_ACCOUNT_TO_GRANT="gmail-api-push@system.gserviceaccount.com"
else
  GMAIL_SERVICE_ACCOUNT_TO_GRANT="service-$YOUR_PROJECT_NUMBER@gcp-sa-gmail.iam.gserviceaccount.com"
fi

echo "Granting Gmail service account '$GMAIL_SERVICE_ACCOUNT_TO_GRANT' the 'roles/pubsub.publisher' role on topic '$YOUR_TOPIC_ID'..."
# AI : Attempt to grant IAM permission and provide specific feedback based on success or failure.
if gcloud pubsub topics add-iam-policy-binding "$YOUR_TOPIC_ID" \
    --member="serviceAccount:${GMAIL_SERVICE_ACCOUNT_TO_GRANT}" \
    --role="roles/pubsub.publisher" \
    --project="$YOUR_PROJECT_ID"; then
  # AI: The gcloud command above will print its own success message (e.g., "Updated IAM policy...").
  # AI: We add a script-specific confirmation.
  echo "Successfully processed IAM permission grant for '$GMAIL_SERVICE_ACCOUNT_TO_GRANT' on topic '$YOUR_TOPIC_ID'."
else
  # AI : The gcloud command failed. It will print its own error message (e.g., service account not found).
  # AI : Below, we provide the detailed explanation and next steps from the script's perspective.
  echo "" # AI : Add a newline for better readability before the big box.
  echo "################################ IMPORTANT ################################"
  echo "# Error: The command to grant IAM permission to '$GMAIL_SERVICE_ACCOUNT_TO_GRANT' likely FAILED."
  echo "# The gcloud command output directly above this message should indicate the specific error."
  echo "#"
  echo "# If the error indicates the service account does not exist (common scenario):"
  echo "# This is often because this specific Gmail service account"
  echo "# (typically 'service-YOUR_PROJECT_NUMBER@gcp-sa-gmail.iam.gserviceaccount.com', where YOUR_PROJECT_NUMBER would be for project '$YOUR_PROJECT_ID')"
  echo "# is only automatically created by Google AFTER the first successful 'users.watch()' API call"
  echo "# is made for this project."
  echo "#"
  echo "# NEXT STEPS (if service account did not exist):"
  echo "# 1. Proceed to configure and run your Python script (e.g., '3_gmail_demo_sub_pub.py') which should call 'users.watch()'."
  echo "# 2. Once 'users.watch()' has been successfully called at least once for any user in project '$YOUR_PROJECT_ID',"
  echo "#    the service account '$GMAIL_SERVICE_ACCOUNT_TO_GRANT' should then exist."
  echo "# 3. You will then need to grant it the 'Pub/Sub Publisher' role on topic '$YOUR_TOPIC_ID'."
  echo "#    You can do this manually in the Google Cloud Console:"
  echo "#    - Go to: Pub/Sub -> Topics -> '$YOUR_TOPIC_ID'"
  echo "#    - Click on the 'PERMISSIONS' tab (you might need to click 'SHOW INFO PANEL' on the right if it's not visible)."
  echo "#    - Click 'ADD PRINCIPAL'."
  echo "#    - New principals: $GMAIL_SERVICE_ACCOUNT_TO_GRANT"
  echo "#    - Role: Pub/Sub Publisher (Select from dropdown: Pub/Sub -> Pub/Sub Publisher or use role ID 'roles/pubsub.publisher')"
  echo "#    - Click 'SAVE'."
  echo "#"
  echo "# Alternatively, after 'users.watch()' has successfully run and the service account exists,"
  echo "# you can try re-running the following command in your Cloud Shell (ensure variables are set or replaced):"
  echo "# ---"
  echo "# gcloud pubsub topics add-iam-policy-binding \"$YOUR_TOPIC_ID\" \\"
  echo "#     --member=\"serviceAccount:${GMAIL_SERVICE_ACCOUNT_TO_GRANT}\" \\"
  echo "#     --role=\"roles/pubsub.publisher\" \\"
  echo "#     --project=\"$YOUR_PROJECT_ID\""
  echo "# ---"
  echo "######################################################################"
  echo "" # AI : Add a newline after the big box.
  echo "IAM permission grant for '$GMAIL_SERVICE_ACCOUNT_TO_GRANT' on topic '$YOUR_TOPIC_ID' requires manual follow-up as detailed above."
  echo "This step in the script encountered an issue, likely because the service account does not exist yet."
  echo "Please ensure your application's 'users.watch()' call is made successfully, then apply the IAM binding manually or by re-running the command."
fi


echo "---------------------------------------------------------------------"
echo "Pub/Sub Setup Potentially Complete!"
echo "---------------------------------------------------------------------"
echo "Summary of created/verified resources:"
echo "  Project ID:         $YOUR_PROJECT_ID"
echo "  Pub/Sub Topic:      projects/$YOUR_PROJECT_ID/topics/$YOUR_TOPIC_ID"
echo "  Pub/Sub Subscription: projects/$YOUR_PROJECT_ID/subscriptions/$YOUR_SUBSCRIPTION_ID"
echo ""
echo "Next critical steps (to be handled by your Python script or manually):"
echo "1. OAuth 2.0 Credentials: Your Python script ('3_gmail_demo_sub_pub.py') will need OAuth 2.0 credentials."
echo "   - Go to Google Cloud Console -> APIs & Services -> Credentials."
echo "   - Click 'Create Credentials' -> 'OAuth client ID'."
echo "   - Select 'Desktop app' (or 'Web application' if appropriate for your final deployment)."
echo "   - Name it (e.g., 'Gmail PubSub Demo Client')."
echo "   - Download the JSON file. Rename it to 'credentials.json' and place it in the same directory as your Python script."
echo ""
echo "2. Gmail API Watch Request: Your Python script needs to call the Gmail API 'users.watch()' method."
echo "   This tells Gmail to send notifications for your chosen user's mailbox to your Pub/Sub topic:"
echo "   - Topic Name for watch(): projects/$YOUR_PROJECT_ID/topics/$YOUR_TOPIC_ID"
echo "   The Python script '3_gmail_demo_sub_pub.py' should be designed to handle this."
echo ""
echo "3. Python Script Configuration: Ensure your '3_gmail_demo_sub_pub.py' script is configured with:"
echo "   - PROJECT_ID: '$YOUR_PROJECT_ID'"
echo "   - TOPIC_NAME (for watch): '$YOUR_TOPIC_ID'"
echo "   - SUBSCRIPTION_NAME (for listening): '$YOUR_SUBSCRIPTION_ID'"
echo ""
echo "Ensure all necessary Python libraries are installed (e.g., google-cloud-pubsub, google-api-python-client, google-auth-oauthlib)."
echo "Example: pip install google-cloud-pubsub google-api-python-client google-auth-httplib2 google-auth-oauthlib"
echo "---------------------------------------------------------------------"

