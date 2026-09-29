import os
import smtplib
import time

from email.message import EmailMessage


class AlertManager:
    """
    Handles PPE violation alerts.

    Email alerts are optional during development/testing.
    Screenshot alerts continue to work even when
    email configuration is not available.
    """

    def __init__(
        self,
        smtp_server,
        smtp_port,
        sender_email,
        sender_password,
        supervisor_email,
        screenshot_dir,
        cooldown_seconds=60
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

        # Email configuration is optional.
        self.supervisor_email = []

        if supervisor_email:
            self.supervisor_email = [
                email.strip()
                for email in supervisor_email.split(",")
                if email.strip()
            ]

        self.email_enabled = bool(
            self.sender_email
            and self.sender_password
            and self.supervisor_email
        )

        self.screenshot_dir = screenshot_dir
        self.cooldown_seconds = cooldown_seconds

        os.makedirs(
            self.screenshot_dir,
            exist_ok=True
        )

        # Key: (worker_id, violation)
        # Value: time of last alert
        self.last_alert_time = {}

        print("Alert Manager initialized.")

        if self.email_enabled:
            print("Email alerts: ENABLED")
        else:
            print("Email alerts: DISABLED")

        print("Screenshot alerts: ENABLED")

    def _can_send_alert(
        self,
        worker_id,
        violation
    ):
        """
        Prevents repeated alerts for the same
        worker and violation within the cooldown.
        """
        key = (
            worker_id,
            violation
        )

        current_time = time.time()
        last_time = self.last_alert_time.get(key)

        if last_time is None:
            return True

        elapsed = current_time - last_time

        return elapsed >= self.cooldown_seconds

    def _mark_alert_sent(
        self,
        worker_id,
        violation
    ):
        key = (
            worker_id,
            violation
        )

        self.last_alert_time[key] = time.time()

    def save_screenshot(
        self,
        frame,
        frame_number,
        worker_id,
        violation
    ):
        """
        Saves the annotated frame as a screenshot.
        """
        safe_violation = (
            violation
            .replace(" ", "_")
            .replace("|", "_")
        )

        filename = (
            f"frame_{frame_number}"
            f"_worker_{worker_id}"
            f"_{safe_violation}.jpg"
        )

        screenshot_path = os.path.join(
            self.screenshot_dir,
            filename
        )

        import cv2

        success = cv2.imwrite(
            screenshot_path,
            frame
        )

        if not success:
            raise RuntimeError(
                f"Failed to save screenshot: "
                f"{screenshot_path}"
            )

        print(
            f"[ALERT SCREENSHOT] "
            f"{screenshot_path}"
        )

        return screenshot_path

    def send_email(
        self,
        worker_id,
        violation,
        frame_number,
        screenshot_path
    ):
        """
        Sends PPE violation email with screenshot attachment.

        If email configuration is not available,
        email sending is skipped.
        """
        if not self.email_enabled:
            print(
                f"[EMAIL DISABLED] "
                f"Skipping email for Worker {worker_id} | "
                f"{violation}"
            )
            return

        message = EmailMessage()

        message["Subject"] = (
            f"PPE Violation Alert - "
            f"Worker {worker_id}"
        )

        message["From"] = self.sender_email

        message["To"] = ", ".join(
            self.supervisor_email
        )

        message.set_content(
            f"""
PPE VIOLATION ALERT

Worker ID      : {worker_id}
Violation      : {violation}
Frame Number   : {frame_number}

Immediate attention is required.

The violation screenshot is attached
to this email.

PPE Monitoring System
"""
        )

        with open(
            screenshot_path,
            "rb"
        ) as file:
            image_data = file.read()

        message.add_attachment(
            image_data,
            maintype="image",
            subtype="jpeg",
            filename=os.path.basename(
                screenshot_path
            )
        )

        try:
            print(
                f"[EMAIL] Sending alert "
                f"for Worker {worker_id}..."
            )

            with smtplib.SMTP(
                self.smtp_server,
                self.smtp_port
            ) as server:
                server.starttls()

                server.login(
                    self.sender_email,
                    self.sender_password
                )

                server.send_message(message)

            print(
                f"[EMAIL SENT] "
                f"Worker {worker_id} | "
                f"{violation}"
            )

        except Exception as e:
            print(
                f"[EMAIL ERROR] {e}"
            )

    def process_alert(
        self,
        frame,
        frame_number,
        worker_id,
        violations
    ):
        """
        Processes PPE violations for one worker.

        Saves a screenshot for each confirmed violation.
        Email is sent only when email configuration
        is available.

        Cooldown prevents repeated alerts for the
        same worker and violation.
        """
        if not violations:
            return

        for violation in violations:
            if not self._can_send_alert(
                worker_id,
                violation
            ):
                continue

            screenshot_path = self.save_screenshot(
                frame,
                frame_number,
                worker_id,
                violation
            )

            self.send_email(
                worker_id,
                violation,
                frame_number,
                screenshot_path
            )

            self._mark_alert_sent(
                worker_id,
                violation
            )
