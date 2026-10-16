"""Utility script to push the Online Food Order Processing System repository to GitHub.

Configures SSL certificates and pushes via Dulwich (Pure Python Git client).
Supports GitHub Personal Access Token (PAT).
"""

import os
import sys
import certifi

# Ensure SSL certificates are properly loaded on macOS
os.environ["SSL_CERT_FILE"] = certifi.where()

from dulwich import porcelain
from dulwich.repo import Repo


def push_with_python(remote_url: str, username: str = "sushantv2301", token: str = ""):
    """Push local main and master branches to remote using pure Python Dulwich."""
    repo = Repo(".")
    print(f"[*] Target GitHub Repository: {remote_url}")

    # Set up remote in git config
    config = repo.get_config()
    config.set((b"remote", b"origin"), b"url", remote_url.encode("utf-8"))
    config.write_to_path()

    # Format URL with credentials if token is provided
    push_url = remote_url
    if token:
        clean_url = remote_url.replace("https://", "").replace("http://", "")
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
        print(f"  View online: https://github.com/sushantv2301/online-food-Processing-System")
        print("==============================================================\n")
    except Exception as e:
        err_str = str(e)
        print(f"\n[!] Push failed: {err_str}")
        if "HTTPUnauthorized" in str(type(e)) or "No valid credentials" in err_str or "401" in err_str or "403" in err_str:
            print("\nGitHub requires authentication to push to your repository.")
            print("Please generate a Personal Access Token (classic) on GitHub:")
            print("  1. Visit: https://github.com/settings/tokens")
            print("  2. Click 'Generate new token (classic)'")
            print("  3. Give it a name and check the 'repo' scope checkbox")
            print("  4. Copy the token (starts with ghp_...)")
            print("  5. Run: python3 push_to_github.py <YOUR_TOKEN>\n")
        elif "nodename nor servname provided" in err_str or "NameResolutionError" in err_str:
            print("\n[!] Network error: Cannot resolve github.com. Please check your internet connection.\n")


def main():
    repo_url = "https://github.com/sushantv2301/online-food-Processing-System.git"
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
        token = os.environ.get("GITHUB_TOKEN", "").strip() or os.environ.get("GH_TOKEN", "").strip()

    if not token:
        print("==============================================================")
        print(f"  Pushing to: {repo_url}")
        print("==============================================================")
        try:
            token = input("Enter your GitHub Personal Access Token (starts with ghp_...): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")
            return

    push_with_python(repo_url, username="sushantv2301", token=token)


if __name__ == "__main__":
    main()
