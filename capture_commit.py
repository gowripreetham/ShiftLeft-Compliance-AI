#!/usr/bin/env python3
import os
import json
import subprocess
from datetime import datetime

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

    # Save payload for later analysis
    out_dir = "./captures/commits"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{datetime.utcnow().timestamp()}.json")

    with open(out_path, "w") as f:
        json.dump(payload, f, indent=4)

    print(f"✅ Commit payload saved at {out_path}")
    return payload


if __name__ == "__main__":
    build_commit_payload()
