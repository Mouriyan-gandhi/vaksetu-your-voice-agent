"""
Twilio Outbound Call — Solo Test
=================================
Run this to test: your phone should ring!

Usage:
    python -m twilio_calls.test_call

Prerequisites:
    1. .env file with Twilio credentials
    2. Webhook server running (python -m twilio_calls.webhook_server)
    3. ngrok tunnel active (ngrok http 5000)
"""

import os
import sys
import time
import json
import subprocess
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from twilio_calls.outbound_call import TwilioDialer


def print_banner():
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   📞  TWILIO OUTBOUND CALL TEST             ║")
    print("║   Mouriyan's Voice Agent                     ║")
    print("╚══════════════════════════════════════════════╝")
    print()


def check_prerequisites():
    """Verify all prerequisites are met."""
    print("🔍 Checking prerequisites...\n")

    checks = []

    # Check Twilio credentials
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_num = os.getenv("TWILIO_PHONE_NUMBER")
    your_num = os.getenv("YOUR_PHONE_NUMBER")

    if sid and sid != "your_twilio_account_sid_here":
        checks.append(("Twilio Account SID", True, sid[:8] + "..."))
    else:
        checks.append(("Twilio Account SID", False, "Not set in .env"))

    if token and token != "your_twilio_auth_token_here":
        checks.append(("Twilio Auth Token", True, "****" + token[-4:]))
    else:
        checks.append(("Twilio Auth Token", False, "Not set in .env"))

    if twilio_num and twilio_num != "+1XXXXXXXXXX":
        checks.append(("Twilio Phone Number", True, twilio_num))
    else:
        checks.append(("Twilio Phone Number", False, "Not set in .env"))

    if your_num and your_num != "+91XXXXXXXXXX":
        checks.append(("Your Phone Number", True, your_num))
    else:
        checks.append(("Your Phone Number", False, "Not set in .env"))

    # Check ngrok URL
    ngrok_url = os.getenv("NGROK_URL")
    if ngrok_url:
        checks.append(("Ngrok URL", True, ngrok_url))
    else:
        checks.append(("Ngrok URL", False, "Not set — will need manual input"))

    # Print results
    all_pass = True
    for name, passed, detail in checks:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name}: {detail}")
        if not passed and name != "Ngrok URL":
            all_pass = False

    print()
    return all_pass


def run_test():
    """Run the full test workflow."""
    print_banner()

    # Step 1: Check prerequisites
    prereqs_ok = check_prerequisites()
    if not prereqs_ok:
        print("⚠️  Some prerequisites are missing!")
        print("   Please update your .env file with the correct values.")
        print("   Run: cp .env.example .env")
        print()
        proceed = input("Continue anyway? (y/N): ").strip().lower()
        if proceed != "y":
            return

    print("─" * 50)
    print()

    # Step 2: Remind about webhook server
    print("📋 CHECKLIST before calling:")
    print("   1. ✅ .env file configured")
    print("   2. ⬜ Webhook server running?")
    print("      → python -m twilio_calls.webhook_server")
    print("   3. ⬜ Ngrok tunnel active?")
    print("      → ngrok http 5000")
    print()

    proceed = input("All ready? Press Enter to place the call (or 'q' to quit): ").strip()
    if proceed.lower() in ("q", "quit"):
        return

    # Step 3: Get inputs
    to_number = os.getenv("YOUR_PHONE_NUMBER")
    if not to_number or to_number == "+91XXXXXXXXXX":
        to_number = input("📱 Your phone number (e.g., +919876543210): ").strip()

    webhook_url = os.getenv("NGROK_URL")
    if not webhook_url:
        webhook_url = input("🌐 Ngrok URL (e.g., https://abc123.ngrok-free.app): ").strip()

    # Step 4: Place the call!
    print()
    print("🚀 PLACING CALL...")
    print("─" * 50)

    try:
        dialer = TwilioDialer()
        result = dialer.call(
            to_number=to_number,
            webhook_url=webhook_url,
            language="english",
        )

        if "call_sid" in result:
            print()
            print("📱 CHECK YOUR PHONE! It should be ringing now!")
            print()

            # Monitor call status
            print("📊 Monitoring call status...")
            call_sid = result["call_sid"]
            for i in range(30):  # Monitor for 30 seconds
                time.sleep(2)
                status = dialer.get_call_status(call_sid)
                current_status = status.get("status", "unknown")
                print(f"   ⏱️  {i*2}s: {current_status}")

                if current_status in ("completed", "failed", "busy", "no-answer", "canceled"):
                    break

            print()
            print("📋 Final call details:")
            print(json.dumps(status, indent=2))

            # Save log
            dialer.save_call_log()

        else:
            print(f"\n❌ Call failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Common fixes:")
        print("   • Make sure webhook server is running")
        print("   • Make sure ngrok is active")
        print("   • Check your Twilio credentials")
        print("   • Verify phone numbers are in E.164 format (+91...)")


if __name__ == "__main__":
    run_test()
