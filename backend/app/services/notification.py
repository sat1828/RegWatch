from __future__ import annotations

import json

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class NotificationService:
    async def send_email(
        self, to: str, subject: str, html_body: str
    ) -> bool:
        api_key = settings.resend_api_key
        if not api_key or not api_key.get_secret_value():
            logger.warning("resend_not_configured", to=to, subject=subject)
            return False

        try:
            import resend

            resend.api_key = api_key.get_secret_value()
            params = {
                "from": settings.notification_email_from,
                "to": [to],
                "subject": subject,
                "html": html_body,
            }
            response = resend.Emails.send(params)
            logger.info("email_sent", to=to, subject=subject, response=response)
            return True
        except Exception as e:
            logger.error("email_send_failed", to=to, subject=subject, error=str(e))
            return False

    async def send_slack_message(self, message: str, blocks: list[dict] | None = None) -> bool:
        webhook_url = settings.slack_webhook_url
        if not webhook_url:
            logger.warning("slack_not_configured")
            return False

        try:
            import httpx

            payload: dict = {"text": message}
            if blocks:
                payload["blocks"] = blocks

            async with httpx.AsyncClient() as client:
                resp = await client.post(webhook_url, json=payload)
                resp.raise_for_status()
                logger.info("slack_message_sent")
                return True
        except Exception as e:
            logger.error("slack_send_failed", error=str(e))
            return False

    async def notify_urgent(
        self,
        subject: str,
        message: str,
        email_to: str | None = None,
        slack_channel: str | None = None,
    ) -> bool:
        success = True

        if email_to:
            ok = await self.send_email(
                to=email_to, subject=f"[URGENT] {subject}", html_body=f"<p>{message}</p>"
            )
            success = success and ok

        if slack_channel:
            ok = await self.send_slack_message(
                message=f"🚨 *URGENT: {subject}*\n{message}"
            )
            success = success and ok

        return success


notification_service = NotificationService()
