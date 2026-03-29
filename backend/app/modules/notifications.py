"""
NEXUS Notification Service
Telegram · WhatsApp · Email · Discord · SMS · Voice Call
"""
import asyncio
from typing import Optional
from loguru import logger

from app.core.config import settings


class NotificationService:

    async def send_telegram(self, chat_id: str, message: str, parse_mode: str = "Markdown"):
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("Telegram not configured")
            return False
        import httpx
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode,
            })
            return r.status_code == 200

    async def send_email(
        self, to: str, subject: str, body: str, html: bool = False
    ):
        if not settings.SMTP_USER:
            logger.warning("Email not configured")
            return False
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = settings.SMTP_USER
            msg["To"]      = to

            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type))

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            return True
        except Exception as e:
            logger.error(f"Email error: {e}")
            return False

    async def send_whatsapp(self, to: str, message: str):
        if not settings.TWILIO_ACCOUNT_SID:
            logger.warning("Twilio not configured")
            return False
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            msg = await asyncio.to_thread(
                client.messages.create,
                body=message,
                from_=f"whatsapp:{settings.TWILIO_PHONE}",
                to=f"whatsapp:{to}",
            )
            return bool(msg.sid)
        except Exception as e:
            logger.error(f"WhatsApp error: {e}")
            return False

    async def send_sms(self, to: str, message: str):
        if not settings.TWILIO_ACCOUNT_SID:
            return False
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            msg = await asyncio.to_thread(
                client.messages.create,
                body=message[:160],
                from_=settings.TWILIO_PHONE,
                to=to,
            )
            return bool(msg.sid)
        except Exception as e:
            logger.error(f"SMS error: {e}")
            return False

    async def make_voice_call(self, to: str, message: str):
        """Voice call for critical alerts — black swan events"""
        if not settings.TWILIO_ACCOUNT_SID:
            return False
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-US">{message}</Say>
    <Pause length="2"/>
    <Say language="en-US">{message}</Say>
</Response>"""
            call = await asyncio.to_thread(
                client.calls.create,
                twiml=twiml,
                to=to,
                from_=settings.TWILIO_PHONE,
            )
            return bool(call.sid)
        except Exception as e:
            logger.error(f"Voice call error: {e}")
            return False

    async def send_discord(self, channel_id: str, message: str):
        if not settings.DISCORD_BOT_TOKEN:
            return False
        try:
            import httpx
            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            headers = {"Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}"}
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url,
                    json={"content": message[:2000]},
                    headers=headers,
                )
                return r.status_code == 200
        except Exception as e:
            logger.error(f"Discord error: {e}")
            return False

    async def send_voice_message(self, chat_id: str, text: str, lang: str = "en"):
        """ElevenLabs TTS → send as voice message"""
        if not settings.ELEVENLABS_KEY:
            return await self.send_telegram(chat_id, text)
        try:
            import httpx
            voice_id = settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": settings.ELEVENLABS_KEY}
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            }
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(url, json=payload, headers=headers)
                if r.status_code == 200:
                    audio = r.content
                    tg_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendVoice"
                    files = {"voice": ("brief.mp3", audio, "audio/mpeg")}
                    data  = {"chat_id": chat_id}
                    send_r = await client.post(tg_url, data=data, files=files)
                    return send_r.status_code == 200
        except Exception as e:
            logger.error(f"Voice message error: {e}")
            return await self.send_telegram(chat_id, text)

    async def broadcast(
        self,
        user_id: str,
        message: str,
        channels: list,
        lang: str = "en",
        priority: str = "normal",
    ):
        """Send to all configured channels"""
        results = {}

        if "telegram" in channels:
            results["telegram"] = await self.send_telegram(
                settings.TELEGRAM_ADMIN_ID or user_id, message
            )

        if "email" in channels and settings.ADMIN_EMAIL:
            results["email"] = await self.send_email(
                settings.ADMIN_EMAIL,
                subject="NEXUS Alert",
                body=message,
            )

        if "whatsapp" in channels and settings.ADMIN_PHONE:
            results["whatsapp"] = await self.send_whatsapp(
                settings.ADMIN_PHONE, message
            )

        if "sms" in channels and settings.ADMIN_PHONE and priority == "critical":
            results["sms"] = await self.send_sms(settings.ADMIN_PHONE, message)

        if "discord" in channels and settings.DISCORD_CHANNEL_ID:
            results["discord"] = await self.send_discord(
                settings.DISCORD_CHANNEL_ID, message
            )

        if "voice" in channels and settings.ADMIN_PHONE and priority == "critical":
            results["voice"] = await self.make_voice_call(
                settings.ADMIN_PHONE, message
            )

        return results


notification_service = NotificationService()
