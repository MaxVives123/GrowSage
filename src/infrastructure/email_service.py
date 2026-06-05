"""Email delivery — uses Resend in production, logs to console in dev."""
from __future__ import annotations
import os


def send_verification_email(to_email: str, token: str) -> None:
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    verify_url = f"{backend_url}/auth/verify/{token}"
    api_key = os.getenv("RESEND_API_KEY", "")

    if not api_key:
        # Local dev / missing key — print link so dev can verify manually
        print(f"\n[EMAIL] Verification link for {to_email}:\n{verify_url}\n")
        return

    try:
        import resend
        resend.api_key = api_key
        resend.Emails.send({
            "from": "GrowSage <onboarding@resend.dev>",
            "to": to_email,
            "subject": "Verify your GrowSage account 🌱",
            "html": f"""
            <div style="font-family:sans-serif;max-width:480px;margin:auto">
              <h2 style="color:#052e16">Welcome to GrowSage 🌱</h2>
              <p>Click the button below to verify your email address.
                 The link expires in <strong>24 hours</strong>.</p>
              <a href="{verify_url}"
                 style="display:inline-block;margin:16px 0;padding:12px 24px;
                        background:#16a34a;color:#fff;border-radius:8px;
                        text-decoration:none;font-weight:600">
                Verify my email
              </a>
              <p style="color:#6b7280;font-size:13px">
                If you didn't create an account, you can safely ignore this email.
              </p>
            </div>
            """,
        })
    except Exception as exc:
        # Never block registration because of email failure — just log it
        print(f"[EMAIL ERROR] Failed to send verification email to {to_email}: {exc}")
