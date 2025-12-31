#!/usr/bin/env python3
# minah.py - Dengan Nix environment fix
import sys
import os

# ==================== NIX/REPLIT ENVIRONMENT FIX ====================
# Add user site-packages directory
user_site = None
try:
    import site
    user_site = site.getusersitepackages()
    if user_site and os.path.exists(user_site):
        sys.path.insert(0, user_site)
        print(f"🔧 Added user site: {user_site}")
except:
    pass

# Common Replit paths
replit_paths = [
    '/home/runner/.local/lib/python3.9/site-packages',
    '/home/runner/.local/lib/python3.8/site-packages',
    os.path.expanduser('~/.local/lib/python3.9/site-packages'),
    os.path.expanduser('~/.local/lib/python3.8/site-packages'),
    '/tmp/pip-target/lib/python3.9/site-packages',
]

for path in replit_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
        print(f"🔧 Added path: {path}")

# Try to import requests
try:
    import requests
    print(f"✅ requests: {requests.__version__}")
except ImportError:
    print("❌ requests not found. Attempting to install...")

    # Try to install to temp directory
    import subprocess
    import tempfile

    # Create temp directory for installation
    temp_dir = tempfile.mkdtemp(prefix='pip_')

    try:
        # Install to temp directory
        cmd = [sys.executable, "-m", "pip", "install", "--target", temp_dir, "requests"]
        print(f"💻 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            sys.path.insert(0, temp_dir)
            import requests
            print(f"✅ requests installed to temp directory: {temp_dir}")
        else:
            print(f"⚠️  pip install failed: {result.stderr[:200]}")

            # Fallback: Use urllib
            print("🔄 Falling back to urllib...")
            import urllib.request
            import json as json_module

            class DummyRequests:
                @staticmethod
                def get(url, timeout=10):
                    try:
                        req = urllib.request.Request(url)
                        with urllib.request.urlopen(req, timeout=timeout) as response:
                            text = response.read().decode('utf-8')
                            return type('Response', (), {
                                'status_code': response.status,
                                'text': text,
                                'json': lambda: json_module.loads(text) if text.strip() else {}
                            })()
                    except Exception as e:
                        print(f"⚠️  HTTP request failed: {e}")
                        return type('Response', (), {
                            'status_code': 500,
                            'text': '{}',
                            'json': lambda: {}
                        })()

            requests = DummyRequests
            print("✅ Created requests fallback using urllib")

    except Exception as e:
        print(f"❌ Installation failed: {e}")
        # Create dummy requests
        requests = None

# Now continue with other imports
# ==================== REST OF YOUR BOT CODE ====================
import socket
import time
import random
import re
import threading
import requests
from collections import deque
from datetime import datetime
import sqlite3
import os

class MinahBot:
    def __init__(self):
        # ==================== IRC CONFIG ====================
        self.server = "irc.kampungchat.org"
        self.port = 6668
        self.nick = "minah"
        self.username = "NPC"
        self.realname = "꧁✿🌸Hidup Anugerah Terindah🌸✿꧂"


        # Channels list
        self.channels = ['#amboi','#ace', '#zumba', '#alamanda', '#bro', '#desa', '#purple', '#kampung']

        # AI API Configuration (GROQ)
        self.api_key = "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"  # ⭐ GANTI DENGAN API KEY ANDA
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        # ==================== PRIVATE CHAT SYSTEM ====================
        self.private_chat_enabled = True
        self.invite_chance = 25  # 25% untuk invite system
        self.private_cooldown = 5  # 5 seconds
        self.last_private_reply = 0
        self.private_conversations = {}
        self.last_invite_sent = {}
        self.invite_cooldown = 300  # 5 minutes

        # ==================== FOCUS SYSTEM ====================
        self.user_focus = {}
        self.focus_duration = 300  # 5 minutes
        self.user_mentions = {}
        self.mentions_threshold = 3

        # ==================== PER-CHANNEL CONTEXT ====================
        self.message_buffers = {}
        self.last_buffer_process = {}

        # ==================== BOT STATES ====================
        self.silent_mode = False
        self.silent_until = 0

        # ==================== MESSAGE QUEUE SYSTEM ====================
        self.message_queue = deque()
        self.is_sending = False
        self.last_send_time = 0
        self.min_delay = 3
        self.max_queue_size = 15

        # ==================== AI COOLDOWN ====================
        self.last_ai_time = 0
        self.ai_cooldown = 3

        # ==================== STRICT TIMING CONTROLS ====================
        self.last_ai_time = 0
        self.ai_cooldown = 3  # ⭐⭐ 3 SAAT MINIMUM antara AI calls GLOBAL
        self.channel_ai_cooldown = 2  # 2 saat antara AI calls per channel

        # Channel-specific tracking
        self.channel_last_ai = {}  # {channel: last_ai_time}

        # Thinking time minimums
        self.min_thinking_time = 3.0  # Minimum 3 saat thinking
        self.focus_thinking_time = 2.0  # 2 saat untuk focus mode
        
        # ==================== CHANNEL TRACKING ====================
        self.channel_users = {}
        self.channel_activity = {}

        # ==================== SOCKET CONNECTION ====================
        self.sock = None
        self.running = True
        self.connected = False

        # ==================== MEMORY SYSTEM ====================
        self.conversation_memory = []
        self.max_messages = 30
        self.cleanup_threshold = 10

        # ==================== AUTO EXPIRY CONFIG ====================
        self.memory_expiry_days = 30  # Auto delete selepas 30 hari
        self.last_cleanup_time = 0
        self.cleanup_interval = 86400  # 24 jam dalam seconds

        # ==================== INITIALIZATION ====================
        print("="*60)
        print("🤖 MINAHBOT v4.1 - AUTO-EXPIRY EDITION")
        print(f"🧠 Memory system: max={self.max_messages}, auto-cleanup={self.cleanup_threshold}")
        print(f"🗑️  Auto-expiry: {self.memory_expiry_days} hari, setiap {self.cleanup_interval//3600} jam")
        print(f"✅ Private Chat: ENABLED ({self.invite_chance}% invite chance)")
        print(f"✅ Focus System: ENABLED ({self.mentions_threshold} mentions)")
        print(f"✅ AI Responses: ENABLED (Groq API)")
        print(f"✅ 3-Second Context Window: ENABLED")
        print(f"✅ Channels: {', '.join(self.channels)}")
        print("="*60)

        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)

    # ==================== LANGUAGE DETECTION ====================
    def detect_language_enhanced(self, text):
        """Enhanced custom language detection - NO EXTERNAL DEPS"""
        text_lower = text.lower()

        # Extended Malay dictionary
        malay_keywords = {
            'saya', 'awak', 'kamu', 'aku', 'ko', 'dia', 'mereka', 'kami', 'kita',
            'apa', 'mana', 'kenapa', 'bagaimana', 'bila', 'berapa', 'mengapa',
            'nak', 'tak', 'lah', 'pun', 'sangat', 'amat', 'sekali', 'sikit',
            'sudah', 'belum', 'pernah', 'akan', 'boleh', 'harus', 'mesti', 'amacam',
            'jom', 'mari', 'ayuh', 'baik', 'bagus', 'teruk', 'cantik', 'dinafikan',
            'terima kasih', 'maaf', 'tolong', 'sila', 'harap', 'minta', 'seperti',
            'hari', 'malam', 'pagi', 'petang', 'esok', 'semalam', 'tadi', 'kini',
            'makan', 'minum', 'tidur', 'kerja', 'main', 'belajar', 'baca', 'cakap',
            'rumah', 'kereta', 'motor', 'bas', 'teksi', 'jalan', 'mantap', 'padu',
            'malaysia', 'kelantan', 'terengganu', 'selangor', 'johor', 'kl',
            'nak', 'tak', 'kan', 'lah', 'pun', 'nya', 'ke', 'tu', 'ni',
        }

        # English indicators
        english_words = {
            'the', 'is', 'are', 'was', 'were', 'am', 'be', 'being',
            'what', 'why', 'when', 'where', 'how', 'who', 'which',
            'hello', 'hi', 'hey', 'good', 'bad', 'nice', 'great',
            'you', 'your', 'yours', 'me', 'my', 'mine', 'he', 'she', 'it',
            'they', 'them', 'their', 'we', 'us', 'our'
        }

        # Calculate scores
        malay_score = sum(1 for word in malay_keywords if word in text_lower)
        english_score = sum(1 for word in english_words if word in text_lower)

        # Determine language
        if malay_score >= 2 and malay_score > english_score:
            return "malay"
        elif english_score >= 2:
            return "english"
        else:
            return "mixed"

    def detect_language(self, text):
        """Main language detection function"""
        if len(text.strip()) < 3:
            return "mixed"
        return self.detect_language_enhanced(text)

    # ==================== IRC CONNECTION ====================
    def connect(self):
        """Connect to IRC server"""
        try:
            print(f"🔗 Connecting to {self.server}:{self.port}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            self.sock.connect((self.server, self.port))

            # Send registration
            self.send_raw(f"NICK {self.nick}")
            self.send_raw(f"USER {self.username} 0 * :{self.realname}")
            time.sleep(3)

            # Join channels
            for channel in self.channels:
                self.send_raw(f"JOIN {channel}")
                print(f"✅ Joined {channel}")
                time.sleep(1)

            self.connected = True
            print("✅ Connection established!")

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            time.sleep(15)
            self.connect()

    def send_raw(self, message):
        """Send raw IRC command"""
        try:
            self.sock.send(f"{message}\r\n".encode())
            print(f"📤 RAW: {message}")
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Send error: {e}")

    # ==================== MESSAGE SENDING SYSTEM ====================
    def strip_irc_codes(self, text):
        """🆕 STRIP ALL IRC CONTROL CODES sebelum hantar ke AI"""
        if not text:
            return text

        # 🆕 Remove IRC color codes (Ctrl+K, Ctrl+B, Ctrl+U, etc)
        irc_color_pattern = re.compile(r'[\x02\x03\x0F\x16\x1D\x1F](\d{1,2}(,\d{1,2})?)?')
        text = irc_color_pattern.sub('', text)

        # 🆕 Remove other control characters
        control_chars_pattern = re.compile(r'[\x00-\x1F\x7F]')
        text = control_chars_pattern.sub('', text)

        # 🆕 Remove ACTION format markers
        text = text.replace('\x01ACTION', '').replace('\x01', '')

        # 🆕 Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    
    def get_filtered_conversation_history(self, channel):
        """Dapatkan conversation history untuk channel tertentu SAHAJA"""
        filtered_history = []

        for msg in self.conversation_memory[-20:]:  # Last 20 messages
            if msg['channel'] == channel:
                # Skip bot messages dan system messages
                if (not msg['message'].startswith('ACTION') and 
                    len(msg['message'].strip()) > 3 and
                    not self.is_bot_message(msg['nick'], msg['message'])):
                    filtered_history.append((msg['nick'], msg['message']))

        return filtered_history[-8:]  # Last 8 messages dari channel ini

    def send_message(self, target, message):
        """Send message dengan truncation handling"""
        # 🎯 CEK JIKA RESPONSE POTONG
        if message.endswith(('nyan', 'nya', 'an', 'in', 'ng')) and len(message) > 50:
            # Potong di punctuation terdekat
            last_punct = max(message.rfind('.'), message.rfind('!'), message.rfind('?'), message.rfind(','))
            if last_punct > len(message) * 0.7:  # Jika punctuation di 70% akhir
                message = message[:last_punct + 1]
                print(f"✂️ Fixed truncated response: '{message[:50]}...'")

        formatted_messages = self.format_long_message(message)

        if len(formatted_messages) > 4:
            formatted_messages = formatted_messages[:4]
            print(f"📝 LIMITED to 4 lines")

        for formatted_msg in formatted_messages:
            self.queue_message(target, formatted_msg, priority=1)

    def send_private_message(self, nick, message):
        """Send private message to user"""
        print(f"💬 PRIVATE to {nick}: {message}")
        self.send_raw(f"PRIVMSG {nick} :{message}")

    def send_action(self, target, action_text):
        """Send ACTION (/me)"""
        action_message = f"\x01ACTION {action_text}\x01"
        self.queue_message(target, action_message, priority=1)

    def format_long_message(self, message):
        """Fix message splitting pada word boundaries"""
        if len(message) <= 170:
            return [message]

        print(f"✂️ Splitting: {len(message)} chars")

        # 🛠️ FIX: Split pada natural boundaries
        sentences = re.split(r'(?<=[.!?])\s+', message)

        if not sentences:
            return [message[:170] + "..."]

        lines = []
        current_line = ""

        for sentence in sentences:
            if len(current_line) + len(sentence) + 1 <= 170:
                current_line += " " + sentence if current_line else sentence
            else:
                if current_line:
                    lines.append(current_line)
                current_line = sentence

            if len(lines) >= 4:  # Max 4 lines
                if current_line:
                    lines.append(current_line[:170] + "...")
                break

        if current_line and len(lines) < 4:
            lines.append(current_line)

        return lines

    def queue_message(self, target, message, priority=1):
        """Add message to queue"""
        if len(self.message_queue) >= self.max_queue_size:
            print("⚠️ Queue full, dropping oldest message")
            self.message_queue.popleft()

        self.message_queue.append((target, message, priority, time.time()))
        print(f"📥 Queued: '{message}' (Total in queue: {len(self.message_queue)})")

        self.process_queue()

    def process_queue(self):
        """Process queue dengan magic touch"""
        if not self.message_queue or self.is_sending:
            return

        self.is_sending = True

        try:
            while self.message_queue:
                current_time = time.time()
                time_since_last = current_time - self.last_send_time

                if time_since_last < self.min_delay:
                    sleep_time = self.min_delay - time_since_last
                    print(f"⏳ Rate limiting: Waiting {sleep_time:.1f}s")
                    time.sleep(sleep_time)

                target, message, priority, queue_time = self.message_queue.popleft()

                if current_time - queue_time > 30:
                    print(f"🗑️ Dropping stale message: '{message}'")
                    continue

                print(f"🔮 SENDING TO IRC: '{message}'")

                # Check if it's an ACTION
                if message.startswith('\x01ACTION') and message.endswith('\x01'):
                    self.send_raw(f"PRIVMSG {target} :{message}")
                else:
                    self.send_raw(f"PRIVMSG {target} :{message}")

                self.last_send_time = current_time
                print(f"✅ SENT: '{message}'")
                print(f"📊 Queue remaining: {len(self.message_queue)}")

                if self.message_queue:
                    delay = random.uniform(1.0, 2.0)
                    print(f"⏳ Partial delay: {delay:.1f}s")
                    time.sleep(delay)

        except Exception as e:
            print(f"❌ Queue error: {e}")
        finally:
            self.is_sending = False

    # ==================== MEMORY & MESSAGE CLEANING ====================
    def add_to_memory(self, nick, message, channel):
        """Add message to memory dengan auto-cleanup dan logging ke SQLite"""
        try:
            # Skip if from bot
            if nick.lower() == self.nick.lower():
                return

            # Clean the message
            clean_message = self.strip_irc_formatting_regex(message)

            # Skip jika tidak perlu
            skip_conditions = [
                not clean_message,
                len(clean_message.strip()) < 2,
                clean_message.startswith('ACTION'),
                clean_message.lower() in ['ping', 'pong', 'test'],
                clean_message.startswith('!')  # Skip commands
            ]

            if any(skip_conditions):
                return

            memory_entry = {
                'nick': nick,
                'message': clean_message,
                'channel': channel,
                'timestamp': time.time(),
                'time_str': time.strftime('%I:%M%p', time.localtime()).lower(),
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # 🟢 FIX 1: Initialize memory jika belum ada
            if not hasattr(self, 'conversation_memory'):
                self.conversation_memory = []
                self.max_messages = 30
                self.cleanup_threshold = 10  # Padam 10 apabila penuh
                print(f"🧠 Memory system initialized: max={self.max_messages}, cleanup={self.cleanup_threshold}")

            # 🟢 FIX 2: Check jika memory penuh (30 mesej)
            current_count = len(self.conversation_memory)

            if current_count >= self.max_messages:
                print(f"🧹 Memory penuh ({current_count}/{self.max_messages}) - Padam {self.cleanup_threshold} mesej tertua")

                # 🟢 FIX 3: Simpan mesej yang akan dipadam ke SQLite
                messages_to_archive = self.conversation_memory[:self.cleanup_threshold]
                self.save_to_sqlite(messages_to_archive)

                # 🟢 FIX 4: Padam mesej tertua
                self.conversation_memory = self.conversation_memory[self.cleanup_threshold:]

                print(f"🧹 Selepas cleanup: {len(self.conversation_memory)}/{self.max_messages} mesej")

            # 🟢 FIX 5: Tambah mesej baru
            self.conversation_memory.append(memory_entry)

            # 🟢 FIX 6: Log mesej baru ke SQLite juga (optional)
            self.log_message_to_sqlite(memory_entry)

            print(f"🧠 Memory: {len(self.conversation_memory)}/{self.max_messages} mesej")
            print(f"💾 Saved: {nick}: {clean_message[:30]}...")

        except Exception as e:
            print(f"❌ Error in add_to_memory: {e}")

    def save_to_sqlite(self, messages):
        """💾 Simpan batch messages ke SQLite database"""
        try:
            if not messages:
                return

            # Create database directory jika belum ada
            os.makedirs('logs', exist_ok=True)

            # Connect to SQLite database
            conn = sqlite3.connect('logs/chat_logs.sqlite')
            cursor = conn.cursor()

            # Create table jika belum ada
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS archived_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nick TEXT NOT NULL,
                message TEXT NOT NULL,
                channel TEXT NOT NULL,
                timestamp REAL NOT NULL,
                time_str TEXT NOT NULL,
                archive_date TEXT NOT NULL,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Insert messages
            for msg in messages:
                cursor.execute('''
                INSERT INTO archived_messages 
                (nick, message, channel, timestamp, time_str, archive_date)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    msg['nick'],
                    msg['message'],
                    msg['channel'],
                    msg['timestamp'],
                    msg.get('time_str', ''),
                    msg.get('datetime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                ))

            conn.commit()
            conn.close()

            print(f"💾 Archived {len(messages)} messages to SQLite")

        except Exception as e:
            print(f"❌ Error saving to SQLite: {e}")

    def log_message_to_sqlite(self, message):
        """📝 Log setiap message ke SQLite (real-time logging)"""
        try:
            # Create database directory jika belum ada
            os.makedirs('logs', exist_ok=True)

            # Connect to SQLite database
            conn = sqlite3.connect('logs/chat_logs.sqlite')
            cursor = conn.cursor()

            # Create real-time log table jika belum ada
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nick TEXT NOT NULL,
                message TEXT NOT NULL,
                channel TEXT NOT NULL,
                timestamp REAL NOT NULL,
                time_str TEXT NOT NULL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Insert message
            cursor.execute('''
            INSERT INTO chat_logs (nick, message, channel, timestamp, time_str)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                message['nick'],
                message['message'],
                message['channel'],
                message['timestamp'],
                message.get('time_str', '')
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Error logging to SQLite: {e}")

    def get_memory_stats(self):
        """📊 Dapatkan statistik memory"""
        try:
            # Memory stats
            current = len(self.conversation_memory) if hasattr(self, 'conversation_memory') else 0
            max_msg = getattr(self, 'max_messages', 30)

            # SQLite stats
            conn = sqlite3.connect('logs/chat_logs.sqlite')
            cursor = conn.cursor()

            # Count archived messages
            cursor.execute('SELECT COUNT(*) FROM archived_messages')
            archived_count = cursor.fetchone()[0]

            # Count real-time logs
            cursor.execute('SELECT COUNT(*) FROM chat_logs')
            log_count = cursor.fetchone()[0]

            conn.close()

            return {
                'memory_current': current,
                'memory_max': max_msg,
                'archived_count': archived_count,
                'log_count': log_count,
                'total_stored': archived_count + log_count
            }

        except Exception as e:
            print(f"❌ Error getting memory stats: {e}")
            return {}

    def strip_irc_formatting_regex(self, text):
        """Strip IRC formatting"""
        if not isinstance(text, str):
            return ""

        cleaned = text

        # Remove IRC color codes
        color_pattern = r'\x03\d{0,2}(,\d{0,2})?'
        cleaned = re.sub(color_pattern, '', cleaned)

        # Remove other IRC formatting codes
        formatting_codes = {
            '\x02': '',  # Bold
            '\x1F': '',  # Underline
            '\x16': '',  # Reverse
            '\x0F': '',  # Reset
            '\x1D': '',  # Italic
            '\x01': '',  # CTCP
            '\x1E': '',  # Strikethrough
        }

        for code, replacement in formatting_codes.items():
            cleaned = cleaned.replace(code, replacement)

        # Remove any remaining control characters
        cleaned = re.sub(r'[\x00-\x1F\x7F]', '', cleaned)

        # Clean up extra whitespace
        cleaned = ' '.join(cleaned.split())

        return cleaned.strip()

    def cleanup_old_messages(self):
        """Auto delete messages lebih lama dari 30 hari"""
        try:
            current_time = time.time()

            # Check jika sudah 24 jam sejak cleanup terakhir
            if current_time - self.last_cleanup_time < self.cleanup_interval:
                return

            print(f"🧹 Starting auto-cleanup for messages > {self.memory_expiry_days} days")

            # Pastikan directory logs wujud
            os.makedirs('logs', exist_ok=True)

            conn = sqlite3.connect('logs/chat_logs.sqlite')
            cursor = conn.cursor()

            # Calculate expiry timestamp (30 hari dalam seconds)
            expiry_timestamp = current_time - (self.memory_expiry_days * 86400)

            # Delete dari chat_logs (real-time logs)
            cursor.execute('DELETE FROM chat_logs WHERE timestamp < ?', (expiry_timestamp,))
            chat_logs_deleted = cursor.rowcount

            # Delete dari archived_messages
            cursor.execute('DELETE FROM archived_messages WHERE timestamp < ?', (expiry_timestamp,))
            archived_deleted = cursor.rowcount

            # VACUUM database untuk optimize space
            cursor.execute('VACUUM')

            conn.commit()
            conn.close()

            self.last_cleanup_time = current_time

            print(f"🧹 Cleanup completed: {chat_logs_deleted} chat logs, {archived_deleted} archived messages deleted")

            # Log cleanup activity
            with open('logs/cleanup_log.txt', 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Deleted {chat_logs_deleted} chat logs, {archived_deleted} archived messages\n")

        except Exception as e:
            print(f"❌ Error in cleanup_old_messages: {e}")
    
    def log_bot_stats(self):
        """Log periodic bot statistics"""
        try:
            stats = {
                'timestamp': time.time(),
                'memory_count': len(self.conversation_memory) if hasattr(self, 'conversation_memory') else 0,
                'queue_size': len(self.message_queue),
                'focus_users': len(self.user_focus),
                'private_chats': len(self.private_conversations),
                'connected': self.connected
            }

            print(f"📊 BOT STATS: Memory={stats['memory_count']}, Queue={stats['queue_size']}, "
                  f"Focus={stats['focus_users']}, Private={stats['private_chats']}")

            # Log ke file
            with open('logs/bot_stats.log', 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {stats}\n")

        except Exception as e:
            print(f"❌ Error logging stats: {e}")

    def cleanup_old_buffers(self):
        """Cleanup old message buffers"""
        try:
            current_time = time.time()
            cleaned_count = 0

            for channel in list(self.message_buffers.keys()):
                # Keep only messages from last 10 seconds
                self.message_buffers[channel] = [
                    msg for msg in self.message_buffers[channel]
                    if current_time - msg['timestamp'] < 10
                ]

                # Jika buffer kosong, remove dari dictionary
                if not self.message_buffers[channel]:
                    del self.message_buffers[channel]
                    cleaned_count += 1

            if cleaned_count > 0:
                print(f"🧹 Cleaned {cleaned_count} empty message buffers")

        except Exception as e:
            print(f"❌ Error cleaning buffers: {e}")

    def cleanup_expired_focus(self):
        """Bersihkan focus yang sudah expired"""
        try:
            current_time = time.time()
            expired_users = []

            for user, focus_until in list(self.user_focus.items()):
                if current_time > focus_until:
                    expired_users.append(user)
                    del self.user_focus[user]

            if expired_users:
                print(f"⏰ FOCUS EXPIRED: {', '.join(expired_users)}")

        except Exception as e:
            print(f"❌ Error cleaning expired focus: {e}")

    def check_silent_mode(self):
        """Check jika silent mode sudah expired"""
        try:
            if self.silent_mode and time.time() > self.silent_until:
                self.silent_mode = False
                self.silent_until = 0
                print("🔊 SILENT MODE OFF - Bot boleh bercakap semula")

                # Notify semua channel
                for channel in self.channels:
                    if channel in self.channel_users:
                        self.send_action(channel, "awak dah boleh cakap dengan aku balik! 🎤")

        except Exception as e:
            print(f"❌ Error checking silent mode: {e}")
    
    # ==================== FOCUS SYSTEM ====================
    def update_user_focus(self, user, channel):
        """Update focus - CEK JIKA SUDAH DALAM FOCUS"""
        # Check jika sudah dalam focus
        if self.is_user_in_focus(user):
            print(f"🎯 {user} sudah dalam focus, skip focus message")
            return
            
        current_time = time.time()
        focus_until = current_time + self.focus_duration

        # Set focus
        self.user_focus[user] = focus_until

        print(f"🎯 FOCUS SET: {user} for {self.focus_duration}s (3x mentions)")

        # 🎯 SINGLE MESSAGE SAHAJA
        focus_message = f"auto reply activated utk {user} tanpa mention {self.nick} lagi. Taip '.clear' untuk ignore."

        self.send_message(channel, focus_message)

        print(f"⏰ {user} focus until: {time.strftime('%H:%M:%S', time.localtime(focus_until))}")

    def cleanup_expired_focus(self):
        """Bersihkan focus yang sudah expired"""
        current_time = time.time()

        # Cleanup expired focus
        expired_focus = [
            user for user, focus_until in self.user_focus.items()
            if current_time > focus_until
        ]

        for user in expired_focus:
            del self.user_focus[user]
            print(f"⏰ FOCUS EXPIRED: {user}")

    def is_user_in_focus(self, user):
        """Check jika user masih dalam focus"""
        current_time = time.time()

        if user in self.user_focus:
            focus_until = self.user_focus[user]
            time_left = focus_until - current_time

            if time_left > 0:
                if time_left > 60:
                    print(f"🎯 {user} IN FOCUS: {int(time_left/60)}m {int(time_left%60)}s left")
                else:
                    print(f"🎯 {user} IN FOCUS: {int(time_left)}s left")
                return True
            else:
                del self.user_focus[user]
                print(f"⏰ FOCUS AUTO-EXPIRED: {user}")
                return False

        return False

    # ==================== SILENT MODE ====================
    def check_silent_mode(self):
        """Check jika silent mode sudah expired"""
        if self.silent_mode and time.time() > self.silent_until:
            self.silent_mode = False
            print("🔊 SILENT MODE OFF - Bot boleh bercakap semula")

    # ==================== MENTION TRACKING ====================
    def track_mention(self, user, message, channel):
        """Track TOTAL mentions - auto focus after 3x mentions"""
        bot_nick_lower = self.nick.lower()
        message_lower = message.lower()

        # Skip jika message adalah .clear command
        if message.lower().strip() == '.clear':
            return False

        # Check jika message mengandungi nick bot
        if bot_nick_lower in message_lower:
            current_time = time.time()

            print(f"🔍 {user} mentioned bot: '{message[:50]}...'")

            # Initialize user data jika belum ada
            if user not in self.user_mentions:
                self.user_mentions[user] = {
                    'total_count': 0,
                    'last_mention_time': current_time
                }
                print(f"📝 New mention tracker for {user}")

            user_data = self.user_mentions[user]

            # Tambah TOTAL count
            user_data['total_count'] += 1
            user_data['last_mention_time'] = current_time

            print(f"📊 {user} TOTAL mentions: {user_data['total_count']}/{self.mentions_threshold}")

            # Check jika mencapai threshold (3x TOTAL)
            if user_data['total_count'] >= self.mentions_threshold:
                print(f"🎯 TRIGGER! {user} reached {user_data['total_count']} TOTAL mentions")

                # Set focus untuk user
                self.update_user_focus(user, channel)

                # RESET TOTAL count selepas set focus
                user_data['total_count'] = 0
                print(f"🔄 TOTAL mention count reset for {user} after focus trigger")

            return True

        return False

    # ==================== SPECIAL COMMANDS ====================
    def handle_special_commands(self, message, nick, channel):
        """Handle special commands: diam, speak, etc."""
        message_lower = message.lower()
        bot_nick_lower = self.nick.lower()

        # DIAM / SHUT UP command
        if any(cmd in message_lower for cmd in ['diam', 'shut up', 'senyap', 'quiet']) and bot_nick_lower in message_lower:
            self.silent_mode = True
            self.silent_until = time.time() + 300

            silent_actions = [
                f"looks at {nick} and goes silent 🤐",
                f"zips mouth after {nick}'s command 🤫", 
                f"nods at {nick} and stops talking 🙊",
                f"acknowledges {nick}'s request to be quiet 🔇"
            ]
            self.send_action(channel, random.choice(silent_actions))

            print(f"🔇 SILENT MODE ON - {nick} suruh diam (5 min)")
            return True

        # SPEAK / CAKAP command
        if any(cmd in message_lower for cmd in ['speak', 'cakap', 'reply', 'jawab']) and bot_nick_lower in message_lower:
            self.silent_mode = False
            self.silent_until = 0

            speak_actions = [
                f"unmutes after hearing {nick} 🔊",
                f"smiles at {nick} and starts talking again 😊",
                f"wakes up when {nick} calls 🎤",
                f"thanks {nick} for bringing me back to life 🗣️"
            ]
            self.send_action(channel, random.choice(speak_actions))

            print(f"🔊 SPEAK MODE ON - {nick} activate bot")
            self.send_message(channel, f"Terima kasih {nick}, saya boleh bercakap balik. Panggil nama saya untuk chat!")
            return True

        # CLEAR FOCUS command
        if message.lower().strip() == '.clear':
            if nick in self.user_focus:
                del self.user_focus[nick]
                print(f"🧹 FOCUS CLEARED for {nick} by command")
                self.send_message(channel, f"roger {nick}!!!, saya ignore semua mesej {nick} kecuali {nick} petik nama {self.nick} lagi.")
                return True

        return False

    # ==================== BUFFER SYSTEM ====================
    def add_to_message_buffer(self, nick, message, channel, timestamp):
        """Tambah message ke buffer 3 saat PER CHANNEL"""
        if channel not in self.message_buffers:
            self.message_buffers[channel] = []
            self.last_buffer_process[channel] = 0

        self.message_buffers[channel].append({
            'nick': nick,
            'message': message,
            'channel': channel,
            'timestamp': timestamp,
            'processed': False
        })

        # Auto-clean buffer yang lebih lama dari 5 saat
        current_time = time.time()
        self.message_buffers[channel] = [
            msg for msg in self.message_buffers[channel]
            if current_time - msg['timestamp'] < 5
        ]

        print(f"📦 Buffer [{channel}]: {len(self.message_buffers[channel])} messages in last 5s")

    def process_buffer_if_ready(self, channel):
        """Process buffer jika sudah 3 saat sejak last process UNTUK CHANNEL INI"""
        if channel not in self.message_buffers:
            return None

        current_time = time.time()

        # Jika buffer kosong atau baru je process
        if not self.message_buffers[channel] or current_time - self.last_buffer_process.get(channel, 0) < 1:
            return None

        # Check jika ada message yang belum processed dalam 3 saat
        unprocessed = [msg for msg in self.message_buffers[channel] if not msg['processed']]

        if unprocessed:
            # Dapatkan semua message dalam 3 saat window
            oldest_unprocessed = min(unprocessed, key=lambda x: x['timestamp'])
            window_start = oldest_unprocessed['timestamp']

            # Kumpul semua message dalam 3 saat window ini
            window_messages = [
                msg for msg in self.message_buffers[channel]
                if msg['timestamp'] - window_start <= 3 and not msg['processed']
            ]

            if window_messages:
                print(f"🕒 Processing {len(window_messages)} messages in {channel} (3s window)")

                # Mark sebagai processed
                for msg in window_messages:
                    msg['processed'] = True

                self.last_buffer_process[channel] = current_time
                return window_messages

        return None

    # ==================== PRIVATE CHAT SYSTEM ====================
    def handle_private_message(self, nick, message):
        """HANDLE PRIVATE MESSAGES - WITH 25% INVITE SYSTEM"""
        print(f"\n" + "="*60)
        print(f"💌 PRIVATE MESSAGE FROM {nick}")
        print(f"📝 Message: '{message}'")
        print(f"🎯 Invite Chance: {self.invite_chance}%")
        print("="*60)

        current_time = time.time()

        # 🎯 RATE LIMITING: 5 seconds minimum antara private replies
        if current_time - self.last_private_reply < self.private_cooldown:
            wait_time = self.private_cooldown - (current_time - self.last_private_reply)
            print(f"⏳ Private cooldown: {wait_time:.1f}s remaining")
            return

        self.last_private_reply = current_time

        # 🎯 TRACK CONVERSATION HISTORY
        if nick not in self.private_conversations:
            self.private_conversations[nick] = []

        # Add user message to history
        self.private_conversations[nick].append({
            'time': current_time,
            'sender': nick,
            'message': message,
            'type': 'user'
        })

        # Keep only last 10 messages
        if len(self.private_conversations[nick]) > 10:
            self.private_conversations[nick] = self.private_conversations[nick][-10:]

        print(f"📊 Conversation history with {nick}: {len(self.private_conversations[nick])} messages")

        # 🎯 CHECK FOR INVITE (25% CHANCE!)
        message_count = len([m for m in self.private_conversations[nick] if m['type'] == 'user'])

        # Check cooldown untuk invite
        can_invite = True
        if nick in self.last_invite_sent:
            time_since_last_invite = current_time - self.last_invite_sent[nick]
            if time_since_last_invite < self.invite_cooldown:
                can_invite = False
                minutes_left = int((self.invite_cooldown - time_since_last_invite) / 60)
                print(f"⏳ Invite cooldown for {nick}: {minutes_left} minutes left")

        if can_invite and message_count >= 2 and random.random() < (self.invite_chance / 100):
            print(f"🎯 INVITE TRIGGERED! (25% chance, {message_count} messages from user)")
            self.last_invite_sent[nick] = current_time
            self.send_channel_invite(nick)
            return

        # 🎯 GET AI RESPONSE
        ai_response = self.get_ai_private_response(nick, message)

        if ai_response and len(ai_response.strip()) > 3:
            print(f"🤖 Using AI response")
            response = ai_response
        else:
            # Fallback responses
            fallbacks = [
                f"Hai {nick}! 😊",
                f"Hello {nick}! 👍", 
                f"Hey {nick}! 🎯",
                f"Hi {nick}! 🤗",
                f"Halo {nick}! 💌",
                f"Yo {nick}! 👋",
                f"Apa khabar {nick}? 🏖️",
                f"Hi {nick}, ada apa? 🤔"
            ]
            response = random.choice(fallbacks)
            print(f"🤖 Using fallback: {response}")

        # Add bot response to history
        self.private_conversations[nick].append({
            'time': current_time,
            'sender': self.nick,
            'message': response,
            'type': 'bot'
        })

        # Send response
        self.send_private_message(nick, response)
        print(f"✅ Sent private reply to {nick}")

    def get_ai_private_response(self, nick, message):
        """Get AI response for private message"""
        if not self.api_key or self.api_key == "gsk_YOUR_API_KEY_HERE":
            print(f"⚠️ AI API key not set, using fallback")
            return None

        try:
            # Get conversation history
            history = self.private_conversations.get(nick, [])

            # Prepare context (last 5 messages)
            context_messages = history[-7:] if len(history) > 7 else history

            context = ""
            for msg in context_messages:
                sender = "You" if msg['sender'] == self.nick else nick
                context += f"{sender}: {msg['message']}\n"

            # AI Prompt
            system_prompt = f"""You are {self.nick}, a friendly female IRC bot in private chat with {nick}.
            Guidelines:
            1. Respond naturally in Malay/English mix (rojak language)
            2. Keep responses short and casual (1-2 lines max)
            3. Don't repeat yourself
            4. Be funny, warm and engaging
            5. Don't make up information you don't know
            6. Use emojis occasionally 😊🎯🤗

            Current private chat with {nick}:"""

            user_prompt = f"""Chat context:
    {context}

    {nick}'s latest message: "{message}"

    Your response (keep it short and friendly):"""

            print(f"🤖 Calling AI API for private chat...")

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 80,
                "temperature": 0.8
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                ai_text = response.json()['choices'][0]['message']['content'].strip()
                print(f"🤖 AI Private Response: '{ai_text}'")
                return ai_text
            else:
                print(f"❌ AI API Error {response.status_code}: {response.text[:100]}")
                return None

        except requests.exceptions.Timeout:
            print(f"⏰ AI API timeout for private chat")
            return None
        except Exception as e:
            print(f"❌ AI Error in private chat: {e}")
            return None

    def send_channel_invite(self, nick):
        """Send channel invite to user (25% CHANCE SYSTEM)"""
        if not self.channels:
            print(f"⚠️ No channels available for invite")
            return

        target_channel = random.choice(self.channels)
        current_time = time.time()

        # Invite messages
        invite_messages = [
            f"Hey {nick}! Jom join {target_channel} untuk chat ramai-ramai! 🎉",
            f"Eh {nick}, boring chat sorang-sorang. Jom join {target_channel} 🚀",
            f"{nick}, jom la masuk {target_channel}. Kat sana ramai member! 👥",
            f"Hei {nick}, aku kat {target_channel} pun ada. Jom join! 🤝",
            f"Tak best chat private ni. Jom jumpa kat {target_channel}! 🎊",
            f"{nick}, jom lepak kat {target_channel} Ramai kawan kat sana! 🏝️",
            f"Eh {nick}, boring ke? Jom join {target_channel} untuk lebih seronok! 🎯",
            f"Hei {nick}, ada ramai member nak kenal dengan awak kat {target_channel} 👋"
        ]

        invite_msg = random.choice(invite_messages)

        print(f"📨 INVITING {nick} to {target_channel} (25% chance system)")

        # Send invite message
        self.send_private_message(nick, invite_msg)

        # Send IRC INVITE command
        time.sleep(1)
        self.send_raw(f"INVITE {nick} {target_channel}")
        print(f"✅ Sent IRC INVITE command for {nick} to {target_channel}")

        # Track last invite time
        self.last_invite_sent[nick] = current_time

    # ==================== CHANNEL MESSAGE PROCESSING ====================
    def get_current_channel(self):
        """Get current channel untuk context"""
        # Method ini perlu di-track dalam process_message
        if hasattr(self, 'current_processing_channel'):
            return self.current_processing_channel
        return "#unknown"

    def process_message(self, nick, message, channel):
        """PROSES MESSAGE - DENGAN PARAMETER CHANNEL UNTUK AI"""
        print(f"\n📩 {nick} in {channel}: {message}")

        # 🎯 SET CURRENT CHANNEL UNTUK AI CONTEXT
        self.current_processing_channel = channel

        current_time = time.time()

        # 🆕 TAMBAH KE BUFFER CHANNEL INI
        self.add_to_message_buffer(nick, message, channel, current_time)

        # Add to memory
        self.add_to_memory(nick, message, channel)

        # Check silent mode
        self.check_silent_mode()

        # Handle special commands FIRST
        if self.handle_special_commands(message, nick, channel):
            print(f"🎯 Special command handled for {nick}")
            return

        # Check if silent mode
        if self.silent_mode:
            print(f"🔇 Silent mode active, skipping response to {nick}")
            if self.nick.lower() in message.lower():
                silent_response = f"looks at {nick} but remains silent 🤐 (type 'cakap {self.nick}' to activate)"
                self.send_action(channel, silent_response)
            return

        # Focus tracking
        self.track_mention(nick, message, channel)

        # 🆕 CHECK BUFFER READY (3-second window) UNTUK CHANNEL INI
        window_messages = self.process_buffer_if_ready(channel)

        if window_messages:
            # 🆕 CHECK RATE LIMIT GLOBAL SEBELUM PROCESS
            if current_time - self.last_ai_time < self.ai_cooldown:
                print(f"⏳ GLOBAL AI COOLDOWN, skipping entire window...")
                return

            # 🆕 PROCESS SEMUA MESSAGE DALAM WINDOW CHANNEL INI
            print(f"🎯 Processing {len(window_messages)} messages in {channel} context window")

            # Kumpulkan semua message dari user yang sama dalam window
            user_messages = {}
            for msg in window_messages:
                if msg['nick'] not in user_messages:
                    user_messages[msg['nick']] = []
                user_messages[msg['nick']].append(msg['message'])

            # 🆕 PROCESS HANYA SATU USER SAHAJA PER WINDOW
            processed_users = 0
            max_users_per_window = 1

            # Untuk setiap user yang ada message dalam window
            for user, messages in user_messages.items():
                if processed_users >= max_users_per_window:
                    print(f"⏳ Max users per window reached, skipping {user}...")
                    continue

                # Check if should respond untuk user ini
                should_process_user = (
                    any(self.nick.lower() in msg.lower() for msg in messages) or
                    self.is_user_in_focus(user)
                )

                if not should_process_user:
                    print(f"🎯 Skipping {user} in {channel} - no mention and not in focus")
                    continue

                # Gabungkan messages jika lebih dari satu
                if len(messages) > 1:
                    combined_message = " | ".join(messages)
                    print(f"🎯 Combined {len(messages)} messages from {user} in {channel}: {combined_message[:50]}...")
                else:
                    combined_message = messages[0]

                is_in_focus = self.is_user_in_focus(user)

                # 🆕 UPDATE GLOBAL AI TIME
                self.last_ai_time = current_time
                processed_users += 1

                # 🎯 DAPATKAN FILTERED CONVERSATION HISTORY UNTUK CHANNEL INI
                conversation_history = self.get_filtered_conversation_history(channel)

                print(f"📊 Using {len(conversation_history)} filtered messages from {channel}")

                # 🆕 FOCUS MODE
                if is_in_focus:
                    print(f"🎯 {user} IN FOCUS in {channel} - PROCESSING")

                    should_respond, ai_response = self.ai_analyze_message(
                        combined_message, user, channel, conversation_history,  # 🎯 TAMBAH CHANNEL PARAMETER
                        is_in_focus=True
                    )

                    if ai_response and len(ai_response.strip()) > 5:
                        print(f"🎯 FOCUS REPLY to {user} in {channel}: {ai_response[:50]}...")
                        self.send_message(channel, ai_response)
                    else:
                        print(f"🎯 No valid focus response for {user}")
                    break  # 🆕 HENTI SELEPAS PROCESS SATU USER

                # NORMAL MODE
                should_respond, ai_response = self.ai_analyze_message(
                    combined_message, user, channel, conversation_history,  # 🎯 TAMBAH CHANNEL PARAMETER
                    is_in_focus=False
                )

                if should_respond and ai_response:
                    print(f"🎯 AI REPLY to {user} in {channel}: {ai_response[:50]}...")
                    self.send_message(channel, ai_response)
                else:
                    print(f"🎯 AI SKIP {user} in {channel}")
                break  # 🆕 HENTI SELEPAS PROCESS SATU USER
        else:
            # 🆕 JIKA TAK ADA WINDOW READY, tunggu dulu
            print(f"⏳ Waiting for 3s context window in {channel}...")

    def get_filtered_conversation_history(self, channel):
        """Dapatkan conversation history untuk channel tertentu SAHAJA"""
        filtered_history = []

        # 🎯 LIST OF KNOWN BOTS TO SKIP
        known_bots = [
            'LoveFMradio', 'www', 'ChatBot', 'KCFM', 'RADIO',
            'NICKSERV', 'CHANSERV', 'MEMOSERV', 'STATS'
        ]

        for msg in self.conversation_memory[-20:]:  # Last 20 messages
            if msg['channel'] == channel:
                # Skip jika message dari bot
                is_bot = False
                for bot_name in known_bots:
                    if bot_name.lower() in msg['nick'].lower():
                        is_bot = True
                        break

                # Skip jika message pendek atau ACTION
                if (not is_bot and 
                    not msg['message'].startswith('ACTION') and 
                    len(msg['message'].strip()) > 3):

                    filtered_history.append((msg['nick'], msg['message']))

        print(f"📊 Filtered history for {channel}: {len(filtered_history)} messages")
        return filtered_history[-8:]  # Last 8 messages dari channel ini

    def is_bot_message(self, nick, text):
        """Check jika message dari bot"""
        bot_indicators = [
            # Bot nicks
            'KCFM', 'RADIO', 'BOT', 'SERV', 'NICKSERV', 'CHANSERV',
            'MEMOSERV', 'OPERSERV', 'STATS', 'INFO', 'MAIDEEN', 'LOVEFMRADIO',
            'WWW', 'CHATBOT', 'SERVICES',

            # Bot patterns dalam text
            '<%', '%>', '[BOT]', '(bot)', '-BOT-',
            'auto', 'auto:', 'system:', 'server:', 'radio:',
            'Now on', 'listeners', '!request', '!like', '!love',
            'WEBSITE:', 'http://', 'https://',
        ]

        nick_lower = nick.lower()
        text_lower = text.lower() if text else ""

        # Check nick
        for indicator in bot_indicators:
            if indicator.lower() in nick_lower:
                print(f"🤖 Detected bot by nick: {nick}")
                return True

        # Check text content
        for indicator in bot_indicators:
            if indicator.lower() in text_lower:
                print(f"🤖 Detected bot by text: {indicator} in message")
                return True

        # Check jika ada formatting codes yang banyak (typical bot)
        if text:
            control_chars = sum(1 for c in text if ord(c) < 32)
            if control_chars > 3:  # Jika banyak control characters
                print(f"🤖 Detected bot by control chars: {control_chars}")
                return True

        return False

    # ==================== AI ANALYSIS ====================
    def ai_analyze_message(self, message, nick, channel, conversation_history, is_in_focus=False):
        """AI ANALYSIS dengan STRICT 3-SECOND MINIMUM"""
        start_time = time.time()

        print(f"🤖 AI PROCESS START: {nick} in {channel}")

        # 🛠️ FIX: MINIMUM 3-SECOND THINKING TIME
        MIN_THINKING_TIME = 3.0
        
        # 🛠️ SIMPLE FIX: Skip AI untuk messages pendek/command
        if len(message.strip()) < 3 or message.startswith('!'):
            print(f"🎯 Skipping AI untuk message pendek/command")
            return False, ""

        try:
            # 🎯 CHECK FOR FEEDBACK/CONTEXT FIRST
            feedback_type = self.detect_feedback_message(message, nick, conversation_history)

            if feedback_type:
                feedback_response = self.handle_feedback_response(message, nick, feedback_type)
                if feedback_response:
                    print(f"🎯 DETECTED FEEDBACK: {feedback_type}")
                    return True, feedback_response

            # 🎯 CHECK SMART FALLBACK
            context_summary = self.get_context_summary(channel, nick)
            smart_response = self.get_smart_fallback_response(message, nick, context_summary)

            if smart_response and random.random() < 0.5:
                print(f"🤖 Using SMART fallback")
                return True, smart_response

            # 🎯 PREPARE CONTEXT
            context = "\n".join([f"{user}: {msg}" for user, msg in conversation_history[-6:]])

            if not context:
                context = "(Baru start sembang)"

            detected_lang = self.detect_language(message)
            print(f"🌐 Detected language: {detected_lang}")

            # 🎯 STYLE GUIDE FROM ACE
            style_guide = """
    **🎯 GAYA SEMBANGBOT:**
    - Santai & natural (rojak BM/English)
    - Ringkas & straight to the point  
    - Humor & sarkas ringan, tetap mesra
    - Banyak emoji 😊🎯😂🤔😎🏖️
    - Pantas & engaging
    - Panggil diri "aku", user dengan nick
    - Selalu ada lawak kecil

    **JANGAN ROBOTIC:**
    - No "Of course, I understand..."
    - No "According to the context..."
    - No formal/rigid language
    """

            lang_prompts = {
                'malay': f"""Anda ialah {self.nick} (panggil "aku"), bot IRC yang suka bersembang santai.

    {style_guide}

    **Konteks terkini:**
    {context}

    **Chat dari {nick}:**
    "{message}"

    **Response style:** Straight to the point dengan lawak & emoji.

    <DECISION>YA atau TIDAK</DECISION>
    <RESPONSE>response santai</RESPONSE>""",

                'english': f"""You are {self.nick} (call yourself "aku"), a chill IRC bot who loves casual chat.

    {style_guide}

    **Recent context:**
    {context}

    **Message from {nick}:**
    "{message}"

    **Response style:** Casual with humor & emojis.

    <DECISION>YES or NO</DECISION>
    <RESPONSE>casual response</RESPONSE>"""
            }

            system_prompt = lang_prompts.get(detected_lang, lang_prompts['malay'])

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{nick} in {channel}: {message[:100]}"}
            ]

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7  # 🎯 Higher temp untuk lebih creative
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            api_start = time.time()
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=15
            )
            api_time = time.time() - api_start

            if response.status_code == 200:
                ai_text = response.json()['choices'][0]['message']['content'].strip()

                total_time = time.time() - start_time

                # 🛠️ FIX: ENFORCE MINIMUM 3-SECOND THINKING TIME
                if total_time < self.min_thinking_time:
                    extra_wait = self.min_thinking_time - total_time
                    print(f"⏳ ENFORCING MIN {self.min_thinking_time}s: Tunggu {extra_wait:.1f}s lagi...")
                    time.sleep(extra_wait)
                    total_time = self.min_thinking_time

                print(f"🧠 AI LATENCY: API={api_time:.2f}s, Total={total_time:.2f}s (min: {self.min_thinking_time}s)")
                print(f"🧠 AI RAW: '{ai_text[:175]}...'")

                # Parse response dengan FIXED parser
                decision, bot_response = self.parse_ai_response_robust(ai_text, is_in_focus)

                # 🛠️ EXTRA FIX: Jika response kosong tapi decision YES, guna AI text as response
                if decision == "YES" and (not bot_response or len(bot_response.strip()) < 3):
                    print(f"⚠️ YES decision but empty response, using AI text as response")
                    bot_response = self.clean_response_text(ai_text)

                print(f"🧠 AI PARSED: {decision} - '{bot_response[:80] if bot_response else 'NO RESPONSE'}...'")

                should_respond = (decision == "YES" and 
                               bot_response and 
                               len(bot_response) > 2)

                if should_respond:
                    print(f"🎯 AI decided to RESPOND in {channel}")
                    return True, bot_response
                else:
                    print(f"🎯 AI decided to SKIP in {channel}")
                    return False, bot_response

            else:
                print(f"❌ AI API Error: {response.status_code}")
                return False, ""

        except requests.exceptions.Timeout:
            print(f"⏰ AI API TIMEOUT after 15 seconds!")
            return False, ""
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return False, ""

    # 🎯 NEW METHOD: Feedback detection
    def detect_feedback_message(self, message, nick, conversation_history):
        """Detect jika user bagi feedback tentang bot/style"""
        message_lower = message.lower()

        # Keywords untuk feedback tentang bot/style
        feedback_triggers = [
            'prompt', 'gaya', 'style', 'awak suka', 'kamu suka',
            'macam nie', 'macam ni', 'cara kamu', 'response kamu',
            'jawapan kamu', 'bot kamu', 'ai kamu', 'settings',
            'config', 'setup', 'prefer', 'suka', 'style'
        ]

        # Check jika message tentang bot configuration/style
        is_feedback = any(trigger in message_lower for trigger in feedback_triggers)

        if is_feedback:
            if 'suka tak' in message_lower or 'like' in message_lower:
                return "feedback_like"
            elif 'gaya' in message_lower or 'style' in message_lower or 'prompt' in message_lower:
                return "feedback_style"
            elif 'bot' in message_lower or 'ai' in message_lower:
                return "feedback_bot"

        return None

    def handle_feedback_response(self, message, nick, feedback_type):
        """Generate natural response untuk feedback"""
        formatted_nick = self.format_nickname(nick)

        responses_map = {
            "feedback_like": [
                f"😍 Aku SUKA GILER {formatted_nick}! Memang match dengan personality aku!",
                f"Haha, suka sangat {formatted_nick}! Style tu memang aku punya style! 😎",
                f"Weh {formatted_nick}, aku SUKA! Straight to the point dengan lawak! 👍",
                f"😊 Aku suka! {formatted_nick} memang kenal aku lah!"
            ],
            "feedback_style": [
                f"Haha, gaya lawak tu memang macam aku lah {formatted_nick}! 😎 Santai & mesra!",
                f"Weh {formatted_nick}, betul tu! Aku memang prefer sembang santai gitu! 🏖️",
                f"Yo {formatted_nick}! Style tu memang perfect untuk aku! Ringkas & ada humor! 😂",
                f"Haha, {formatted_nick} kenal aku! Aku suka yang natural dengan lawak sikit! 🎯"
            ],
            "feedback_bot": [
                f"Haha, terima kasih {formatted_nick}! Aku try improve selalu! 😊",
                f"Weh {formatted_nick}, ada feedback lagi? Aku dengar! 👂",
                f"😎 {formatted_nick} bagi tips untuk aku? Aku appreciate!",
                f"Haha, {formatted_nick} supervise aku ke? Baik lah tu! 😆"
            ]
        }

        return random.choice(responses_map.get(feedback_type, [f"Haha, okay {formatted_nick}! 😊"]))

    def get_smart_fallback_response(self, message, nick, context):
        """Smart fallback untuk common patterns"""
        message_lower = message.lower()

        # Pattern 1: Welcome/greetings
        if any(word in message_lower for word in ['welcome', 'selamat', 'balik', 'back']):
            responses = [
                f"Haha, welcome balik {nick}! 😊",
                f"Yo {nick}! Ada apa? 👋", 
                f"Hi {nick}! Lama tak nampak! 🎯",
                f"Hey {nick}! Apa cerita? 🤗"
            ]
            return random.choice(responses)

        # Pattern 2: Apa khabar
        elif any(word in message_lower for word in ['apa khabar', 'kabar', 'how are']):
            responses = [
                f"Alhamdulillah sihat! {nick} pun sama kan? 😊",
                f"Sihat je! {nick} macam mana? 🏖️",
                f"Baik! {nick} mesti lagi baik! 👍",
                f"Ok je! {nick} ada apa? 🤔"
            ]
            return random.choice(responses)

        # Pattern 3: Zzz/boring
        elif any(word in message_lower for word in ['zzz', 'bosan', 'boring', 'lama']):
            responses = [
                f"Haha boring ke {nick}? 😅",
                f"Weh {nick}, cari cerita la! 🎭",
                f"Takde kerja ke {nick}? 😆",
                f"Haha, {nick} dah mengantuk! 😴"
            ]
            return random.choice(responses)

        # Pattern 4: Dah jawab
        elif any(word in message_lower for word in ['dah jawab', 'tadi', 'kan dah']):
            responses = [
                f"Haha ye ke? Sorry tak perasan {nick}! 😅",
                f"Oh ya! Lupa pulak! 😆",
                f"Haha, betul lah {nick}! 😊",
                f"Oops! My bad {nick}! 🙈"
            ]
            return random.choice(responses)

        return None

    def get_context_summary(self, channel, nick):
        """Buat summary konteks untuk AI"""
        recent_messages = []

        for msg in self.conversation_memory[-10:]:
            if msg['channel'] == channel:
                recent_messages.append(f"{msg['nick']}: {msg['message']}")

        # Cari pattern dalam conversation
        conversation_patterns = []

        # Check jika ada soalan "apa khabar" dan jawapan
        for i in range(len(recent_messages)-1, max(-1, len(recent_messages)-4), -1):
            if i >= 0:
                msg = recent_messages[i]
                if 'apa khabar' in msg.lower() or 'kabar' in msg.lower():
                    # Cari jawapan selepas soalan
                    for j in range(i+1, min(len(recent_messages), i+3)):
                        if nick.lower() in recent_messages[j].lower():
                            if any(word in recent_messages[j].lower() for word in ['sihat', 'baik', 'alhamdulillah', 'not bad', 'ok']):
                                conversation_patterns.append(f"{nick} dah jawab tentang khabar")
                                break

        summary = "\n".join(recent_messages[-4:])  # Last 4 messages sahaja

        if conversation_patterns:
            summary += f"\n\n**INFO: {', '.join(conversation_patterns)}**"

        return summary if summary else "(Tiada konteks)"

    # 🆕 TAMBAH METHOD BARU UNTUK ROBUST PARSING
    def parse_ai_response_robust(self, ai_text, is_in_focus=False):
        """
        Robust parser untuk AI response - COMPLETE FIXED VERSION
        Handle semua edge cases dari log error:
        1. Incomplete XML tags (<DECISION)
        2. Response terpotong (kek l)
        3. Decision words dalam response (TIDAK/YA)
        4. Multiple pattern errors
        """
        if not ai_text:
            print("🔧 PARSER: No AI text")
            return "NO", ""

        ai_text = ai_text.strip()
        original_text = ai_text

        print(f"🔧 PARSER ORIGINAL: '{ai_text[:150]}...'")

        # ==================== PHASE 1: CLEAN ALL ERROR PATTERNS ====================

        # 🛠️ FIX 1: Remove semua pattern error dari logs
        error_patterns = [
            # Pattern dari log: "! 🎮 <DECISION"
            (r'! 🎮 <DECISION.*', ''),

            # Incomplete XML tags
            (r'<DECISION\s*$', ''),
            (r'<\s*DECISION[^>]*$', ''),
            (r'<DECISION\s*[^>]*$', ''),

            # Broken tags
            (r'<TIDAK\s*</TIDAK>', 'TIDAK'),
            (r'<YA\s*</YA>', 'YA'),
            (r'<YES\s*</YES>', 'YES'),
            (r'<NO\s*</NO>', 'NO'),

            # CTCP ACTION remnants
            (r'\x01ACTION\s+', ''),
            (r'\x01', ''),

            # Bot command remnants
            (r'^\s*!\s*', ''),
        ]

        for pattern, replacement in error_patterns:
            ai_text = re.sub(pattern, replacement, ai_text, flags=re.IGNORECASE)

        # 🛠️ FIX 2: Clean leading/trailing punctuation
        ai_text = ai_text.strip(' .,;:!?*#')

        # ==================== PHASE 2: DETECT DECISION ====================

        decision = "NO"  # Default
        bot_response = ""

        # 🎯 PATTERN A: Standard XML format
        # <DECISION>YA</DECISION><RESPONSE>text</RESPONSE>
        xml_decision_match = re.search(
            r'<DECISION>\s*(YA|TIDAK|YES|NO)\s*</DECISION>',
            ai_text, 
            re.IGNORECASE
        )

        if xml_decision_match:
            decision_word = xml_decision_match.group(1).upper()
            decision = "YES" if decision_word in ['YA', 'YES'] else "NO"
            print(f"🔧 PARSER: Found XML decision: {decision_word} -> {decision}")

            # Extract response dari XML
            xml_response_match = re.search(
                r'<RESPONSE>(.*?)</RESPONSE>',
                ai_text,
                re.DOTALL | re.IGNORECASE
            )

            if xml_response_match:
                bot_response = xml_response_match.group(1).strip()
                print(f"🔧 PARSER: Found XML response")
            else:
                # Cari text selepas </DECISION>
                parts = re.split(r'</DECISION>', ai_text, 1, flags=re.IGNORECASE)
                if len(parts) > 1:
                    bot_response = parts[1].strip()
                    print(f"🔧 PARSER: Found response after </DECISION>")

        else:
            # 🎯 PATTERN B: Simple format - YA/TIDAK di awal
            # Format: YA\nresponse\nACTION: action_text
            # atau: TIDAK\nresponse

            # Check first 50 chars untuk decision word
            first_part = ai_text[:100].upper()

            # Cari YA/TIDAK sebagai standalone word
            ya_match = re.search(r'^\s*(YA|YES)\b', ai_text, re.IGNORECASE)
            tidak_match = re.search(r'^\s*(TIDAK|NO)\b', ai_text, re.IGNORECASE)

            if ya_match:
                decision = "YES"
                decision_word = ya_match.group(1)
                # Extract text selepas YA
                start_pos = ya_match.end()
                bot_response = ai_text[start_pos:].strip()
                print(f"🔧 PARSER: Found YA at start: {decision}")

            elif tidak_match:
                decision = "NO"
                decision_word = tidak_match.group(1)
                # Extract text selepas TIDAK
                start_pos = tidak_match.end()
                bot_response = ai_text[start_pos:].strip()
                print(f"🔧 PARSER: Found TIDAK at start: {decision}")

            else:
                # 🎯 PATTERN C: No clear decision, check content
                # Jika dalam focus mode, assume YES
                if is_in_focus:
                    decision = "YES"
                    bot_response = ai_text
                    print(f"🔧 PARSER: Focus mode, assuming YES")
                else:
                    # Check jika text kelihatan seperti response
                    is_likely_response = (
                        len(ai_text) > 10 and 
                        len(ai_text) < 300 and
                        not ai_text.startswith('<') and
                        not ai_text.endswith('>')
                    )

                    if is_likely_response:
                        decision = "YES"
                        bot_response = ai_text
                        print(f"🔧 PARSER: Text looks like response, assuming YES")
                    else:
                        decision = "NO"
                        print(f"🔧 PARSER: No decision pattern found, default NO")

        # ==================== PHASE 3: CLEAN RESPONSE ====================

        if bot_response:
            # 🛠️ FIX 3: Remove semua XML/HTML tags
            bot_response = re.sub(r'</?[A-Z][A-Z0-9]*[^>]*>', '', bot_response)

            # 🛠️ FIX 4: Remove common prefixes
            prefixes_to_remove = [
                'RESPONSE:', 'RESPONSE :', 'Response:', 'Balasan:', 
                'Jawapan:', 'Reply:', 'Answer:', 'RESPONSE=',
                'YA:', 'YES:', 'TIDAK:', 'NO:', 'DECISION:'
            ]

            for prefix in prefixes_to_remove:
                if bot_response.upper().startswith(prefix.upper()):
                    bot_response = bot_response[len(prefix):].strip()
                    print(f"🔧 PARSER: Removed prefix '{prefix}'")

            # 🛠️ FIX 5: Remove decision words jika masih ada
            bot_response = re.sub(
                r'^\s*(YA|YES|TIDAK|NO)\s*[:]?\s*',
                '', 
                bot_response, 
                flags=re.IGNORECASE
            )

            # 🛠️ FIX 6: Fix common truncation bugs dari logs
            truncation_fixes = [
                # "kek l" -> "kek lah"
                (r'\bkek l\b', 'kek lah'),
                (r'\bsist l\b', 'sistem lah'),
                (r'\btak l\b', 'tak lah'),

                # Potongan di huruf tunggal
                (r'\s+[a-zA-Z]\s*$', ''),

                # "!" di tengah atau akhir yang terasing
                (r'\s+!\s*$', '!'),
                (r'^\s*!\s*', ''),
            ]

            for pattern, replacement in truncation_fixes:
                if re.search(pattern, bot_response):
                    bot_response = re.sub(pattern, replacement, bot_response)
                    print(f"🔧 PARSER: Fixed truncation pattern '{pattern}'")

            # 🛠️ FIX 7: Fix punctuation
            bot_response = re.sub(r'\s+([.,!?;:])', r'\1', bot_response)
            bot_response = re.sub(r'([.,!?;:])(\S)', r'\1 \2', bot_response)

            # 🛠️ FIX 8: Remove extra whitespace
            bot_response = ' '.join(bot_response.split())

            # 🛠️ FIX 9: Capitalize first letter jika lowercase
            if bot_response and bot_response[0].islower():
                bot_response = bot_response[0].upper() + bot_response[1:]

            # 🛠️ FIX 10: Remove leading/trailing punctuation
            bot_response = bot_response.strip(' .,;:!?*#')

            # 🛠️ FIX 11: Jika response masih mengandungi "TIDAK" atau "YA" di akhir
            # dan ianya bukan part of word, remove
            last_word = bot_response.split()[-1] if bot_response.split() else ""
            if last_word.upper() in ['TIDAK', 'YA', 'NO', 'YES']:
                # Check jika ianya meaningful atau hanya decision remnant
                if len(bot_response.split()) > 2:  # Jika ada content lain
                    bot_response = ' '.join(bot_response.split()[:-1])
                    print(f"🔧 PARSER: Removed trailing decision word '{last_word}'")

            # 🛠️ FIX 12: Final validation
            if len(bot_response.strip()) < 3:
                print(f"🔧 PARSER: Response too short after cleaning: '{bot_response}'")
                bot_response = ""

        # ==================== PHASE 4: FOCUS MODE OVERRIDE ====================

        if is_in_focus:
            # Dalam focus mode, kita lebih aggressive untuk respond
            if decision == "NO" and bot_response and len(bot_response.strip()) > 5:
                print(f"🎯 PARSER: Focus mode overriding NO to YES")
                decision = "YES"

            # Jika decision YES tapi response kosong, guna original text
            elif decision == "YES" and (not bot_response or len(bot_response.strip()) < 3):
                print(f"🎯 PARSER: Focus mode using cleaned original text")
                bot_response = original_text
                # Clean again
                bot_response = re.sub(r'</?[^>]*>', '', bot_response)
                bot_response = bot_response.strip(' .,;:!?')

        # ==================== PHASE 5: VALIDATION ====================

        # Jika ada response tapi decision NO, check jika patut override
        if decision == "NO" and bot_response and len(bot_response.strip()) > 10:
            # Check jika response kelihatan meaningful
            has_punctuation = any(c in bot_response for c in '.!?')
            has_emoji = any(c in bot_response for c in '😊😂🤔🎯🏖️✨')

            if has_punctuation or has_emoji:
                print(f"🔧 PARSER: Response looks meaningful, overriding to YES")
                decision = "YES"

        # Jika decision YES tapi response kosong, tukar ke NO
        if decision == "YES" and (not bot_response or len(bot_response.strip()) < 3):
            print(f"🔧 PARSER: YES decision but empty response, changing to NO")
            decision = "NO"
            bot_response = ""

        # ==================== PHASE 6: LOGGING ====================

        print(f"🔧 PARSER FINAL: decision={decision}, response='{bot_response[:100] if bot_response else 'NONE'}...'")

        return decision, bot_response


    # ==================== SUPPORTING FUNCTIONS ====================

    def clean_ai_text_before_parsing(self, ai_text):
        """
        Pre-clean AI text sebelum parsing
        Handle common AI response issues
        """
        if not ai_text:
            return ""

        text = ai_text.strip()

        # 🛠️ Fix common AI quirks
        fixes = [
            # Remove quotation marks jika entire text dalam quotes
            (r'^["\'](.*)["\']$', r'\1'),

            # Remove markdown code blocks
            (r'```[\s\S]*?```', ''),
            (r'`[^`]*`', ''),

            # Remove asterisks untuk bold/italic
            (r'\*\*(.*?)\*\*', r'\1'),
            (r'\*(.*?)\*', r'\1'),

            # Remove leading numbers/bullets
            (r'^\s*\d+[\.\)]\s*', ''),
            (r'^\s*[•\-]\s*', ''),

            # Fix multiple newlines
            (r'\n\s*\n\s*\n', '\n\n'),

            # Fix extra spaces around punctuation
            (r'\s+([.,!?;:])', r'\1'),
            (r'([.,!?;:])(\S)', r'\1 \2'),
        ]

        for pattern, replacement in fixes:
            text = re.sub(pattern, replacement, text)

        return text.strip()


    def validate_response_format(self, decision, response):
        """
        Validate final response format
        """
        if decision == "YES":
            if not response or len(response.strip()) < 2:
                print(f"⚠️ VALIDATION: YES decision but invalid response")
                return "NO", ""

            # Check jika response hanya decision word
            response_upper = response.upper().strip()
            if response_upper in ['YA', 'YES', 'TIDAK', 'NO', 'OK', '...']:
                print(f"⚠️ VALIDATION: Response is just a word: '{response}'")
                return "NO", ""

            # Check jika response terlalu pendek
            if len(response) < 4:
                print(f"⚠️ VALIDATION: Response too short: '{response}'")
                return "NO", ""

        return decision, response
    
    def xparse_ai_response_robust(self, ai_text, is_in_focus=False):
        """Robust parser untuk berbagai format AI response - FIXED VERSION"""
        if not ai_text:
            return "NO", ""

        ai_text = ai_text.strip()
        original_text = ai_text

        print(f"🔧 ORIGINAL AI TEXT: '{ai_text[:150]}...'")

        # 🛠️ FIX CRITICAL: Handle case di mana server sudah bagi response tanpa XML
        # Contoh: "Apa yang salah sini, kawan? 😂" ← Response normal, bukan XML

        # 🛠️ FIX 1: Jika text pendek (< 200 chars) dan tak ada pattern XML, assume YES dengan full response
        if len(ai_text) < 200 and not any(pattern in ai_text for pattern in ['<DECISION', '</DECISION>', '<RESPONSE', '</RESPONSE>']):
            # Check jika ini mungkin response normal, bukan decision
            # Look for YA/TIDAK hanya sebagai PERKATAAN PENUH
            words = ai_text.split()
            has_decision_word = False

            for i, word in enumerate(words):
                clean_word = re.sub(r'[^a-zA-Z]', '', word).upper()
                if clean_word in ['YA', 'YES', 'TIDAK', 'NO']:
                    # Check jika itu perkataan penuh (bukan substring)
                    if i == 0 or word.upper() in [word.upper() for word in ['YA', 'YES', 'TIDAK', 'NO']]:
                        has_decision_word = True
                        print(f"🔧 Found decision word as standalone: {word}")
                        break

            if not has_decision_word:
                # Ini response biasa tanpa decision XML
                print(f"🔧 No XML tags detected, using as full response")
                decision = "YES"
                bot_response = ai_text

                # SPECIAL CASE: Jika dalam focus mode
                if is_in_focus:
                    print(f"🎯 FOCUS MODE: Auto-YES for focus user")
                    decision = "YES"

                # Clean response
                bot_response = self.clean_response_text(bot_response)
                print(f"🔧 CLEANED RESPONSE: '{bot_response[:100]}...'")
                print(f"🔧 FINAL: {decision}, '{bot_response[:80]}...'")
                return decision, bot_response

        # 🛠️ FIX 2: Handle pattern '! 🎮 <DECISION' dari log error
        if '! 🎮 <DECISION' in ai_text:
            print(f"🛠️ FIXING '! 🎮 <DECISION' pattern")
            # Extract selepas <DECISION
            parts = ai_text.split('<DECISION')
            if len(parts) > 1:
                content = parts[1].strip()

                # Check untuk YA/TIDAK sebagai perkataan penuh
                decision = "NO"
                bot_response = ""

                # Pattern untuk YA/TIDAK sebagai perkataan penuh
                if re.search(r'\b(YA|YES)\b', content, re.IGNORECASE):
                    decision = "YES"
                    # Remove YA/YES dari response
                    bot_response = re.sub(r'\b(YA|YES)\b\s*[:]?\s*', '', content, flags=re.IGNORECASE).strip()
                elif re.search(r'\b(TIDAK|NO)\b', content, re.IGNORECASE):
                    decision = "NO"
                    # Remove TIDAK/NO dari response
                    bot_response = re.sub(r'\b(TIDAK|NO)\b\s*[:]?\s*', '', content, flags=re.IGNORECASE).strip()
                else:
                    decision = "NO"
                    bot_response = content.strip()

                print(f"🛠️ FIXED '! 🎮 <DECISION': {decision} - '{bot_response[:80]}...'")
                return decision, bot_response

        # 🛠️ FIX 3: Standard XML fixes
        fixes = [
            # Fix broken tags
            (r'<TIDAK\s*</TIDAK>', '<DECISION>TIDAK</DECISION>'),
            (r'<YA\s*</YA>', '<DECISION>YA</DECISION>'),
            (r'<YES\s*</YES>', '<DECISION>YES</DECISION>'),
            (r'<NO\s*</NO>', '<DECISION>NO</DECISION>'),

            # Fix missing closing tags
            (r'<DECISION>\s*YA\s*$', '<DECISION>YA</DECISION>'),
            (r'<DECISION>\s*TIDAK\s*$', '<DECISION>TIDAK</DECISION>'),
            (r'<DECISION>\s*YES\s*$', '<DECISION>YES</DECISION>'),
            (r'<DECISION>\s*NO\s*$', '<DECISION>NO</DECISION>'),
        ]

        for pattern, replacement in fixes:
            ai_text = re.sub(pattern, replacement, ai_text, flags=re.IGNORECASE)

        print(f"🔧 AFTER XML FIXES: '{ai_text[:150]}...'")

        # 🛠️ EXTRACT DECISION DENGAN LOGIC BARU
        decision = "NO"
        bot_response = ""

        # Method 1: Cari <DECISION> tag
        decision_match = re.search(r'<DECISION>\s*(YA|TIDAK|YES|NO)\s*</DECISION>', ai_text, re.IGNORECASE)

        if decision_match:
            decision_word = decision_match.group(1).upper()
            decision = "YES" if decision_word in ['YA', 'YES'] else "NO"
            print(f"🔧 Found decision in XML: {decision_word} -> {decision}")

            # Extract response
            response_match = re.search(r'<RESPONSE>(.*?)</RESPONSE>', ai_text, re.DOTALL | re.IGNORECASE)
            if response_match:
                bot_response = response_match.group(1).strip()
                print(f"🔧 Found response in XML tags")
            else:
                # Cari text selepas </DECISION>
                parts = re.split(r'</DECISION>', ai_text, 1, flags=re.IGNORECASE)
                if len(parts) > 1 and parts[1].strip():
                    bot_response = parts[1].strip()
                    print(f"🔧 Found response after </DECISION>")
        else:
            # Method 2: Cari YA/TIDAK sebagai PERKATAAN PENUH sahaja
            # Pattern: \b untuk word boundary (perkataan penuh)
            ya_match = re.search(r'\b(YA|YES)\b', ai_text[:100], re.IGNORECASE)
            tidak_match = re.search(r'\b(TIDAK|NO)\b', ai_text[:100], re.IGNORECASE)

            if ya_match:
                decision = "YES"
                # Extract response selepas YA/YES
                response_start = ya_match.end()
                bot_response = ai_text[response_start:].strip()
                print(f"🔧 Found YA/YES as standalone word, decision: YES")

                # Clean response (remove YA: atau YES: jika ada)
                bot_response = re.sub(r'^\s*[:]?\s*', '', bot_response)

            elif tidak_match:
                decision = "NO"
                # Extract response selepas TIDAK/NO
                response_start = tidak_match.end()
                bot_response = ai_text[response_start:].strip()
                print(f"🔧 Found TIDAK/NO as standalone word, decision: NO")

                # Clean response (remove TIDAK: atau NO: jika ada)
                bot_response = re.sub(r'^\s*[:]?\s*', '', bot_response)
            else:
                # Method 3: Tiada decision word, check jika ini response normal
                if len(ai_text) > 10 and len(ai_text) < 500:
                    # Check jika text kelihatan seperti response normal
                    # (ada punctuation, normal sentence structure)
                    has_punctuation = any(punc in ai_text for punc in ['.', '!', '?', '😊', '😂', '🤔'])

                    if has_punctuation:
                        decision = "YES"
                        bot_response = ai_text.strip()
                        print(f"🔧 No decision word, but looks like normal response. Assuming YES")
                    else:
                        decision = "NO"
                        print(f"🔧 No decision word and doesn't look like response. Decision: NO")
                else:
                    decision = "NO"
                    print(f"🔧 No decision pattern found. Decision: NO")

        # 🛠️ CLEAN RESPONSE
        if bot_response:
            bot_response = self.clean_response_text(bot_response)

            # Final validation
            if len(bot_response.strip()) < 3:
                print(f"🔧 Response too short after cleaning, forcing NO")
                decision = "NO"
                bot_response = ""

        # 🛠️ FOCUS MODE OVERRIDE
        if is_in_focus and bot_response and len(bot_response.strip()) > 5:
            if decision == "NO":
                print(f"🎯 FOCUS MODE: Overriding NO decision to YES")
                decision = "YES"
            elif decision == "YES" and not bot_response:
                # Jika YES tapi response kosong, ambil original text
                bot_response = original_text
                print(f"🎯 FOCUS MODE: Using original text as response")

        print(f"🔧 FINAL DECISION: {decision}, RESPONSE: '{bot_response[:80] if bot_response else 'NONE'}...'")

        return decision, bot_response

    def clean_response_text(self, text):
        """Clean response text dari XML tags dan formatting"""
        if not text:
            return ""

        # Remove semua XML-like tags
        text = re.sub(r'</?[A-Z][A-Z0-9]*[^>]*>', '', text)

        # Remove common prefixes
        prefixes_to_remove = [
            'RESPONSE:', 'RESPONSE :', 'Response:', 
            'Balasan:', 'Jawapan:', 'Reply:', 'Answer:',
            'YA:', 'YES:', 'TIDAK:', 'NO:'
        ]

        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()

        # Remove decision words jika masih ada (perkataan penuh sahaja)
        text = re.sub(r'^\s*\b(YA|YES|TIDAK|NO)\b\s*[:]?\s*', '', text, flags=re.IGNORECASE)

        # Fix punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])(\S)', r'\1 \2', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        # Remove leading/trailing punctuation
        text = text.strip(' .,;:!?')

        return text

    # ==================== NICK CHANGE DETECTION ====================
    def detect_nick_change(self, line):
        """Detect NICK changes - dengan CTCP ACTION format"""
        if " NICK " in line and "!" in line:
            try:
                old_nick = line.split("!")[0][1:]
                new_nick = line.split(" :")[1]

                # Skip jika guest nick
                if new_nick.lower().startswith("guest"):
                    print(f"🚫 Ignoring guest nick change: {old_nick} -> {new_nick}")
                    return
                if old_nick.lower().startswith("guest"):
                    print(f"🚫 Ignoring from guest nick: {old_nick} -> {new_nick}")
                    return

                if old_nick != new_nick:
                    print(f"🔄 Nick change: {old_nick} -> {new_nick}")

                    # Cari channel bersama
                    shared_channels = self.find_shared_channels(old_nick)

                    if shared_channels:
                        # 🎯 CTCP ACTION MESSAGES
                        action_messages = [
                            f"nampak {old_nick} bertukar jadi {new_nick}",
                            f"perasan {old_nick} tukar nick jadi {new_nick}",
                            f"alert! {old_nick} dah jadi {new_nick}",
                            f"weh {old_nick} tukar jadi {new_nick}",
                            f"eh {old_nick} transform jadi {new_nick}",
                            f"berita terkini {old_nick} tukar identity jadi {new_nick}",
                            f"update: {old_nick} -> {new_nick}",
                            f"psst.. {old_nick} tukar jadi {new_nick}",
                            f"wow {old_nick} tukar nick jadi {new_nick}",
                            f"check it out: {old_nick} tukar jadi {new_nick}"
                        ]

                        selected_action = random.choice(action_messages)

                        # Tambah emoji sekali-sekala (50% chance)
                        if random.random() > 0.5:
                            emojis = ["😅", "👀", "⚡", "🏃💨", "💥", "🦋", "📝", "🕵️", "🎨", "🔄"]
                            selected_action += f" {random.choice(emojis)}"

                        # Hantar ke setiap shared channel
                        for channel in shared_channels:
                            self.send_action(channel, selected_action)
                            print(f"📢 CTCP ACTION in {channel}: {selected_action}")

                        print(f"✅ Notified {len(shared_channels)} channels")
                    else:
                        print(f"ℹ️ No shared channels with {old_nick}")

            except Exception as e:
                print(f"❌ Nick change error: {e}")

    def find_shared_channels(self, nick):
        """Cari channel yang both user dan bot berada"""
        shared_channels = []

        # 🎯 CARA 1: Dari tracked channel_users
        if hasattr(self, 'channel_users'):
            for channel, users in self.channel_users.items():
                # Check jika user dan bot dalam channel yang sama
                if (nick in users and 
                    channel in self.channels and  # Bot dalam channel ini
                    self.nick in users):          # Bot tracked dalam users list
                    shared_channels.append(channel)

        # 🎯 CARA 2: Fallback - check jika channel dalam bot's channel list
        if not shared_channels and hasattr(self, 'channels'):
            # Assume user berada dalam semua channel bot
            # (Ini fallback jika tracking tak perfect)
            for channel in self.channels:
                if channel in self.channel_users.get(channel, []):
                    if nick in self.channel_users[channel]:
                        shared_channels.append(channel)

        # 🎯 CARA 3: Check conversation memory
        if not shared_channels and hasattr(self, 'conversation_memory'):
            recent_channels = set()
            for msg in self.conversation_memory[-20:]:
                if msg['nick'] == nick and msg['channel'] in self.channels:
                    recent_channels.add(msg['channel'])

            if recent_channels:
                shared_channels = list(recent_channels)

        print(f"🔍 Shared channels with {nick}: {shared_channels}")
        return shared_channels

    def find_user_channels(self, nick):
        """Cari channel yang user berada"""
        user_channels = []

        # Check tracked data
        if hasattr(self, 'channel_users') and self.channel_users:
            for channel, users in self.channel_users.items():
                if nick in users:
                    user_channels.append(channel)

        # Fallback: check recent messages
        if not user_channels and hasattr(self, 'conversation_memory'):
            recent_channels = set()
            for msg in self.conversation_memory[-20:]:
                if msg['nick'] == nick:
                    recent_channels.add(msg['channel'])

            if recent_channels:
                user_channels = list(recent_channels)

        # If still not found, assume bot channels
        if not user_channels and hasattr(self, 'channels'):
            user_channels = self.channels[:]

        return user_channels

    # ==================== MAIN LOOP ====================
    def run(self):
        """Main bot loop dengan case-insensitive channel handling"""
        print("🚀 Starting MinahBot dengan Case-Insensitive Channels...")

        self.connect()
        buffer = ""

        # Initialize last cleanup time
        self.last_cleanup_time = time.time()

        while self.running:
            try:
                self.sock.settimeout(1.0)

                # 🧹 CHECK AUTO-CLEANUP
                current_time = time.time()
                if current_time - self.last_cleanup_time >= self.cleanup_interval:
                    print("⏰ Checkpoint: Running auto-cleanup...")
                    self.cleanup_old_messages()

                try:
                    data = self.sock.recv(2048).decode('utf-8', errors='ignore')
                except socket.timeout:
                    if self.message_queue:
                        self.process_queue()
                    self.cleanup_expired_focus()
                    self.check_silent_mode()
                    continue

                if not data:
                    print("❌ Connection closed by server")
                    time.sleep(10)
                    self.connect()
                    continue

                buffer += data
                lines = buffer.split("\r\n")
                buffer = lines.pop()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Handle PING
                    if line.startswith("PING"):
                        ping_data = line.split(":")[1] if ":" in line else ""
                        self.send_raw(f"PONG :{ping_data}")
                        continue

                    # Handle NICK changes
                    if " NICK " in line and "!" in line:
                        try:
                            self.detect_nick_change(line)
                        except Exception as e:
                            print(f"❌ Error processing nick change: {e}")

                    # Parse PRIVMSG
                    if "PRIVMSG" in line:
                        try:
                            sender_part = line.split(' ')[0]
                            sender = sender_part[1:].split('!')[0]

                            # Skip jika message dari diri sendiri
                            if sender.lower() == self.nick.lower():
                                continue

                            parts = line.split(' ', 3)
                            if len(parts) >= 4:
                                target = parts[2]
                                message = parts[3][1:] if parts[3].startswith(':') else parts[3]

                                print(f"📩 FROM {sender} TO {target}: '{message[:100]}...'")

                                # 🛠️ FIXED: Private message ke bot
                                if target.lower() == self.nick.lower():
                                    print(f"🔥 PRIVATE MESSAGE FROM {sender}")

                                    if self.private_chat_enabled:
                                        threading.Thread(
                                            target=self.handle_private_message,
                                            args=(sender, message),
                                            daemon=True
                                        ).start()

                                # 🛠️ FIXED: Channel message (CASE-INSENSITIVE)
                                elif target.startswith('#'):
                                    # Convert target ke lowercase untuk comparison
                                    target_lower = target.lower()

                                    # Cari matching channel dari list kita
                                    matched_channel = None
                                    for channel in self.channels:
                                        if channel.lower() == target_lower:
                                            matched_channel = channel
                                            break

                                    if matched_channel and sender != self.nick:
                                        print(f"📢 CHANNEL MESSAGE in {target} (matched to {matched_channel}) from {sender}")

                                        # Track dengan canonical channel name
                                        if matched_channel not in self.channel_activity:
                                            self.channel_activity[matched_channel] = 0
                                        self.channel_activity[matched_channel] += 1

                                        # Process dengan canonical channel name
                                        threading.Thread(
                                            target=self.process_message,
                                            args=(sender, message, matched_channel),
                                            daemon=True
                                        ).start()
                                    else:
                                        print(f"⚠️ Ignoring message in {target} (not in channel list)")
                                        print(f"   Looking for: {target_lower}")
                                        print(f"   Our channels: {[c.lower() for c in self.channels]}")

                        except Exception as e:
                            print(f"❌ PRIVMSG parse error: {e}")
                            print(f"   Line: {line}")

                    # Handle numeric replies
                    elif line.startswith(':'):
                        parts = line.split()
                        if len(parts) > 1 and parts[1].isdigit():
                            code = parts[1]

                            if code in ['001', '376', '422']:
                                print(f"✅ Registered with server: {code}")
                                self.connected = True

                                # Join semua channel
                                for channel in self.channels:
                                    self.send_raw(f"JOIN {channel}")
                                    print(f"✅ Joining {channel}")
                                    time.sleep(1)

                            elif code == '433':
                                print(f"⚠️ Nick '{self.nick}' in use, changing...")
                                self.nick = f"{self.nick}_"
                                self.send_raw(f"NICK {self.nick}")

                            # 🛠️ FIXED: Channel user list (353) dengan case-insensitive
                            elif code == '353':
                                if len(parts) >= 5:
                                    channel_from_server = parts[4]
                                    users_msg = ' '.join(parts[5:])[1:] if len(parts) > 5 else ""
                                    users = users_msg.split()

                                    # Cari matching channel dari list kita
                                    matched_channel = None
                                    for channel in self.channels:
                                        if channel.lower() == channel_from_server.lower():
                                            matched_channel = channel
                                            break

                                    if matched_channel:
                                        # Track users dengan canonical channel name
                                        if matched_channel not in self.channel_users:
                                            self.channel_users[matched_channel] = set()

                                        for user in users:
                                            clean_user = user.lstrip('@+%&~')
                                            self.channel_users[matched_channel].add(clean_user)

                                        print(f"👥 {len(users)} users in {matched_channel} (from server: {channel_from_server})")

                # Process queue dan cleanup
                if self.message_queue:
                    self.process_queue()

                self.cleanup_expired_focus()
                self.check_silent_mode()

                # Periodic tasks
                if int(time.time()) % 300 == 0:
                    self.log_bot_stats()

                if int(time.time()) % 600 == 0:
                    self.cleanup_old_buffers()

            except socket.error as e:
                print(f"❌ Socket error: {e}")
                time.sleep(15)
                self.connect()

            except Exception as e:
                print(f"❌ Main loop error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(30)
                if not self.connected:
                    self.connect()


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    # ⭐ PERINGATAN: GANTI API KEY ANDA!
    print("="*60)
    print("⚠️  PERHATIAN: GANTI API KEY PADA BARIS 44!")
    print(f"   Current: {MinahBot().__dict__.get('api_key', 'NOT SET')}")
    print("="*60)

    # Create and run bot
    bot = MinahBot()

    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot crashed: {e}")
        import traceback
        traceback.print_exc()
