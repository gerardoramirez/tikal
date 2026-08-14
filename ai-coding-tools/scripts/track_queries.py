#!/usr/bin/env python3
"""
Track Claude Code query metrics and save to CSV.

Parses Claude Code logs to extract:
- Query type (auto-detected from content)
- Risk level (based on tools used)
- Token counts (actual if available, estimated via hybrid heuristic otherwise)
- Cost (using Claude Opus 4.5 pricing)

Output: .ai-data/query_log.csv

TOKEN ESTIMATION HEURISTIC (Hybrid Approach)
============================================
For historical queries where actual token data is unavailable, we estimate
tokens using a three-step hybrid approach:

STEP 1: Character-based input estimation
    - Convert query text length to estimated input tokens
    - Rule of thumb: ~4 characters = 1 token for English text
    - Formula: input_tokens = len(query_text) / 4

STEP 2: Daily aggregate calibration
    - Load actual daily token totals from stats-cache.json
    - Calculate total estimated tokens for all queries on that day
    - Compute calibration factor: actual_daily_total / estimated_daily_total
    - Apply calibration factor to individual query estimates
    - This anchors our estimates to real aggregate data

STEP 3: Query-type output multipliers
    - Different query types produce different response lengths
    - Apply multipliers to estimate output tokens from input tokens:
        * code_generation: 5x (short request yields substantial code)
        * explanation: 3x (questions get detailed answers)
        * research: 4x (search + synthesis)
        * debugging: 2x (back-and-forth, targeted fixes)
        * refactoring: 3x (analysis + rewritten code)
        * testing: 2x (test code is often concise)
        * other: 2x (conservative default)

CACHE TOKEN ESTIMATION
    - Cache read: estimated as 80% of input tokens (typical for follow-up queries)
    - Cache creation: estimated as 20% of input tokens (first query in context)
    - These are rough approximations; actual caching behavior varies
"""

import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

# Paths
CLAUDE_DIR = Path.home() / ".claude"
HISTORY_FILE = CLAUDE_DIR / "history.jsonl"
STATS_FILE = CLAUDE_DIR / "stats-cache.json"
CONFIG_FILE = CLAUDE_DIR / ".claude.json"
DEBUG_DIR = CLAUDE_DIR / "debug"

PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / ".ai-data"
OUTPUT_CSV = OUTPUT_DIR / "query_log.csv"
LAST_PROCESSED_FILE = OUTPUT_DIR / ".last_processed"

# Claude Opus 4.5 pricing (per 1M tokens)
PRICING = {
    "input": 15.00,
    "output": 75.00,
    "cache_read": 1.50,
    "cache_creation": 18.75,
}

# -----------------------------------------------------------------------------
# STEP 1 CONFIG: Character-to-token ratio
# -----------------------------------------------------------------------------
# Research suggests ~4 characters per token for English text.
# This varies by content type (code may be ~3 chars/token due to syntax).
CHARS_PER_TOKEN = 4

# -----------------------------------------------------------------------------
# STEP 3 CONFIG: Query type output multipliers
# -----------------------------------------------------------------------------
# These multipliers estimate output tokens as a multiple of input tokens.
# Based on typical interaction patterns for each query type.
QUERY_TYPE_OUTPUT_MULTIPLIERS = {
    "code_generation": 5.0,  # Short request -> substantial code output
    "explanation": 3.0,      # Question -> detailed explanatory answer
    "research": 4.0,         # Search query -> results + synthesis
    "debugging": 2.0,        # Targeted fix, back-and-forth
    "refactoring": 3.0,      # Analysis + rewritten code
    "testing": 2.0,          # Test code tends to be concise
    "other": 2.0,            # Conservative default
}

# Cache estimation ratios (proportion of input tokens)
CACHE_READ_RATIO = 0.8      # Most queries benefit from prior context
CACHE_CREATION_RATIO = 0.2  # Some new context added each query

# Query type detection patterns
QUERY_PATTERNS = {
    "code_generation": [
        r"\b(write|create|implement|add|build|make|generate)\b",
    ],
    "debugging": [
        r"\b(fix|bug|error|issue|broken|crash|fail|wrong)\b",
    ],
    "explanation": [
        r"\b(explain|what is|how does|why|understand|describe)\b",
    ],
    "refactoring": [
        r"\b(refactor|improve|clean|optimize|restructure)\b",
    ],
    "research": [
        r"\b(find|search|where|look for|locate|show me)\b",
    ],
    "testing": [
        r"\b(test|verify|check|validate|ensure)\b",
    ],
}

# Risk levels based on tools
TOOL_RISK = {
    "low": ["Read", "Glob", "Grep", "WebSearch", "WebFetch", "Task"],
    "medium": ["Edit", "Write", "NotebookEdit"],
    "high": ["Bash", "KillShell"],
}


# =============================================================================
# STEP 1: CHARACTER-BASED INPUT ESTIMATION
# =============================================================================

def estimate_input_tokens_from_text(query_text):
    """
    STEP 1: Estimate input tokens from query text length.

    Process:
    1. Count characters in the query text
    2. Divide by CHARS_PER_TOKEN (default: 4)
    3. Return estimated token count

    Assumptions:
    - English text averages ~4 characters per token
    - This is a rough estimate; actual tokenization varies
    - Code content may have slightly different ratios

    Args:
        query_text: The raw query string from the user

    Returns:
        Estimated number of input tokens (integer)
    """
    if not query_text:
        return 0

    char_count = len(query_text)
    estimated_tokens = char_count / CHARS_PER_TOKEN

    return int(estimated_tokens)


# =============================================================================
# STEP 2: DAILY AGGREGATE CALIBRATION
# =============================================================================

def load_daily_token_aggregates():
    """
    Load actual daily token totals from stats-cache.json.

    Returns:
        Dict mapping date strings (YYYY-MM-DD) to token totals:
        {
            "2025-01-15": {
                "input": 50000,
                "output": 150000,
                "cache_read": 40000,
                "cache_creation": 10000
            },
            ...
        }
    """
    if not STATS_FILE.exists():
        return {}

    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

    daily_aggregates = {}

    # Extract from dailyModelTokens if available
    daily_model_tokens = stats.get("dailyModelTokens", [])
    for day_entry in daily_model_tokens:
        date = day_entry.get("date")
        if not date:
            continue

        # Sum tokens across all models for this day
        tokens_by_model = day_entry.get("tokensByModel", {})
        total_tokens = sum(tokens_by_model.values())

        # We only get total tokens here, not broken down by type
        # Use model usage ratios to estimate breakdown
        daily_aggregates[date] = {"total": total_tokens}

    # Get overall ratios from modelUsage for breakdown estimation
    model_usage = stats.get("modelUsage", {})
    total_input = sum(m.get("inputTokens", 0) for m in model_usage.values())
    total_output = sum(m.get("outputTokens", 0) for m in model_usage.values())
    total_cache_read = sum(
        m.get("cacheReadInputTokens", 0) for m in model_usage.values()
    )
    total_cache_creation = sum(
        m.get("cacheCreationInputTokens", 0) for m in model_usage.values()
    )

    grand_total = total_input + total_output + total_cache_read + total_cache_creation

    if grand_total > 0:
        # Calculate ratios
        input_ratio = total_input / grand_total
        output_ratio = total_output / grand_total
        cache_read_ratio = total_cache_read / grand_total
        cache_creation_ratio = total_cache_creation / grand_total

        # Apply ratios to daily totals
        for date, data in daily_aggregates.items():
            total = data.get("total", 0)
            daily_aggregates[date] = {
                "input": int(total * input_ratio),
                "output": int(total * output_ratio),
                "cache_read": int(total * cache_read_ratio),
                "cache_creation": int(total * cache_creation_ratio),
            }

    return daily_aggregates


def calculate_calibration_factors(entries_by_date, daily_aggregates):
    """
    STEP 2: Calculate calibration factors using daily aggregates.

    Process:
    1. For each date, sum up all estimated tokens from queries
    2. Compare to actual daily totals from stats-cache.json
    3. Calculate calibration factor: actual / estimated
    4. Return factors for each date

    This anchors our character-based estimates to real aggregate data,
    correcting for systematic over/under-estimation.

    Args:
        entries_by_date: Dict mapping dates to list of (query, query_type) tuples
        daily_aggregates: Dict mapping dates to actual token totals

    Returns:
        Dict mapping dates to calibration factors (float)
    """
    calibration_factors = {}

    for date, queries in entries_by_date.items():
        # Sum estimated tokens for this date
        estimated_total = 0
        for query_text, query_type in queries:
            input_est = estimate_input_tokens_from_text(query_text)
            output_mult = QUERY_TYPE_OUTPUT_MULTIPLIERS.get(query_type, 2.0)
            output_est = int(input_est * output_mult)
            estimated_total += input_est + output_est

        # Get actual total for this date
        actual_data = daily_aggregates.get(date, {})
        actual_total = (
            actual_data.get("input", 0) +
            actual_data.get("output", 0)
        )

        # Calculate calibration factor
        if estimated_total > 0 and actual_total > 0:
            calibration_factors[date] = actual_total / estimated_total
        else:
            # No calibration data available; use 1.0 (no adjustment)
            calibration_factors[date] = 1.0

    return calibration_factors


# =============================================================================
# STEP 3: QUERY-TYPE OUTPUT MULTIPLIERS
# =============================================================================

def estimate_output_tokens(input_tokens, query_type):
    """
    STEP 3: Estimate output tokens using query-type multipliers.

    Process:
    1. Look up the multiplier for this query type
    2. Multiply input tokens by the multiplier
    3. Return estimated output tokens

    Rationale for multipliers:
    - code_generation (5x): User requests are brief; code responses are substantial
    - explanation (3x): Questions typically get detailed explanatory answers
    - research (4x): Search queries yield results plus synthesized summaries
    - debugging (2x): Fixes tend to be targeted, less verbose
    - refactoring (3x): Requires analysis plus rewritten code
    - testing (2x): Test code is typically concise
    - other (2x): Conservative default for uncategorized queries

    Args:
        input_tokens: Estimated input token count
        query_type: Detected query type string

    Returns:
        Estimated number of output tokens (integer)
    """
    multiplier = QUERY_TYPE_OUTPUT_MULTIPLIERS.get(query_type, 2.0)
    return int(input_tokens * multiplier)


def estimate_cache_tokens(input_tokens):
    """
    Estimate cache read and creation tokens.

    Process:
    1. Cache read: 80% of input tokens (most queries use prior context)
    2. Cache creation: 20% of input tokens (some new context each query)

    These are rough approximations. Actual caching behavior depends on:
    - Conversation length and context window usage
    - Whether this is a new session or continuation
    - System prompt and tool definitions

    Args:
        input_tokens: Estimated input token count

    Returns:
        Tuple of (cache_read_tokens, cache_creation_tokens)
    """
    cache_read = int(input_tokens * CACHE_READ_RATIO)
    cache_creation = int(input_tokens * CACHE_CREATION_RATIO)
    return cache_read, cache_creation


# =============================================================================
# COMBINED ESTIMATION FUNCTION
# =============================================================================

def estimate_tokens_hybrid(query_text, query_type, calibration_factor=1.0):
    """
    Estimate all token counts using the hybrid approach.

    This combines all three steps:
    1. Character-based input estimation
    2. Calibration factor from daily aggregates
    3. Query-type output multipliers

    Args:
        query_text: The raw query string
        query_type: Detected query type
        calibration_factor: Adjustment factor from daily aggregates (default 1.0)

    Returns:
        Dict with token estimates:
        {
            "input": int,
            "output": int,
            "cache_read": int,
            "cache_creation": int,
            "is_estimated": True
        }
    """
    # STEP 1: Character-based input estimation
    raw_input = estimate_input_tokens_from_text(query_text)

    # STEP 2: Apply calibration factor
    calibrated_input = int(raw_input * calibration_factor)

    # STEP 3: Query-type output multiplier
    output = estimate_output_tokens(calibrated_input, query_type)

    # Estimate cache tokens
    cache_read, cache_creation = estimate_cache_tokens(calibrated_input)

    return {
        "input": calibrated_input,
        "output": output,
        "cache_read": cache_read,
        "cache_creation": cache_creation,
        "is_estimated": True,
    }


# =============================================================================
# EXISTING HELPER FUNCTIONS
# =============================================================================

def detect_query_type(query_text):
    """Auto-detect query type from content using keyword patterns."""
    query_lower = query_text.lower()
    for qtype, patterns in QUERY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                return qtype
    return "other"


def detect_risk_level(session_id):
    """Detect risk level by parsing debug logs for tool usage."""
    if not DEBUG_DIR.exists():
        return "unknown"

    tools_used = set()
    for debug_file in DEBUG_DIR.glob("*.txt"):
        try:
            content = debug_file.read_text(errors="ignore")
            # Look for tool invocations in debug logs
            tool_matches = re.findall(r'\[TOOL\]\s+(\w+)', content)
            tools_used.update(tool_matches)
            # Also check for tool names in function calls
            for tool in ["Bash", "Edit", "Write", "Read", "Glob", "Grep"]:
                if tool in content:
                    tools_used.add(tool)
        except Exception:
            continue

    # Determine highest risk level
    for tool in tools_used:
        if tool in TOOL_RISK["high"]:
            return "high"
    for tool in tools_used:
        if tool in TOOL_RISK["medium"]:
            return "medium"
    if tools_used:
        return "low"
    return "unknown"


def calculate_cost(input_tokens, output_tokens, cache_read, cache_creation):
    """Calculate cost using Opus 4.5 pricing."""
    cost = 0.0
    cost += (input_tokens / 1_000_000) * PRICING["input"]
    cost += (output_tokens / 1_000_000) * PRICING["output"]
    cost += (cache_read / 1_000_000) * PRICING["cache_read"]
    cost += (cache_creation / 1_000_000) * PRICING["cache_creation"]
    return round(cost, 6)


def get_last_processed_timestamp():
    """Get the timestamp of the last processed entry."""
    if LAST_PROCESSED_FILE.exists():
        return int(LAST_PROCESSED_FILE.read_text().strip())
    return 0


def save_last_processed_timestamp(timestamp):
    """Save the timestamp of the last processed entry."""
    LAST_PROCESSED_FILE.write_text(str(timestamp))


def load_history():
    """Load query history from history.jsonl."""
    if not HISTORY_FILE.exists():
        return []

    entries = []
    with open(HISTORY_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def load_config():
    """Load config from .claude.json for per-project stats."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def get_session_tokens(config, session_id):
    """
    Get actual token counts for a session from config.

    This returns real token data if the session is the most recent
    for any project. Otherwise returns None.
    """
    projects = config.get("projects", {})
    for project_path, project_data in projects.items():
        if project_data.get("lastSessionId") == session_id:
            return {
                "input": project_data.get("lastTotalInputTokens", 0),
                "output": project_data.get("lastTotalOutputTokens", 0),
                "cache_read": project_data.get("lastTotalCacheReadInputTokens", 0),
                "cache_creation": project_data.get(
                    "lastTotalCacheCreationInputTokens", 0
                ),
                "is_estimated": False,
            }
    return None


def ensure_csv_exists():
    """Create CSV file with headers if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not OUTPUT_CSV.exists():
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "session_id",
                "query_type",
                "risk_level",
                "input_tokens",
                "output_tokens",
                "cache_read_tokens",
                "cache_creation_tokens",
                "cost_usd",
                "is_estimated",
                "query_preview",
            ])


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Main entry point for the query tracking script.

    Process:
    1. Load new entries from history.jsonl (after last processed timestamp)
    2. Group entries by date for calibration
    3. Load daily aggregates and calculate calibration factors
    4. For each entry:
       a. Try to get actual tokens from config (for recent sessions)
       b. If not available, use hybrid estimation
       c. Calculate cost
       d. Write to CSV
    5. Update last processed timestamp
    """
    ensure_csv_exists()

    last_processed = get_last_processed_timestamp()
    history = load_history()
    config = load_config()

    # Filter to entries after last processed
    new_entries = [
        e for e in history
        if e.get("timestamp", 0) > last_processed
    ]

    if not new_entries:
        print("No new entries to process.")
        return

    # Group entries by date for calibration (STEP 2 preparation)
    entries_by_date = defaultdict(list)
    for entry in new_entries:
        timestamp = entry.get("timestamp", 0)
        query = entry.get("display", "")
        query_type = detect_query_type(query)

        # Convert timestamp to date string
        dt = datetime.fromtimestamp(timestamp / 1000)
        date_str = dt.strftime("%Y-%m-%d")

        entries_by_date[date_str].append((query, query_type))

    # Load daily aggregates and calculate calibration factors
    daily_aggregates = load_daily_token_aggregates()
    calibration_factors = calculate_calibration_factors(
        entries_by_date, daily_aggregates
    )

    # Group entries by session for processing
    sessions = {}
    for entry in new_entries:
        sid = entry.get("sessionId", "unknown")
        if sid not in sessions:
            sessions[sid] = []
        sessions[sid].append(entry)

    rows_written = 0
    estimated_count = 0
    actual_count = 0
    max_timestamp = last_processed

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)

        for session_id, entries in sessions.items():
            # Try to get actual token data for this session
            actual_tokens = get_session_tokens(config, session_id)

            for entry in entries:
                timestamp = entry.get("timestamp", 0)
                query = entry.get("display", "")

                # Detect query type and risk
                query_type = detect_query_type(query)
                risk_level = detect_risk_level(session_id)

                # Get date for calibration factor
                dt = datetime.fromtimestamp(timestamp / 1000)
                date_str = dt.strftime("%Y-%m-%d")
                calibration_factor = calibration_factors.get(date_str, 1.0)

                # Determine token counts
                if actual_tokens is not None:
                    # Use actual data (for most recent sessions)
                    tokens = actual_tokens
                    actual_count += 1
                else:
                    # Use hybrid estimation (for historical queries)
                    tokens = estimate_tokens_hybrid(
                        query, query_type, calibration_factor
                    )
                    estimated_count += 1

                # Calculate cost
                cost = calculate_cost(
                    tokens["input"],
                    tokens["output"],
                    tokens["cache_read"],
                    tokens["cache_creation"],
                )

                # Format timestamp
                ts_str = dt.isoformat()

                # Truncate query for preview
                preview = query[:100].replace("\n", " ")
                if len(query) > 100:
                    preview += "..."

                writer.writerow([
                    ts_str,
                    session_id,
                    query_type,
                    risk_level,
                    tokens["input"],
                    tokens["output"],
                    tokens["cache_read"],
                    tokens["cache_creation"],
                    cost,
                    tokens.get("is_estimated", True),
                    preview,
                ])
                rows_written += 1
                max_timestamp = max(max_timestamp, timestamp)

    if max_timestamp > last_processed:
        save_last_processed_timestamp(max_timestamp)

    print(f"Processed {rows_written} entries ({actual_count} actual, "
          f"{estimated_count} estimated). Output: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
