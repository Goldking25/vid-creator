"""
Key management utility – store and remove API keys in Windows Credential Manager.

Usage:
    python keys.py store       # Prompts for keys and saves them securely
    python keys.py show        # Shows which keys are configured (masked)
    python keys.py delete      # Removes stored keys
"""

import sys
import getpass

try:
    import keyring
except ImportError:
    print("Error: 'keyring' is not installed. Run: pip install keyring")
    sys.exit(1)

SERVICE_NAME = "vid-creator"
KEY_NAMES = ["YOUTUBE_API_KEY", "GOOGLE_API_KEY"]


def store_keys():
    """Prompt user for API keys and store them in the credential manager."""
    print("Store API keys in Windows Credential Manager\n")
    for name in KEY_NAMES:
        existing = keyring.get_password(SERVICE_NAME, name)
        status = "(currently set)" if existing else "(not set)"
        value = getpass.getpass(f"  {name} {status}: ").strip()
        if value:
            keyring.set_password(SERVICE_NAME, name, value)
            print(f"    ✓ {name} saved.\n")
        else:
            print(f"    → Skipped (kept existing).\n")
    print("Done! Keys are stored securely. You can now delete your .env file.")


def show_keys():
    """Show which keys are configured (masked)."""
    print("Stored API keys:\n")
    for name in KEY_NAMES:
        val = keyring.get_password(SERVICE_NAME, name)
        if val:
            masked = val[:4] + "****" + val[-4:]
            print(f"  {name}: {masked}")
        else:
            print(f"  {name}: (not set)")


def delete_keys():
    """Remove stored keys from credential manager."""
    print("Deleting stored API keys...\n")
    for name in KEY_NAMES:
        try:
            keyring.delete_password(SERVICE_NAME, name)
            print(f"  ✓ {name} deleted.")
        except keyring.errors.PasswordDeleteError:
            print(f"  → {name} was not set.")
    print("\nDone.")


if __name__ == "__main__":
    commands = {"store": store_keys, "show": show_keys, "delete": delete_keys}

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("Usage: python keys.py [store|show|delete]")
        sys.exit(1)

    commands[sys.argv[1]]()
