#!/usr/bin/env python3
"""Summarize GitHub account usage for the current authenticated user.

This helper uses documented GitHub CLI/API endpoints only. It is intended to
support the ccusage skill, not to replace the browser fallback for fields that
are only exposed in the billing UI.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from decimal import Decimal
from typing import Any

API_VERSION = "2022-11-28"
SUMMARY_ENDPOINT = "/user/settings/billing/usage/summary"
SUMMARY_URL = "https://github.com/settings/billing/summary"
USAGE_URL = "https://github.com/settings/billing/usage?period=3&group=0"
REPO_LIST_LIMIT = 200


def run_gh(args: list[str]) -> str:
    completed = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        message = (
            completed.stderr.strip() or completed.stdout.strip() or "gh command failed"
        )
        raise RuntimeError(message)
    return completed.stdout


def is_authenticated() -> bool:
    completed = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.returncode == 0


def get_user() -> dict[str, Any]:
    return json.loads(
        run_gh(["api", "user", "-H", f"X-GitHub-Api-Version: {API_VERSION}"])
    )


def get_usage_summary() -> dict[str, Any]:
    return json.loads(
        run_gh(["api", SUMMARY_ENDPOINT, "-H", f"X-GitHub-Api-Version: {API_VERSION}"])
    )


def get_repositories(owner: str) -> list[dict[str, Any]]:
    return json.loads(
        run_gh(
            [
                "repo",
                "list",
                owner,
                "--limit",
                str(REPO_LIST_LIMIT),
                "--json",
                "name,nameWithOwner,description,isPrivate,isFork,updatedAt",
            ]
        )
    )


def to_decimal(value: Any) -> Decimal:
    return Decimal(str(value or 0))


def normalize_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data")
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    return []


def summarize_products(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_product: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "amount": Decimal("0"),
            "quantity": Decimal("0"),
            "unit_type": None,
            "currency": None,
        }
    )

    for row in rows:
        product = str(row.get("product_name") or "unknown").strip().lower()
        entry = by_product[product]
        entry["amount"] += to_decimal(row.get("amount"))
        entry["quantity"] += to_decimal(row.get("quantity"))
        entry["unit_type"] = row.get("unit_type") or entry["unit_type"]
        entry["currency"] = row.get("currency") or entry["currency"]

    copilot_total = Decimal("0")
    github_total = Decimal("0")
    for product, entry in by_product.items():
        if "copilot" in product:
            copilot_total += entry["amount"]
        else:
            github_total += entry["amount"]

    return {
        "github_total": github_total,
        "copilot_total": copilot_total,
        "by_product": by_product,
    }


def format_money(value: Decimal, currency: str | None = "USD") -> str:
    suffix = f" {currency}" if currency else ""
    return f"{value.quantize(Decimal('0.01'))}{suffix}"


def format_quantity(value: Decimal) -> str:
    normalized = value.normalize() if value != 0 else Decimal("0")
    return format(normalized, "f").rstrip("0").rstrip(".") or "0"


def print_web_fallback(mode: str) -> None:
    print("web fallback:")
    print(f"- overview: {SUMMARY_URL}")
    print(f"- usage: {USAGE_URL}")
    if mode == "storage":
        print(
            "- in overview, inspect products selector for Codespaces, Git LFS, Packages, and Actions-related storage if shown"
        )
        print(
            "- in usage, keep timeframe at Current month and compare gross amount vs billed amount"
        )
        print(
            "- repository git size is separate from billing storage; check local size with `git count-objects -vH`"
        )
        return
    print(
        "- in overview, read Current metered usage, Current included usage, Copilot usage, and Copilot premium requests"
    )
    print(
        "- in usage, keep timeframe at Current month and compare gross amount vs billed amount"
    )


def print_summary(
    user: dict[str, Any], rows: list[dict[str, Any]], summary: dict[str, Any]
) -> None:
    login = user.get("login", "unknown")
    plan = (user.get("plan") or {}).get("name", "unknown")

    currencies = [row.get("currency") for row in rows if row.get("currency")]
    currency = currencies[0] if currencies else "USD"

    print("[ccusage run]")
    print(f"account: {login}")
    print(f"plan: {plan}")
    print("scope: documented billing API summary for current authenticated user")
    print("period: current year aggregate from GitHub API")
    print(f"github usage total: {format_money(summary['github_total'], currency)}")
    print(f"copilot usage total: {format_money(summary['copilot_total'], currency)}")
    print(
        "remaining included usage: not available from documented personal billing API"
    )
    print(
        "storage usage: billing API may include storage-related products such as packages/actions/lfs when they are billed, but repository git size itself is not exposed here as a billing quota"
    )
    print(
        "next step: open GitHub billing overview/usage page for current-month included usage and billed amount"
    )
    print("")
    print("products:")
    for product in sorted(summary["by_product"]):
        entry = summary["by_product"][product]
        unit_type = entry["unit_type"] or "unit"
        print(
            f"- {product}: amount={format_money(entry['amount'], entry['currency'] or currency)}, "
            f"quantity={format_quantity(entry['quantity'])} {unit_type}"
        )


def print_storage_summary(
    user: dict[str, Any], rows: list[dict[str, Any]], summary: dict[str, Any]
) -> None:
    login = user.get("login", "unknown")
    plan = (user.get("plan") or {}).get("name", "unknown")

    storage_keywords = ("storage", "package", "packages", "lfs", "codespace", "actions")
    storage_products = {
        product: entry
        for product, entry in summary["by_product"].items()
        if any(keyword in product for keyword in storage_keywords)
    }

    print("[ccusage storage]")
    print(f"account: {login}")
    print(f"plan: {plan}")
    print("scope: storage-related usage visible from documented billing API")
    print("period: current year aggregate from GitHub API")
    print(
        "note: repository git size itself is not a billed storage quota in this API; use local git size checks or repository limits guidance separately"
    )
    print(
        "note: remaining included storage is not directly exposed by the documented personal billing API and may require the billing web UI"
    )
    print("")
    print("storage products:")
    if not storage_products:
        print(
            "- no storage-related billed products were returned by the documented API"
        )
        return

    for product in sorted(storage_products):
        entry = storage_products[product]
        unit_type = entry["unit_type"] or "unit"
        currency = entry["currency"] or "USD"
        print(
            f"- {product}: amount={format_money(entry['amount'], currency)}, "
            f"quantity={format_quantity(entry['quantity'])} {unit_type}"
        )


def print_repositories(
    user: dict[str, Any], repositories: list[dict[str, Any]]
) -> None:
    login = user.get("login", "unknown")

    print("[ccusage repos]")
    print(f"account: {login}")
    print(f"repository count: {len(repositories)}")
    print(f"scope: repositories owned by {login}")
    print("")
    print("repositories:")

    if not repositories:
        print("- no repositories found")
        return

    for repository in repositories:
        visibility = "private" if repository.get("isPrivate") else "public"
        fork = ", fork" if repository.get("isFork") else ""
        description = repository.get("description") or ""
        updated_at = repository.get("updatedAt") or "unknown"
        summary = f"- {repository.get('nameWithOwner', 'unknown')}: {visibility}{fork}, updated={updated_at}"
        if description:
            summary = f"{summary}, description={description}"
        print(summary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ccusage helper")
    parser.add_argument(
        "mode",
        nargs="?",
        default="run",
        choices=("run", "storage", "repos"),
        help="output mode",
    )
    return parser.parse_args()


def print_auth_error(mode: str) -> None:
    print(f"[ccusage {mode}] GitHub CLI is not authenticated.")
    print("- run `gh auth login` or set `GH_TOKEN`")
    print("- then rerun this script")
    if mode == "repos":
        print("- repository listing requires GitHub CLI authentication")
        return
    if mode == "storage":
        print(
            "- for storage usage, check GitHub billing web UI for Codespaces/Packages/LFS/Actions storage details"
        )
        print_web_fallback(mode)
        return
    print(
        "- for current-month included usage and billed amount, use the GitHub billing web UI fallback"
    )
    print_web_fallback(mode)


def main() -> int:
    args = parse_args()

    if not is_authenticated():
        print_auth_error(args.mode)
        return 1

    try:
        user = get_user()
    except RuntimeError as error:
        print(f"[ccusage {args.mode}] failed to query GitHub user API: {error}")
        return 1

    if args.mode == "repos":
        try:
            repositories = get_repositories(user.get("login", ""))
        except RuntimeError as error:
            print(f"[ccusage repos] failed to query repository list: {error}")
            return 1

        print_repositories(user, repositories)
        return 0

    try:
        payload = get_usage_summary()
    except RuntimeError as error:
        print(f"[ccusage {args.mode}] failed to query GitHub billing API: {error}")
        print("Use the GitHub billing web UI fallback to inspect current-month usage.")
        print_web_fallback(args.mode)
        return 1

    rows = normalize_rows(payload)
    if not rows:
        print(
            f"[ccusage {args.mode}] no usage rows were returned by the documented billing API."
        )
        print("Use the GitHub billing web UI fallback to inspect current-month usage.")
        print_web_fallback(args.mode)
        return 1

    summary = summarize_products(rows)
    if args.mode == "storage":
        print_storage_summary(user, rows, summary)
    else:
        print_summary(user, rows, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
