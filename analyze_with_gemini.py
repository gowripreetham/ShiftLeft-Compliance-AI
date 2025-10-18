#!/usr/bin/env python3
import os
import re
import json
from datetime import datetime

# ---------------------------------------------------------------------
# Helper: Regex-based detection rules
# ---------------------------------------------------------------------
PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret_key": r"(?i)aws(.{0,20})?(secret|key)['\"]?\s*[:=]\s*['\"][A-Za-z0-9/+=]{40}['\"]",
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "phone": r"(\+?\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})",
    "http_url": r"http://[^\s]+",
    "password_assign": r"password\s*=\s*['\"].+['\"]",
    "public_s3": r"acl\s*=\s*['\"]public-read['\"]",
    "api_key": r"(?i)(api[_-]?key|token)\s*[:=]\s*['\"A-Za-z0-9_\-]+['\"]",
    "pii_ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "error_log": r"(?i)(error|unauthorized|denied|failed|exception)"
}


def scan_text(name, text):
    """Scan a text blob for risky patterns."""
    findings = []
    for label, pattern in PATTERNS.items():
        matches = re.findall(pattern, text or "")
        if matches:
            findings.append({
                "type": label,
                "count": len(matches),
                "example": str(matches[0])[:100],
                "source": name
            })
    return findings


# ---------------------------------------------------------------------
# Core Analyzer
# ---------------------------------------------------------------------
def analyze_capture(capture_path):
    """Read a capture JSON and produce analysis output."""
    with open(capture_path, "r", errors="ignore") as f:
        data = json.load(f)

    all_findings = []

    # 1️⃣ Diff content
    if "diff_content" in data:
        all_findings += scan_text("diff_content", data["diff_content"])

    # 2️⃣ Terminal history
    if "recent_terminal_history" in data:
        joined = "\n".join(data["recent_terminal_history"])
        all_findings += scan_text("terminal_history", joined)

    # 3️⃣ Config snapshots (hashes can’t be scanned, but path names can)
    if "config_snapshots" in data:
        for path in data["config_snapshots"].keys():
            all_findings += scan_text("config_file_path", path)

    # 4️⃣ Log snippets
    if "log_snippets" in data:
        for name, content in data["log_snippets"].items():
            all_findings += scan_text(name, content)

    # Risk level heuristic
    risk_level = (
        "high" if any("aws" in f["type"] or "password" in f["type"] for f in all_findings)
        else "medium" if len(all_findings) > 2
        else "low"
    )

    analysis = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source_capture": capture_path,
        "risk_level": risk_level,
        "finding_count": len(all_findings),
        "findings": all_findings
    }

    # Save to /captures/analysis/
    base_dir = os.path.dirname(capture_path).replace("commits", "analysis")
    os.makedirs(base_dir, exist_ok=True)

    # Derive filename from capture
    capture_name = os.path.basename(capture_path).replace(".json", "_analysis.json")
    out_path = os.path.join(base_dir, capture_name)

    with open(out_path, "w") as f:
        json.dump(analysis, f, indent=4)

    print(f"✅ Analysis complete: {out_path}")
    print(f"🔍 Risk level: {risk_level} | {len(all_findings)} finding(s)")
    return analysis


if __name__ == "__main__":
    import glob

    # Automatically analyze the latest capture file
    paths = sorted(glob.glob("captures/commits/**/*.json", recursive=True))
    if not paths:
        print("⚠️ No capture files found. Commit something first.")
    else:
        latest = paths[-1]
        print(f"🧠 Analyzing latest capture: {latest}")
        analyze_capture(latest)
