"""Utility script to push the repository to GitHub.

Configures SSL certificates and pushes via Dulwich (Pure Python Git client).
"""

import os
import sys
import certifi

# Ensure SSL certificates are properly loaded on macOS
os.environ["SSL_CERT_FILE"] = certifi.where()

from dulwich import porcelain
from dulwich.repo import Repo


def push_with_python(remote_url: str, username: str = "sushantv2301", token: str = ""):
    """Push local main branch to remote using pure Python Dulwich."""
    repo = Repo(".")
    print(f"[*] Target GitHub Repository: {remote_url}")

    # Set up remote in git config
    config = repo.get_config()
    config.set((b"remote", b"origin"), b"url", remote_url.encode("utf-8"))
    config.write_to_path()

    # If token provided, format URL with credentials
    push_url = remote_url
    if token:
        clean_url = remote_url.replace("https://", "").replace("http://", "")
        # GitHub accepts https://<token>@github.com/... or https://<username>:<token>@github.com/...
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
        print("\n==============================================================")
        print("  🎉 SUCCESS! Project successfully pushed to GitHub!")
        print(f"  View online: https://github.com/sushantv2301/Movie-Recommendation-system")
        print("==============================================================\n")
    except Exception as e:
        print(f"\n[!] Push failed: {e}")
        if "HTTPUnauthorized" in str(type(e)) or "No valid credentials" in str(e):
            print("\nGitHub requires authentication to push.")
            print("Please provide a Personal Access Token (PAT) from GitHub:")
            print("1. Go to https://github.com/settings/tokens")
            print("2. Generate a token with 'repo' scope")
            print("3. Re-run this script with your token.")


def main():
    repo_url = "https://github.com/sushantv2301/Movie-Recommendation-system.git"
    token = ""

    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg.startswith("ghp_") or arg.startswith("github_pat_"):
            token = arg
        elif "github.com" in arg:
            repo_url = arg
            if len(sys.argv) > 2:
                token = sys.argv[2].strip()

    if not token:
        token = os.environ.get("GITHUB_TOKEN", "").strip()

    if not token:
        print("==============================================================")
        print("  Pushing to: https://github.com/sushantv2301/Movie-Recommendation-system.git")
        print("==============================================================")
        token = input("Enter your GitHub Personal Access Token (starts with ghp_ or github_pat_): ").strip()

    push_with_python(repo_url, username="sushantv2301", token=token)


if __name__ == "__main__":
    main()
