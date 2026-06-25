#!/usr/bin/env python3
"""Read-only script: scans a Java source file for common Effective Java antipatterns."""

import sys
import re

CHECKS = [
    (r'\bnew\s+String\s*\(', "Item 6", "Unnecessary String object — use a string literal directly"),
    (r'\.ordinal\(\)', "Item 35/37", "Avoid ordinal() indexing — use EnumMap or instance fields"),
    (r'\bswitch\s*\(.*\.ordinal\(\)', "Item 37", "ordinal() in switch — prefer EnumMap"),
    (r'public\s+\w+\s*\(\s*\)', "Item 4", "Public no-arg constructor on utility-like class — consider private constructor + AssertionError"),
    (r'catch\s*\(\s*Exception\s+\w+\s*\)\s*\{\s*\}', "Item 77", "Empty catch block — never silently ignore exceptions"),
    (r'\.wait\s*\(', "Item 81", "Object.wait() — prefer java.util.concurrent utilities"),
    (r'\.notify\s*\(', "Item 81", "Object.notify() — prefer java.util.concurrent utilities"),
    (r'\bfinalize\s*\(\s*\)', "Item 8", "finalize() method — use Cleaner or AutoCloseable instead"),
    (r'implements\s+Serializable', "Item 86", "Serializable detected — implement with caution, consider a serialization proxy (Item 90)"),
    (r'@SuppressWarnings\("unchecked"\)', "Item 27", "@SuppressWarnings(\"unchecked\") — ensure the cast is truly safe and add a comment"),
    (r'\braw\b|List\s+\w+\s*=|Map\s+\w+\s*=|Set\s+\w+\s*=', "Item 26", "Possible raw type — always parameterize generic types"),
    (r'try\s*\{[^}]*\}\s*finally', "Item 9", "try-finally — prefer try-with-resources for AutoCloseable resources"),
]

def analyze(filepath: str):
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    findings = []
    for lineno, line in enumerate(lines, start=1):
        for pattern, item, message in CHECKS:
            if re.search(pattern, line):
                findings.append((lineno, item, message, line.rstrip()))

    if not findings:
        print(f"OK: No common antipatterns detected in {filepath}")
        return

    print(f"Findings in {filepath}:")
    for lineno, item, message, src in findings:
        print(f"  Line {lineno:4d} [{item}] {message}")
        print(f"           >>> {src.strip()}")

    print(f"\n{len(findings)} finding(s). See SKILL.md for remediation guidance.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: analyze-java.py <path-to-java-file>", file=sys.stderr)
        sys.exit(1)
    analyze(sys.argv[1])
