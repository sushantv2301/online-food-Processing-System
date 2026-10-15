"""Utility script to push the repository to GitHub.

Supports:
1. Pushing via standard Git command (if git is configured).
2. Pushing via Dulwich (Pure Python Git client).
"""

import os
import sys
import subprocess
from dulwich import porcelain
from dulwich.repo import Repo


def push_with_python(remote_url: str, username: str = "", token: str = ""):
    """Push local main branch to remote using pure Python Dulwich."""
    repo = Repo(".")
    print(f"[*] Connecting to remote: {remote_url}")

    # Set up remote in git config
    config = repo.get_config()
    config.set((b"remote", b"origin"), b"url", remote_url.encode("utf-8"))
    config.write_to_path()

    # If username and token provided, inject into URL if https
    push_url = remote_url
    if token and "https://" in remote_url:
        clean_url = remote_url.replace("https://", "")
        if username:
            push_url = f"https://{username}:{token}@{clean_url}"
        else:
            push_url = f"https://{token}@{clean_url}"

    try:
        print("[*] Pushing 'main' branch to GitHub...")
        porcelain.push(
            repo,
            push_url.encode("utf-8"),
            refspecs=[b"refs/heads/main:refs/heads/main"],
        )
        print("\n[✓] Successfully pushed to GitHub!")
        print(f"    Repository: {remote_url}\n")
    except Exception as e:
        print(f"\n[!] Push failed via Python: {e}")
        print("[*] Trying master branch refspec...")
        try:
            porcelain.push(
                repo,
                push_url.encode("utf-8"),
                refspecs=[b"refs/heads/master:refs/heads/master"],
            )
            print("\n[✓] Successfully pushed 'master' branch to GitHub!\n")
        except Exception as e2:
            print(f"[!] Push error: {e2}")


def main():
    if len(sys.argv) > 1:
        remote_url = sys.argv[1].strip()
    else:
        print("==============================================================")
        print("  Push Movie Recommendation System to GitHub")
        print("==============================================================")
        remote_url = input("Enter your GitHub repository URL (e.g. https://github.com/username/repo.git): ").strip()

    if not remote_url:
        print("[!] No repository URL provided.")
        sys.exit(1)

    # Optional credentials for private or non-interactive push
    token = os.environ.get("GITHUB_TOKEN", "")
    username = os.environ.get("GITHUB_USER", "")

    if not token and "@" not in remote_url and remote_url.startswith("https://"):
        print("\nNote: GitHub requires a Personal Access Token (PAT) for HTTPS.")
        token = input("Enter your GitHub Personal Access Token (or press Enter if already in URL / SSH): ").strip()
        if token:
            username = input("Enter your GitHub Username: ").strip()

    push_with_python(remote_url, username=username, token=token)


if __name__ == "__main__":
    main()
