#!/usr/bin/env python3
import os
import json
import subprocess
from datetime import datetime
from re import sub


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def get_git_info():
    """Collects metadata from the local repo."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        ).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        branch = "unknown"

    try:
        author = subprocess.check_output(
            ["git", "config", "user.name"]
        ).decode("utf-8").strip()
        email = subprocess.check_output(
            ["git", "config", "user.email"]
        ).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        author, email = "unknown", "unknown"

    try:
        commit_msg = open(".git/COMMIT_EDITMSG").read().strip()
    except FileNotFoundError:
        commit_msg = "N/A"

    return branch, author, email, commit_msg


def get_new_history_lines(history_path="~/.zsh_history",
                          checkpoint_path="~/.gemini_capture_checkpoint"):
    """
    Reads only new lines added to the user's shell history file
    since the last time this function was called.
    """
    history_path = os.path.expanduser(history_path)
    checkpoint_path = os.path.expanduser(checkpoint_path)

    if not os.path.exists(history_path):
        return ["History file not found."]

    with open(history_path, "r", errors="ignore") as f:
        all_lines = f.readlines()

    last_index = 0
    if os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r") as c:
                last_index = int(c.read().strip() or 0)
        except Exception:
            last_index = 0

    # Slice only new lines
    new_lines = all_lines[last_index:]
    # Update checkpoint
    with open(checkpoint_path, "w") as c:
        c.write(str(len(all_lines)))

    # Clean lines
    clean = []
    for l in new_lines:
        line = l.strip()
        if not line:
            continue
        # Optional filter: only keep relevant commands
        if any(k in line for k in ["aws", "kubectl", "terraform", "gcloud", "docker"]):
            clean.append(line)
    return clean or ["No relevant new commands."]


# ---------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------
def build_commit_payload(diff_path="/tmp/staged.diff"):
    """Build JSON payload combining diff + metadata + recent terminal history."""
    branch, author, email, commit_msg = get_git_info()

    # Read the diff file
    if os.path.exists(diff_path):
        with open(diff_path, "r") as f:
            diff_content = f.read()
    else:
        diff_content = ""

    # Collect recent terminal commands
    recent_history = get_new_history_lines()

    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "branch": branch,
        "author": author,
        "email": email,
        "commit_message": commit_msg,
        "diff_file": diff_path,
        "diff_content": diff_content,
        "recent_terminal_history": recent_history
    }

    # -----------------------------------------------------------------
    # Build clean folder + filename
    # -----------------------------------------------------------------
    safe_branch = sub(r"[^a-zA-Z0-9_-]", "_", branch)
    safe_msg = sub(r"[^a-zA-Z0-9_-]", "_", commit_msg[:30])
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

    out_dir = os.path.join("captures", "commits", safe_branch)
    os.makedirs(out_dir, exist_ok=True)

    filename = f"{timestamp}_{safe_msg}.json"
    out_path = os.path.join(out_dir, filename)

    with open(out_path, "w") as f:
        json.dump(payload, f, indent=4)

    print(f"✅ Commit payload saved at {out_path}")
    print(f"🧩 Captured {len(recent_history)} new terminal command(s).")
    return payload


if __name__ == "__main__":
    build_commit_payload()
