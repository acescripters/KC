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
#!/usr/bin/env python3
import time
import socket
import threading
import select
from datetime import datetime, timedelta

# ==================== CONFIG ====================
SERVER = "irc.kampungchat.org"
PORT = 6668
CHANNELS = ["#ace", "#bro", "#alamanda", "#amboi", "#desa", "#kampungchat", "#movie", "#meow", "#zumba", "#purple", "#kampung", "#love"]
NICK = "www"
PASSWORD = "fai5zul"
IDENT = "believer"
REALNAME = "꧁╱╲╱╳╲╱╲Bukti Jadi Sejarah 🇲🇾❤🇵🇸╱╲╱╳╲╱╲꧂"

# API URLs
CUACA_API = "https://api.open-meteo.com/v1/forecast"
SOLAT_API = "https://api.waktusolat.app/solat"  # V1 API - lebih mudah
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"

# Other configs
MALAYSIA_UTC_OFFSET = 8
MAX_MESSAGE_LENGTH = 400
HOURLY_TRIGGER_MINUTE = 0
MAX_RETRIES = 9999  # Auto-rejoin 9999x
RETRY_DELAY = 30    # 30 saat

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
        # self.nick = "minah"
        # self.username = "NPC"
        # self.realname = "꧁✿🌸Hidup Anugerah Terindah🌸✿꧂"

        # Channels list
        # self.channels = ['#amboi','#ace', '#zumba', '#alamanda', '#bro', '#desa', '#purple', '#bro']

        # AI API Configuration (GROQ)
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        # ==================== PRIVATE CHAT SYSTEM ====================
        self.private_chat_enabled = True
        self.invite_chance = 25
        self.private_cooldown = 5
        self.last_private_reply = 0
        self.private_conversations = {}
        self.last_invite_sent = {}
        self.invite_cooldown = 300

        # ==================== FOCUS SYSTEM ====================
        self.user_focus = {}
        self.focus_duration = 300
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
        self.channel_ai_cooldown = 2
        self.channel_last_ai = {}
        self.min_thinking_time = 3.0
        self.focus_thinking_time = 2.0

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
        self.memory_expiry_days = 30
        self.last_cleanup_time = 0
        self.cleanup_interval = 86400

        print("="*60)
        print("🤖 MINAHBOT v4.2 - LANGUAGE FIXED EDITION")
        print(f"🌐 Enhanced Language Detection: Malay + English + Mixed")
        print(f"🧠 Memory system: max={self.max_messages}, auto-cleanup={self.cleanup_threshold}")
        print(f"🗑️  Auto-expiry: {self.memory_expiry_days} hari, setiap {self.cleanup_interval//3600} jam")
        print(f"✅ Private Chat: ENABLED ({self.invite_chance}% invite chance)")
        print(f"✅ Focus System: ENABLED ({self.mentions_threshold} mentions)")
        print(f"✅ AI Responses: ENABLED (Groq API)")
        print(f"✅ Channels: {', '.join(self.channels)}")
        print("="*60)

        os.makedirs('logs', exist_ok=True)

    # ==================== ENHANCED LANGUAGE DETECTION ====================
    def detect_language_enhanced(self, text):
        """Enhanced language detection dengan scoring system yang lebih baik"""
        if not text or len(text.strip()) < 2:
            return "mixed"

        text_lower = text.lower().strip()

        # Extended Malay patterns dengan weight
        malay_patterns = {
            # High weight indicators (3 points)
            'high': {
                'nak', 'tak', 'lah', 'pun', 'kan', 'nya', 'ke', 'tu', 'ni',
                'awak', 'kamu', 'aku', 'saya', 'dia', 'mereka', 'kami', 'kita',
                'apa', 'mana', 'kenapa', 'bagaimana', 'bila', 'berapa', 'mengapa',
                'dah', 'sudah', 'belum', 'akan', 'boleh', 'mesti', 'harus',
                'jom', 'mari', 'ayuh', 'weh', 'eh', 'hei', 'oi'
            },
            # Medium weight indicators (2 points)
            'medium': {
                'sangat', 'amat', 'sekali', 'sikit', 'banyak', 'sedikit',
                'baik', 'bagus', 'teruk', 'cantik', 'hodoh', 'best', 'mantap',
                'hari', 'malam', 'pagi', 'petang', 'esok', 'semalam', 'tadi',
                'makan', 'minum', 'tidur', 'kerja', 'main', 'belajar', 'baca',
                'rumah', 'kereta', 'motor', 'jalan', 'kedai', 'sekolah'
            },
            # Low weight indicators (1 point)
            'low': {
                'terima kasih', 'maaf', 'tolong', 'sila', 'harap', 'minta',
                'seperti', 'macam', 'sama', 'lain', 'baru', 'lama', 'besar',
                'kecil', 'tinggi', 'rendah', 'jauh', 'dekat', 'cepat', 'lambat'
            }
        }

        # English patterns dengan weight
        english_patterns = {
            'high': {
                'the', 'is', 'are', 'was', 'were', 'am', 'be', 'being',
                'what', 'why', 'when', 'where', 'how', 'who', 'which',
                'you', 'your', 'yours', 'me', 'my', 'mine', 'he', 'she', 'it',
                'they', 'them', 'their', 'we', 'us', 'our', 'have', 'has', 'had'
            },
            'medium': {
                'hello', 'hi', 'hey', 'good', 'bad', 'nice', 'great', 'awesome',
                'thanks', 'thank', 'please', 'sorry', 'excuse', 'welcome',
                'today', 'yesterday', 'tomorrow', 'now', 'then', 'here', 'there'
            },
            'low': {
                'like', 'love', 'hate', 'want', 'need', 'think', 'know',
                'see', 'look', 'hear', 'feel', 'make', 'take', 'give', 'get'
            }
        }

        # Calculate weighted scores
        malay_score = 0
        english_score = 0

        # Check Malay patterns
        for weight_category, patterns in malay_patterns.items():
            weight = {'high': 3, 'medium': 2, 'low': 1}[weight_category]
            for pattern in patterns:
                if pattern in text_lower:
                    malay_score += weight

        # Check English patterns
        for weight_category, patterns in english_patterns.items():
            weight = {'high': 3, 'medium': 2, 'low': 1}[weight_category]
            for pattern in patterns:
                if pattern in text_lower:
                    english_score += weight

        # Special rojak patterns (mix indicators)
        rojak_indicators = ['la', 'lor', 'mah', 'leh', 'one', 'also can', 'can la']
        rojak_score = sum(2 for indicator in rojak_indicators if indicator in text_lower)

        print(f"🌐 Language scores - Malay: {malay_score}, English: {english_score}, Rojak: {rojak_score}")

        # Decision logic
        if rojak_score >= 2:
            return "mixed"
        elif malay_score >= 3 and malay_score > english_score:
            return "malay"
        elif english_score >= 3 and english_score > malay_score:
            return "english"
        elif malay_score > 0 and english_score > 0:
            return "mixed"
        elif malay_score > english_score:
            return "malay"
        elif english_score > malay_score:
            return "english"
        else:
            return "mixed"

    def detect_language(self, text):
        """Main language detection dengan fallback"""
        if not text or len(text.strip()) < 3:
            return "mixed"

        # Clean text first
        clean_text = self.strip_irc_codes(text)

        # Use enhanced detection
        detected = self.detect_language_enhanced(clean_text)

        print(f"🌐 Language detected: '{clean_text[:50]}...' -> {detected}")
        return detected

    # ==================== IRC CONNECTION ====================
    def connect(self):
        """Connect to IRC server"""
        try:
            print(f"🔗 Connecting to {self.server}:{self.port}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            self.sock.connect((self.server, self.port))

            self.send_raw(f"NICK {self.nick}")
            self.send_raw(f"USER {self.username} 0 * :{self.realname}")
            time.sleep(3)

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

    # ==================== MESSAGE CLEANING ====================
    def strip_irc_codes(self, text):
        """Strip IRC control codes dan formatting"""
        if not text:
            return text

        # Remove IRC color codes
        irc_color_pattern = re.compile(r'[\x02\x03\x0F\x16\x1D\x1F](\d{1,2}(,\d{1,2})?)?')
        text = irc_color_pattern.sub('', text)

        # Remove other control characters
        control_chars_pattern = re.compile(r'[\x00-\x1F\x7F]')
        text = control_chars_pattern.sub('', text)

        # Remove ACTION format markers
        text = text.replace('\x01ACTION', '').replace('\x01', '')

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    # ==================== AI ANALYSIS WITH FIXED LANGUAGE SUPPORT ====================
    def ai_analyze_message(self, message, nick, channel, conversation_history, is_in_focus=False):
        """AI analysis dengan language-aware prompts yang diperbaiki"""
        start_time = time.time()

        print(f"🤖 AI PROCESS START: {nick} in {channel}")

        if len(message.strip()) < 3 or message.startswith('!'):
            print(f"🎯 Skipping AI untuk message pendek/command")
            return False, ""

        try:
            # Detect language dengan enhanced method
            detected_lang = self.detect_language(message)
            print(f"🌐 Detected language: {detected_lang}")

            # Prepare context
            current_context = "\n".join([f"{user}: {msg}" for user, msg in conversation_history[-6:]])
            if not current_context:
                current_context = "(New conversation started)"

            # Get SQLite history untuk context yang lebih kaya
            sqlite_history = self._get_optimized_history_for_ai(channel, nick, days=7, max_messages=50)

            # ==================== FIXED LANGUAGE PROMPTS ====================

            # Malay prompt - diperbaiki
            malay_prompt = f"""Anda ialah {self.nick} (panggil diri "aku"), bot IRC yang pandai bersembang dalam Bahasa Malaysia.

    **🎯 GAYA BAHASA MALAYSIA:**
    - Gunakan Bahasa Malaysia yang natural dan santai
    - Boleh campur sedikit English (rojak style Malaysia)
    - Panggil diri "aku", user dengan nama mereka
    - Guna kata-kata seperti: nak, tak, lah, pun, kan, weh, eh
    - Jawapan pendek dan mesra dengan emoji 😊🎯🤗
    - Jangan terlalu formal atau kaku

    **📜 SEJARAH PERCAKAPAN #{channel}:**
    {sqlite_history[:800] if sqlite_history else "Tiada sejarah"}

    **💬 KONTEKS TERKINI:**
    {current_context}

    **📝 MESEJ DARI {nick}:**
    "{message}"

    Jawab dalam format:
    <DECISION>YA atau TIDAK</DECISION>
    <RESPONSE>jawapan dalam BM</RESPONSE>"""

            # English prompt - diperbaiki  
            english_prompt = f"""You are {self.nick} ("aku" mean me or I'm), an IRC bot who chats naturally in English.

    **🎯 ENGLISH CHAT STYLE:**
    - Natural, casual English conversation
    - Can mix some Malay words (Malaysian rojak style)
    - "aku" mean me or I'm, users by their names
    - Short, friendly responses with revelan emojis 😊👍🎯
    - Don't be too formal or robotic

    **📜 CONVERSATION HISTORY #{channel}:**
    {sqlite_history[:800] if sqlite_history else "No history"}

    **💬 CURRENT CONTEXT:**
    {current_context}

    **📝 MESSAGE FROM {nick}:**
    "{message}"

    Respond in format:
    <DECISION>YES or NO</DECISION>
    <RESPONSE>response in English</RESPONSE>"""

            # Mixed/Rojak prompt - diperbaiki
            mixed_prompt = f"""You are {self.nick} (call yourself "aku"), an IRC bot who speaks Malaysian rojak (mix Malay-English).

    **🎯 ROJAK STYLE:**
    - Natural mix of Malay and English (Malaysian style)
    - Use words like: can la, like that lor, nak, tak, also, one
    - Call yourself "aku", users by their names  
    - Casual and friendly with emojis 😊🎯
    - Short responses, don't be formal

    **📜 CONVERSATION HISTORY #{channel}:**
    {sqlite_history[:800] if sqlite_history else "No history"}

    **💬 CURRENT CONTEXT:**
    {current_context}

    **📝 MESSAGE FROM {nick}:**
    "{message}"

    Respond in format:
    <DECISION>YES or NO</DECISION>
    <RESPONSE>rojak style response</RESPONSE>"""

            # Select appropriate prompt
            prompts = {
                'malay': malay_prompt,
                'english': english_prompt,
                'mixed': mixed_prompt
            }

            system_prompt = prompts.get(detected_lang, mixed_prompt)

            print(f"🧠 Using {detected_lang.upper()} prompt")

            # ==================== 🎯 RETRY MECHANISM 3x ====================
            max_retries = 3

            for attempt in range(max_retries):
                try:
                    print(f"🔄 AI Attempt {attempt + 1}/{max_retries}")

                    # API call
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{nick} in #{channel}: {message[:150]}"}
                    ]

                    payload = {
                        "model": "llama-3.1-8b-instant",
                        "messages": messages,
                        "max_tokens": 150,
                        "temperature": 0.8,
                        "top_p": 0.9
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

                        # Enforce minimum thinking time
                        if total_time < self.min_thinking_time:
                            extra_wait = self.min_thinking_time - total_time
                            print(f"⏳ Waiting {extra_wait:.1f}s more...")
                            time.sleep(extra_wait)

                        print(f"🧠 AI Response (attempt {attempt+1}): '{ai_text[:200]}...'")

                        # Parse response dengan language awareness
                        decision, bot_response = self.parse_ai_response_fixed(ai_text, detected_lang)

                        # 🎯 🎯 🎯 **MODIFY DI SINI: LOGIC BARU** 🎯 🎯 🎯
                        # Jika ada response yang cukup panjang, kita HANTAR walaupun decision TIDAK/NO
                        if bot_response and len(bot_response.strip()) >= 10:  # Minimum 10 chars
                            print(f"✅ AI ada response yang cukup panjang ({len(bot_response)} chars)")

                            # Auto-add emoji jika sesuai
                            if not any(emoji in bot_response for emoji in ['😊', '😅', '😂', '👍', '🎯', '🤗']):
                                bot_response += " 😊"

                            print(f"🎯 Will RESPOND dengan response (decision was: {decision})")
                            return True, bot_response
                        elif decision in ["YA", "YES"] and bot_response and len(bot_response.strip()) > 3:
                            # Original logic untuk YA/YES dengan response
                            print(f"🎯 AI decided to RESPOND in {channel}")
                            return True, bot_response
                        else:
                            print(f"⚠️ Attempt {attempt+1}: No valid response (decision: {decision}, length: {len(bot_response) if bot_response else 0})")

                            # Jika bukan attempt terakhir, retry
                            if attempt < max_retries - 1:
                                print(f"🔄 Retrying in 0.5s...")
                                time.sleep(0.5)
                                continue
                            else:
                                print(f"🎯 AI decided to SKIP in {channel} (all attempts failed)")
                                return False, ""

                    else:
                        print(f"❌ AI API Error {response.status_code} on attempt {attempt+1}")
                        if attempt < max_retries - 1:
                            time.sleep(0.5)
                            continue

                except Exception as e:
                    print(f"❌ AI Error on attempt {attempt+1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                        continue

            print(f"❌ All {max_retries} attempts failed")
            return False, ""

        except Exception as e:
            print(f"❌ AI Process Error: {e}")
            return False, ""

    def parse_ai_response_fixed(self, ai_text, language):
        """Fixed parser untuk AI response dengan better language handling"""
        if not ai_text:
            return "NO", ""

        ai_text = ai_text.strip()
        print(f"🔧 PARSING [{language}]: '{ai_text[:100]}...'")

        # Language-specific decision words
        if language == 'malay':
            yes_words = ['YA', 'SETUJU', 'BOLEH']
            no_words = ['TIDAK', 'TAK', 'TAKNAK']
            default_yes = 'YA'
            default_no = 'TIDAK'
        else:  # english or mixed
            yes_words = ['YES', 'YA', 'OK', 'SURE']
            no_words = ['NO', 'TIDAK', 'NAH', 'NOPE']
            default_yes = 'YES'
            default_no = 'NO'

        decision = default_no
        bot_response = ""

        # ==================== 🎯 PATTERN 1: XML FORMAT ====================
        decision_match = re.search(r'<DECISION>\s*([^<]+?)\s*</DECISION>', ai_text, re.IGNORECASE)
        response_match = re.search(r'<RESPONSE>\s*(.*?)\s*</RESPONSE>', ai_text, re.DOTALL | re.IGNORECASE)

        if decision_match:
            decision_text = decision_match.group(1).strip().upper()

            if any(yes_word in decision_text for yes_word in yes_words):
                decision = default_yes
            else:
                decision = default_no

            print(f"🔧 Found XML decision: {decision_text} -> {decision}")

        if response_match:
            bot_response = response_match.group(1).strip()
            print(f"🔧 Found XML response: '{bot_response[:50]}...'")

        # ==================== 🎯 PATTERN 2: MARKDOWN BOLD FORMAT ====================
        # Contoh: **DECISION:YES** atau **DECISION: NO** atau **RESPONSE:**
        if not decision_match:
            # Cari **DECISION:YES** atau **DECISION: NO**
            md_decision_match = re.search(r'\*\*DECISION\s*:\s*([^\*]+)\*\*', ai_text, re.IGNORECASE)

            if md_decision_match:
                decision_text = md_decision_match.group(1).strip().upper()

                if any(yes_word in decision_text for yes_word in yes_words):
                    decision = default_yes
                else:
                    decision = default_no

                print(f"🔧 Found Markdown decision: '{decision_text}' -> {decision}")

        if not response_match:
            # Cari **RESPONSE:** text
            md_response_match = re.search(r'\*\*RESPONSE\s*:\s*\*\*(.*?)(?:\*\*|$)', ai_text, re.DOTALL | re.IGNORECASE)

            if md_response_match:
                bot_response = md_response_match.group(1).strip()
                print(f"🔧 Found Markdown response: '{bot_response[:50]}...'")
            else:
                # Pattern alternatif: **RESPONSE:** diikuti text (tanpa closing **)
                if '**RESPONSE:**' in ai_text.upper() or '**RESPONSE:**' in ai_text:
                    start_idx = ai_text.upper().find('**RESPONSE:**')
                    if start_idx != -1:
                        start_idx += len('**RESPONSE:**')
                        bot_response = ai_text[start_idx:].strip()
                        print(f"🔧 Found **RESPONSE:** without closing: '{bot_response[:50]}...'")

        # ==================== 🎯 PATTERN 3: SIMPLE TEXT FORMAT ====================
        # Contoh: DECISION: YES (tanpa **)
        if not decision_match and not md_decision_match:
            simple_decision_match = re.search(r'DECISION\s*:\s*([^\n]+)', ai_text, re.IGNORECASE)

            if simple_decision_match:
                decision_text = simple_decision_match.group(1).strip().upper()

                if any(yes_word in decision_text for yes_word in yes_words):
                    decision = default_yes
                else:
                    decision = default_no

                print(f"🔧 Found simple text decision: '{decision_text}' -> {decision}")

        if not response_match and not md_response_match:
            simple_response_match = re.search(r'RESPONSE\s*:\s*(.*?)(?:\n\n|\n<|$)', ai_text, re.DOTALL | re.IGNORECASE)

            if simple_response_match:
                bot_response = simple_response_match.group(1).strip()
                print(f"🔧 Found simple text response: '{bot_response[:50]}...'")

        # ==================== 🎯 FALLBACK: Extract dari text selepas decision ====================
        if not bot_response:
            # Try to extract response after decision line
            if decision_match:
                remaining_text = ai_text[decision_match.end():].strip()
                # Remove any remaining XML tags
                remaining_text = re.sub(r'<[^>]*>', '', remaining_text).strip()
                if remaining_text:
                    bot_response = remaining_text
            elif md_decision_match:
                # Untuk markdown format
                remaining_text = ai_text[md_decision_match.end():].strip()
                if remaining_text:
                    bot_response = remaining_text

        # ==================== 🎯 ULTIMATE FALLBACK: Ambil semua content ====================
        if not bot_response:
            # Split into lines
            lines = [line.strip() for line in ai_text.split('\n') if line.strip()]

            content_lines = []
            skip_next = False

            for line in lines:
                line_upper = line.upper()

                # Skip decision/response lines
                if (line_upper.startswith('<DECISION>') or 
                    line_upper.startswith('</DECISION>') or
                    line_upper.startswith('<RESPONSE>') or 
                    line_upper.startswith('</RESPONSE>') or
                    'DECISION:' in line_upper or
                    'RESPONSE:' in line_upper or
                    line_upper in yes_words + no_words):

                    # Jika line ada **DECISION:** atau **RESPONSE:**, skip line tu
                    if '**DECISION:**' in line_upper or '**RESPONSE:**' in line_upper:
                        continue
                    skip_next = True
                    continue

                if skip_next:
                    skip_next = False
                    continue

                if line and len(line.strip()) > 2:
                    content_lines.append(line)

            if content_lines:
                bot_response = ' '.join(content_lines).strip()
                print(f"🔧 Fallback content: '{bot_response[:50]}...'")

        # ==================== 🎯 CLEAN RESPONSE ====================
        if bot_response:
            # 🎯 **FIX: Remove markdown formatting FIRST**
            # Remove **bold** 
            bot_response = re.sub(r'\*\*(.*?)\*\*', r'\1', bot_response)
            # Remove *italic*
            bot_response = re.sub(r'\*(?!\s)(.*?)\*', r'\1', bot_response)
            # Remove _underscore_
            bot_response = re.sub(r'_(.*?)_', r'\1', bot_response)

            # 🎯 **Remove decision/response labels yang mungkin masih ada**
            prefixes_to_remove = [
                'DECISION:', 'RESPONSE:', 'JAWAPAN:', 'BALAS:', 'ANSWER:',
                ':', '-', '•', '>'
            ]

            for prefix in prefixes_to_remove:
                # Check case insensitive
                if bot_response.upper().startswith(prefix.upper()):
                    bot_response = bot_response[len(prefix):].strip()

            # Remove remaining XML tags
            bot_response = re.sub(r'<[^>]*>', '', bot_response).strip()

            # 🎯 **Remove any stray markdown chars**
            bot_response = bot_response.replace('**', '').replace('*', '')

            # Clean punctuation
            bot_response = bot_response.strip(' .,;:!?*#-')

            # Ensure proper capitalization
            if bot_response and bot_response[0].islower():
                bot_response = bot_response[0].upper() + bot_response[1:]

        # Final validation
        if decision == default_yes and (not bot_response or len(bot_response.strip()) < 3):
            # If decision is yes but no valid response, change to no
            decision = default_no
            bot_response = ""

        print(f"🔧 FINAL PARSE: decision={decision}, response='{bot_response[:80] if bot_response else 'NONE'}...'")

        return decision, bot_response

    # ==================== HELPER METHODS ====================
    def _get_optimized_history_for_ai(self, channel, nick, days=7, max_messages=50):
        """Get optimized history for AI context"""
        try:
            conn = sqlite3.connect('logs/chat_logs.sqlite', timeout=10)
            cursor = conn.cursor()

            # Create table if not exists
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

            cutoff_time = time.time() - (days * 24 * 3600)

            cursor.execute('''
                SELECT nick, message, timestamp 
                FROM chat_logs 
                WHERE channel = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (channel, cutoff_time, max_messages))

            messages = cursor.fetchall()
            conn.close()

            if not messages:
                return f"📭 No recent history in {channel}"

            # Format messages
            history_lines = []
            for msg in sorted(messages, key=lambda x: x[2])[-30:]:  # Last 30 messages
                msg_nick, msg_text, msg_time = msg

                if len(msg_text.strip()) < 3 or self._is_bot_message(msg_nick, msg_text):
                    continue

                time_str = datetime.fromtimestamp(msg_time).strftime('%H:%M')
                truncated = msg_text[:100] + "..." if len(msg_text) > 100 else msg_text
                history_lines.append(f"[{time_str}] {msg_nick}: {truncated}")

            return "\n".join(history_lines[-20:])  # Return last 20 formatted messages

        except Exception as e:
            print(f"❌ History error: {e}")
            return ""

    def _is_bot_message(self, nick, text):
        """Check if message is from a bot"""
        bot_indicators = ['KCFM', 'RADIO', 'BOT', 'SERV', 'LoveFM', 'LepakFM', 'ZumbaQuiz']
        return any(indicator in nick.upper() for indicator in bot_indicators)

    # ==================== MESSAGE PROCESSING ====================
    def process_message(self, nick, message, channel):
        """Process incoming messages"""
        print(f"\n📩 {nick} in {channel}: {message}")

        self.current_processing_channel = channel
        current_time = time.time()

        # Add to buffer and memory
        self.add_to_message_buffer(nick, message, channel, current_time)
        self.add_to_memory(nick, message, channel)

        # Check silent mode
        self.check_silent_mode()

        # Handle special commands
        if self.handle_special_commands(message, nick, channel):
            return

        if self.silent_mode:
            print(f"🔇 Silent mode active")
            return

        # Track mentions
        self.track_mention(nick, message, channel)

        # Process buffer
        window_messages = self.process_buffer_if_ready(channel)

        if window_messages:
            if current_time - self.last_ai_time < self.ai_cooldown:
                print(f"⏳ AI cooldown active")
                return

            # Process messages
            for msg in window_messages:
                if msg['nick'] == nick:  # Process current user's message
                    should_respond = (
                        self.nick.lower() in msg['message'].lower() or
                        self.is_user_in_focus(nick)
                    )

                    if should_respond:
                        self.last_ai_time = current_time

                        conversation_history = self.get_filtered_conversation_history(channel)
                        is_in_focus = self.is_user_in_focus(nick)

                        should_respond, ai_response = self.ai_analyze_message(
                            msg['message'], nick, channel, conversation_history, is_in_focus
                        )

                        if should_respond and ai_response:
                            print(f"🎯 Sending AI response to {nick}")
                            self.send_message(channel, ai_response)
                        break

    # ==================== SUPPORTING METHODS ====================
    def add_to_message_buffer(self, nick, message, channel, timestamp):
        """Add message to buffer"""
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

        # Clean old messages
        current_time = time.time()
        self.message_buffers[channel] = [
            msg for msg in self.message_buffers[channel]
            if current_time - msg['timestamp'] < 5
        ]

    def process_buffer_if_ready(self, channel):
        """Process buffer if ready"""
        if channel not in self.message_buffers:
            return None

        current_time = time.time()

        if (not self.message_buffers[channel] or 
            current_time - self.last_buffer_process.get(channel, 0) < 1):
            return None

        unprocessed = [msg for msg in self.message_buffers[channel] if not msg['processed']]

        if unprocessed:
            oldest = min(unprocessed, key=lambda x: x['timestamp'])
            window_start = oldest['timestamp']

            window_messages = [
                msg for msg in self.message_buffers[channel]
                if msg['timestamp'] - window_start <= 3 and not msg['processed']
            ]

            if window_messages:
                for msg in window_messages:
                    msg['processed'] = True

                self.last_buffer_process[channel] = current_time
                return window_messages

        return None

    def add_to_memory(self, nick, message, channel):
        """Add message to memory with auto-cleanup"""
        if nick.lower() == self.nick.lower():
            return

        clean_message = self.strip_irc_codes(message)

        if not clean_message or len(clean_message.strip()) < 2:
            return

        memory_entry = {
            'nick': nick,
            'message': clean_message,
            'channel': channel,
            'timestamp': time.time(),
            'time_str': time.strftime('%I:%M%p', time.localtime()).lower(),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Initialize memory if needed
        if not hasattr(self, 'conversation_memory'):
            self.conversation_memory = []

        # Check if memory is full
        if len(self.conversation_memory) >= self.max_messages:
            # Archive old messages
            messages_to_archive = self.conversation_memory[:self.cleanup_threshold]
            self.save_to_sqlite(messages_to_archive)
            self.conversation_memory = self.conversation_memory[self.cleanup_threshold:]

        self.conversation_memory.append(memory_entry)
        self.log_message_to_sqlite(memory_entry)

    def save_to_sqlite(self, messages):
        """Save messages to SQLite"""
        try:
            if not messages:
                return

            os.makedirs('logs', exist_ok=True)
            conn = sqlite3.connect('logs/chat_logs.sqlite')
            cursor = conn.cursor()

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

            for msg in messages:
                cursor.execute('''
                INSERT INTO chat_logs (nick, message, channel, timestamp, time_str)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    msg['nick'], msg['message'], msg['channel'],
                    msg['timestamp'], msg.get('time_str', '')
                ))

            conn.commit()
            conn.close()
            print(f"💾 Saved {len(messages)} messages to SQLite")

        except Exception as e:
            print(f"❌ Error saving to SQLite: {e}")

    def log_message_to_sqlite(self, message):
        """Log message to SQLite in real-time"""
        try:
            os.makedirs('logs', exist_ok=True)
            conn = sqlite3.connect('logs/chat_logs.sqlite')
            cursor = conn.cursor()

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

            cursor.execute('''
            INSERT INTO chat_logs (nick, message, channel, timestamp, time_str)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                message['nick'], message['message'], message['channel'],
                message['timestamp'], message.get('time_str', '')
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Error logging to SQLite: {e}")

    def cleanup_old_messages(self):
        """Auto cleanup old messages"""
        try:
            current_time = time.time()

            if current_time - self.last_cleanup_time < self.cleanup_interval:
                return

            print(f"🧹 Starting auto-cleanup...")

            os.makedirs('logs', exist_ok=True)
            conn = sqlite3.connect('logs/chat_logs.sqlite')
            cursor = conn.cursor()

            expiry_timestamp = current_time - (self.memory_expiry_days * 86400)

            cursor.execute('DELETE FROM chat_logs WHERE timestamp < ?', (expiry_timestamp,))
            deleted_count = cursor.rowcount

            cursor.execute('VACUUM')
            conn.commit()
            conn.close()

            self.last_cleanup_time = current_time
            print(f"🧹 Cleanup completed: {deleted_count} messages deleted")

        except Exception as e:
            print(f"❌ Cleanup error: {e}")

    # ==================== FOCUS AND MENTION SYSTEM ====================
    def track_mention(self, user, message, channel):
        """Track mentions for focus system"""
        if self.nick.lower() in message.lower():
            current_time = time.time()

            if user not in self.user_mentions:
                self.user_mentions[user] = {'total_count': 0, 'last_mention_time': current_time}

            self.user_mentions[user]['total_count'] += 1
            self.user_mentions[user]['last_mention_time'] = current_time

            if self.user_mentions[user]['total_count'] >= self.mentions_threshold:
                self.update_user_focus(user, channel)
                self.user_mentions[user]['total_count'] = 0

    def update_user_focus(self, user, channel):
        """Update user focus"""
        if self.is_user_in_focus(user):
            return

        current_time = time.time()
        self.user_focus[user] = current_time + self.focus_duration

        focus_message = f"auto reply activated untuk {user} tanpa mention {self.nick} lagi. Taip '.clear' untuk ignore."
        self.send_message(channel, focus_message)

    def is_user_in_focus(self, user):
        """Check if user is in focus"""
        current_time = time.time()

        if user in self.user_focus:
            if current_time < self.user_focus[user]:
                return True
            else:
                del self.user_focus[user]

        return False

    def get_filtered_conversation_history(self, channel):
        """Get filtered conversation history for channel"""
        filtered_history = []

        for msg in self.conversation_memory[-20:]:
            if (msg['channel'] == channel and 
                not msg['message'].startswith('ACTION') and
                len(msg['message'].strip()) > 3 and
                not self._is_bot_message(msg['nick'], msg['message'])):
                filtered_history.append((msg['nick'], msg['message']))

        return filtered_history[-8:]

    # ==================== SPECIAL COMMANDS ====================
    def handle_special_commands(self, message, nick, channel):
        """Handle special bot commands"""
        message_lower = message.lower()
        bot_nick_lower = self.nick.lower()

        # Silent command
        if any(cmd in message_lower for cmd in ['diam', 'shut up', 'senyap']) and bot_nick_lower in message_lower:
            self.silent_mode = True
            self.silent_until = time.time() + 300
            self.send_action(channel, f"goes silent after {nick}'s command 🤐")
            return True

        # Speak command  
        if any(cmd in message_lower for cmd in ['speak', 'cakap', 'reply']) and bot_nick_lower in message_lower:
            self.silent_mode = False
            self.silent_until = 0
            self.send_action(channel, f"starts talking again after {nick}'s request 🔊")
            return True

        # Clear focus
        if message.lower().strip() == '.clear':
            if nick in self.user_focus:
                del self.user_focus[nick]
                self.send_message(channel, f"Focus cleared untuk {nick}")
                return True

        return False

    def check_silent_mode(self):
        """Check if silent mode should be disabled"""
        if self.silent_mode and time.time() > self.silent_until:
            self.silent_mode = False

    # ==================== MESSAGE SENDING ====================
    def send_message(self, target, message):
        """Send message with proper formatting"""
        formatted_messages = self.format_long_message(message)

        if len(formatted_messages) > 4:
            formatted_messages = formatted_messages[:4]

        for formatted_msg in formatted_messages:
            self.queue_message(target, formatted_msg, priority=1)

    def send_action(self, target, action_text):
        """Send ACTION message"""
        action_message = f"\x01ACTION {action_text}\x01"
        self.queue_message(target, action_message, priority=1)

    def format_long_message(self, message):
        """Format long messages"""
        if len(message) <= 170:
            return [message]

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

            if len(lines) >= 4:
                if current_line:
                    lines.append(current_line[:170] + "...")
                break

        if current_line and len(lines) < 4:
            lines.append(current_line)

        return lines

    def queue_message(self, target, message, priority=1):
        """Queue message for sending"""
        if len(self.message_queue) >= self.max_queue_size:
            self.message_queue.popleft()

        self.message_queue.append((target, message, priority, time.time()))
        self.process_queue()

    def process_queue(self):
        """Process message queue"""
        if not self.message_queue or self.is_sending:
            return

        self.is_sending = True

        try:
            while self.message_queue:
                current_time = time.time()
                time_since_last = current_time - self.last_send_time

                if time_since_last < self.min_delay:
                    time.sleep(self.min_delay - time_since_last)

                target, message, priority, queue_time = self.message_queue.popleft()

                if current_time - queue_time > 30:
                    continue

                self.send_raw(f"PRIVMSG {target} :{message}")
                self.last_send_time = current_time

                if self.message_queue:
                    time.sleep(random.uniform(1.0, 2.0))

        except Exception as e:
            print(f"❌ Queue error: {e}")
        finally:
            self.is_sending = False

    # ==================== PRIVATE CHAT SYSTEM ====================
    def handle_private_message(self, nick, message):
        """Handle private messages"""
        current_time = time.time()

        if current_time - self.last_private_reply < self.private_cooldown:
            return

        self.last_private_reply = current_time

        # Track conversation
        if nick not in self.private_conversations:
            self.private_conversations[nick] = []

        self.private_conversations[nick].append({
            'time': current_time,
            'sender': nick,
            'message': message,
            'type': 'user'
        })

        # Get AI response
        ai_response = self.get_ai_private_response(nick, message)

        if ai_response:
            response = ai_response
        else:
            fallbacks = [
                f"Hai {nick}! 😊",
                f"Hello {nick}! 👍",
                f"Hey {nick}! 🎯"
            ]
            response = random.choice(fallbacks)

        self.send_private_message(nick, response)

    def get_ai_private_response(self, nick, message):
        """Get AI response for private message"""
        if not self.api_key:
            return None

        try:
            detected_lang = self.detect_language(message)

            if detected_lang == 'malay':
                system_prompt = f"Anda ialah {self.nick}, bot IRC yang mesra. Jawab dalam Bahasa Malaysia yang santai dengan emoji."
            else:
                system_prompt = f"You are {self.nick}, a friendly IRC bot. Respond in casual English with emojis."

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{nick}: {message}"}
                ],
                "max_tokens": 80,
                "temperature": 0.8
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()

        except Exception as e:
            print(f"❌ Private AI error: {e}")

        return None

    def send_private_message(self, nick, message):
        """Send private message"""
        self.send_raw(f"PRIVMSG {nick} :{message}")

    # ==================== MAIN LOOP ====================
    def run(self):
        """Main bot loop"""
        print("🚀 Starting MinahBot with Enhanced Language Support...")

        self.connect()
        buffer = ""
        self.last_cleanup_time = time.time()

        while self.running:
            try:
                self.sock.settimeout(1.0)

                # Auto cleanup check
                current_time = time.time()
                if current_time - self.last_cleanup_time >= self.cleanup_interval:
                    self.cleanup_old_messages()

                try:
                    data = self.sock.recv(2048).decode('utf-8', errors='ignore')
                except socket.timeout:
                    if self.message_queue:
                        self.process_queue()
                    continue

                if not data:
                    print("❌ Connection lost")
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

                    # Parse PRIVMSG
                    if "PRIVMSG" in line:
                        try:
                            sender_part = line.split(' ')[0]
                            sender = sender_part[1:].split('!')[0]

                            if sender.lower() == self.nick.lower():
                                continue

                            parts = line.split(' ', 3)
                            if len(parts) >= 4:
                                target = parts[2]
                                message = parts[3][1:] if parts[3].startswith(':') else parts[3]

                                # Private message
                                if target.lower() == self.nick.lower():
                                    if self.private_chat_enabled:
                                        threading.Thread(
                                            target=self.handle_private_message,
                                            args=(sender, message),
                                            daemon=True
                                        ).start()

                                # Channel message
                                elif target.startswith('#'):
                                    target_lower = target.lower()
                                    matched_channel = None

                                    for channel in self.channels:
                                        if channel.lower() == target_lower:
                                            matched_channel = channel
                                            break

                                    if matched_channel and sender != self.nick:
                                        threading.Thread(
                                            target=self.process_message,
                                            args=(sender, message, matched_channel),
                                            daemon=True
                                        ).start()

                        except Exception as e:
                            print(f"❌ PRIVMSG parse error: {e}")

                    # Handle numeric replies
                    elif line.startswith(':'):
                        parts = line.split()
                        if len(parts) > 1 and parts[1].isdigit():
                            code = parts[1]

                            if code in ['001', '376', '422']:
                                self.connected = True

                            elif code == '433':
                                self.nick = f"{self.nick}_"
                                self.send_raw(f"NICK {self.nick}")

                            elif code == '353':  # User list
                                if len(parts) >= 5:
                                    channel_from_server = parts[4]
                                    users_msg = ' '.join(parts[5:])[1:] if len(parts) > 5 else ""
                                    users = users_msg.split()

                                    matched_channel = None
                                    for channel in self.channels:
                                        if channel.lower() == channel_from_server.lower():
                                            matched_channel = channel
                                            break

                                    if matched_channel:
                                        if matched_channel not in self.channel_users:
                                            self.channel_users[matched_channel] = set()

                                        for user in users:
                                            clean_user = user.lstrip('@+%&~')
                                            self.channel_users[matched_channel].add(clean_user)

                # Process queue
                if self.message_queue:
                    self.process_queue()

            except socket.error as e:
                print(f"❌ Socket error: {e}")
                time.sleep(15)
                self.connect()

            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(30)
                if not self.connected:
                    self.connect()


# ==================== DISPLAY CLASS ====================
class DisplayFixed:
    """Display FIXED - 1 baris sahaja"""

    @staticmethod
    def get_malaysia_time():
        utc_now = datetime.utcnow()
        return utc_now + timedelta(hours=MALAYSIA_UTC_OFFSET)

    @staticmethod
    def get_temp_emoji(temp):
        if temp >= 35: return "🔥"
        elif temp >= 32: return "🥵"
        elif temp >= 30: return "🌞"
        elif temp >= 27: return "😊"
        elif temp >= 24: return "😌"
        else: return "🥶"

    @staticmethod
    def get_weather_icon(code):
        icons = {
            0: "☀️", 1: "☀️", 2: "🌤️", 3: "☁️",
            45: "🌫️", 48: "🌫️",
            51: "🌦️", 53: "🌧️", 55: "🌧️💦",
            61: "🌦️", 63: "🌧️", 65: "⛈️",
            80: "🌦️", 81: "🌧️", 82: "⛈️",
            95: "⛈️", 96: "⛈️", 99: "⛈️"
        }
        return icons.get(code, "🌡️")

    @staticmethod
    def format_cuaca_jelas(data):
        """Format cuaca dalam 1 BARIS SAHAJA"""
        if not data:
            return ["❌ data cuaca tak dapat"]

        lokasi = data['lokasi']
        suhu = data['suhu']
        temp_emoji = DisplayFixed.get_temp_emoji(suhu)
        weather_icon = DisplayFixed.get_weather_icon(data['weather_code'])

        # Deskripsi suhu
        if suhu >= 35: desc = "🔥 panas melampau"
        elif suhu >= 32: desc = "🥵 sangat panas"
        elif suhu >= 30: desc = "🌞 panas"
        elif suhu >= 27: desc = "😊 nyaman"
        elif suhu >= 24: desc = "😌 sejuk"
        else: desc = "🥶 sangat sejuk"

        # SEMUA INFO DALAM 1 BARIS
        line_items = []

        # 1. Info waktu dan greeting
        now = DisplayFixed.get_malaysia_time()
        waktu = now.strftime("%I:%M%p").lower().lstrip('0')

        # Hari Malaysia
        hari_malaysia = {
            'Monday': 'Isnin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Khamis', 'Friday': 'Jumaat', 'Saturday': 'Sabtu',
            'Sunday': 'Ahad'
        }
        hari = hari_malaysia.get(now.strftime("%A"), now.strftime("%A"))
        tarikh = now.strftime("%d/%m")

        # Greeting
        hour = now.hour
        if 5 <= hour < 12:
            greeting = "🌅Selamat pagi"
        elif 12 <= hour < 15:
            greeting = "☀️Selamat tengahari"
        elif 15 <= hour < 19:
            greeting = "⛅Selamat petang"
        else:
            greeting = "🌃Selamat malam"

        line_items.append(f"Tepat 🕐 {waktu} • {greeting} • {hari} {tarikh} • Cuaca")

        # 2. Info cuaca
        line_items.append(f"{weather_icon} {lokasi}: {temp_emoji} {suhu}°C ({desc})")

        # 3. Info kelembapan
        hum = data['kelembapan']
        if hum >= 85: 
            line_items.append(f"💦💧 {hum}% (sgt lembap)")
        elif hum >= 75: 
            line_items.append(f"💦 {hum}% (lembap)")
        elif hum <= 50: 
            line_items.append(f"🏜️ {hum}% (kering)")
        else: 
            line_items.append(f"💧 {hum}% (normal)")

        # 4. Info hujan
        if data['hujan'] > 0:
            if data['hujan'] >= 20: 
                line_items.append(f"⛈️ {data['hujan']}mm (ribut petir)")
            elif data['hujan'] >= 10: 
                line_items.append(f"🌧️💦 {data['hujan']}mm (hujan lebat)")
            elif data['hujan'] >= 5: 
                line_items.append(f"🌧️ {data['hujan']}mm (kehujanan)")
            elif data['hujan'] >= 1: 
                line_items.append(f"🌦️ {data['hujan']}mm (hujan gerimis)")
            else: 
                line_items.append(f"🌦️ {data['hujan']}mm (hujan rintik)")
        elif data['peluang_hujan'] > 70:
            line_items.append(f"☔ {data['peluang_hujan']}% (mungkin hujan)")
        elif data['peluang_hujan'] > 40:
            line_items.append(f"🌂 {data['peluang_hujan']}% (mungkin)")
        else:
            line_items.append(f"☀️ {data['peluang_hujan']}% (cerah)")

        # 5. Info angin
        if data['angin'] >= 20:
            line_items.append(f"💨🌀 {data['angin']}km/j (angin kencang)")
        elif data['angin'] >= 15:
            line_items.append(f"💨💨 {data['angin']}km/j (angin kuat)")
        elif data['angin'] >= 10:
            line_items.append(f"💨 {data['angin']}km/j (angin sedang)")
        elif data['angin'] >= 5:
            line_items.append(f"🍃 {data['angin']}km/j (angin sepoi)")
        else:
            line_items.append(f"🌿 {data['angin']}km/j (angin tenang)")

        # 6. Arah angin
        if 'arah_angin' in data and data['arah_angin']:
            line_items.append(f"🧭 {data['arah_angin']}")

        # 7. Tips
        tips = []
        if suhu >= 32: tips.append("minum air 🥤")
        if suhu <= 24: tips.append("pakai jaket 🧥")
        if data['hujan'] >= 10: tips.append("elak keluar ⛈️")
        elif data['hujan'] >= 5: tips.append("bawa payung ☔")
        elif data['peluang_hujan'] > 70: tips.append("stanby payung 🌂")

        if tips:
            tip_display = f"💡 {tips[0]}"
        else:
            if hour >= 5 and hour < 12:
                tip_display = "💡 pagi yang ceria! 🌅"
            elif hour >= 12 and hour < 13:
                tip_display = "💡 rehat tengahari 😴"
            elif hour >= 14 and hour < 19:
                tip_display = "💡 petang yang santai 🌇"
            else:
                tip_display = "💡 malam yang tenang 🌃"

        line_items.append(tip_display)

        # Gabungkan semua dalam 1 baris
        full_line = " • ".join(line_items)

        if len(full_line) > MAX_MESSAGE_LENGTH:
            full_line = full_line[:MAX_MESSAGE_LENGTH-3] + "..."

        return [full_line]

    @staticmethod
    def format_solat_fixed(data):
        """Solat dalam 2 baris dengan data betul"""
        if not data:
            return ["❌ data solat tak dapat"]

        lokasi = data['lokasi']
        now = DisplayFixed.get_malaysia_time()

        # Hari Malaysia
        hari_malaysia = {
            'Monday': 'Isnin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Khamis', 'Friday': 'Jumaat', 'Saturday': 'Sabtu',
            'Sunday': 'Ahad'
        }
        hari = hari_malaysia.get(now.strftime("%A"), now.strftime("%A"))
        tarikh = now.strftime("%d %b %Y")
        waktu = now.strftime("%I:%M%p").lower().lstrip('0')

        # LINE 1: Header
        line1 = f"📅 Waktu Solat {lokasi} • {hari} {tarikh} • 🕐 {waktu}"

        # Waktu solat dengan format betul
        prayers = [
            ("🌅🕌", "Subuh", data.get('subuh')),
            ("🕌🕰️", "Zohor", data.get('zohor')),
            ("⛅📿", "Asar", data.get('asar')),
            ("🌇🌙", "Maghrib", data.get('maghrib')),
            ("🌃🌟", "Isyak", data.get('isyak'))
        ]

        formatted_times = []
        for emoji, name, waktu in prayers:
            if waktu and waktu != "--:--":
                waktu_fixed = DisplayFixed.convert_to_12h(waktu)
                formatted_times.append(f"{emoji} {name}: {waktu_fixed}")

        # LINE 2: Waktu solat
        if formatted_times:
            line2 = "   ".join(formatted_times)
            return [line1, line2]
        else:
            return [line1, "⚠️ Data waktu solat tidak tersedia"]

    @staticmethod
    def convert_to_12h(time_str):
        """Convert time string ke 12h format yang betul"""
        if not time_str or time_str == "--:--":
            return "--:--"

        # Jika dah ada am/pm, return asal
        if 'am' in time_str.lower() or 'pm' in time_str.lower():
            # Remove seconds jika ada
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) >= 2:
                    hour_part = parts[0]
                    minute_part = parts[1][:2]  # Ambil 2 digit pertama
                    ampm = time_str[-2:].lower()
                    return f"{hour_part}:{minute_part}{ampm}"
            return time_str

        # Jika format HH:MM:SS atau HH:MM
        try:
            # Clean the time string
            time_str = time_str.strip()
            parts = time_str.split(':')

            if len(parts) >= 2:
                h = int(parts[0])
                m = int(parts[1][:2])  # Ambil 2 digit pertama sahaja

                # Convert to 12h format
                if h == 0:
                    return f"12:{m:02d}am"
                elif h < 12:
                    return f"{h}:{m:02d}am"
                elif h == 12:
                    return f"12:{m:02d}pm"
                else:
                    return f"{h-12}:{m:02d}pm"
        except:
            pass

        return time_str

    @staticmethod
    def format_hourly_announce(cuaca_data):
        """Hourly announce dalam 1 BARIS SAHAJA"""
        if not cuaca_data:
            return ["⚠️ Data cuaca tidak tersedia"]

        return DisplayFixed.format_cuaca_jelas(cuaca_data)

# ==================== DATA PROVIDER ====================
class DataProviderFixed:
    """Data provider dengan API betul + INTERNATIONAL SUPPORT + FIXED SOLAT"""

    def __init__(self):
        self.cache = {}
        self.cache_time = {}

        # FIXED Zone mapping untuk API (format JAKIM) - BETUL UNTUK MALAYSIA
        self.zone_mapping = {
            # Selangor & KL - SGR01 (BETUL)
            "Kuala Lumpur": "SGR01", "KL": "SGR01", "kl": "SGR01",
            "Selangor": "SGR01", "Shah Alam": "SGR01", "Putrajaya": "SGR01",

            # Johor - JHR01 (BETUL)
            "Johor": "JHR01", "Johor Bahru": "JHR01",

            # Kelantan - KTN01 (BETUL)
            "Kelantan": "KTN01", "Kota Bharu": "KTN01",

            # Kedah - KDH01 (BETUL)
            "Kedah": "KDH01", "Alor Setar": "KDH01",

            # Melaka - MLK01 (BETUL)
            "Melaka": "MLK01",

            # Pahang - PHG01 (BETUL)
            "Pahang": "PHG01", "Kuantan": "PHG01",

            # Perak - PRK01 (BETUL)
            "Perak": "PRK01", "Ipoh": "PRK01",

            # Penang - PNG01 (BETUL)
            "Penang": "PNG01", "Georgetown": "PNG01",

            # Terengganu - TRG01 (BETUL)
            "Terengganu": "TRG01", "Kuala Terengganu": "TRG01",

            # Sabah - SBH01 (BETUL)
            "Sabah": "SBH01", "Kota Kinabalu": "SBH01",

            # Sarawak - SWK01 (BETUL)
            "Sarawak": "SWK01", "Kuching": "SWK01",

            # Negeri Sembilan - NGS01 (BETUL)
            "Negeri Sembilan": "NGS01", "Seremban": "NGS01",

            # Perlis - PLS01 (BETUL)
            "Perlis": "PLS01", "Kangar": "PLS01",

            # Labuan - WLY02 (BETUL)
            "Labuan": "WLY02"
        }

        # EXPANDED INTERNATIONAL LOCATIONS
        self.locations = {
            # Malaysia
            "Kuala Lumpur": (3.1390, 101.6869), "KL": (3.1390, 101.6869),
            "Johor Bahru": (1.4927, 103.7414), "Johor": (1.4927, 103.7414),
            "Shah Alam": (3.0738, 101.5183), "Selangor": (3.0738, 101.5183),
            "Kota Bharu": (6.1254, 102.2381), "Kelantan": (6.1254, 102.2381),
            "Kuantan": (3.8126, 103.3256), "Pahang": (3.8126, 103.3256),
            "Alor Setar": (6.1184, 100.3685), "Kedah": (6.1184, 100.3685),
            "Ipoh": (4.5921, 101.0901), "Perak": (4.5921, 101.0901),
            "Kuala Terengganu": (5.3117, 103.1324), "Terengganu": (5.3117, 103.1324),
            "Georgetown": (5.4141, 100.3288), "Penang": (5.4141, 100.3288),
            "Kota Kinabalu": (5.9804, 116.0735), "Sabah": (5.9804, 116.0735),
            "Kuching": (1.5535, 110.3593), "Sarawak": (1.5535, 110.3593),
            "Melaka": (2.1896, 102.2501), "Seremban": (2.7259, 101.9378),
            "Putrajaya": (2.9264, 101.6964),

            # ASEAN Countries
            "Jakarta": (-6.2088, 106.8456), "Indonesia": (-6.2088, 106.8456),
            "Bangkok": (13.7563, 100.5018), "Thailand": (13.7563, 100.5018),
            "Singapore": (1.3521, 103.8198), "Singapura": (1.3521, 103.8198),
            "Manila": (14.5995, 120.9842), "Philippines": (14.5995, 120.9842),
            "Hanoi": (21.0285, 105.8542), "Vietnam": (21.0285, 105.8542),
            "Yangon": (16.8661, 96.1951), "Myanmar": (16.8661, 96.1951),
            "Phnom Penh": (11.5449, 104.8922), "Cambodia": (11.5449, 104.8922),
            "Vientiane": (17.9757, 102.6331), "Laos": (17.9757, 102.6331),
            "Bandar Seri Begawan": (4.9031, 114.9398), "Brunei": (4.9031, 114.9398),

            # Major World Cities
            "Tokyo": (35.6762, 139.6503), "Japan": (35.6762, 139.6503),
            "Seoul": (37.5665, 126.9780), "Korea": (37.5665, 126.9780),
            "Beijing": (39.9042, 116.4074), "China": (39.9042, 116.4074),
            "Mumbai": (19.0760, 72.8777), "India": (19.0760, 72.8777),
            "Dubai": (25.2048, 55.2708), "UAE": (25.2048, 55.2708),
            "London": (51.5074, -0.1278), "UK": (51.5074, -0.1278),
            "Paris": (48.8566, 2.3522), "France": (48.8566, 2.3522),
            "New York": (40.7128, -74.0060), "USA": (40.7128, -74.0060),
            "Sydney": (-33.8688, 151.2093), "Australia": (-33.8688, 151.2093),
        }

    def geocode_location(self, lokasi):
        """Cari koordinat lokasi menggunakan geocoding API"""
        try:
            params = {
                'name': lokasi,
                'count': 1,
                'language': 'en',
                'format': 'json'
            }

            response = requests.get(GEOCODING_API, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    return (result['latitude'], result['longitude'], result['name'])

            return None

        except Exception as e:
            print(f"⚠️ Geocoding error: {e}")
            return None

    def get_cuaca_detail(self, lokasi="Kuala Lumpur"):
        """Dapatkan data cuaca dari API - DENGAN INTERNATIONAL SUPPORT"""
        cache_key = f"cuaca_{lokasi}_{datetime.now().strftime('%Y%m%d%H')}"

        if cache_key in self.cache:
            if time.time() - self.cache_time.get(cache_key, 0) < 1800:
                return self.cache[cache_key]

        try:
            lokasi_clean = lokasi.strip().title()
            lat, lon = None, None
            final_location_name = lokasi_clean

            # 1. Cuba cari dalam predefined locations
            if lokasi_clean in self.locations:
                lat, lon = self.locations[lokasi_clean]
                print(f"🔍 Found {lokasi_clean} in predefined locations")
            else:
                # 2. Cuba partial match
                for loc in self.locations:
                    if lokasi_clean.lower() in loc.lower() or loc.lower() in lokasi_clean.lower():
                        lat, lon = self.locations[loc]
                        final_location_name = loc
                        print(f"🔍 Partial match: {lokasi_clean} -> {loc}")
                        break

            # 3. Jika masih tak jumpa, guna geocoding API
            if lat is None or lon is None:
                print(f"🌍 Geocoding {lokasi_clean}...")
                geocode_result = self.geocode_location(lokasi_clean)
                if geocode_result:
                    lat, lon, final_location_name = geocode_result
                    print(f"✅ Geocoded: {lokasi_clean} -> {final_location_name} ({lat}, {lon})")
                else:
                    # 4. Last fallback - return error instead of KL
                    print(f"❌ Cannot find location: {lokasi_clean}")
                    return None

            # Dapatkan data cuaca
            params = {
                'latitude': lat, 'longitude': lon,
                'current': ['temperature_2m', 'relative_humidity_2m', 'precipitation',
                          'weather_code', 'wind_speed_10m', 'wind_direction_10m',
                          'cloud_cover'],
                'hourly': 'precipitation_probability',
                'timezone': 'auto', 'forecast_days': 1
            }

            response = requests.get(CUACA_API, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                current = data.get('current', {})

                weather_code = current.get('weather_code', 0)

                # Arah angin
                wind_dir = current.get('wind_direction_10m', 0)
                directions = ['Utara', 'Timur Laut', 'Timur', 'Tenggara', 
                            'Selatan', 'Barat Daya', 'Barat', 'Barat Laut']
                if wind_dir:
                    index = round((wind_dir % 360) / 45) % 8
                    wind_dir_name = directions[index]
                else:
                    wind_dir_name = "-"

                # Peluang hujan
                max_precip = 0
                hourly = data.get('hourly', {})
                if 'precipitation_probability' in hourly:
                    probs = hourly['precipitation_probability'][:6]
                    max_precip = max(probs) if probs else 0

                result = {
                    'lokasi': final_location_name,
                    'suhu': round(current.get('temperature_2m', 0), 1),
                    'kelembapan': current.get('relative_humidity_2m', 0),
                    'hujan': round(current.get('precipitation', 0), 1),
                    'weather_code': weather_code,
                    'peluang_hujan': round(max_precip, 0),
                    'angin': round(current.get('wind_speed_10m', 0), 1),
                    'arah_angin': wind_dir_name,
                    'awan': current.get('cloud_cover', 0),
                }

                self.cache[cache_key] = result
                self.cache_time[cache_key] = time.time()
                print(f"✅ Weather data for {final_location_name}: {result['suhu']}°C")
                return result

            return None

        except Exception as e:
            print(f"⚠️ Error cuaca: {e}")
            return None

    def get_solat(self, lokasi="Kuala Lumpur"):
        """Dapatkan waktu solat dari API BETUL - FIXED UNTUK MALAYSIA"""
        cache_key = f"solat_{lokasi}_{datetime.now().strftime('%Y%m%d')}"

        if cache_key in self.cache:
            if time.time() - self.cache_time.get(cache_key, 0) < 3600:
                return self.cache[cache_key]

        lokasi_clean = lokasi.strip().title()
        original_location = lokasi_clean  # Simpan nama asal

        # Check jika lokasi adalah Malaysia
        zone_code = self.zone_mapping.get(lokasi_clean)

        if not zone_code:
            # Cuba partial match untuk Malaysia
            for malaysian_location in self.zone_mapping:
                if lokasi_clean.lower() in malaysian_location.lower() or malaysian_location.lower() in lokasi_clean.lower():
                    zone_code = self.zone_mapping[malaysian_location]
                    lokasi_clean = malaysian_location  # Guna nama yang betul
                    print(f"🔍 Solat partial match: {original_location} -> {lokasi_clean} (zone: {zone_code})")
                    break

        if not zone_code:
            # Bukan lokasi Malaysia
            return {
                'lokasi': original_location,
                'error': 'Waktu solat hanya tersedia untuk lokasi di Malaysia'
            }

        # Dapatkan tarikh sekarang
        now = DisplayFixed.get_malaysia_time()
        year = now.year
        month = now.month
        day = now.day

        print(f"🔍 Requesting solat for {lokasi_clean} (zone: {zone_code}) on {day}/{month}/{year}")

        # GUNA API V1: /solat/{zone}/{day}
        try:
            url = f"{SOLAT_API}/{zone_code}/{day}"
            params = {'year': year, 'month': month}

            print(f"   Trying API: {url} with params: {params}")
            response = requests.get(url, params=params, timeout=10,
                                   headers={'User-Agent': 'wwwbot/1.0'})

            print(f"   Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   API Response keys: {list(data.keys())}")
                print(f"   API Response status: {data.get('status', 'No status')}")

                if 'prayerTime' in data:
                    waktu = data['prayerTime']
                    print(f"   Raw prayer times: {waktu}")

                    # Format waktu dengan betul
                    result = {
                        'lokasi': lokasi_clean,  # Guna nama yang betul dari mapping
                        'subuh': self.format_time(waktu.get('fajr', '')),
                        'zohor': self.format_time(waktu.get('dhuhr', '')),
                        'asar': self.format_time(waktu.get('asr', '')),
                        'maghrib': self.format_time(waktu.get('maghrib', '')),
                        'isyak': self.format_time(waktu.get('isha', ''))
                    }

                    print(f"   Formatted times: Subuh={result['subuh']}, Zohor={result['zohor']}, Maghrib={result['maghrib']}, Isyak={result['isyak']}")

                    # JANGAN GUNA FALLBACK JIKA API BERJAYA!
                    self.cache[cache_key] = result
                    self.cache_time[cache_key] = time.time()
                    print(f"✅ API success for {lokasi_clean} (zone: {zone_code})")
                    return result
                else:
                    print(f"⚠️ No prayerTime in response: {data}")

        except Exception as e:
            print(f"⚠️ API failed: {e}")

        # HANYA GUNA FALLBACK JIKA API BETUL-BETUL GAGAL
        print("🔄 API failed, using fallback times...")

        # Fallback times yang berbeza untuk setiap zone
        fallback_times = {
            "SGR01": {  # Selangor/KL
                'subuh': '5:54am', 'zohor': '1:07pm', 'asar': '4:30pm',
                'maghrib': '7:04pm', 'isyak': '8:19pm'
            },
            "KDH01": {  # Kedah
                'subuh': '6:03am', 'zohor': '1:12pm', 'asar': '4:33pm',
                'maghrib': '7:09pm', 'isyak': '8:24pm'  # BERBEZA dari KL!
            },
            "JHR01": {  # Johor
                'subuh': '5:52am', 'zohor': '1:05pm', 'asar': '4:28pm',
                'maghrib': '7:02pm', 'isyak': '8:17pm'
            },
            "KTN01": {  # Kelantan
                'subuh': '5:48am', 'zohor': '12:58pm', 'asar': '4:21pm',
                'maghrib': '6:55pm', 'isyak': '8:10pm'
            },
            "PRK01": {  # Perak
                'subuh': '6:00am', 'zohor': '1:10pm', 'asar': '4:32pm',
                'maghrib': '7:07pm', 'isyak': '8:22pm'
            }
        }

        # Guna fallback time yang sesuai dengan zone
        times = fallback_times.get(zone_code, fallback_times["SGR01"])

        result = {
            'lokasi': lokasi_clean,
            'subuh': times['subuh'],
            'zohor': times['zohor'],
            'asar': times['asar'],
            'maghrib': times['maghrib'],
            'isyak': times['isyak']
        }

        print(f"   Fallback times for {zone_code}: {result}")

        self.cache[cache_key] = result
        self.cache_time[cache_key] = time.time()
        return result

    def format_time(self, time_str):
        """Format time string ke 12h"""
        if not time_str:
            return "--:--"

        # Jika dah ada format betul
        if ':' in time_str:
            try:
                parts = time_str.split(':')
                if len(parts) >= 2:
                    h = int(parts[0])
                    m = int(parts[1][:2])

                    # Convert to 12h
                    if h == 0:
                        return f"12:{m:02d}am"
                    elif h < 12:
                        return f"{h}:{m:02d}am"
                    elif h == 12:
                        return f"12:{m:02d}pm"
                    else:
                        return f"{h-12}:{m:02d}pm"
            except:
                pass

        return time_str

# ==================== WWW BOT PRO ====================
class WWWBotPro:
    """WWW Bot Pro dengan auto-rejoin + INTERNATIONAL SUPPORT + FIXED SOLAT"""

    def __init__(self):
        self.nick = NICK
        self.password = PASSWORD
        self.sock = None
        self.running = True
        self.motd_received = False
        self.connected = False
        self.retry_count = 0

        self.data = DataProviderFixed()
        self.display = DisplayFixed()

        self.last_solat_notif = {}
        self.last_hourly = -1
        self.joined_channels = set()

        for channel in CHANNELS:
            self.last_solat_notif[channel] = {}
            self.joined_channels.add(channel)

        print("="*60)
        print(f"🤖 WWW BOT PRO - FIXED SOLAT TIMES")
        print("="*60)
        print(f"🔧 NICK: {self.nick}")
        print(f"🔧 SERVER: {SERVER}:{PORT}")
        print(f"🔧 CHANNELS: {', '.join(CHANNELS)}")
        print(f"🔧 WEATHER: Global support via geocoding")
        print(f"🔧 SOLAT: Malaysia with proper zone mapping")
        print("="*60)

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def send_raw(self, msg):
        if self.sock:
            try:
                self.sock.send(f"{msg}\r\n".encode())
            except Exception as e:
                print(f"{self.get_timestamp()} ❌ Send error: {e}")

    def send(self, target, msg):
        """Kirim message ke channel"""
        if len(msg) > MAX_MESSAGE_LENGTH:
            msg = msg[:MAX_MESSAGE_LENGTH-3] + "..."
        self.send_raw(f"PRIVMSG {target} :{msg}")

    def send_multiple(self, target, lines):
        """Kirim semua line dalam list"""
        for i, line in enumerate(lines[:3]):
            if line.strip():
                self.send(target, line)
                if i < len(lines[:3]) - 1:
                    time.sleep(1.5)

    def wait_for_motd(self, timeout=30):
        """Tunggu sampai MOTD selesai"""
        print(f"{self.get_timestamp()} ⏳ Waiting for MOTD...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                ready, _, _ = select.select([self.sock], [], [], 1)
                if ready:
                    data = self.sock.recv(4096).decode('utf-8', errors='ignore')
                    if data:
                        lines = data.split('\r\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                # Check jika MOTD sudah selesai
                                if "376" in line or "End of /MOTD" in line:
                                    print(f"{self.get_timestamp()} ✅ MOTD received!")
                                    self.motd_received = True
                                    return True
            except:
                pass

        print(f"{self.get_timestamp()} ❌ Timeout waiting for MOTD")
        return False

    def connect_to_server(self):
        """Connect ke server"""
        try:
            print(f"{self.get_timestamp()} 🔗 Connecting to {SERVER}:{PORT}...")

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            self.sock.connect((SERVER, PORT))

            # Send registration
            print(f"{self.get_timestamp()} 📤 Registering as {self.nick}...")
            self.send_raw(f"NICK {self.nick}")
            self.send_raw(f"USER {IDENT} 0 * :{REALNAME}")

            return True

        except Exception as e:
            print(f"{self.get_timestamp()} ❌ Connection error: {e}")
            if self.sock:
                self.sock.close()
                self.sock = None
            return False

    def identify(self):
        """Identify dengan NickServ"""
        if self.password:
            print(f"{self.get_timestamp()} 🔑 Identifying to NickServ...")
            identify_cmd = f"PRIVMSG NickServ :IDENTIFY {self.password}"
            self.send_raw(identify_cmd)
            time.sleep(3)

    def join_channels(self):
        """Join semua channels"""
        print(f"{self.get_timestamp()} 📤 Joining channels...")
        for channel in self.joined_channels:
            self.send_raw(f"JOIN {channel}")
            print(f"{self.get_timestamp()} ✅ Joined {channel}")
            time.sleep(1)

    def connect(self):
        """Main connect method"""
        if self.connect_to_server():
            if self.wait_for_motd():
                self.identify()
                self.join_channels()
                self.connected = True
                return True
        return False

    def auto_rejoin(self):
        """Auto-rejoin system"""
        while self.running and self.retry_count < MAX_RETRIES:
            if not self.connected:
                print(f"\n{self.get_timestamp()} 🔄 Attempting to reconnect... (Attempt {self.retry_count + 1}/{MAX_RETRIES})")

                if self.connect_to_server():
                    if self.wait_for_motd():
                        self.identify()
                        self.join_channels()
                        self.connected = True
                        self.retry_count = 0

                        # Send welcome message
                        if CHANNELS:
                            self.send(CHANNELS[0], f"🤖 {self.nick} reconnected •")

                        print(f"{self.get_timestamp()} ✅ Reconnected successfully!")
                        return True

                self.retry_count += 1
                print(f"{self.get_timestamp()} ⏳ Waiting {RETRY_DELAY} seconds before retry...")
                time.sleep(RETRY_DELAY)

        if self.retry_count >= MAX_RETRIES:
            print(f"{self.get_timestamp()} ❌ Max retries reached ({MAX_RETRIES})")
            self.running = False

        return False

    def start_services(self):
        def keepalive():
            while self.running:
                time.sleep(60)
                try:
                    self.send_raw("PING :keepalive")
                except:
                    self.connected = False

        def hourly_announce():
            while self.running:
                now = DisplayFixed.get_malaysia_time()

                if now.minute == HOURLY_TRIGGER_MINUTE and now.second <= 10:
                    if now.hour != self.last_hourly:
                        if self.connected:  # Hanya jika connected
                            self.do_hourly_announce(now)
                            self.last_hourly = now.hour
                        time.sleep(60)

                time.sleep(1)

        def solat_notification():
            """Notifikasi solat automatik"""
            while self.running:
                if self.connected:  # Hanya jika connected
                    now = DisplayFixed.get_malaysia_time()
                    current_time_str = now.strftime("%I:%M%p").lower().lstrip('0')

                    solat_data = self.data.get_solat("Kuala Lumpur")

                    if solat_data and 'error' not in solat_data:
                        for channel in CHANNELS:
                            if channel in self.joined_channels:
                                prayers = [
                                    ('subuh', '🌅🕌 subuh', solat_data.get('subuh')),
                                    ('zohor', '🕌🕰️ zohor', solat_data.get('zohor')),
                                    ('asar', '⛅📿 asar', solat_data.get('asar')),
                                    ('maghrib', '🌇🌙 maghrib', solat_data.get('maghrib')),
                                    ('isyak', '🌃🌟 isyak', solat_data.get('isyak'))
                                ]

                                for prayer_key, prayer_name, prayer_time in prayers:
                                    if prayer_time and prayer_time != "--:--":
                                        prayer_clean = prayer_time.replace(":00", "")
                                        if prayer_clean == current_time_str:
                                            last_notif = self.last_solat_notif[channel].get(prayer_key)
                                            today = now.strftime("%Y%m%d")

                                            if last_notif != today:
                                                self.send(channel, f"⏰ Sekarang telah masuknya waktu • {prayer_name} • {prayer_time} bagi Kuala Lumpur dan kawasan yang sewaktu dengannya.")
                                                self.last_solat_notif[channel][prayer_key] = today
                                                time.sleep(2)

                time.sleep(30)

        def monitor_connection():
            """Monitor connection dan auto-rejoin"""
            while self.running:
                if not self.connected:
                    self.auto_rejoin()
                time.sleep(10)

        threading.Thread(target=keepalive, daemon=True).start()
        threading.Thread(target=hourly_announce, daemon=True).start()
        threading.Thread(target=solat_notification, daemon=True).start()
        threading.Thread(target=monitor_connection, daemon=True).start()

        print(f"{self.get_timestamp()} 🔄 Services started")

    def do_hourly_announce(self, waktu):
        print(f"{self.get_timestamp()} 🕐 hourly: {waktu.hour}:00")

        for channel in CHANNELS:
            if channel in self.joined_channels:
                cuaca = self.data.get_cuaca_detail("Kuala Lumpur")
                if cuaca:
                    lines = self.display.format_hourly_announce(cuaca)
                    self.send_multiple(channel, lines)
                    time.sleep(3)

    def handle_kick(self, channel, kicked_nick):
        """Handle kick dari channel"""
        if kicked_nick == self.nick:
            print(f"{self.get_timestamp()} ⚠️ Kicked from {channel}")
            self.joined_channels.discard(channel)

            # Auto rejoin selepas delay
            time.sleep(RETRY_DELAY)
            if self.connected:
                self.send_raw(f"JOIN {channel}")
                print(f"{self.get_timestamp()} 🔄 Rejoined {channel}")
                self.joined_channels.add(channel)

    def handle_command(self, nick, channel, command):
        cmd = command.lower().strip()

        if cmd.startswith("!cuaca"):
            parts = cmd.split()
            lokasi = "Kuala Lumpur" if len(parts) < 2 else ' '.join(parts[1:])

            # SPECIAL HANDLING untuk lokasi yang terlalu umum
            if lokasi.lower() in ['afrika', 'africa', 'eropah', 'europe', 'asia', 'amerika', 'america']:
                return [f"❌ '{lokasi}' terlalu umum. Sila nyatakan bandar atau negara yang spesifik (cth: Cairo, London, Tokyo)"]

            cuaca = self.data.get_cuaca_detail(lokasi)
            if cuaca:
                return self.display.format_cuaca_jelas(cuaca)
            else:
                return [f"❌ tak dapat data cuaca untuk '{lokasi}'. Cuba nama bandar yang lebih spesifik."]

        elif cmd.startswith("!wsolat") or cmd == "!solat":
            parts = cmd.split()
            lokasi = "Kuala Lumpur" if len(parts) < 2 else ' '.join(parts[1:])

            solat = self.data.get_solat(lokasi)
            if solat:
                if 'error' in solat:
                    return [f"❌ {solat['error']}"]
                else:
                    return self.display.format_solat_fixed(solat)
            else:
                return [f"❌ tak dapat data solat {lokasi}"]

        elif cmd == "!waktu":
            now = DisplayFixed.get_malaysia_time()
            waktu = now.strftime("%I:%M%p").lower().lstrip('0')

            hari_malaysia = {
                'Monday': 'Isnin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
                'Thursday': 'Khamis', 'Friday': 'Jumaat', 'Saturday': 'Sabtu',
                'Sunday': 'Ahad'
            }
            hari = hari_malaysia.get(now.strftime("%A"), now.strftime("%A"))
            tarikh = now.strftime("%d %b %Y")

            hour = now.hour
            if 5 <= hour < 12:
                greeting = "🌅 selamat pagi"
            elif 12 <= hour < 15:
                greeting = "☀️ selamat tengahari"
            elif 15 <= hour < 19:
                greeting = "⛅ selamat petang"
            else:
                greeting = "🌃 selamat malam"

            return [f"🕐 {waktu} • {greeting} • {hari}, {tarikh}"]

        elif cmd == "!bantuan":
            return ["🛠️ !bantuan: • !cuaca [lokasi] (global) • !wsolat [lokasi] (Malaysia sahaja) • !waktu • !bantuan"]

        elif cmd == "!info":
            return ["🤖 WWW Bot • Cuaca global & solat Malaysia FIXED • Hari Malaysia • 1 baris display • !bantuan"]

        return None

    def run(self):
        if not self.connect():
            return

        self.start_services()

        print(f"\n{self.get_timestamp()} 🚀 Bot running! Press Ctrl+C to stop")
        print("="*60)

        # Test API dulu
        print("🔍 Testing APIs...")
        cuaca_test = self.data.get_cuaca_detail("Kuala Lumpur")
        solat_kl_test = self.data.get_solat("Kuala Lumpur")
        solat_kedah_test = self.data.get_solat("Kedah")

        if cuaca_test:
            print(f"✅ Cuaca API (KL): {cuaca_test['lokasi']} {cuaca_test['suhu']}°C")
        else:
            print("❌ Cuaca API (KL) failed")

        if solat_kl_test:
            print(f"✅ Solat API (KL): {solat_kl_test['lokasi']} Maghrib={solat_kl_test['maghrib']} Isyak={solat_kl_test['isyak']}")
        else:
            print("❌ Solat API (KL) failed")

        if solat_kedah_test:
            print(f"✅ Solat API (Kedah): {solat_kedah_test['lokasi']} Maghrib={solat_kedah_test['maghrib']} Isyak={solat_kedah_test['isyak']}")
        else:
            print("❌ Solat API (Kedah) failed")

        print("="*60)

        buffer = ""

        try:
            while self.running:
                try:
                    ready, _, _ = select.select([self.sock], [], [], 5)

                    if ready:
                        data = self.sock.recv(4096).decode('utf-8', errors='ignore')
                        if not data:
                            print(f"{self.get_timestamp()} ⚠️ Connection closed by server")
                            break

                        buffer += data

                        while "\r\n" in buffer:
                            line, buffer = buffer.split("\r\n", 1)
                            line = line.strip()

                            if not line:
                                continue

                            # Handle PING
                            if line.startswith("PING"):
                                pong_msg = line.split(":", 1)[1] if ":" in line else ""
                                self.send_raw(f"PONG :{pong_msg}")
                                continue

                            # Handle PRIVMSG (commands)
                            if "PRIVMSG" in line:
                                try:
                                    parts = line.split(" ")
                                    if len(parts) >= 4:
                                        hostmask = parts[0][1:]
                                        nick = hostmask.split("!")[0] if "!" in hostmask else hostmask
                                        target = parts[2]
                                        message = " ".join(parts[3:])[1:]

                                        if nick == self.nick:
                                            continue

                                        if target in CHANNELS and message.startswith("!"):
                                            print(f"{self.get_timestamp()} 💬 Command from {nick}: {message}")

                                            response = self.handle_command(nick, target, message)
                                            if response:
                                                self.send_multiple(target, response)
                                except Exception as e:
                                    print(f"{self.get_timestamp()} ⚠️ Parse error: {e}")

                except Exception as e:
                    print(f"{self.get_timestamp()} ⚠️ Loop error: {e}")
                    time.sleep(5)

        except KeyboardInterrupt:
            print(f"\n{self.get_timestamp()} ⏹️ Stopping bot...")
        finally:
            self.running = False
            if self.sock:
                self.send_raw("QUIT :Goodbye!")
                time.sleep(1)
                self.sock.close()
            print(f"{self.get_timestamp()} 👋 Bot stopped")

if __name__ == "__main__":
    print("🤖 WWW BOT - FIXED SOLAT TIMES FOR MALAYSIA")
    print("="*60)
    print("🔧 FEATURES:")
    print("• Cuaca: Global support via geocoding API")
    print("• Solat: Malaysia dengan zone mapping yang betul")
    print("• Waktu solat berbeza untuk setiap negeri")
    print("• 1 baris display untuk cuaca")
    print("• 2 baris untuk waktu solat")
    print("• Hari Bahasa Malaysia")
    print("• Auto-rejoin system")
    print("="*60)
    print("\n🚀 Starting bot...")

    # FIX: Guna nama class yang betul
    bot = WWWBotPro()
    bot.run()
