"""
Twilio Outbound Call Dialer
============================
Places outbound phone calls via Twilio API.
Supports single calls and bulk calling (1000+ simultaneous).

Usage:
    from twilio_calls.outbound_call import TwilioDialer
    
    dialer = TwilioDialer()
    dialer.call("+91XXXXXXXXXX")
"""

import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    print("❌ Twilio SDK not installed. Run: pip install twilio")
    sys.exit(1)


class TwilioDialer:
    """Handles outbound call automation via Twilio."""

    def __init__(
        self,
        account_sid: str = None,
        auth_token: str = None,
        from_number: str = None,
    ):
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_PHONE_NUMBER")

        if not all([self.account_sid, self.auth_token, self.from_number]):
            missing = []
            if not self.account_sid:
                missing.append("TWILIO_ACCOUNT_SID")
            if not self.auth_token:
                missing.append("TWILIO_AUTH_TOKEN")
            if not self.from_number:
                missing.append("TWILIO_PHONE_NUMBER")
            raise ValueError(
                f"❌ Missing Twilio credentials: {', '.join(missing)}\n"
                f"   Set them in your .env file."
            )

        self.client = Client(self.account_sid, self.auth_token)
        self.call_log = []

    # ─── Single Call ──────────────────────────────────────────────

    def call(
        self,
        to_number: str,
        webhook_url: str = None,
        language: str = "english",
        status_callback: str = None,
    ) -> dict:
        """
        Place a single outbound call.

        Args:
            to_number: Recipient phone number (e.g., +91XXXXXXXXXX).
            webhook_url: Your ngrok webhook URL (e.g., https://xxxx.ngrok-free.app).
            language: Language for the greeting (hindi/english/kannada).
            status_callback: URL for call status updates.

        Returns:
            Dict with call SID and status.
        """
        if not webhook_url:
            webhook_url = os.getenv("NGROK_URL")
            if not webhook_url:
                raise ValueError(
                    "❌ No webhook URL provided!\n"
                    "   Start ngrok: ngrok http 5000\n"
                    "   Then pass the URL or set NGROK_URL in .env"
                )

        voice_url = f"{webhook_url.rstrip('/')}/voice?lang={language}"
        status_url = f"{webhook_url.rstrip('/')}/status" if not status_callback else status_callback

        print(f"📞 Calling {to_number}...")
        print(f"   From: {self.from_number}")
        print(f"   Webhook: {voice_url}")

        try:
            call = self.client.calls.create(
                url=voice_url,
                to=to_number,
                from_=self.from_number,
                status_callback=status_url,
                status_callback_event=["initiated", "ringing", "answered", "completed"],
                status_callback_method="POST",
            )

            result = {
                "call_sid": call.sid,
                "to": to_number,
                "from": self.from_number,
                "status": call.status,
                "timestamp": datetime.now().isoformat(),
                "language": language,
            }

            self.call_log.append(result)
            print(f"✅ Call initiated! SID: {call.sid}")
            print(f"   Status: {call.status}")
            return result

        except TwilioRestException as e:
            error_result = {
                "error": str(e),
                "to": to_number,
                "timestamp": datetime.now().isoformat(),
            }
            self.call_log.append(error_result)
            print(f"❌ Call failed: {e}")
            return error_result

    # ─── Bulk Calls ───────────────────────────────────────────────

    def bulk_call(
        self,
        numbers: list,
        webhook_url: str,
        language: str = "english",
        delay_between: float = 0.5,
        max_concurrent: int = 50,
    ) -> list:
        """
        Place calls to multiple numbers (for ASHA/Bank follow-ups).
        
        Args:
            numbers: List of phone numbers to call.
            webhook_url: Your ngrok/production webhook URL.
            language: Language for all calls.
            delay_between: Seconds between each call (rate limiting).
            max_concurrent: Max simultaneous calls.

        Returns:
            List of call results.
        """
        total = len(numbers)
        print(f"\n📞 BULK CALLING: {total} numbers")
        print(f"   Language: {language}")
        print(f"   Delay: {delay_between}s between calls")
        print(f"   Max concurrent: {max_concurrent}")
        print("─" * 50)

        results = []
        for i, number in enumerate(numbers, 1):
            print(f"\n[{i}/{total}] ", end="")
            result = self.call(number, webhook_url, language)
            results.append(result)

            # Rate limiting
            if i < total:
                time.sleep(delay_between)

            # Respect max concurrent limit
            if i % max_concurrent == 0 and i < total:
                print(f"\n⏸️  Batch limit reached. Waiting 10s for calls to complete...")
                time.sleep(10)

        # Summary
        successful = sum(1 for r in results if "call_sid" in r)
        failed = total - successful
        print(f"\n{'=' * 50}")
        print(f"📊 BULK CALL SUMMARY")
        print(f"   Total: {total} | Success: {successful} | Failed: {failed}")
        print(f"{'=' * 50}")

        return results

    # ─── Call Status ──────────────────────────────────────────────

    def get_call_status(self, call_sid: str) -> dict:
        """Check the current status of a call."""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "direction": call.direction,
                "to": call.to,
                "from_": call.from_,
                "start_time": str(call.start_time),
                "end_time": str(call.end_time),
            }
        except TwilioRestException as e:
            return {"error": str(e)}

    # ─── Logging ──────────────────────────────────────────────────

    def save_call_log(self, filepath: str = "output/call_log.json") -> str:
        """Save the call log to a JSON file."""
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.call_log, f, indent=2, default=str)
        print(f"💾 Call log saved to {filepath}")
        return filepath


# ─── CLI Interface ────────────────────────────────────────────────
if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   📞  TWILIO OUTBOUND DIALER                ║")
    print("║   Mouriyan's Voice Agent                     ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    try:
        dialer = TwilioDialer()
        print("✅ Twilio credentials loaded!\n")
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    to_number = os.getenv("YOUR_PHONE_NUMBER") or input("📱 Enter phone number to call (e.g., +91...): ").strip()
    webhook_url = os.getenv("NGROK_URL") or input("🌐 Enter ngrok URL (e.g., https://xxxx.ngrok-free.app): ").strip()

    if not to_number or not webhook_url:
        print("❌ Both phone number and webhook URL are required!")
        sys.exit(1)

    result = dialer.call(to_number, webhook_url)
    print(f"\n📋 Result: {json.dumps(result, indent=2)}")
