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
import requests
import json
import os
from collections import deque

class MinahBot:
    def __init__(self):
        # IRC Config
        self.server = "irc.kampungchat.org"
        self.port = 6668
        self.nick = "minah"
        self.channels = ["#ace", "#alamanda", "#bro", "#desa", "#zumba"]

        # AI API Config
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        # Connection objects
        self.connection = None
        self.running = False

        # Focus system
        self.user_focus = {}  # {user: focus_until_timestamp}
        self.focus_duration = 300  # 5 minutes focus

        # Mention tracking for focus trigger
        self.user_mentions = {}  # user -> {'total_count': X, 'last_mention_time': timestamp}
        self.mentions_threshold = 3  # 3 total mentions to trigger focus

        # 🆕 PER-CHANNEL 3-SECOND CONTEXT WINDOW
        self.message_buffers = {}  # channel -> list of messages
        self.last_buffer_process = {}  # channel -> last process time

        # Silent mode
        self.silent_mode = False
        self.silent_until = 0

        # Memory System
        self.conversation_memory = []
        self.max_messages = 30

        # Message Queue System
        self.message_queue = deque()
        self.is_sending = False
        self.last_send_time = 0
        self.min_delay = 3
        self.max_queue_size = 15

        # AI Cooldown
        self.last_ai_time = 0

        # 🆕 CHANNEL TRACKING
        self.channel_users = {}  # {channel: set([user1, user2, ...])}
        self.channel_activity = {}  # {channel: message_count}

        # Debug info
        print(f"🤖 Bot initialized:")
        print(f"   Nick: {self.nick}")
        print(f"   Channels: {self.channels}")
        print(f"   Private chat: ENABLED (40% invite chance)")
        print(f"   Focus system: ENABLED (3 mentions)")

    def detect_language_enhanced(self, text):
        """Enhanced custom language detection - NO EXTERNAL DEPS"""
        text_lower = text.lower()

        # Extended Malay dictionary
        malay_keywords = {
            'saya', 'awak', 'kamu', 'aku', 'ko', 'dia', 'mereka', 'kami', 'kita',
            'apa', 'mana', 'kenapa', 'bagaimana', 'bila', 'berapa', 'mengapa',
            'nak', 'tak', 'lah', 'pun', 'sangat', 'amat', 'sekali', 'sikit',
            'sudah', 'belum', 'pernah', 'akan', 'boleh', 'harus', 'mesti',
            'jom', 'mari', 'ayuh', 'baik', 'bagus', 'teruk', 'cantik',
            'terima kasih', 'maaf', 'tolong', 'sila', 'harap', 'minta',
            'hari', 'malam', 'pagi', 'petang', 'esok', 'semalam', 'tadi',
            'makan', 'minum', 'tidur', 'kerja', 'main', 'belajar', 'baca',
            'rumah', 'kereta', 'motor', 'bas', 'teksi', 'jalan',
            'malaysia', 'kelantan', 'terengganu', 'selangor', 'johor', 'kl',
            'nak', 'tak', 'kan', 'lah', 'pun', 'nya', 'ke', 'tu', 'ni'
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

        print(f"🔍 Language detection - Malay: {malay_score}, English: {english_score}")

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

    def connect(self):
        """Simple connection"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            self.sock.connect((self.server, self.port))

            self.send_raw(f"NICK {self.nick}")
            self.send_raw(f"USER {self.nick} 0 * :Hidup Anugerah Terindah")
            time.sleep(3)

            for channel in self.channels:
                self.send_raw(f"JOIN {channel}")
                print(f"✅ Joined {channel}")
                time.sleep(1)

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            time.sleep(15)
            self.connect()

    def send_raw(self, message):
        """Simple send method"""
        try:
            self.sock.send(f"{message}\r\n".encode())
            print(f"📤: {message}")
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Send error: {e}")

    def send_message(self, target, message):
        """Send message dengan queue system - MAX 4 LINES"""
        formatted_messages = self.format_long_message(message)

        if len(formatted_messages) > 4:
            formatted_messages = formatted_messages[:4]
            print(f"📝 LIMITED to 4 lines")

        for formatted_msg in formatted_messages:
            self.queue_message(target, formatted_msg, priority=1)

    def format_long_message(self, message):
        """Format long messages into multiple shorter lines"""
        if len(message) <= 120:
            return [message]

        print(f"✂️ Splitting long message: {len(message)} chars")

        sentences = re.split(r'([.!?]+[\s])', message)
        sentences = [s.strip() for s in sentences if s.strip()]

        formatted_lines = []
        current_line = ""

        for sentence in sentences:
            test_line = current_line + " " + sentence if current_line else sentence

            if len(test_line) <= 80:
                current_line = test_line
            else:
                if current_line:
                    formatted_lines.append(current_line.strip())
                current_line = sentence

        if current_line:
            formatted_lines.append(current_line.strip())

        print(f"📄 Formatted into {len(formatted_lines)} lines")
        return formatted_lines

    def send_action(self, target, action_text):
        """Send ACTION (/me)"""
        action_message = f"\x01ACTION {action_text}\x01"
        self.queue_message(target, action_message, priority=1)

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
                self.send_raw(f"PRIVMSG {target} :{message}")
                self.last_send_time = current_time

                print(f"✅ MAGIC SENT: '{message}'")
                print(f"📊 Queue remaining: {len(self.message_queue)}")

                if self.message_queue:
                    delay = random.uniform(1.0, 2.0)
                    print(f"⏳ Partial delay: {delay:.1f}s")
                    time.sleep(delay)

        except Exception as e:
            print(f"❌ Queue error: {e}")
        finally:
            self.is_sending = False

    def add_to_memory(self, nick, message, channel):
        """Add message to memory - DIPERBAIKI VERSION"""

        # 🎯 Check jika message dari bot sendiri
        if nick.lower() == self.nick.lower():
            return

        # 🎯 Check jika dari bot lain
        is_bot = self.is_bot_message(nick, message)

        if is_bot:
            # Special cleaning untuk bot messages
            clean_message = self.clean_bot_message(message, nick)

            # Skip jika tidak ada meaningful content selepas cleaning
            if not clean_message or len(clean_message) < 5:
                print(f"🤖 Skipped bot message from {nick}: No meaningful content")
                return

            print(f"🤖 Bot message cleaned ({nick}): '{clean_message[:50]}...'")
        else:
            # Normal cleaning untuk human messages
            clean_message = self.strip_irc_formatting_regex(message)

        # 🎯 Skip conditions
        skip_conditions = [
            not clean_message,
            len(clean_message.strip()) < 2,
            clean_message.startswith('ACTION'),
            clean_message.lower() in ['ping', 'pong', 'test', 'hello', 'hi'],
        ]

        if any(skip_conditions):
            return

        # 🎯 Add to memory
        self.conversation_memory.append({
            'nick': nick,
            'message': clean_message,
            'channel': channel,
            'timestamp': time.time(),
            'time_str': time.strftime('%I:%M%p', time.localtime()).lower(),
            'is_bot': is_bot
        })

        # 🎯 MEMORY MANAGEMENT - FIXED VERSION
        MAX_MEMORY = 30

        if len(self.conversation_memory) > MAX_MEMORY:
            # 🎯 Calculate how many to remove
            to_remove = len(self.conversation_memory) - MAX_MEMORY
            removed = self.conversation_memory[:to_remove]

            # 🎯 Keep only last MAX_MEMORY messages
            self.conversation_memory = self.conversation_memory[-MAX_MEMORY:]

            # 🎯 Log details
            bot_count = sum(1 for msg in removed if msg.get('is_bot', False))
            human_count = len(removed) - bot_count

            print(f"🧹 Memory: Removed {len(removed)} messages ({human_count} humans, {bot_count} bots)")
            print(f"🧹 Kept: {len(self.conversation_memory)}/{MAX_MEMORY} messages")

        # 🎯 Print current memory status
        bot_in_memory = sum(1 for msg in self.conversation_memory if msg.get('is_bot', False))
        human_in_memory = len(self.conversation_memory) - bot_in_memory

        print(f"🧠 Memory: {len(self.conversation_memory)}/{MAX_MEMORY} ({human_in_memory} humans, {bot_in_memory} bots)")

    def strip_irc_formatting_regex(self, text):
        """Strip IRC formatting using regex - WITH KCFM SPECIAL HANDLING"""
        import re

        if not isinstance(text, str):
            return ""

        # ⭐⭐⭐ SPECIAL CASE: KCFM BOT MESSAGES ⭐⭐⭐
        # Jika dari bot KCFM, handle secara special
        if '<%KCFM>' in text or 'KCFM' in text:
            return self.clean_kcfm_message(text)

        cleaned = text

        # Remove IRC color codes: \x03NN or \x03NN,MM
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

    def clean_kcfm_message(self, text):
        """Special cleaner untuk KCFM bot messages"""
        import re

        # Contoh: "01,14[11,14K07,14C04,14F03,14M 08,14Radio01,14]01,14 Song: ..."

        # Step 1: Remove KCFM number codes (NN,NN pattern)
        # Pattern: 2 digits, comma, 2 digits
        kcfm_code_pattern = r'\b\d{1,2},\d{1,2}\b'
        cleaned = re.sub(kcfm_code_pattern, '', text)

        # Step 2: Remove angle brackets and bot name
        cleaned = cleaned.replace('<', '').replace('>', '')
        cleaned = cleaned.replace('%KCFM', '').replace('KCFM:', '')

        # Step 3: Remove IRC formatting jika ada
        cleaned = re.sub(r'\x03\d{0,2}(,\d{0,2})?', '', cleaned)
        cleaned = re.sub(r'[\x00-\x1F]', '', cleaned)

        # Step 4: Clean up brackets and extra punctuation
        cleaned = cleaned.replace('[,]', '').replace('[]', '')
        cleaned = cleaned.replace('  ', ' ')

        # Step 5: Extract hanya content yang meaningful
        # Cari "Song:" untuk dapatkan song info
        if 'Song:' in cleaned:
            song_start = cleaned.find('Song:')
            cleaned = cleaned[song_start:]  # Keep dari "Song:" dan seterusnya

        # Step 6: Remove leading/trailing punctuation
        cleaned = cleaned.strip(' ,:;[]')

        # Step 7: Final cleanup
        cleaned = ' '.join(cleaned.split())

        # Jika terlalu pendek selepas cleaning, mungkin kita nak skip
        if len(cleaned) < 10:
            return ""  # Skip dari memory

        return cleaned.strip()

    def clean_bot_message(self, text, bot_name=None):
        """Universal cleaner untuk semua bot messages dengan formatting codes"""
        import re

        if not text:
            return ""

        cleaned = text

        # 🆕 CHECK JIKA INI AI RESPONSE (dari bot kita sendiri)
        is_ai_response = (bot_name == self.nick)

        if is_ai_response:
            # 🆕 AI-SPECIFIC CLEANING (lebih gentle)
            # Fix punctuation spacing
            cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned)
            cleaned = re.sub(r'([.,!?;:])(?!\.\.\.)(\w)', r'\1 \2', cleaned)
            cleaned = re.sub(r'\s+\.\.\.', '...', cleaned)

            # Remove XML tags
            cleaned = re.sub(r'</?[A-Z]+[^>]*>', '', cleaned, flags=re.IGNORECASE)

            # Clean multiple spaces
            cleaned = ' '.join(cleaned.split())

            # Capitalize first letter
            if len(cleaned) > 1:
                cleaned = cleaned[0].upper() + cleaned[1:]

            # Remove leading/trailing punctuation
            cleaned = cleaned.strip(' .,!?;:')

            return cleaned

        # 🆕 ORIGINAL CLEANING FOR OTHER BOTS

        # ⭐⭐⭐ LIST OF COMMON BOT FORMATTING PATTERNS ⭐⭐⭐
        # Pattern 1: NN,NN (KCFM style)
        cleaned = re.sub(r'\b\d{1,2},\d{1,2}\b', '', cleaned)

        # Pattern 2: [NN] or (NN) 
        cleaned = re.sub(r'\[?\d{1,3}\]?', '', cleaned)
        cleaned = re.sub(r'\(?\d{1,3}\)?', '', cleaned)

        # Pattern 3: Color tags seperti {red}, [blue], etc.
        cleaned = re.sub(r'\{[a-z]+\}', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\[[a-z]+\]', '', cleaned, flags=re.IGNORECASE)

        # Pattern 4: HTML-like tags <color=red>
        cleaned = re.sub(r'<[^>]+>', '', cleaned)

        # Pattern 5: ANSI color codes \x1b[31m
        cleaned = re.sub(r'\x1b\[[0-9;]*m', '', cleaned)

        # ⭐⭐⭐ REMOVE COMMON BOT PREFIXES ⭐⭐⭐
        bot_prefixes = [
            '>>', '<<', '--', '++', '**', '%%', '&&',
            '[BOT]', '[INFO]', '[STATUS]', '[UPDATE]',
            '<BOT>', '<INFO>', '<STATUS>',
            '•', '→', '»', '›'
        ]

        for prefix in bot_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()

        # ⭐⭐⭐ REMOVE IRC FORMATTING ⭐⭐⭐
        cleaned = re.sub(r'\x03\d{0,2}(,\d{0,2})?', '', cleaned)  # Colors
        cleaned = re.sub(r'[\x00-\x1F\x7F]', '', cleaned)  # Control chars

        # Remove common formatting codes
        formatting = {
            '\x02': '', '\x1F': '', '\x16': '', '\x0F': '', 
            '\x1D': '', '\x01': '', '\x1E': '', '\x11': '',
            '\x12': '', '\x13': '', '\x14': '', '\x15': '',
        }

        for code, replacement in formatting.items():
            cleaned = cleaned.replace(code, replacement)

        # ⭐⭐⭐ EXTRACT MEANINGFUL CONTENT ⭐⭐⭐
        # Cari keywords yang meaningful
        meaningful_keywords = [
            'song:', 'music:', 'playing:', 'now playing:',
            'dj:', 'listeners:', 'title:', 'artist:',
            'news:', 'weather:', 'time:', 'score:', 
            'result:', 'update:', 'alert:', 'warning:',
        ]

        # Jika ada meaningful keywords, keep dari keyword itu
        for keyword in meaningful_keywords:
            if keyword in cleaned.lower():
                idx = cleaned.lower().find(keyword)
                cleaned = cleaned[idx:]  # Keep dari keyword
                break

        # ⭐⭐⭐ FINAL CLEANUP ⭐⭐⭐
        # Remove extra punctuation
        cleaned = re.sub(r'[\[\]{}()<>]', '', cleaned)

        # Remove multiple spaces
        cleaned = ' '.join(cleaned.split())

        # Remove leading/trailing punctuation
        cleaned = cleaned.strip(' ,.:;!?+-=|*')

        # Jika terlalu pendek, mungkin kosong sahaja
        if len(cleaned) < 5:
            return ""

        return cleaned.strip()

    def is_bot_message(self, nick, text):
        """Check jika message dari bot"""
        bot_indicators = [
            # Bot nicks
            'KCFM', 'RADIO', 'BOT', 'SERV', 'NICKSERV', 'CHANSERV',
            'MEMOSERV', 'OPERSERV', 'STATS', 'INFO', 'HELP',

            # Bot patterns dalam text
            '<%', '%>', '[BOT]', '(bot)', '-BOT-',
            'auto', 'auto:', 'system:', 'server:',
        ]

        nick_lower = nick.lower()
        text_lower = text.lower() if text else ""

        # Check nick
        for indicator in bot_indicators:
            if indicator.lower() in nick_lower:
                return True

        # Check text content
        for indicator in bot_indicators:
            if indicator.lower() in text_lower:
                return True

        # Check jika ada formatting codes yang banyak (typical bot)
        if text:
            control_chars = sum(1 for c in text if ord(c) < 32)
            if control_chars > 3:  # Jika banyak control characters
                return True

        return False

    def update_user_focus(self, user, channel):
        """Update focus untuk user - TRIGGERED BY 3x TOTAL MENTIONS"""
        current_time = time.time()
        focus_until = current_time + self.focus_duration

        # Always update focus time
        self.user_focus[user] = focus_until

        # Check jika baru set focus (bukan extend)
        was_in_focus = user in self.user_focus

        if not was_in_focus:
            print(f"🎯 FOCUS SET: {user} for {self.focus_duration}s (3x total mentions)")

            # Send focus action
            focus_actions = [
                f"notices {user} has been trying to get attention 🎯",
                f"focuses on {user} after multiple attempts 👀",
                f"pays full attention to {user} after persistence 👂",
                f"acknowledges {user}'s repeated calls 💭"
            ]
            import random
            self.send_action(channel, random.choice(focus_actions))

            # Juga beritahu user
            self.send_message(channel, f"{user}: Okay saya fokus pada awak sekarang. Tak payah panggil nama saya lagi, saya akan reply semua message awak untuk {int(self.focus_duration/60)} minit. Taip '.clear' untuk stop.")
        else:
            # Extend focus time
            print(f"🎯 FOCUS EXTENDED: {user} for {self.focus_duration}s")
            self.send_action(channel, f"extends focus on {user} ⏱️")

        print(f"⏰ {user} focus until: {time.strftime('%H:%M:%S', time.localtime(focus_until))}")

    def cleanup_expired_focus(self):
        """Bersihkan focus yang sudah expired (5 minit idle)"""
        current_time = time.time()

        # Cleanup expired focus
        expired_focus = [
            user for user, focus_until in self.user_focus.items()
            if current_time > focus_until
        ]

        for user in expired_focus:
            del self.user_focus[user]
            print(f"⏰ FOCUS AUTO-EXPIRED: {user} (5 minit idle)")
            # Optional: notify user
            # self.send_action(channel, f"stops focusing on {user} (auto-expired)")

        # Cleanup mention data untuk user yang dah lama tak mention (30 minit)
        expired_mentions = [
            user for user, data in self.user_mentions.items()
            if current_time - data['last_mention_time'] > 1800  # 30 minit
        ]

        for user in expired_mentions:
            del self.user_mentions[user]
            print(f"🧹 Mention data cleared for {user} (30 min inactive)")

    def cleanup_expired_focus(self):
        """Bersihkan focus dan mention counts yang sudah expired"""
        current_time = time.time()

        # Cleanup expired focus
        expired_focus = [
            user for user, focus_until in self.user_focus.items()
            if current_time > focus_until
        ]

        for user in expired_focus:
            del self.user_focus[user]
            print(f"⏰ FOCUS EXPIRED: {user}")

        # Cleanup old mention counts
        expired_mentions = [
            user for user, data in self.user_mentions.items()
            if current_time - data['last_mention'] > 300  # 5 minutes no mention
        ]

        for user in expired_mentions:
            del self.user_mentions[user]
            print(f"🧹 Mention count cleared for {user} (inactive)")

    def is_user_in_focus(self, user):
        """Check jika user masih dalam focus"""
        current_time = time.time()

        if user in self.user_focus:
            focus_until = self.user_focus[user]
            time_left = focus_until - current_time

            if time_left > 0:
                # Update last activity time dalam mention tracker
                if user in self.user_mentions:
                    self.user_mentions[user]['last_mention_time'] = current_time

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

    def check_silent_mode(self):
        """Check jika silent mode sudah expired"""
        if self.silent_mode and time.time() > self.silent_until:
            self.silent_mode = False
            print("🔊 SILENT MODE OFF - Bot boleh bercakap semula")

    def handle_special_commands(self, message, nick, channel):
        """Handle special commands: diam, speak, etc. - NATURAL"""
        message_lower = message.lower()

        if any(cmd in message_lower for cmd in ['diam', 'shut up', 'senyap', 'quiet']) and self.nick.lower() in message_lower:
            self.silent_mode = True
            print(f"🔇 SILENT MODE ON - {nick} suruh diam")
            return False

        if any(cmd in message_lower for cmd in ['speak', 'cakap', 'reply', 'jawab']) and self.nick.lower() in message_lower:
            self.silent_mode = False
            print("🔊 SPEAK MODE ON - Bot boleh bercakap")
            return False

        return False

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

            # Tambah TOTAL count (tak reset)
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

    def detect_nick_change(self, line):
        """Detect NICK changes - notify semua channel user berada"""
        if " NICK " in line and "!" in line:
            try:
                old_nick = line.split("!")[0][1:]
                new_nick = line.split(" :")[1]

                if old_nick != new_nick:
                    print(f"🔄 Nick change: {old_nick} -> {new_nick}")

                    # 🆕 CARI SEMUA CHANNEL USER BERADA
                    user_channels = self.find_user_channels(old_nick)

                    if user_channels:
                        jokes = [
                            f"nampak {old_nick} tukar nick jadi {new_nick} 😅",
                            f"weh {old_nick} dah jadi {new_nick} 🏃💨",
                            f"eh {old_nick} transform jadi {new_nick} 💥",
                            f"alert! {old_nick} evolve jadi {new_nick} ⚡",
                            f"perhatian: {old_nick} dah bertukar jadi {new_nick} 🔄",
                            f"whoa {old_nick} rebrand jadi {new_nick} 🎨",
                            f"apekah! {old_nick} telah jadi {new_nick} 🦋",
                            f"update: {old_nick} sekarang dikenali sebagai {new_nick} 📝"
                        ]

                        import random
                        selected_joke = random.choice(jokes)

                        # 🆕 NOTIFY SETIAP CHANNEL
                        for channel in user_channels:
                            self.send_action(channel, selected_joke)
                            print(f"📢 Notified {channel} about {old_nick}->{new_nick}")

                        print(f"✅ Total channels notified: {len(user_channels)}")
                    else:
                        print(f"ℹ️ No channels found for {old_nick}")

            except Exception as e:
                print(f"❌ Nick change error: {e}")

    def find_user_channels(self, nick):
        """Cari channel yang user berada (dari tracked data)"""
        user_channels = []

        # 🆕 CARA 1: Jika kita track JOIN/PART
        if hasattr(self, 'channel_users') and self.channel_users:
            for channel, users in self.channel_users.items():
                if nick in users:
                    user_channels.append(channel)

        # 🆕 CARA 2: Fallback - check recent messages dari user
        if not user_channels and hasattr(self, 'conversation_memory'):
            recent_channels = set()
            for msg in self.conversation_memory[-20:]:  # Check last 20 messages
                if msg['nick'] == nick:
                    recent_channels.add(msg['channel'])

            if recent_channels:
                user_channels = list(recent_channels)
                print(f"📝 Found {nick} in recent channels: {user_channels}")

        # 🆕 CARA 3: Jika masih tak jumpa, assume channel bot berada
        if not user_channels and hasattr(self, 'channels'):
            user_channels = self.channels[:]  # Semua channel bot
            print(f"⚠️ Using fallback: assuming {nick} in bot channels: {user_channels}")

        return user_channels

    def find_shared_channels(self, nick):
        """Cari channel yang bot dan user berada bersama"""
        shared_channels = []

        # 🆕 KALAU ADA TRACKING SYSTEM (JOIN/PART)
        if hasattr(self, 'channel_users') and self.channel_users:
            for channel, users in self.channel_users.items():
                if nick in users and self.nick in users:
                    shared_channels.append(channel)

        # 🆕 FALLBACK: Jika tak ada tracking, check semua channel bot
        elif self.channels:
            # Assume user berada dalam semua channel bot (untuk sementara)
            shared_channels = self.channels[:]
            print(f"⚠️ Using fallback: assuming {nick} in all bot channels")

        return shared_channels

    def get_most_active_channel(self, channels):
        """Dapatkan channel yang paling active dari senarai"""
        # 🆕 LOGIC: Pilih channel dengan activity tertinggi
        if hasattr(self, 'channel_activity'):
            # Cari channel dengan message count tertinggi
            active_channels = []
            for channel in channels:
                activity = self.channel_activity.get(channel, 0)
                active_channels.append((channel, activity))

            if active_channels:
                active_channels.sort(key=lambda x: x[1], reverse=True)
                return active_channels[0][0]

        # Default: channel pertama
        return channels[0]

    def ai_analyze_message(self, message, nick, conversation_history, is_in_focus=False):
        """AI ANALYSIS dengan smart language detection"""
        start_time = time.time()

        try:
            context = "\n".join([f"{user}: {msg}" for user, msg in conversation_history[-15:]])

            # 🆕 SMART LANGUAGE DETECTION
            detected_lang = self.detect_language(message)
            print(f"🌐 Detected language: {detected_lang}")

            # 🆕 LANGUAGE-SPECIFIC PROMPTS - DENGAN FOCUS HINT
            focus_hint_malay = "⚠️ USER DALAM FOCUS MODE - MESTI BALAS!" if is_in_focus else ""
            focus_hint_english = "⚠️ USER IN FOCUS MODE - MUST RESPOND!" if is_in_focus else ""
            focus_rule_malay = "FOCUS RULE: User ni dah panggil anda 3x. Mereka nak perhatian. BALAS dengan mesra kecuali spam." if is_in_focus else ""
            focus_rule_english = "FOCUS RULE: User called you 3x. They want attention. RESPOND friendly except spam." if is_in_focus else ""

            lang_prompts = {
                'malay': f"""Anda ialah {self.nick}, sebuah bot IRC yang mesra. {focus_hint_malay}

    Konteks: {context}
    Mesej: "{message}" dari {nick}

    {focus_rule_malay}

    1. Respond naturally in Malay/English mix (rojak language)
    2. Keep responses short and casual (1-2 lines max)
    3. Don't repeat yourself
    4. Be funny and engaging
    5. Don't make up information you don't know

    **PENTING: PASTIKAN GUNA FORMAT INI:**
    <DECISION>YA atau TIDAK</DECISION>
    <RESPONSE>balasan anda</RESPONSE>

    Contoh:
    <DECISION>YA</DECISION>
    <RESPONSE>Hai! Apa khabar?</RESPONSE>

    JANGAN LUPA TAGS <DECISION> dan <RESPONSE>!""",

                'english': f"""You are {self.nick}, a friendly IRC bot. {focus_hint_english}

    Context: {context}  
    Message: "{message}" from {nick}

    {focus_rule_english}

    Respond naturally in English. Keep it short and casual.
    Maximum 3-4 lines only.

    **IMPORTANT: USE THIS FORMAT:**
    <DECISION>YES or NO</DECISION>
    <RESPONSE>your response</RESPONSE>

    Example:
    <DECISION>YES</DECISION>
    <RESPONSE>Hello! How are you?</RESPONSE>

    DON'T FORGET THE <DECISION> and <RESPONSE> tags!""",

                'mixed': f"""You are {self.nick} in IRC chat. {'⚠️ FOCUS MODE ACTIVE!' if is_in_focus else ''}

    Context: {context}
    Message: "{message}" from {nick}

    {'User really wants attention. Be extra responsive.' if is_in_focus else ''}

    Respond naturally. Keep it short and casual.
    Maximum 3-4 lines only.

    **MUST USE FORMAT:**
    <DECISION>YES or NO</DECISION>
    <RESPONSE>your response</RESPONSE>

    Include the XML tags!"""
            }

            system_prompt = lang_prompts.get(detected_lang, lang_prompts['mixed'])

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Respond to {nick}: '{message}'"}
            ]

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "max_tokens": 120,
                "temperature": 0.7
            }

            api_start = time.time()
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=15
            )
            api_time = time.time() - api_start

            if response.status_code == 200:
                ai_text = response.json()['choices'][0]['message']['content'].strip()

                total_time = time.time() - start_time
                print(f"🧠 AI LATENCY: API={api_time:.2f}s, Total={total_time:.2f}s")
                print(f"🧠 AI RAW: {ai_text}")

                decision = "NO"
                bot_response = ""

                # ⭐⭐⭐ FIXED DECISION DETECTION ⭐⭐⭐
                # Pattern 1: Dengan XML tags
                if '<DECISION>' in ai_text.upper() or '<DECISION>' in ai_text:
                    # Cari YA/TIDAK/YES/NO dalam <DECISION> tags
                    decision_match = re.search(r'<DECISION>\s*(YA|TIDAK|YES|NO)\s*</DECISION>', ai_text, re.IGNORECASE)
                    if decision_match:
                        decision_word = decision_match.group(1).upper()
                        decision = "YES" if decision_word in ['YA', 'YES'] else "NO"
                else:
                    # Pattern 2: Tanpa tags - cari YA/TIDAK/YES/NO di awal
                    first_word = ai_text.split()[0].upper() if ai_text.split() else ""
                    if first_word in ['YA', 'YES', 'TIDAK', 'NO']:
                        decision = "YES" if first_word in ['YA', 'YES'] else "NO"
                        # Response adalah selebihnya
                        bot_response = ' '.join(ai_text.split()[1:])

                # ⭐⭐⭐ FIXED RESPONSE EXTRACTION ⭐⭐⭐
                # Cari <RESPONSE> tags
                response_match = re.search(r'<RESPONSE>(.*?)</RESPONSE>', ai_text, re.DOTALL | re.IGNORECASE)

                if response_match:
                    bot_response = response_match.group(1).strip()
                elif not bot_response:  # Jika belum ada response dari pattern 2
                    # Cari RESPONSE: tanpa tags
                    response_match = re.search(r'RESPONSE:\s*(.*)', ai_text, re.DOTALL | re.IGNORECASE)
                    if response_match:
                        bot_response = response_match.group(1).strip()
                    else:
                        # Ambil semua text selepas decision (jika ada pattern YA/TIDAK di awal)
                        if ai_text[:3].upper() in ['YA ', 'YES', 'TID', 'NO ']:
                            parts = ai_text.split(' ', 1)
                            if len(parts) > 1:
                                bot_response = parts[1].strip()
                        else:
                            bot_response = ai_text

                # ⭐⭐⭐ CLEAN RESPONSE ⭐⭐⭐
                # Remove any leftover tags
                bot_response = re.sub(r'</?[A-Z]+[^>]*>', '', bot_response)

                # Remove leading/trailing punctuation
                bot_response = bot_response.strip(' :.-,')

                # Remove multiple spaces
                bot_response = ' '.join(bot_response.split())

                print(f"🧠 AI PARSED: {decision} - '{bot_response}'")

                should_respond = (decision == "YES" and 
                               bot_response and 
                               len(bot_response) > 2 and 
                               bot_response.upper() != "NONE")

                if should_respond:
                    print(f"🎯 AI decided to RESPOND: '{bot_response}'")
                    return True, bot_response
                else:
                    print(f"🎯 AI decided to SKIP (decision:{decision}, response:'{bot_response}')")
                    return False, bot_response

            else:
                print(f"❌ AI API Error: {response.status_code}")
                return False, ""

        except requests.exceptions.Timeout:
            print(f"⏰ AI API TIMEOUT after 15 seconds!")
            return False, ""
        except Exception as e:
            print(f"❌ AI Error: {e}")
            import traceback
            traceback.print_exc()
            return False, ""

    def clean_ai_response(self, text):
        """Clean AI response dari berbagai format"""
        if not text:
            return ""

        # Remove all XML tags
        cleaned = re.sub(r'</?[A-Z][A-Z0-9]*>', '', text)

        # Remove DECISION: YES/NO lines
        cleaned = re.sub(r'DECISION:\s*(YES|NO|YA|TIDAK)', '', cleaned, flags=re.IGNORECASE)

        # Remove RESPONSE: prefix
        cleaned = re.sub(r'RESPONSE:\s*', '', cleaned, flags=re.IGNORECASE)

        # Fix angle brackets yang tidak close
        if cleaned.startswith('<') and '>' not in cleaned:
            cleaned = cleaned[1:]  # Remove leading <

        # Remove leading/trailing punctuation
        cleaned = cleaned.strip(' .,;:!?<>')

        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        return cleaned

    def handle_special_commands(self, message, nick, channel):
        """Handle special commands: diam, speak, etc. - NATURAL"""
        message_lower = message.lower()
        bot_nick_lower = self.nick.lower()

        # DIAM / SHUT UP command
        if any(cmd in message_lower for cmd in ['diam', 'shut up', 'senyap', 'quiet']) and bot_nick_lower in message_lower:
            self.silent_mode = True
            self.silent_until = time.time() + 300  # 5 minutes silent

            # TUNJUK CTCP ACTION supaya semua nampak
            silent_actions = [
                f"looks at {nick} and goes silent 🤐",
                f"zips mouth after {nick}'s command 🤫", 
                f"nods at {nick} and stops talking 🙊",
                f"acknowledges {nick}'s request to be quiet 🔇"
            ]
            import random
            self.send_action(channel, random.choice(silent_actions))

            print(f"🔇 SILENT MODE ON - {nick} suruh diam (5 min)")
            return True

        # SPEAK / CAKAP command - HANYA UNTUK AKTIFKAN BOT, TAK AUTO-FOCUS
        if any(cmd in message_lower for cmd in ['speak', 'cakap', 'reply', 'jawab']) and bot_nick_lower in message_lower:
            self.silent_mode = False
            self.silent_until = 0

            # TUNJUK CTCP ACTION supaya semua nampak
            speak_actions = [
                f"unmutes after hearing {nick} 🔊",
                f"smiles at {nick} and starts talking again 😊",
                f"wakes up when {nick} calls 🎤",
                f"thanks {nick} for bringing me back to life 🗣️"
            ]
            import random
            self.send_action(channel, random.choice(speak_actions))

            # HANYA NOTIFY, TAK AUTO-FOCUS
            print(f"🔊 SPEAK MODE ON - {nick} activate bot")

            # Beritahu user bot dah boleh cakap balik
            self.send_message(channel, f"Terima kasih {nick}, saya boleh bercakap balik. Panggil nama saya untuk chat!")
            return True

        return False

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

    def process_message(self, nick, message, channel):
        """PROSES MESSAGE dengan 3-second context window PER CHANNEL"""
        print(f"📩 {nick} in {channel}: {message}")

        current_time = time.time()

        # 🆕 TAMBAH KE BUFFER CHANNEL INI
        self.add_to_message_buffer(nick, message, channel, current_time)

        self.add_to_memory(nick, message, channel)
        self.check_silent_mode()

        # Handle .clear command untuk focus
        if message.lower().strip() == '.clear':
            if nick in self.user_focus:
                del self.user_focus[nick]
                print(f"🧹 FOCUS CLEARED for {nick} by command")
                self.send_message(channel, f"Okay {nick}, saya stop reply semua message anda.")
                return

        if message.startswith('\x01ACTION') and message.endswith('\x01'):
            print(f"🎯 ACTION message from {nick}, skipping AI...")
            return

        # Check special commands FIRST (diam/speak)
        if self.handle_special_commands(message, nick, channel):
            print(f"🎯 Special command handled for {nick}")
            return

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
            if current_time - self.last_ai_time < 3:
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
            max_users_per_window = 1  # 🆕 HANYA 1 USER PER 3-SAAT WINDOW

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

                # 🆕 FOCUS MODE
                if is_in_focus:
                    print(f"🎯 {user} IN FOCUS in {channel} - PROCESSING")

                    conversation_history = [
                        (msg['nick'], msg['message']) for msg in self.conversation_memory[-10:]
                    ]

                    should_respond, ai_response = self.ai_analyze_message(
                        combined_message, user, conversation_history,
                        is_in_focus=True
                    )

                    if ai_response and len(ai_response.strip()) > 5:
                        print(f"🎯 FOCUS REPLY to {user} in {channel}: {ai_response[:50]}...")
                        self.send_message(channel, ai_response)
                    else:
                        print(f"🎯 No valid focus response for {user}")
                    break  # 🆕 HENTI SELEPAS PROCESS SATU USER

                # NORMAL MODE
                conversation_history = [
                    (msg['nick'], msg['message']) for msg in self.conversation_memory[-10:]
                ]

                should_respond, ai_response = self.ai_analyze_message(
                    combined_message, user, conversation_history,
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

    def find_user_channels(self, nick):
        """Cari channel yang user berada (dari tracked data)"""
        user_channels = []

        # 🆕 CARA 1: Jika kita track JOIN/PART
        if hasattr(self, 'channel_users') and self.channel_users:
            for channel, users in self.channel_users.items():
                if nick in users:
                    user_channels.append(channel)

        # 🆕 CARA 2: Fallback - check recent messages dari user
        if not user_channels and hasattr(self, 'conversation_memory'):
            recent_channels = set()
            for msg in self.conversation_memory[-20:]:  # Check last 20 messages
                if msg['nick'] == nick:
                    recent_channels.add(msg['channel'])

            if recent_channels:
                user_channels = list(recent_channels)
                print(f"📝 Found {nick} in recent channels: {user_channels}")

        # 🆕 CARA 3: Jika masih tak jumpa, assume channel bot berada
        if not user_channels and hasattr(self, 'channels'):
            user_channels = self.channels[:]  # Semua channel bot
            print(f"⚠️ Using fallback: assuming {nick} in bot channels: {user_channels}")

        return user_channels

    def run(self):
        """Main bot loop"""
        print("🚀 Starting MinahBot dengan Custom Language Detection...")
        self.connect()
        buffer = ""

        while True:
            try:
                self.sock.settimeout(1.0)

                try:
                    data = self.sock.recv(2048).decode('utf-8', errors='ignore')
                except socket.timeout:
                    if self.message_queue:
                        self.process_queue()
                    continue

                if not data:
                    print("❌ Connection closed")
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

                    if " NICK " in line:
                        self.detect_nick_change(line)

                    if line.startswith("PING"):
                        ping_data = line.split(":")[1] if ":" in line else ""
                        self.send_raw(f"PONG :{ping_data}")
                        continue

                    for channel in self.channels:
                        if "PRIVMSG" in line and channel in line:
                            try:
                                parts = line.split(" ")
                                nick = parts[0][1:].split("!")[0]
                                message = " ".join(parts[3:])[1:]

                                if nick != self.nick:
                                    self.process_message(nick, message, channel)

                            except Exception as e:
                                print(f"❌ Parse error: {e}")

                if self.message_queue:
                    self.process_queue()

            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(5)
                self.connect()

class BotMinah:
    def __init__(self, server, port, nick, channels=None, api_key=None, api_url=None):
        # 🎯 GABUNGKAN SEMUA FEATURES:

        # 1. IRC Connection (dari private chat version)
        self.server = server
        self.port = port
        self.nick = nick
        self.username = nick
        self.realname = f"{nick} Bot"

        # 2. Channels (dari kedua-dua version)
        self.channels = channels or []
        self.pending_channels = self.channels.copy()

        # 3. AI System (dari private chat AI version)
        self.api_key = api_key
        self.api_url = api_url or "https://api.groq.com/openai/v1/chat/completions"

        # 4. Connection State
        self.connection = None
        self.running = False
        self.registered = False

        # 5. 🎯 SEMUA FEATURES DARI BOT ASAL:
        # Focus system
        self.user_focus = {}
        self.user_mentions = {}
        self.focus_duration = 300
        self.mentions_threshold = 3

        # Buffer system (3-second window)
        self.message_buffers = {}
        self.last_buffer_process = {}

        # Silent mode
        self.silent_mode = False
        self.silent_until = 0

        # Memory system
        self.conversation_memory = []
        self.max_messages = 30

        # Queue system
        self.message_queue = deque()
        self.is_sending = False
        self.last_send_time = 0
        self.min_delay = 3

        # AI Cooldown
        self.last_ai_time = 0

        # Channel tracking
        self.channel_users = {}
        self.channel_activity = {}

        # 6. 🎯 FEATURES DARI PRIVATE CHAT VERSION:
        self.last_private_reply = 0
        self.private_cooldown = 5
        self.private_conversations = {}

        # Check requests module
        try:
            import requests
            self.requests_available = True
        except ImportError:
            self.requests_available = False
            print("⚠️ Requests module not available")

        print(f"🤖 BOT MINAH - SUPER VERSION LOADED")
        print(f"   ✅ Public Channel Features")
        print(f"   ✅ Private Chat AI Features")
        print(f"   ✅ Focus System (3 mentions)")
        print(f"   ✅ 3-second Context Window")
        print(f"   ✅ Nick Change Detection")
        print(f"   ✅ AI Responses with Groq")

    # ==================== MESSAGE SENDING ====================

    def send_raw(self, message):
        """Send raw IRC command"""
        if self.connection is None:
            print(f"❌ No connection!")
            return False

        try:
            self.connection.send(f"{message}\r\n".encode('utf-8'))
            print(f"📤 RAW: {message}")
            return True
        except Exception as e:
            print(f"❌ Send failed: {e}")
            return False

    def send_private_message(self, nick, message):
        """Send private message to user"""
        print(f"💬 PRIVATE to {nick}: {message}")
        return self.send_raw(f"PRIVMSG {nick} :{message}")

    def send_channel_message(self, channel, message):
        """Send message to channel"""
        print(f"📢 CHANNEL to {channel}: {message}")
        return self.send_raw(f"PRIVMSG {channel} :{message}")

    # ==================== MESSAGE PARSING ====================

    def parse_line(self, line):
        """Parse IRC line - FULL PARSING"""
        print(f"\n📨 IN: {line}")

        # PING-PONG (MUST BE FIRST!)
        if line.startswith('PING'):
            pong_msg = f"PONG {line.split()[1]}"
            print(f"🏓 PING -> {pong_msg}")
            self.send_raw(pong_msg)
            return

        if not line.startswith(':'):
            return

        parts = line.split()
        if len(parts) < 2:
            return

        # ===== NUMERIC REPLIES (001, 376, etc) =====
        if parts[1].isdigit():
            code = parts[1]

            # 🎯 REGISTRATION COMPLETE (001 atau 376)
            if code in ['001', '376']:
                if code == '001':
                    welcome = ' '.join(parts[3:])[1:] if len(parts) > 3 else ""
                    print(f"🎉🎉🎉 REGISTERED (001): {welcome}")
                else:  # 376
                    print(f"🎉🎉🎉 REGISTERED (376 - End of MOTD)")

                self.registered = True
                self.join_channels()  # 🎯 JOIN CHANNELS SEKARANG!

            # NICK IN USE (433)
            elif code == '433':
                print(f"❌ Nick {self.nick} in use, trying alternative...")
                self.nick = f"{self.nick}_"
                self.send_raw(f"NICK {self.nick}")

            # CHANNEL USER LIST (353)
            elif code == '353':  # RPL_NAMREPLY
                if len(parts) >= 5:
                    channel = parts[4]
                    users_msg = ' '.join(parts[5:])[1:] if len(parts) > 5 else ""
                    users = users_msg.split()
                    print(f"👥 Users in {channel}: {len(users)} users")

                    # Track users in channel
                    if channel not in self.channel_users:
                        self.channel_users[channel] = set()
                    for user in users:
                        clean_user = user.lstrip('@+%&~')
                        self.channel_users[channel].add(clean_user)

            return

        # ===== PRIVMSG (CHANNEL OR PRIVATE) =====
        if parts[1] == 'PRIVMSG' and len(parts) >= 4:
            try:
                sender = parts[0].split('!')[0][1:]
                target = parts[2]
                message = ' '.join(parts[3:])[1:]

                print(f"🎯 PRIVMSG DETAILS:")
                print(f"   From: {sender}")
                print(f"   Target: '{target}'")
                print(f"   Message: '{message}'")
                print(f"   Is private? {target.lower() == self.nick.lower()}")
                print(f"   Is channel? {target.startswith('#')}")

                # 🎯 PRIVATE MESSAGE TO BOT
                if target.lower() == self.nick.lower():
                    print(f"🔥🔥🔥 PRIVATE MESSAGE TO BOT!")
                    self.handle_private_message(sender, message)

                # 🎯 CHANNEL MESSAGE
                elif target.startswith('#'):
                    print(f"📢 CHANNEL MESSAGE in {target}")
                    self.handle_channel_message(sender, target, message)

                else:
                    print(f"❓ Unknown target type")

            except Exception as e:
                print(f"❌ PRIVMSG parse error: {e}")

        # ===== JOIN =====
        elif parts[1] == 'JOIN' and len(parts) >= 3:
            nick = parts[0].split('!')[0][1:]
            channel = parts[2].lstrip(':')

            print(f"👤 {nick} joined {channel}")

            # Track user in channel
            if channel not in self.channel_users:
                self.channel_users[channel] = set()
            self.channel_users[channel].add(nick)

            # If bot sendiri join
            if nick == self.nick:
                print(f"✅ Bot joined {channel}")

        # ===== PART =====
        elif parts[1] == 'PART' and len(parts) >= 3:
            nick = parts[0].split('!')[0][1:]
            channel = parts[2]

            print(f"👤 {nick} left {channel}")

            # Remove user from tracking
            if channel in self.channel_users and nick in self.channel_users[channel]:
                self.channel_users[channel].remove(nick)

        # ===== QUIT =====
        elif parts[1] == 'QUIT':
            nick = parts[0].split('!')[0][1:]
            print(f"👤 {nick} quit")

            # Remove from all channels
            for channel in self.channel_users:
                if nick in self.channel_users[channel]:
                    self.channel_users[channel].remove(nick)

        # ===== NICK CHANGE =====
        elif parts[1] == 'NICK' and len(parts) >= 3:
            old_nick = parts[0].split('!')[0][1:]
            new_nick = parts[2].lstrip(':')

            print(f"🔄 {old_nick} changed nick to {new_nick}")

            # Update in tracking
            for channel in self.channel_users:
                if old_nick in self.channel_users[channel]:
                    self.channel_users[channel].remove(old_nick)
                    self.channel_users[channel].add(new_nick)

        # ===== NOTICE =====
        elif parts[1] == 'NOTICE' and len(parts) >= 3:
            source = parts[0]
            target = parts[2]
            notice_msg = ' '.join(parts[3:])[1:] if len(parts) > 3 else ""
            print(f"📝 NOTICE from {source}: {notice_msg}")

    # ==================== MESSAGE HANDLING ====================

    def handle_private_message(self, nick, message):
        """Handle private messages - WITH AI + INVITE SYSTEM"""
        print(f"\n" + "="*60)
        print(f"💌 PRIVATE MESSAGE HANDLER")
        print(f"   From: {nick}")
        print(f"   Message: '{message}'")

        current_time = time.time()

        # 🎯 RATE LIMITING: 5 seconds minimum
        if current_time - self.last_private_reply < 5:
            wait_time = 5 - (current_time - self.last_private_reply)
            print(f"⏳ Rate limiting: {wait_time:.1f}s remaining")
            return

        self.last_private_reply = current_time

        # 🎯 TRACK CONVERSATION HISTORY
        if nick not in self.private_conversations:
            self.private_conversations[nick] = []

        # Add user message to history
        self.private_conversations[nick].append({
            'time': current_time,
            'sender': nick,
            'message': message
        })

        # Keep only last 10 messages
        if len(self.private_conversations[nick]) > 10:
            self.private_conversations[nick] = self.private_conversations[nick][-10:]

        print(f"📊 History with {nick}: {len(self.private_conversations[nick])} messages")

        # 🎯 CHECK FOR INVITE (25% chance after 5 messages)
        message_count = len([m for m in self.private_conversations[nick] if m['sender'] == nick])

        if message_count >= 5 and random.random() < 0.25:
            print(f"🎯 INVITE TRIGGERED! ({message_count} user messages)")
            self.send_channel_invite(nick)
            return

        # 🎯 GET AI RESPONSE
        ai_response = self.get_ai_response(nick, message)

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
                f"Halo {nick}! 💌"
            ]
            response = random.choice(fallbacks)
            print(f"🤖 Using fallback: {response}")

        # Add bot response to history
        self.private_conversations[nick].append({
            'time': current_time,
            'sender': self.nick,
            'message': response
        })

        # Send response
        self.send_private_message(nick, response)

    def get_ai_response(self, nick, message):
        """Get AI response for private message"""
        # 🎯 Check jika AI enabled
        if not self.api_key:
            print(f"🤖 AI disabled, using fallback response")
            return None

        try:
            # Get conversation history
            history = self.private_conversations.get(nick, [])

            # Prepare context (last 5 messages)
            context_messages = history[-5:] if len(history) > 5 else history

            context = ""
            for msg in context_messages:
                sender = "Bot" if msg['sender'] == self.nick else nick
                context += f"{sender}: {msg['message']}\n"

            # AI Prompt
            system_prompt = f"""You are {self.nick}, a friendly IRC bot in private chat with {nick}.
            Guidelines:
            1. Respond naturally in Malay/English mix (rojak language)
            2. Keep responses short and casual (1-2 lines max)
            3. Don't repeat yourself
            4. Be funny and engaging
            5. If user asks about channels, mention: #amboi #desa #movie #alamanda
            6. Don't make up information you don't know

            Current conversation with {nick}:"""

            user_prompt = f"""Chat context:
    {context}

    {nick}'s message: "{message}"

    Your response:"""

            print(f"🤖 Calling AI API...")

            import requests

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 60,
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
                timeout=8
            )

            if response.status_code == 200:
                ai_text = response.json()['choices'][0]['message']['content'].strip()
                print(f"🤖 AI Response raw: '{ai_text}'")
                return ai_text
            else:
                print(f"❌ AI API Error {response.status_code}: {response.text[:100]}")
                return None

        except requests.exceptions.Timeout:
            print(f"⏰ AI API timeout")
            return None
        except Exception as e:
            print(f"❌ AI Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def send_channel_invite(self, nick):
        """Send channel invite to user"""
        channels = ["#ace", "#alamanda", "#kampung", "#desa"]
        target_channel = random.choice(channels)

        invite_messages = [
            f"Hey {nick}! Jom join {target_channel} untuk chat ramai-ramai! 🎉",
            f"Eh {nick}, boring chat sorang-sorang. Jom join {target_channel}! 🚀",
            f"{nick}, jom la masuk {target_channel}. Kat sana ramai member! 👥",
            f"Hei {nick}, aku kat {target_channel} pun ada. Jom join! 🤝",
            f"Tak best chat private ni. Jom jumpa kat {target_channel}! 🎊"
        ]

        invite_msg = random.choice(invite_messages)

        print(f"📨 INVITING {nick} to {target_channel}")

        # Send invite message
        self.send_private_message(nick, invite_msg)

        # Send IRC INVITE command
        self.send_raw(f"INVITE {nick} {target_channel}")

    def handle_channel_message(self, nick, channel, message):
        """Handle channel messages (optional - boleh expand nanti)"""
        print(f"\n📢 CHANNEL MESSAGE in {channel}")
        print(f"   From: {nick}")
        print(f"   Message: '{message}'")

        # Basic channel handling - cuma log untuk sekarang
        # Boleh tambah AI reply, commands, etc nanti

        # Contoh: Jika seseorang mention bot dalam channel
        if self.nick.lower() in message.lower():
            print(f"   🎯 Bot mentioned in channel!")
            # Boleh reply kat channel nanti

    # ==================== MAIN LOOP ====================

    def run(self):
        """Main bot loop"""
        print(f"\n🚀 Starting bot...")

        if not self.connect_to_server():
            print(f"❌ Cannot start, connection failed")
            return

        print(f"\n⏳ Entering main loop...")
        print(f"   Waiting for registration complete...")
        print(f"   Then will join channels: {self.channels}")
        print(f"   Ready for private messages!")
        print("-"*60)

        self.running = True

        try:
            while self.running:
                try:
                    # Receive data
                    data = self.connection.recv(2048).decode('utf-8', errors='ignore')

                    if not data:
                        print(f"⚠️ No data, connection closed?")
                        break

                    # Process each line
                    lines = data.split('\r\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            self.parse_line(line)

                except socket.timeout:
                    print(f"⏰ Socket timeout, still waiting...")
                    continue
                except ConnectionResetError:
                    print(f"❌ Connection reset by peer")
                    break
                except Exception as e:
                    print(f"❌ Error in main loop: {e}")
                    import traceback
                    traceback.print_exc()
                    break

        except KeyboardInterrupt:
            print(f"\n🛑 Stopped by user")
        finally:
            print(f"\n🛑 Bot stopped")
            self.running = False
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass

if __name__ == "__main__":
    bot = MinahBot()
    bot.run()
