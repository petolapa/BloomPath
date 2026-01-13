import os
import logging
import time
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from functools import wraps

load_dotenv()

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("BloomPath")

app = Flask(__name__)

# ============================================================================
# Configuration
# ============================================================================
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

UE5_REMOTE_CONTROL_URL = os.getenv("UE5_REMOTE_CONTROL_URL", "http://localhost:8080/remote/object/call")
UE5_ACTOR_PATH = os.getenv("UE5_ACTOR_PATH", "/Game/Maps/Main.Main:PersistentLevel.GrowerActor")
UE5_GROW_FUNCTION = os.getenv("UE5_GROW_FUNCTION", "Grow_Leaves")
UE5_SHRINK_FUNCTION = os.getenv("UE5_SHRINK_FUNCTION", "Shrink_Leaves")
UE5_THORNS_FUNCTION = os.getenv("UE5_THORNS_FUNCTION", "Add_Thorns")
UE5_REMOVE_THORNS_FUNCTION = os.getenv("UE5_REMOVE_THORNS_FUNCTION", "Remove_Thorns")

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Blocker status detection
BLOCKER_STATUSES = ["Blocked", "Impediment", "On Hold", "Waiting"]

# Issue type to growth type mapping
ISSUE_TYPE_GROWTH = {
    "Bug": "flower",      # Bugs bloom into flowers when fixed
    "Story": "branch",    # Stories grow new branches
    "Task": "leaf",       # Tasks grow leaves
    "Epic": "trunk",      # Epics grow the trunk
    "Sub-task": "bud",    # Sub-tasks create buds
}

# Priority to growth modifier mapping
PRIORITY_MODIFIER = {
    "Highest": 2.0,   # Double growth
    "High": 1.5,      # 50% more growth
    "Medium": 1.0,    # Normal growth
    "Low": 0.75,      # Smaller growth
    "Lowest": 0.5,    # Half growth
}

# Priority to color mapping (RGB values for UE5)
PRIORITY_COLORS = {
    "Highest": {"R": 1.0, "G": 0.2, "B": 0.2},  # Red - urgent
    "High": {"R": 1.0, "G": 0.6, "B": 0.1},     # Gold - important
    "Medium": {"R": 0.3, "G": 0.8, "B": 0.3},   # Green - normal
    "Low": {"R": 0.4, "G": 0.6, "B": 0.4},      # Moss - low priority
    "Lowest": {"R": 0.5, "G": 0.5, "B": 0.5},   # Gray - minimal
}

# ============================================================================
# Retry Decorator
# ============================================================================
def retry_on_failure(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """Decorator to retry a function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            logger.error(f"All {max_retries} attempts failed")
            raise last_exception
        return wrapper
    return decorator


# ============================================================================
# UE5 Remote Control Functions
# ============================================================================
@retry_on_failure()
def trigger_ue5_growth(branch_id, growth_type="leaf", growth_modifier=1.0, color=None, epic_key=None):
    """Calls the UE5 Remote Control API to trigger the Grow_Leaves function.
    
    Args:
        branch_id: The Jira issue key (e.g., KAN-28)
        growth_type: Type of growth based on issue type (leaf, branch, flower, etc.)
        growth_modifier: Size modifier based on priority
        color: RGB color dict based on priority
        epic_key: Parent Epic key for tree mapping
    """
    if color is None:
        color = PRIORITY_COLORS.get("Medium")
    
    payload = {
        "objectPath": UE5_ACTOR_PATH,
        "functionName": UE5_GROW_FUNCTION,
        "parameters": {
            "Target_Branch_ID": branch_id,
            "Growth_Type": growth_type,
            "Growth_Modifier": growth_modifier,
            "Color_R": color.get("R", 0.3),
            "Color_G": color.get("G", 0.8),
            "Color_B": color.get("B", 0.3),
            "Epic_ID": epic_key or ""
        },
        "generateTransaction": True
    }
    
    logger.info(f"Triggering UE5 growth: {branch_id} (type={growth_type}, modifier={growth_modifier}, epic={epic_key})")
    response = requests.put(UE5_REMOTE_CONTROL_URL, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()


@retry_on_failure()
def trigger_ue5_shrink(branch_id):
    """Calls the UE5 Remote Control API to trigger the Shrink_Leaves function."""
    payload = {
        "objectPath": UE5_ACTOR_PATH,
        "functionName": UE5_SHRINK_FUNCTION,
        "parameters": {
            "Target_Branch_ID": branch_id
        },
        "generateTransaction": True
    }
    
    logger.info(f"Triggering UE5 shrink: {branch_id}")
    response = requests.put(UE5_REMOTE_CONTROL_URL, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()


@retry_on_failure()
def trigger_ue5_thorns(branch_id, epic_key=None):
    """Calls the UE5 Remote Control API to add thorns for blocked issues."""
    payload = {
        "objectPath": UE5_ACTOR_PATH,
        "functionName": UE5_THORNS_FUNCTION,
        "parameters": {
            "Target_Branch_ID": branch_id,
            "Epic_ID": epic_key or ""
        },
        "generateTransaction": True
    }
    
    logger.info(f"Triggering UE5 thorns (blocker): {branch_id}")
    response = requests.put(UE5_REMOTE_CONTROL_URL, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()


@retry_on_failure()
def trigger_ue5_remove_thorns(branch_id):
    """Calls the UE5 Remote Control API to remove thorns when blocker is resolved."""
    payload = {
        "objectPath": UE5_ACTOR_PATH,
        "functionName": UE5_REMOVE_THORNS_FUNCTION,
        "parameters": {
            "Target_Branch_ID": branch_id
        },
        "generateTransaction": True
    }
    
    logger.info(f"Triggering UE5 remove thorns: {branch_id}")
    response = requests.put(UE5_REMOTE_CONTROL_URL, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()


# ============================================================================
# Jira Integration
# ============================================================================
def get_epic_key(issue):
    """Extract Epic key from Jira issue.
    
    Jira Cloud uses 'parent' field for Epic links in next-gen projects,
    or custom fields in classic projects.
    """
    fields = issue.get('fields', {})
    
    # Next-gen projects: Check parent field
    parent = fields.get('parent', {})
    parent_type = parent.get('fields', {}).get('issuetype', {}).get('name', '')
    if parent_type == 'Epic':
        return parent.get('key')
    
    # Classic projects: Check epic link custom field (commonly customfield_10014)
    epic_link = fields.get('customfield_10014')  # May vary by instance
    if epic_link:
        return epic_link
    
    return None


def get_growth_params(issue):
    """Extract all growth parameters from Jira issue data.
    
    Returns:
        tuple: (growth_type, growth_modifier, color, epic_key)
    """
    fields = issue.get('fields', {})
    
    # Get issue type
    issue_type = fields.get('issuetype', {}).get('name', 'Task')
    growth_type = ISSUE_TYPE_GROWTH.get(issue_type, 'leaf')
    
    # Get priority
    priority = fields.get('priority', {}).get('name', 'Medium')
    growth_modifier = PRIORITY_MODIFIER.get(priority, 1.0)
    color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS['Medium'])
    
    # Get Epic key
    epic_key = get_epic_key(issue)
    
    return growth_type, growth_modifier, color, epic_key


def sync_initial_state():
    """Queries Jira for all 'Done' issues and triggers growth in UE5."""
    logger.info("Starting initial state synchronization...")
    
    if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY]):
        logger.warning("Missing Jira configuration. Skipping synchronization.")
        return

    jql = f"project = '{JIRA_PROJECT_KEY}' AND status = 'Done'"
    url = f"https://{JIRA_DOMAIN}/rest/api/3/search"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(
            url, 
            params={"jql": jql, "maxResults": 100, "fields": "key,issuetype,priority,parent,customfield_10014"}, 
            auth=auth
        )
        response.raise_for_status()
        issues = response.json().get("issues", [])
        
        logger.info(f"Found {len(issues)} issues in 'Done' status")
        
        for issue in issues:
            issue_key = issue.get("key")
            growth_type, growth_modifier, color, epic_key = get_growth_params(issue)
            
            logger.info(f"Syncing {issue_key} (type={growth_type}, modifier={growth_modifier}, epic={epic_key})")
            try:
                trigger_ue5_growth(issue_key, growth_type, growth_modifier, color, epic_key)
            except Exception as e:
                logger.error(f"Failed to sync {issue_key}: {e}")
            
        logger.info("Initial state synchronization complete")
    except Exception as e:
        logger.error(f"Error during Jira synchronization: {e}")


def was_reopened(data):
    """Check if the issue was reopened (status changed FROM Done)."""
    changelog = data.get('changelog', {})
    for item in changelog.get('items', []):
        if item.get('field') == 'status' and item.get('fromString') == 'Done':
            return True
    return False


def was_blocked(data):
    """Check if the issue was just blocked (status changed TO a blocker status)."""
    changelog = data.get('changelog', {})
    for item in changelog.get('items', []):
        if item.get('field') == 'status' and item.get('toString') in BLOCKER_STATUSES:
            return True
    return False


def was_unblocked(data):
    """Check if the issue was unblocked (status changed FROM a blocker status)."""
    changelog = data.get('changelog', {})
    for item in changelog.get('items', []):
        if item.get('field') == 'status' and item.get('fromString') in BLOCKER_STATUSES:
            return True
    return False


# ============================================================================
# Flask Routes
# ============================================================================
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "BloomPath",
        "jira_configured": all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN]),
        "ue5_endpoint": UE5_REMOTE_CONTROL_URL
    }), 200


@app.route('/webhook', methods=['POST'])
def jira_webhook():
    """Handle Jira webhook events."""
    data = request.json
    if not data:
        logger.warning("Received webhook with no JSON payload")
        return jsonify({"status": "error", "message": "No JSON payload"}), 400

    # Optional: Verify webhook secret
    if WEBHOOK_SECRET:
        received_secret = request.headers.get('X-Atlassian-Webhook-Identifier')
        # Note: Jira Cloud uses different header, adjust as needed
    
    # Extract event data
    event_type = data.get('issue_event_type_name', data.get('webhookEvent', 'unknown'))
    issue = data.get('issue', {})
    issue_key = issue.get('key')
    fields = issue.get('fields', {})
    status = fields.get('status', {}).get('name')
    
    logger.info(f"Webhook received: [{event_type}] {issue_key} → {status}")
    
    # Get all growth parameters
    growth_type, growth_modifier, color, epic_key = get_growth_params(issue)

    # Check if issue was blocked (add thorns)
    if was_blocked(data):
        logger.info(f"Issue {issue_key} was blocked, triggering thorns")
        try:
            trigger_ue5_thorns(issue_key, epic_key)
            return jsonify({"status": "thorns_triggered", "issue": issue_key}), 200
        except Exception as e:
            logger.error(f"Failed to trigger thorns for {issue_key}: {e}")
            return jsonify({"status": "ue5_error", "issue": issue_key, "error": str(e)}), 500
    
    # Check if issue was unblocked (remove thorns)
    if was_unblocked(data):
        logger.info(f"Issue {issue_key} was unblocked, removing thorns")
        try:
            trigger_ue5_remove_thorns(issue_key)
        except Exception as e:
            logger.warning(f"Failed to remove thorns for {issue_key}: {e}")
        # Continue processing - might also be going to Done

    # Check if issue was reopened (status changed FROM Done)
    if was_reopened(data):
        logger.info(f"Issue {issue_key} was reopened, triggering shrink")
        try:
            trigger_ue5_shrink(issue_key)
            return jsonify({"status": "shrink_triggered", "issue": issue_key}), 200
        except Exception as e:
            logger.error(f"Failed to trigger shrink for {issue_key}: {e}")
            return jsonify({"status": "ue5_error", "issue": issue_key, "error": str(e)}), 500

    # Trigger growth when status changes to 'Done'
    if status == "Done":
        logger.info(f"Issue {issue_key} completed (type={growth_type}, modifier={growth_modifier}, epic={epic_key})")
        
        try:
            result = trigger_ue5_growth(issue_key, growth_type, growth_modifier, color, epic_key)
            logger.info(f"Successfully triggered growth for {issue_key}")
            return jsonify({"status": "growth_triggered", "issue": issue_key, "epic": epic_key}), 200
        except Exception as e:
            logger.error(f"Failed to trigger growth for {issue_key}: {e}")
            return jsonify({"status": "ue5_error", "issue": issue_key, "error": str(e)}), 500

    return jsonify({"status": "received", "issue": issue_key}), 200


# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🌱 BloomPath Middleware Starting")
    logger.info("=" * 50)
    logger.info(f"Jira Project: {JIRA_PROJECT_KEY}")
    logger.info(f"UE5 Endpoint: {UE5_REMOTE_CONTROL_URL}")
    logger.info(f"Log Level: {LOG_LEVEL}")
    
    # Run initial sync
    sync_initial_state()
    
    logger.info("Starting webhook server on port 5000...")
    app.run(port=5000, debug=(LOG_LEVEL == "DEBUG"))
