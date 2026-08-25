"""Notification and Invoice Service for MediMind.

Handles:
- HTML & text invoice generation
- Email dispatch (SMTP or simulated)
- SMS notification (Twilio API or simulated)
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import requests


def generate_invoice_html(order):
    """Generate a clean, professional HTML invoice for an order."""
    order_id = order.get("order_id", "MM-DRAFT")
    customer_name = order.get("customer_name", "Customer")
    phone = order.get("phone", "N/A")
    email = order.get("email", "N/A")
    address = order.get("address", "N/A")
    created_at = order.get("created_at", "")
    items = order.get("items", [])
    total_pkr = order.get("total_pkr", 0)

    items_rows = ""
    for item in items:
        items_rows += f"""
        <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0; font-weight: 500; color: #1e293b;">{item['name']}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0; color: #64748b;">{item.get('category', 'General')}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0; text-align: center; color: #1e293b;">{item['quantity']}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0; text-align: right; color: #1e293b;">PKR {item['price_pkr']:,.0f}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600; color: #0f766e;">PKR {item['total_pkr']:,.0f}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>MediMind Invoice - {order_id}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #334155;">
    <div style="max-width: 680px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0;">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #0f766e 0%, #115e59 100%); padding: 28px 32px; color: #ffffff;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td>
                        <h1 style="margin: 0; font-size: 26px; font-weight: 700; letter-spacing: -0.5px; color: #ffffff;">🧠 MediMind</h1>
                        <p style="margin: 4px 0 0 0; font-size: 13px; color: #ccfbf1;">Medical Knowledge & Pharmacy Companion</p>
                    </td>
                    <td style="text-align: right; vertical-align: top;">
                        <span style="background-color: rgba(255, 255, 255, 0.2); padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #ffffff;">Official Invoice</span>
                    </td>
                </tr>
            </table>
        </div>

        <!-- Meta Details -->
        <div style="padding: 24px 32px; background-color: #f1f5f9; border-bottom: 1px solid #e2e8f0;">
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr>
                    <td style="width: 50%; vertical-align: top;">
                        <p style="margin: 0 0 4px 0; font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px;">Invoice To</p>
                        <p style="margin: 0; font-weight: 700; font-size: 15px; color: #0f172a;">{customer_name}</p>
                        <p style="margin: 3px 0 0 0; color: #475569;">📞 {phone}</p>
                        <p style="margin: 3px 0 0 0; color: #475569;">✉️ {email}</p>
                        <p style="margin: 3px 0 0 0; color: #475569;">📍 {address}</p>
                    </td>
                    <td style="width: 50%; vertical-align: top; text-align: right;">
                        <p style="margin: 0 0 4px 0; font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px;">Order Details</p>
                        <p style="margin: 0; font-weight: 700; font-size: 15px; color: #0f766e;">ID: {order_id}</p>
                        <p style="margin: 3px 0 0 0; color: #475569;">📅 Date: {created_at}</p>
                        <p style="margin: 3px 0 0 0; color: #475569;">💳 Payment Mode: Cash on Delivery</p>
                    </td>
                </tr>
            </table>
        </div>

        <!-- Itemized Table -->
        <div style="padding: 24px 32px;">
            <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #0f172a; font-weight: 600;">Prescribed Items Summary</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <thead>
                    <tr style="background-color: #f8fafc; border-bottom: 2px solid #cbd5e1;">
                        <th style="padding: 10px 12px; text-align: left; font-size: 12px; text-transform: uppercase; color: #64748b;">Medicine</th>
                        <th style="padding: 10px 12px; text-align: left; font-size: 12px; text-transform: uppercase; color: #64748b;">Category</th>
                        <th style="padding: 10px 12px; text-align: center; font-size: 12px; text-transform: uppercase; color: #64748b;">Qty</th>
                        <th style="padding: 10px 12px; text-align: right; font-size: 12px; text-transform: uppercase; color: #64748b;">Unit Price</th>
                        <th style="padding: 10px 12px; text-align: right; font-size: 12px; text-transform: uppercase; color: #64748b;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_rows}
                </tbody>
            </table>

            <!-- Order Totals -->
            <div style="margin-top: 20px; padding-top: 16px; border-top: 2px dashed #e2e8f0;">
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <tr>
                        <td style="text-align: right; color: #64748b; padding-bottom: 6px;">Subtotal:</td>
                        <td style="text-align: right; font-weight: 600; color: #1e293b; width: 140px; padding-bottom: 6px;">PKR {total_pkr:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="text-align: right; color: #64748b; padding-bottom: 6px;">Delivery Fee:</td>
                        <td style="text-align: right; font-weight: 600; color: #16a34a; width: 140px; padding-bottom: 6px;">FREE</td>
                    </tr>
                    <tr>
                        <td style="text-align: right; font-size: 16px; font-weight: 700; color: #0f172a; padding-top: 8px; border-top: 1px solid #cbd5e1;">Grand Total:</td>
                        <td style="text-align: right; font-size: 18px; font-weight: 800; color: #0f766e; padding-top: 8px; border-top: 1px solid #cbd5e1;">PKR {total_pkr:,.0f}</td>
                    </tr>
                </table>
            </div>
        </div>

        <!-- Footer / Disclaimer -->
        <div style="padding: 20px 32px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.5;">
            <p style="margin: 0 0 6px 0; font-weight: 600; color: #475569;">ℹ️ Important Medical Note:</p>
            <p style="margin: 0;">This invoice is issued by MediMind Demonstration Pharmacy. Medicine recommendations are for informational purposes only and do not replace professional medical advice from a licensed healthcare practitioner.</p>
            <p style="margin: 12px 0 0 0; text-align: center; color: #94a3b8; font-size: 11px;">Thank you for choosing MediMind!</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def generate_sms_text(order):
    """Generate concise SMS text message for order notification."""
    order_id = order.get("order_id", "MM-DRAFT")
    items_count = sum(item["quantity"] for item in order.get("items", []))
    total_pkr = order.get("total_pkr", 0)
    customer_name = order.get("customer_name", "Customer")
    return (
        f"MediMind Order Confirmed! Hello {customer_name}, your order #{order_id} "
        f"({items_count} item(s), Total: PKR {total_pkr:,.0f}) is being processed for Cash on Delivery. "
        f"Thank you for choosing MediMind!"
    )


def send_email_invoice(order, recipient_email):
    """Send HTML invoice via SMTP if configured, else fallback to simulation."""
    if not recipient_email or "@" not in recipient_email:
        return False, "Invalid email address provided."

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL", smtp_user or "noreply@medimind.com")

    html_content = generate_invoice_html(order)
    order_id = order.get("order_id", "MM-DRAFT")

    # If SMTP is configured, attempt live email dispatch
    if smtp_server and smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"MediMind Order Invoice #{order_id}"
            msg["From"] = sender_email
            msg["To"] = recipient_email

            # Text version
            text_summary = (
                f"MediMind Order Invoice #{order_id}\n\n"
                f"Customer: {order.get('customer_name')}\n"
                f"Total Amount: PKR {order.get('total_pkr'):,.0f}\n\n"
                f"Please open this email in an HTML-compatible client to view the formatted invoice."
            )
            msg.attach(MIMEText(text_summary, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Attach invoice as downloadable HTML file
            attachment = MIMEApplication(html_content.encode("utf-8"), Name=f"Invoice_{order_id}.html")
            attachment['Content-Disposition'] = f'attachment; filename="Invoice_{order_id}.html"'
            msg.attach(attachment)

            port = int(smtp_port)
            if port == 465:
                with smtplib.SMTP_SSL(smtp_server, port) as server:
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(sender_email, recipient_email, msg.as_string())
            else:
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(sender_email, recipient_email, msg.as_string())

            return True, f"Invoice email sent successfully to {recipient_email}."
        except Exception as err:
            return False, f"SMTP delivery failed ({err}). Invoice available for direct download below."

    # Simulation fallback if SMTP is not configured in .env
    return True, f"[Simulated Mode] Email invoice created for {recipient_email} (Configure SMTP in .env for live email)."


def send_sms_notification(order, recipient_phone):
    """Send SMS notification via Twilio if configured, else fallback to simulation."""
    if not recipient_phone or len(recipient_phone.strip()) < 5:
        return False, "Invalid phone number provided."

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")

    sms_body = generate_sms_text(order)

    # If Twilio is configured, attempt live SMS dispatch
    if account_sid and auth_token and from_phone:
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            data = {
                "From": from_phone,
                "To": recipient_phone,
                "Body": sms_body
            }
            res = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=10)
            if res.status_code in (200, 201):
                return True, f"SMS notification dispatched to {recipient_phone} via Twilio."
            return False, f"Twilio SMS failed (HTTP {res.status_code}: {res.text[:100]})."
        except Exception as err:
            return False, f"SMS dispatch error ({err})."

    # Simulation fallback if Twilio is not configured in .env
    return True, f"[Simulated Mode] SMS order confirmation dispatched to {recipient_phone}."
