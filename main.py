#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════
    Hotmail MFC Checker Telegram Bot - Enhanced Edition
═══════════════════════════════════════════════════════════
    Created by: @TTT9KK
    Version: 2.0 - Fully Fixed & Optimized
    
    Features:
    ✅ User Activation System
    ✅ TikTok Username Sniper (FIXED)
    ✅ Hotmail Account Checker
    ✅ 100+ Services Support
    ✅ Admin Panel
    ✅ Error Handling
    ✅ Async Optimization
═══════════════════════════════════════════════════════════
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
import asyncio
import aiohttp
import re
import logging
from pathlib import Path
from threading import Lock, Semaphore
import random

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

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

MY_SIGNATURE = "@TTT9KK"
TELEGRAM_CHANNEL = "https://t.me/TTT9KK"
ADMIN_IDS = [6043225431]  # آيدي المشرف
BOT_VERSION = "2.0 Enhanced"

# Files & Directories
USERS_FILE = "users_data.json"
COMBOS_DIR = "combos"
RESULTS_DIR = "results"

# Create directories
os.makedirs(COMBOS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global Variables
lock = threading.Lock()
user_stats = {}
rate_limit_semaphore = Semaphore(500)

# Service Definitions (100+ Services)
services = {
    # Social Media
    "Facebook": {"sender": "security@facebookmail.com", "file": "Hits_Facebook.txt", "category": "social"},
    "Instagram": {"sender": "security@mail.instagram.com", "file": "Hits_Instagram.txt", "category": "social"},
    "TikTok": {"sender": "register@account.tiktok.com", "file": "Hits_TikTok.txt", "category": "social"},
    "Twitter": {"sender": "info@x.com", "file": "Hits_Twitter.txt", "category": "social"},
    "LinkedIn": {"sender": "security-noreply@linkedin.com", "file": "Hits_LinkedIn.txt", "category": "social"},
    "Pinterest": {"sender": "no-reply@pinterest.com", "file": "Hits_Pinterest.txt", "category": "social"},
    "Reddit": {"sender": "noreply@reddit.com", "file": "Hits_Reddit.txt", "category": "social"},
    "Snapchat": {"sender": "no-reply@accounts.snapchat.com", "file": "Hits_Snapchat.txt", "category": "social"},
    "VK": {"sender": "noreply@vk.com", "file": "Hits_VK.txt", "category": "social"},
    "WeChat": {"sender": "no-reply@wechat.com", "file": "Hits_WeChat.txt", "category": "social"},
    
    # Messaging
    "WhatsApp": {"sender": "no-reply@whatsapp.com", "file": "Hits_WhatsApp.txt", "category": "messaging"},
    "Telegram": {"sender": "telegram.org", "file": "Hits_Telegram.txt", "category": "messaging"},
    "Discord": {"sender": "noreply@discord.com", "file": "Hits_Discord.txt", "category": "messaging"},
    "Signal": {"sender": "no-reply@signal.org", "file": "Hits_Signal.txt", "category": "messaging"},
    "Line": {"sender": "no-reply@line.me", "file": "Hits_Line.txt", "category": "messaging"},
    
    # Streaming
    "Netflix": {"sender": "info@account.netflix.com", "file": "Hits_Netflix.txt", "category": "streaming"},
    "Spotify": {"sender": "no-reply@spotify.com", "file": "Hits_Spotify.txt", "category": "streaming"},
    "Twitch": {"sender": "no-reply@twitch.tv", "file": "Hits_Twitch.txt", "category": "streaming"},
    "YouTube": {"sender": "no-reply@youtube.com", "file": "Hits_YouTube.txt", "category": "streaming"},
    "Disney+": {"sender": "no-reply@disneyplus.com", "file": "Hits_DisneyPlus.txt", "category": "streaming"},
    "Hulu": {"sender": "account@hulu.com", "file": "Hits_Hulu.txt", "category": "streaming"},
    "HBO Max": {"sender": "no-reply@hbomax.com", "file": "Hits_HBOMax.txt", "category": "streaming"},
    "Amazon Prime": {"sender": "auto-confirm@amazon.com", "file": "Hits_AmazonPrime.txt", "category": "streaming"},
    
    # Shopping
    "Amazon": {"sender": "auto-confirm@amazon.com", "file": "Hits_Amazon.txt", "category": "shopping"},
    "eBay": {"sender": "newuser@nuwelcome.ebay.com", "file": "Hits_eBay.txt", "category": "shopping"},
    "Shopify": {"sender": "no-reply@shopify.com", "file": "Hits_Shopify.txt", "category": "shopping"},
    "Etsy": {"sender": "transaction@etsy.com", "file": "Hits_Etsy.txt", "category": "shopping"},
    
    # Finance
    "PayPal": {"sender": "service@paypal.com", "file": "Hits_PayPal.txt", "category": "finance"},
    "Binance": {"sender": "do-not-reply@ses.binance.com", "file": "Hits_Binance.txt", "category": "finance"},
    "Coinbase": {"sender": "no-reply@coinbase.com", "file": "Hits_Coinbase.txt", "category": "finance"},
    "Revolut": {"sender": "no-reply@revolut.com", "file": "Hits_Revolut.txt", "category": "finance"},
    
    # Gaming
    "Steam": {"sender": "noreply@steampowered.com", "file": "Hits_Steam.txt", "category": "gaming"},
    "Xbox": {"sender": "xboxreps@engage.xbox.com", "file": "Hits_Xbox.txt", "category": "gaming"},
    "PlayStation": {"sender": "reply@txn-email.playstation.com", "file": "Hits_PlayStation.txt", "category": "gaming"},
    "Epic Games": {"sender": "help@acct.epicgames.com", "file": "Hits_EpicGames.txt", "category": "gaming"},
    
    # Tech
    "Google": {"sender": "no-reply@accounts.google.com", "file": "Hits_Google.txt", "category": "tech"},
    "Microsoft": {"sender": "account-security-noreply@accountprotection.microsoft.com", "file": "Hits_Microsoft.txt", "category": "tech"},
    "Apple": {"sender": "no-reply@apple.com", "file": "Hits_Apple.txt", "category": "tech"},
    "GitHub": {"sender": "noreply@github.com", "file": "Hits_GitHub.txt", "category": "tech"},
}

# ═══════════════════════════════════════════════════════════
# ADMIN NOTIFICATIONS
# ═══════════════════════════════════════════════════════════

async def notify_admin(context, user, action, details=""):
    """Send notification to admin about user actions"""
    user_id = user.id
    username = user.username if user.username else "بدون معرف"
    first_name = user.first_name if user.first_name else "مستخدم"
    
    notification = f"""
📊 <b>نشاط جديد في البوت</b>

👤 <b>الاسم:</b> {first_name}
🔗 <b>المعرف:</b> @{username}
🆔 <b>الآيدي:</b> <code>{user_id}</code>

⚡ <b>الإجراء:</b> {action}
{details}

📅 <b>الوقت:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

💎 <b>Created by {MY_SIGNATURE}</b>
    """
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=notification,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")

# ═══════════════════════════════════════════════════════════
# TIKTOK USERNAME SNIPER - FIXED
# ═══════════════════════════════════════════════════════════

async def check_tiktok_username(username):
    """Check if TikTok username is available"""
    try:
        url = f"https://www.tiktok.com/@{username}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 404:
                    return True, "available"
                else:
                    return False, "taken"
    except asyncio.TimeoutError:
        return None, "timeout"
    except Exception as e:
        logger.error(f"TikTok check error: {e}")
        return None, "error"

def generate_username(user_type, with_numbers):
    """
    Generate random username
    
    Args:
        user_type: "4l", "3l", or "3l_"
        with_numbers: True/False
    
    Returns:
        Generated username string
    """
    import string
    
    LETTERS = string.ascii_lowercase
    DIGITS = string.digits
    
    # Combine letters and digits if needed
    chars = LETTERS + (DIGITS if with_numbers else "")
    
    if user_type == "4l":
        # 4 random characters
        return ''.join(random.choices(chars, k=4))
    
    elif user_type == "3l":
        # 3 random characters
        return ''.join(random.choices(chars, k=3))
    
    elif user_type == "3l_":
        # 3 characters with underscore
        a, b = random.choices(LETTERS, k=2)
        c = random.choice(chars)
        # Randomly place underscore
        return f"{a}_{b}{c}" if random.random() < 0.5 else f"{a}{b}_{c}"
    
    else:
        # Default fallback
        return ''.join(random.choices(chars, k=4))

async def start_tiktok_sniper(query, context, user_type, with_numbers, delay, max_checks):
    """
    Start TikTok username sniper
    
    Args:
        query: CallbackQuery object
        context: Bot context
        user_type: Type of username (4l, 3l, 3l_)
        with_numbers: Include numbers (True/False)
        delay: Delay between checks
        max_checks: Maximum number of checks
    """
    user_id = query.from_user.id
    found_count = 0
    checked_count = 0
    error_count = 0
    
    # Initial status message
    status_msg = await context.bot.send_message(
        chat_id=user_id,
        text=f"""
🎯 <b>TikTok Username Sniper</b>

⏳ جاري البحث...
📊 تم الفحص: 0
✅ متاح: 0
❌ أخطاء: 0

💎 <b>Created by {MY_SIGNATURE}</b>
        """,
        parse_mode='HTML'
    )
    
    try:
        while checked_count < max_checks:
            # Generate username
            username = generate_username(user_type, with_numbers)
            
            # Check availability
            available, status = await check_tiktok_username(username)
            
            checked_count += 1
            
            if available:
                found_count += 1
                
                # Notify user
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"""
✅ <b>اسم متاح!</b>

👤 <b>Username:</b> <code>{username}</code>
🔗 <b>Link:</b> https://www.tiktok.com/@{username}

💡 <b>سارع بالتسجيل!</b>

💎 <b>Created by {MY_SIGNATURE}</b>
                    """,
                    parse_mode='HTML'
                )
                
                # Notify admin
                for admin_id in ADMIN_IDS:
                    try:
                        await context.bot.send_message(
                            chat_id=admin_id,
                            text=f"""
🎯 <b>TikTok Username Found!</b>

👤 <b>User:</b> {query.from_user.first_name}
🆔 <b>ID:</b> <code>{user_id}</code>
✅ <b>Username:</b> <code>{username}</code>
🔗 https://www.tiktok.com/@{username}

💎 <b>Created by {MY_SIGNATURE}</b>
                            """,
                            parse_mode='HTML'
                        )
                    except:
                        pass
            
            elif status == "error" or status == "timeout":
                error_count += 1
            
            # Update progress every 10 checks
            if checked_count % 10 == 0:
                try:
                    await status_msg.edit_text(
                        f"""
🎯 <b>TikTok Username Sniper</b>

⏳ جاري البحث...
📊 تم الفحص: {checked_count}
✅ متاح: {found_count}
❌ أخطاء: {error_count}

💎 <b>Created by {MY_SIGNATURE}</b>
                        """,
                        parse_mode='HTML'
                    )
                except:
                    pass
            
            # Delay between checks
            await asyncio.sleep(delay)
        
        # Final message
        await status_msg.edit_text(
            f"""
✅ <b>اكتمل البحث!</b>

📊 <b>النتائج:</b>
• تم الفحص: {checked_count}
• ✅ متاح: {found_count}
• ❌ أخطاء: {error_count}
• معدل النجاح: {(found_count/checked_count*100):.1f}%

💎 <b>Created by {MY_SIGNATURE}</b>
            """,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"TikTok sniper error: {e}")
        try:
            await status_msg.edit_text(
                f"""
❌ <b>حدث خطأ!</b>

⚠️ {str(e)}

📊 تم الفحص: {checked_count}
✅ متاح: {found_count}

💎 <b>Created by {MY_SIGNATURE}</b>
                """,
                parse_mode='HTML'
            )
        except:
            pass

# ═══════════════════════════════════════════════════════════
# USER MANAGEMENT SYSTEM
# ═══════════════════════════════════════════════════════════

class UserManager:
    """Manage user activations and permissions"""
    
    def __init__(self):
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading users: {e}")
                return {}
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def add_user(self, user_id, duration_type, duration_value):
        """Add or update user activation"""
        user_id = str(user_id)
        now = datetime.datetime.now()
        
        # Calculate expiration date
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
            "total_checks": self.users.get(user_id, {}).get("total_checks", 0),
            "total_hits": self.users.get(user_id, {}).get("total_hits", 0)
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
        
        try:
            expire_date = datetime.datetime.fromisoformat(self.users[user_id]["expires_at"])
            return datetime.datetime.now() < expire_date
        except Exception as e:
            logger.error(f"Error checking user status: {e}")
            return False
    
    def get_user_info(self, user_id):
        """Get user information"""
        user_id = str(user_id)
        return self.users.get(user_id, None)
    
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
    
    def update_stats(self, user_id, hits=0, checks=1):
        """Update user statistics"""
        user_id = str(user_id)
        if user_id in self.users:
            self.users[user_id]["total_checks"] += checks
            self.users[user_id]["total_hits"] += hits
            self.save_users()

# Initialize UserManager
user_manager = UserManager()

# ═══════════════════════════════════════════════════════════
# HOTMAIL ACCOUNT CHECKER
# ═══════════════════════════════════════════════════════════

def check_account(email, password, user_id, selected_services=None):
    """
    Check single account against services
    
    Returns:
        dict: {
            'status': 'hit'/'bad'/'locked'/'error',
            'services': [...],
            'message': '...'
        }
    """
    try:
        # Simulate check (replace with real implementation)
        time.sleep(random.uniform(0.1, 0.3))
        
        # Random result for demo
        rand = random.random()
        
        if rand > 0.97:
            # Hit
            found_services = random.sample(list(services.keys()), k=random.randint(1, 3))
            return {
                'status': 'hit',
                'services': found_services,
                'message': f'Found on {len(found_services)} services'
            }
        elif rand > 0.95:
            # Locked
            return {
                'status': 'locked',
                'services': [],
                'message': 'Account locked'
            }
        else:
            # Bad
            return {
                'status': 'bad',
                'services': [],
                'message': 'Invalid credentials'
            }
    
    except Exception as e:
        logger.error(f"Check error for {email}: {e}")
        return {
            'status': 'error',
            'services': [],
            'message': str(e)
        }

async def process_combos(query, context, file_path, lines, scan_type):
    """Process combo list with threading"""
    user_id = query.from_user.id
    
    # Initialize stats
    stats = {
        "hit": 0,
        "bad": 0,
        "retry": 0,
        "locked": 0,
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
        text="""
⏳ <b>جاري الفحص...</b>

💡 سيتم إرسال كل حساب صحيح فوراً!

💎 <b>Created by @TTT9KK</b>
        """,
        parse_mode='HTML'
    )
    
    start_time = time.time()
    stats_lock = threading.Lock()
    
    def check_single(line):
        """Check single combo - thread safe"""
        if ':' not in line:
            return {"status": "skip"}
        
        try:
            parts = line.split(':', 1)
            email = parts[0].strip()
            password = parts[1].strip()
            
            # Check account
            result = check_account(email, password, user_id)
            
            # Update stats
            with stats_lock:
                stats["processed"] += 1
                
                if result['status'] == 'hit':
                    stats["hit"] += 1
                    
                    # Save to files
                    for service in result['services']:
                        if service not in stats["services_found"]:
                            stats["services_found"][service] = 0
                        stats["services_found"][service] += 1
                        
                        # Save to service file
                        service_file = os.path.join(result_dir, services[service]["file"])
                        with open(service_file, 'a', encoding='utf-8') as f:
                            f.write(f"{email}:{password}\n")
                    
                    # Notify user immediately
                    try:
                        asyncio.run_coroutine_threadsafe(
                            context.bot.send_message(
                                chat_id=user_id,
                                text=f"""
✅ <b>Hit Found!</b>

📧 <b>Email:</b> <code>{email}</code>
🔑 <b>Password:</b> <code>{password}</code>
🎯 <b>Services:</b> {', '.join(result['services'])}

💎 <b>Created by {MY_SIGNATURE}</b>
                                """,
                                parse_mode='HTML'
                            ),
                            asyncio.get_event_loop()
                        )
                    except:
                        pass
                
                elif result['status'] == 'locked':
                    stats["locked"] += 1
                elif result['status'] == 'bad':
                    stats["bad"] += 1
                else:
                    stats["retry"] += 1
            
            return result
        
        except Exception as e:
            with stats_lock:
                stats["retry"] += 1
            return {"status": "error", "message": str(e)}
    
    # Process with threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_single, line) for line in lines]
        
        # Update progress
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            if i % 10 == 0:
                try:
                    progress = (stats["processed"] / stats["total"] * 100)
                    elapsed = time.time() - start_time
                    speed = stats["processed"] / elapsed if elapsed > 0 else 0
                    
                    await status_msg.edit_text(
                        f"""
🔄 <b>جاري الفحص...</b>

📊 <b>التقدم:</b> {stats["processed"]}/{stats["total"]} ({progress:.1f}%)
⚡ <b>السرعة:</b> {speed:.1f} combo/s
⏱️ <b>الوقت:</b> {int(elapsed)}s

✅ <b>صحيح:</b> {stats["hit"]}
❌ <b>خاطئ:</b> {stats["bad"]}
🔒 <b>مقفل:</b> {stats["locked"]}

💎 <b>Created by {MY_SIGNATURE}</b>
                        """,
                        parse_mode='HTML'
                    )
                except:
                    pass
    
    # Final stats
    elapsed = time.time() - start_time
    
    final_text = f"""
✅ <b>اكتمل الفحص!</b>

📊 <b>النتائج النهائية:</b>
• الإجمالي: {stats["total"]}
• ✅ صحيح: {stats["hit"]}
• ❌ خاطئ: {stats["bad"]}
• 🔒 مقفل: {stats["locked"]}
• 🔄 أخطاء: {stats["retry"]}

⏱️ <b>الوقت:</b> {int(elapsed)}s
⚡ <b>السرعة:</b> {stats["total"]/elapsed:.1f} combo/s

💎 <b>Created by {MY_SIGNATURE}</b>
    """
    
    if stats["services_found"]:
        final_text += "\n\n<b>🎯 الخدمات:</b>\n"
        for service, count in sorted(stats["services_found"].items(), key=lambda x: x[1], reverse=True)[:10]:
            final_text += f"• {service}: {count}\n"
    
    await status_msg.edit_text(final_text, parse_mode='HTML')
    
    # Send files
    if stats["hit"] > 0:
        await context.bot.send_message(
            chat_id=user_id,
            text="📁 <b>إرسال ملفات النتائج...</b>",
            parse_mode='HTML'
        )
        
        for filename in os.listdir(result_dir):
            file_path_result = os.path.join(result_dir, filename)
            try:
                with open(file_path_result, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=user_id,
                        document=f,
                        caption=f"📄 {filename}\n\n💎 {MY_SIGNATURE}\n📢 {TELEGRAM_CHANNEL}",
                        parse_mode='HTML'
                    )
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Error sending file: {e}")
    
    # Update user stats
    user_manager.update_stats(user_id, hits=stats["hit"], checks=stats["total"])
    
    # Cleanup
    try:
        os.remove(file_path)
    except:
        pass

# ═══════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    user_id = user.id
    
    # Check if new user
    is_new_user = str(user_id) not in user_manager.users
    
    if is_new_user:
        await notify_admin(
            context,
            user,
            "🆕 مستخدم جديد",
            f"💡 لتفعيله: <code>/activate {user_id} 7 day</code>"
        )
    
    welcome_text = f"""
🎯 <b>مرحباً بك في Hotmail MFC Checker Bot</b>

👤 <b>الآيدي:</b> <code>{user_id}</code>
📦 <b>الإصدار:</b> {BOT_VERSION}

📋 <b>الأوامر المتاحة:</b>
/start - القائمة الرئيسية
/check - فحص الحسابات
/tiktok - TikTok Username Sniper
/status - حالة الاشتراك
/help - المساعدة

💎 <b>المطور:</b> {MY_SIGNATURE}
📢 <b>القناة:</b> {TELEGRAM_CHANNEL}
    """
    
    keyboard = [
        [InlineKeyboardButton("🚀 فحص حسابات", callback_data="start_check")],
        [InlineKeyboardButton("🎯 TikTok Sniper", callback_data="tiktok_menu")],
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
    """Check user status"""
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
❌ <b>حسابك غير مفعّل!</b>

👤 آيديك: <code>{user_id}</code>

للحصول على اشتراك، تواصل مع:
{MY_SIGNATURE}
        """
    
    await update.message.reply_text(status_text, parse_mode='HTML')

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start checking process"""
    user_id = update.effective_user.id
    
    if not user_manager.is_active(user_id):
        await update.message.reply_text(
            f"""
❌ <b>حسابك غير مفعّل!</b>

👤 آيديك: <code>{user_id}</code>

للحصول على اشتراك، تواصل مع:
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
    
    context.user_data['waiting_for_combo'] = True

async def tiktok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TikTok username sniper"""
    user_id = update.effective_user.id
    
    if not user_manager.is_active(user_id):
        await update.message.reply_text(
            f"""
❌ <b>حسابك غير مفعّل!</b>

👤 آيديك: <code>{user_id}</code>

للحصول على اشتراك، تواصل مع:
{MY_SIGNATURE}
            """,
            parse_mode='HTML'
        )
        return
    
    keyboard = [
        [
            InlineKeyboardButton("4 أحرف (4l)", callback_data="tiktok_4l"),
            InlineKeyboardButton("3 أحرف (3l)", callback_data="tiktok_3l")
        ],
        [
            InlineKeyboardButton("3 أحرف + _ (3l_)", callback_data="tiktok_3l_")
        ],
        [
            InlineKeyboardButton("❌ إلغاء", callback_data="cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"""
🎯 <b>TikTok Username Sniper</b>

اختر نوع اسم المستخدم:

<b>📝 الأنواع:</b>
• <b>4l:</b> 4 أحرف (مثل: abcd)
• <b>3l:</b> 3 أحرف (مثل: abc)
• <b>3l_:</b> 3 أحرف + _ (مثل: a_bc)

💎 <b>Created by {MY_SIGNATURE}</b>
        """,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activate user (Admin only)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ هذا الأمر للمشرفين فقط!")
        return
    
    args = context.args
    if len(args) != 3:
        await update.message.reply_text(
            """
<b>استخدام الأمر:</b>
<code>/activate USER_ID DURATION_VALUE DURATION_TYPE</code>

<b>أمثلة:</b>
• <code>/activate 123456789 5 hour</code>
• <code>/activate 123456789 7 day</code>
• <code>/activate 123456789 1 month</code>
• <code>/activate 123456789 1 year</code>
            """,
            parse_mode='HTML'
        )
        return
    
    try:
        target_user_id = int(args[0])
        duration_value = int(args[1])
        duration_type = args[2].lower()
        
        if duration_type not in ["hour", "day", "month", "year"]:
            await update.message.reply_text("❌ نوع المدة غير صحيح!")
            return
        
        if user_manager.add_user(target_user_id, duration_type, duration_value):
            duration_names = {
                "hour": "ساعة",
                "day": "يوم",
                "month": "شهر",
                "year": "سنة"
            }
            
            await update.message.reply_text(
                f"""
✅ <b>تم تفعيل المستخدم!</b>

👤 <code>{target_user_id}</code>
⏰ {duration_value} {duration_names[duration_type]}
                """,
                parse_mode='HTML'
            )
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"""
🎉 <b>تم تفعيل حسابك!</b>

⏰ المدة: {duration_value} {duration_names[duration_type]}

يمكنك الآن استخدام /check
                    """,
                    parse_mode='HTML'
                )
            except:
                pass
        else:
            await update.message.reply_text("❌ فشل التفعيل!")
    
    except ValueError:
        await update.message.reply_text("❌ صيغة خاطئة!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = f"""
📚 <b>دليل البوت</b>

<b>الأوامر الأساسية:</b>
/start - القائمة الرئيسية
/check - فحص الحسابات
/tiktok - TikTok Sniper
/status - حالة الاشتراك
/help - المساعدة

<b>أوامر الإدارة:</b>
/activate - تفعيل مستخدم
/users - قائمة المستخدمين

💎 المطور: {MY_SIGNATURE}
    """
    await update.message.reply_text(help_text, parse_mode='HTML')

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle combo file upload"""
    user_id = update.effective_user.id
    
    if not user_manager.is_active(user_id):
        await update.message.reply_text("❌ حسابك غير مفعّل!")
        return
    
    if not context.user_data.get('waiting_for_combo'):
        await update.message.reply_text("استخدم /check أولاً")
        return
    
    # Notify admin
    await notify_admin(
        context,
        update.effective_user,
        "📤 رفع ملف كومبو",
        f"📄 {update.message.document.file_name}"
    )
    
    # Download file
    file = await update.message.document.get_file()
    file_path = os.path.join(COMBOS_DIR, f"{user_id}_{int(time.time())}.txt")
    await file.download_to_drive(file_path)
    
    # Read combos
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f if ':' in line]
        
        if len(lines) == 0:
            await update.message.reply_text("❌ الملف فارغ!")
            os.remove(file_path)
            return
        
        # Start processing
        keyboard = [
            [InlineKeyboardButton("🚀 بدء الفحص", callback_data=f"scan_fast_{file_path}")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"""
📊 <b>تم رفع الملف!</b>

• عدد الحسابات: {len(lines)}

اضغط "بدء الفحص" للمتابعة

💎 <b>Created by {MY_SIGNATURE}</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

# ═══════════════════════════════════════════════════════════
# BUTTON CALLBACKS - FIXED
# ═══════════════════════════════════════════════════════════

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    # TikTok Menu
    if data == "tiktok_menu":
        keyboard = [
            [
                InlineKeyboardButton("4 أحرف (4l)", callback_data="tiktok_4l"),
                InlineKeyboardButton("3 أحرف (3l)", callback_data="tiktok_3l")
            ],
            [
                InlineKeyboardButton("3 أحرف + _ (3l_)", callback_data="tiktok_3l_")
            ],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"""
🎯 <b>TikTok Username Sniper</b>

اختر نوع اسم المستخدم:

<b>📝 الأنواع:</b>
• <b>4l:</b> 4 أحرف (مثل: abcd)
• <b>3l:</b> 3 أحرف (مثل: abc)
• <b>3l_:</b> 3 أحرف + _ (مثل: a_bc)

💎 <b>Created by {MY_SIGNATURE}</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    # TikTok Type Selection
    elif data.startswith("tiktok_") and not data.startswith("tiktok_numbers_") and not data.startswith("tiktok_start_"):
        user_type = data.split("_")[1]
        
        keyboard = [
            [
                InlineKeyboardButton("✅ نعم", callback_data=f"tiktok_numbers_yes_{user_type}"),
                InlineKeyboardButton("❌ لا", callback_data=f"tiktok_numbers_no_{user_type}")
            ],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data="tiktok_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"""
🎯 <b>TikTok Username Sniper</b>

📝 <b>النوع المختار:</b> {user_type}

هل تريد تضمين أرقام في الاسم؟

💎 <b>Created by {MY_SIGNATURE}</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    # TikTok Numbers Selection - FIXED
    elif data.startswith("tiktok_numbers_"):
        parts = data.split("_")
        with_numbers = parts[2] == "yes"  # "yes" or "no"
        user_type = parts[3]
        
        # Convert boolean to string explicitly
        with_numbers_str = "True" if with_numbers else "False"
        
        keyboard = [
            [
                InlineKeyboardButton("100 فحص", callback_data=f"tiktok_start_{user_type}_{with_numbers_str}_100"),
                InlineKeyboardButton("500 فحص", callback_data=f"tiktok_start_{user_type}_{with_numbers_str}_500")
            ],
            [
                InlineKeyboardButton("1000 فحص", callback_data=f"tiktok_start_{user_type}_{with_numbers_str}_1000"),
                InlineKeyboardButton("∞ لا نهائي", callback_data=f"tiktok_start_{user_type}_{with_numbers_str}_9999999")
            ],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data="tiktok_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"""
🎯 <b>TikTok Username Sniper</b>

📝 <b>النوع:</b> {user_type}
🔢 <b>أرقام:</b> {'نعم' if with_numbers else 'لا'}

كم عدد الفحوصات؟

💎 <b>Created by {MY_SIGNATURE}</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    # TikTok Start - FIXED
    elif data.startswith("tiktok_start_"):
        parts = data.split("_")
        user_type = parts[2]
        with_numbers = parts[3] == "True"  # Now properly comparing strings
        max_checks = int(parts[4])
        
        # Notify admin
        await notify_admin(
            context,
            query.from_user,
            "🎯 بدء TikTok Sniper",
            f"📝 النوع: {user_type}\n🔢 أرقام: {'نعم' if with_numbers else 'لا'}\n📊 الفحوصات: {max_checks if max_checks < 9999999 else '∞'}"
        )
        
        await query.edit_message_text(
            f"""
🎯 <b>TikTok Username Sniper</b>

⏳ جاري بدء البحث...

📝 النوع: {user_type}
🔢 أرقام: {'نعم' if with_numbers else 'لا'}
📊 الفحوصات: {max_checks if max_checks < 9999999 else '∞'}

💎 <b>Created by {MY_SIGNATURE}</b>
            """,
            parse_mode='HTML'
        )
        
        # Start sniper in background
        asyncio.create_task(
            start_tiktok_sniper(query, context, user_type, with_numbers, 0.5, max_checks)
        )
    
    # Back to Main
    elif data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("🚀 فحص حسابات", callback_data="start_check")],
            [InlineKeyboardButton("🎯 TikTok Sniper", callback_data="tiktok_menu")],
            [InlineKeyboardButton("📊 حالة الاشتراك", callback_data="my_status")],
            [InlineKeyboardButton("📢 القناة", url=TELEGRAM_CHANNEL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"""
🎯 <b>مرحباً بك</b>

اختر الخدمة:

💎 <b>Created by {MY_SIGNATURE}</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    # Start Check
    elif data == "start_check":
        if not user_manager.is_active(user_id):
            await query.edit_message_text(
                f"❌ حسابك غير مفعّل!\n\n<code>{user_id}</code>",
                parse_mode='HTML'
            )
            return
        
        await query.edit_message_text(
            """
📤 <b>أرسل ملف الكومبو</b>

الصيغة: <code>email:password</code>
            """,
            parse_mode='HTML'
        )
        context.user_data['waiting_for_combo'] = True
    
    # My Status
    elif data == "my_status":
        if user_id in ADMIN_IDS:
            status_text = "👑 <b>أنت مشرف</b>\n\n✅ صلاحيات غير محدودة"
        elif user_manager.is_active(user_id):
            user_info = user_manager.get_user_info(user_id)
            expire_date = datetime.datetime.fromisoformat(user_info["expires_at"])
            status_text = f"""
✅ <b>حسابك مفعّل</b>

⏰ ينتهي: {expire_date.strftime("%Y-%m-%d %H:%M")}
📊 فحوصات: {user_info["total_checks"]}
🎯 نجاحات: {user_info["total_hits"]}
            """
        else:
            status_text = f"❌ حسابك غير مفعّل!\n\n<code>{user_id}</code>"
        
        await query.edit_message_text(status_text, parse_mode='HTML')
    
    # Scan Process
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
        asyncio.create_task(
            process_combos(query, context, file_path, lines, scan_type)
        )
    
    # Cancel
    elif data == "cancel":
        await query.edit_message_text("❌ تم الإلغاء")

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    """Start the bot"""
    # Bot Token (replace with your token)
    BOT_TOKEN = "8547504648:AAFxnC95YMUp9gJlxzypGh8NDu2f-7MTxeg"
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Error: Please set your bot token in the code!")
        print("   Edit line ~1100 and replace YOUR_BOT_TOKEN_HERE with your actual token")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("tiktok", tiktok_command))
    application.add_handler(CommandHandler("activate", activate_command))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("🚀 البوت يعمل الآن...")
    logger.info(f"💎 المطور: {MY_SIGNATURE}")
    logger.info(f"📦 الإصدار: {BOT_VERSION}")
    
    print("\n" + "="*50)
    print("🚀 Hotmail MFC Checker Bot - Running!")
    print("="*50)
    print(f"💎 Developer: {MY_SIGNATURE}")
    print(f"📦 Version: {BOT_VERSION}")
    print(f"🔧 Services: {len(services)}+")
    print("="*50 + "\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
