"""
Email Utility for sending decryption keys
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_decryption_key_email(receiver_email, receiver_name, sender_name, decryption_key, message_id):
    """Send decryption key to receiver via email"""
    
    # Email configuration (should be loaded from config in production)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'testsam360@gmail.com'  # Change this
    MAIL_PASSWORD = 'rddwmbynfcbgpywf'  # Change this (use app password, not regular password)
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '🔐 SecureBinary - Decryption Key for Encrypted Image'
    msg['From'] = f'SecureBinary <{MAIL_USERNAME}>'
    msg['To'] = receiver_email
    
    # HTML email body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #00f2ff, #0072ff);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .key-box {{
                background-color: #050a10;
                border: 2px solid #00f2ff;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .key-text {{
                font-size: 32px;
                font-weight: bold;
                color: #00f2ff;
                letter-spacing: 8px;
                font-family: 'Courier New', monospace;
            }}
            .info {{
                background-color: #f8f9fa;
                padding: 15px;
                border-left: 4px solid #00f2ff;
                margin: 20px 0;
            }}
            .footer {{
                background-color: #050a10;
                color: #888;
                text-align: center;
                padding: 20px;
                font-size: 12px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(90deg, #00f2ff, #0072ff);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧬 SecureBinary</h1>
                <p style="margin: 10px 0 0 0;">DNA Image Cryptography System</p>
            </div>
            
            <div class="content">
                <h2 style="color: #333;">Hello {receiver_name},</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    You have received an encrypted image from <strong>{sender_name}</strong> 
                    through our secure DNA encryption system.
                </p>
                
                <div class="info">
                    <strong>📨 Message ID:</strong> #{message_id}<br>
                    <strong>📅 Sent on:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </div>
                
                <p style="color: #555;">
                    To decrypt and view the image, use the following 8-character DNA key:
                </p>
                
                <div class="key-box">
                    <div class="key-text">{decryption_key}</div>
                </div>
                
                <p style="color: #555; font-size: 14px; font-style: italic;">
                    ⚠️ Keep this key secure. Anyone with this key can decrypt your image.
                </p>
                
                <div style="text-align: center;">
                    <a href="http://localhost:5000/login" class="button">Login to Decrypt Image</a>
                </div>
                
                <p style="color: #888; font-size: 13px; margin-top: 30px;">
                    <strong>How to decrypt:</strong><br>
                    1. Login to your SecureBinary account<br>
                    2. Go to your dashboard<br>
                    3. Find the message from {sender_name}<br>
                    4. Enter the 8-character key above<br>
                    5. Download your decrypted image
                </p>
            </div>
            
            <div class="footer">
                <p>© 2026 SecureBinary | Advanced DNA Cryptography System</p>
                <p style="color: #555;">This is an automated message. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version (fallback)
    text_body = f"""
    SecureBinary - Decryption Key
    
    Hello {receiver_name},
    
    You have received an encrypted image from {sender_name}.
    
    Message ID: #{message_id}
    Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    
    Your 8-character DNA decryption key is:
    
    {decryption_key}
    
    To decrypt:
    1. Login at http://localhost:5000/login
    2. Find the message in your dashboard
    3. Enter the key above
    4. Download your image
    
    Keep this key secure!
    
    © 2026 SecureBinary
    """
    
    # Attach both versions
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    # Send email
    try:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False


def send_wrong_key_email(sender_email, sender_name, receiver_name, receiver_ip, receiver_username, message_id):
    """Send email to sender when receiver enters wrong decryption key"""
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'testsam360@gmail.com'  # Change this
    MAIL_PASSWORD = 'rddwmbynfcbgpywf'  # Change this (use app password, not regular password)
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '⚠️ SecureBinary - Failed Decryption Attempt on Your Message'
    msg['From'] = f'SecureBinary <{MAIL_USERNAME}>'
    msg['To'] = sender_email
    
    # HTML email body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .alert {{
                background-color: #fff3cd;
                border-left: 4px solid #ff6b6b;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .details-box {{
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .detail-row {{
                margin: 12px 0;
                color: #333;
            }}
            .detail-label {{
                font-weight: bold;
                color: #555;
                display: inline-block;
                width: 150px;
            }}
            .detail-value {{
                color: #333;
                font-family: 'Courier New', monospace;
                background-color: #fff;
                padding: 8px 12px;
                border-radius: 4px;
                display: inline-block;
            }}
            .footer {{
                background-color: #050a10;
                color: #888;
                text-align: center;
                padding: 20px;
                font-size: 12px;
            }}
            .warning-icon {{
                font-size: 48px;
                text-align: center;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚠️ SecureBinary</h1>
                <p style="margin: 10px 0 0 0;">Security Alert - Wrong Decryption Key Attempt</p>
            </div>
            
            <div class="content">
                <h2 style="color: #d32f2f;">Alert: Failed Decryption Attempt</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    A failed decryption attempt was made on your encrypted message (ID: <strong>#{message_id}</strong>).
                    The recipient entered an incorrect decryption key.
                </p>
                
                <div class="warning-icon">⚠️</div>
                
                <div class="alert">
                    <strong>📢 Security Notice:</strong> Someone attempted to decrypt your message with an incorrect key.
                    This could indicate an unauthorized access attempt. Review the details below.
                </div>
                
                <h3 style="color: #333; margin-top: 30px;">Failed Attempt Details:</h3>
                <div class="details-box">
                    <div class="detail-row">
                        <span class="detail-label">Message ID:</span>
                        <span class="detail-value">#{message_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Receiver Name:</span>
                        <span class="detail-value">{receiver_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Receiver Username:</span>
                        <span class="detail-value">@{receiver_username}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Receiver IP Address:</span>
                        <span class="detail-value">{receiver_ip}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Attempt Time:</span>
                        <span class="detail-value">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span>
                    </div>
                </div>
                
                <p style="color: #d32f2f; font-weight: bold; margin-top: 20px;">
                    ⚠️ What You Should Do:
                </p>
                <ul style="color: #555; line-height: 1.8;">
                    <li>If this was expected, ignore this message.</li>
                    <li>If this was unauthorized, contact the recipient immediately.</li>
                    <li>Consider resending your message to a trusted recipient only.</li>
                    <li>Review your account security settings.</li>
                </ul>
                
                <p style="color: #888; font-size: 13px; margin-top: 30px;">
                    <strong>SecureBinary System Information:</strong><br>
                    This email serves as a security log entry for your encrypted communication.
                    Each failed decryption attempt is recorded and logged for your protection.
                </p>
            </div>
            
            <div class="footer">
                <p>© 2026 SecureBinary | Advanced DNA Cryptography System</p>
                <p style="color: #555;">This is an automated security notification. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_body = f"""
    SecureBinary - Failed Decryption Alert
    
    A failed decryption attempt was made on your message.
    
    Message ID: #{message_id}
    Receiver Name: {receiver_name}
    Receiver Username: @{receiver_username}
    Receiver IP Address: {receiver_ip}
    Attempt Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    
    Someone attempted to decrypt your message with an incorrect key.
    If this was not expected, please contact the recipient or contact support.
    
    © 2026 SecureBinary
    """
    
    # Attach both versions
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    # Send email
    try:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Failed decryption alert email failed: {e}")
        return False


def send_test_email():
    """Test email function"""
    return send_decryption_key_email(
        receiver_email='test@example.com',
        receiver_name='Test User',
        sender_name='Alice',
        decryption_key='ATGCATGC',
        message_id=1
    )
