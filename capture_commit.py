#!/usr/bin/env python3
import os
import json
import subprocess
from datetime import datetime
from re import sub


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


def build_commit_payload(diff_path="/tmp/staged.diff"):
    """Build JSON payload combining diff + metadata."""
    branch, author, email, commit_msg = get_git_info()

    # Read the diff file
    if os.path.exists(diff_path):
        with open(diff_path, "r") as f:
            diff_content = f.read()
    else:
        diff_content = ""

    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "branch": branch,
        "author": author,
        "email": email,
        "commit_message": commit_msg,
        "diff_file": diff_path,
        "diff_content": diff_content,
    }

    # ---------------------------------------------------------------------
    # Build clean folder + filename
    # ---------------------------------------------------------------------
    safe_branch = sub(r"[^a-zA-Z0-9_-]", "_", branch)
    safe_msg = sub(r"[^a-zA-Z0-9_-]", "_", commit_msg[:30])
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

    out_dir = os.path.join("captures", "commits", safe_branch)
    os.makedirs(out_dir, exist_ok=True)

    filename = f"{timestamp}_{safe_msg}.json"
    out_path = os.path.join(out_dir, filename)

    # Save the payload
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=4)

    print(f"✅ Commit payload saved at {out_path}")
    return payload


if __name__ == "__main__":
    build_commit_payload()
