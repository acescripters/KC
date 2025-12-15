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
import socket
import time
import requests
from collections import deque
import re
import random
import http.client
import json
import urllib.parse

# ==================== KONFIGURASI ====================
SERVER = "irc.kampungchat.org"
PORT = 6668
NICK = "deep"
CHANNELS = ["#ace", "#amboi", "#desa", "#alamanda", "#bro"]
PASSWORD = "ace:123456"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ==================== GENIUS AI SYSTEM ====================
class GeniusAIBot:
    def __init__(self):
        self.focus_users = {}
        self.silent_users = {}
        self.conversation_memory = {}
        self.last_response_time = {}
        self.processed_messages = set()
        self.current_processing = None
        self.current_processing_user = None
        self.last_search_data = {}
        self.last_search_query = {}
        self.channel_topics = {}
        self.used_facts = {}
        self.nick_history = {}

        # 🆕 CRITICAL FIX: User-specific tracking
        self.user_contexts = {}
        self.last_interaction = {}
        self.nick = NICK  # 🆕 ADD FOR NICK DETECTION

        # 🆕 STATIC RESPONSE SYSTEM - ORGANIZED
        self.static_response_sets = {
            "greeting_responses": [
                "Hai {user}! Ada apa yang boleh saya bantu? 😊",
                "Hey {user}! Apa khabar? 👋", 
                "Hello {user}! Sedia membantu! 🎯",
                "Hi {user}! Bagaimana hari anda? 🙂",
                "Hai {user}! Ada soalan untuk saya? 🤔"
            ],

            "confusion_responses": [
                "Boleh terangkan dengan lebih jelas?",
                "Tak berapa faham, boleh huraikan?",
                "Maksud kamu apa sebenarnya?",
                "Beri saya lebih context.",
                "Boleh kamu jelaskan?",
                "Tak pasti saya tangkap maksud.",
                "Boleh ulaskan dengan cara lain?",
                "Apa point yang nak disampaikan?",
                "Jelas sedikit, saya cuba fahami.",
                "Nak saya faham dari sudut mana?"
            ],

            "repair_responses": [
                "Sedang dalam proses pembaikan! ⚡",
                "Sistem sedang dioptimalkan. 🔧",
                "Proses upgrade sedang berjalan. 🚀",
                "Maintenance routine aktif. 📊",
                "Update sistem dalam progres. 🔄"
            ],

            "general_responses": [
                "Faham, teruskan.",
                "Okay, saya dengar.",
                "Jelas, apa next?",
                "Noted, ada lagi?",
                "Roger that!",
                "Copy that!",
                "Acknowledged.",
                "Loud and clear!",
                "Terima kasih inputnya.",
                "Appreciate the feedback."
            ],

            "followup_responses": [
                "Nak maklumat tambahan? Cuba `!more`.",
                "Ada soalan lain? Sedia bantu!",
                "Mau teruskan dengan topik lain?",
                "Nak explore lebih lanjut?",
                "Ada aspek khusus yang nak ditanya?",
                "Saya sedia dengan soalan seterusnya!",
                "Apa yang kamu nak tahu seterusnya?",
                "Ready untuk soalan berikutnya!",
                "Ada input atau soalan tambahan?",
                "Mau bincang perkara lain?"
            ]
        }

        self.response_indices = {}

    # 🆕 GOOGLE TRANSLATE API SYSTEM
    def translate_indonesia_to_malaysia(self, text):
        """Gunakan Google Translate API untuk terjemahan tepat"""
        try:
            # 🎯 GUNA GOOGLE TRANSLATE API
            encoded_text = urllib.parse.quote(text)

            # Google Translate API endpoint
            conn = http.client.HTTPSConnection("translate.googleapis.com")
            url = f"/translate_a/single?client=gtx&sl=id&tl=ms&dt=t&q={encoded_text}"

            conn.request("GET", url)
            response = conn.getresponse()
            data = response.read().decode('utf-8')
            conn.close()

            # Parse response JSON
            translated_data = json.loads(data)

            # Extract translated text
            if translated_data and len(translated_data) > 0:
                translated_text = ""
                for item in translated_data[0]:
                    if item[0]:  # Translated text
                        translated_text += item[0]

                if translated_text and translated_text != text:
                    print(f"🔤 Google Translate: '{text}' -> '{translated_text}'")
                    return translated_text

            # Fallback ke common words replacement
            return self.simple_translation_fallback(text)

        except Exception as e:
            print(f"⚠️ Google Translate error: {e}")
            # Fallback ke simple translation
            return self.simple_translation_fallback(text)

    def simple_translation_fallback(self, text):
        """Simple common words replacement fallback"""
        common_translations = {
            'aku': 'saya', 'kamu': 'awak', 'gue': 'saya', 'lu': 'awak',
            'mau': 'nak', 'pengen': 'nak', 'bisa': 'boleh',
            'lihat': 'tengok', 'tonton': 'tengok', 'saksikan': 'tengok',
            'keren': 'menarik', 'gaya': 'style', 'mantap': 'hebat',
            'nanti': 'sebentar', 'sih': '', 'deh': '', 'dong': '',
            'ayo': 'jom', 'yuk': 'jom', 'sini': 'sini', 'sana': 'sana',
            'apa kabar': 'apa khabar', 'bagaimana': 'macam mana',
            'kenapa': 'kenapa', 'karena': 'sebab', 'sebab': 'sebab'
        }

        # Simple word replacement untuk common terms
        result = text
        for id_word, my_word in common_translations.items():
            if my_word:  # Only replace if not empty
                result = re.sub(r'\b' + re.escape(id_word) + r'\b', my_word, result, flags=re.IGNORECASE)

        if result != text:
            print(f"🔤 Simple Translate: '{text}' -> '{result}'")

        return result

    def detect_indonesia_language(self, text):
        """Detect Bahasa Indonesia patterns"""
        indonesia_indicators = [
            'apa kabar', 'bisa', 'mau', 'pengen', 'gue', 'lu', 
            'saksikan', 'keren', 'gaya', 'mantap', 'sih', 'deh', 'dong',
            'ayo', 'yuk', 'karena'
        ]

        text_lower = text.lower()
        return any(indicator in text_lower for indicator in indonesia_indicators)

    # 🆕 SERVER TRANSLATION COMMAND HANDLER
    def handle_translation_commands(self, nick, channel, message):
        """Handle server translation commands jika ada"""
        if message.startswith('!translate') or message.startswith('/translate'):
            # Server translation command format: !translate id ms <text>
            parts = message.split(' ', 3)
            if len(parts) >= 4:
                source_lang, target_lang, text_to_translate = parts[1], parts[2], parts[3]
                if source_lang == 'id' and target_lang == 'ms':
                    translated = self.translate_indonesia_to_malaysia(text_to_translate)
                    return f"🔤 Terjemahan: {translated}"
        return None

    # 🆕 SINGLE UNIFIED PROMPT SYSTEM
    def unified_genius_response(self, message, context_type, search_data="", memory_context="", username=""):
        """SINGLE PROMPT SYSTEM dengan server-based translation"""

        # 🎯 SINGLE MASTER PROMPT - Arahkan guna Bahasa Malaysia terus
        master_prompt = f"""
# GENIUS AI BOT - BAHASA MALAYSIA MODE
# GUNA BAHASA MALAYSIA SAHAJA (bukan Indonesia)

CONTEXT: {context_type}
USER: {username}
MEMORY: {memory_context}
SEARCH_DATA: {search_data}
MESSAGE: {message}

INSTRUCTIONS:
1. 🎯 GUNA BAHASA MALAYSIA - Malaysian Malay, bukan Indonesian
2. 🚀 Response pendek & relevant (max 4 baris, 200 chars)
3. 📝 Natural conversation style
4. ❌ JANGAN guna Bahasa Indonesia

CONTOH BAHASA MALAYSIA:
- "Hai! Ada apa?" (bukan "Hai! Apa kabar?")
- "Saya boleh bantu" (bukan "Saya bisa bantu")  
- "Nak tengok?" (bukan "Mau lihat?")
- "Bagaimana boleh saya bantu?" (bukan "Bagaimana bisa saya bantu?")

RESPONSE BAHASA MALAYSIA:
"""

        response = self.call_groq(master_prompt, timeout=8)

        if response:
            response = response.strip()
            # Clean response
            response = re.sub(r'\s+', ' ', response)
            response = response.replace('"', '').replace('**', '')

            # 🎯 SERVER-BASED TRANSLATION CHECK
            # Biar server handle complex translation
            if self.detect_indonesia_language(response):
                print(f"🔍 Detected Indonesian: {response}")
                response = self.translate_indonesia_to_malaysia(response)

            # 🎯 HARDCODED BAHASA MALAYSIA RESPONSES UNTUK COMMON CASES
            if context_type == "GREETING":
                malay_greetings = [
                    "Hai! Ada apa yang boleh saya bantu? 😊",
                    "Hello! Sedia membantu! 🎯", 
                    "Hi! Apa khabar? 👋",
                    "Hai! Bagaimana hari anda? 🙂"
                ]
                if any(indonesian_word in response.lower() for indonesian_word in ['apa kabar', 'bisa', 'mau']):
                    response = random.choice(malay_greetings)

        return response or "Sistem sedang..."

    def clean_irc_message(self, message):
        """Clean IRC message dari formatting codes"""
        message = re.sub(r'\x03(\d{1,2}(,\d{1,2})?)?', '', message)

        formatting_codes = ['\x02', '\x1D', '\x1F', '\x16', '\x0F']
        for code in formatting_codes:
            message = message.replace(code, '')

        message = message.replace('\xa0', ' ')

        message = re.sub(r'\s+', ' ', message).strip()

        return message

    def detect_nick_mentions(self, message):
        """Convert dari mIRC: Detect nick mentions dalam message"""
        cleaned_message = message.replace('\xa0', ' ')

        prefix_chars = ['@', '+', '%', '&', '~']
        for prefix in prefix_chars:
            cleaned_message = cleaned_message.replace(prefix, '')

        words = cleaned_message.split()

        if self.nick.lower() in [word.lower() for word in words]:
            return True

        if 'bot' in [word.lower() for word in words]:
            return True

        return False

    def detect_nick_mentions_advanced(self, message):
        """Advanced version dengan regex untuk better detection"""
        cleaned_message = self.clean_irc_message(message)

        words = re.findall(r'\b\w+\b', cleaned_message.lower())

        if self.nick.lower() in words:
            return True

        bot_keywords = ['bot', 'bots', 'robot', 'ai', 'assistant']
        if any(bot_word in words for bot_word in bot_keywords):
            return True

        command_patterns = [
            r'^!cari\b', r'^!more\b', r'^!next\b',
            r'^cari\b', r'^search\b', r'^find\b'
        ]

        if any(re.search(pattern, cleaned_message, re.IGNORECASE) for pattern in command_patterns):
            return True

        return False

    def is_mention(self, message):
        """FIXED: Gunakan advanced nick detection"""
        return self.detect_nick_mentions_advanced(message)

    def is_message_for_bot(self, message, username):
        """FIXED: Smart detection untuk tahu sama ada message untuk bot atau user lain"""
        message_lower = message.lower()

        # 🆕 FIX: JANGAN treat commands sebagai mentions
        if message.strip() in ['!more', '!next', '!cari']:
            return True

        if self.detect_nick_mentions_advanced(message):
            return True

        command_patterns = [
            r'^!cari\b', r'^!more\b', r'^!next\b',
            r'^cari\b', r'^search\b', r'^find\b'
        ]

        if any(re.search(pattern, message_lower) for pattern in command_patterns):
            return True

        if self.is_in_focus(username):
            return True

        mentioned_users = re.findall(r'@?(\w+)', message_lower)
        if mentioned_users:
            valid_users = [
                user for user in mentioned_users 
                if user not in [self.nick.lower(), 'www', 'minah', 'bot'] 
                and len(user) > 2
                and user != username.lower()
            ]
            if valid_users:
                return False

        return False

    def is_message_for_other_user(self, message):
        """Better detection untuk messages antara users"""
        message_lower = message.lower()

        user_convo_patterns = [
            r'tq\s+\w+', r'thanks\s+\w+', r'thank you\s+\w+',
            r'terima kasih\s+\w+', 
            r'\w+\s+from where', r'\w+\s+dari mana',
            r'ko dari mana', r'awak dari mana', r'hang dari mana',
            r'same2\s+\w+', r'sama2\s+\w+',
            r'welcome\s+\w+', r'selamat datang\s+\w+'
        ]

        if any(re.search(pattern, message_lower) for pattern in user_convo_patterns):
            return True

        mentioned_users = re.findall(r'@?(\w+)', message_lower)
        if mentioned_users:
            valid_users = [
                user for user in mentioned_users 
                if user not in [self.nick.lower(), 'www', 'bot', 'bots', 'deep']
                and len(user) > 2
            ]
            if len(valid_users) >= 1:
                return True

        return False

    def get_user_context(self, username):
        """Dapatkan context khusus untuk user"""
        if username not in self.user_contexts:
            self.user_contexts[username] = {
                'last_topic': '',
                'conversation_count': 0,
                'last_response': '',
                'interaction_time': time.time()
            }
        return self.user_contexts[username]

    def update_user_context(self, username, message, response):
        """Update user context dengan accurate"""
        context = self.get_user_context(username)
        context['last_response'] = response
        context['interaction_time'] = time.time()
        context['conversation_count'] += 1

        words = message.lower().split()
        topic_keywords = ['otak', 'repair', 'operasi', 'bateri', 'menteri', 'search', 'cari', 'gaza']
        for word in words:
            if word in topic_keywords:
                context['last_topic'] = word
                break

    def get_static_response(self, username, response_type):
        """Static response dengan user context"""
        if username not in self.response_indices:
            self.response_indices[username] = {}

        if response_type not in self.response_indices[username]:
            self.response_indices[username][response_type] = 0

        response_set = self.static_response_sets.get(response_type, ["Faham."])
        current_index = self.response_indices[username][response_type]
        response = response_set[current_index % len(response_set)]

        response = response.replace("{user}", username)

        self.response_indices[username][response_type] = (current_index + 1) % len(response_set)
        return response

    def detect_response_type(self, message):
        """Better response type detection"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['hai', 'hello', 'hi', 'hey', 'halo', 'welcome']):
            return "greeting_responses"
        elif any(word in message_lower for word in ['tak faham', 'tak jelas', 'apa maksud', 'kenapa', 'pelik']):
            return "confusion_responses"
        elif any(word in message_lower for word in ['repair', 'baiki', 'otak', 'senget', 'operasi']):
            return "repair_responses"
        elif any(word in message_lower for word in ['tu je?', 'jem lagi?', 'lagi?', 'next', 'sambung', 'kamu la next']):
            return "followup_responses"
        else:
            return "general_responses"

    def cleanup_memory(self, username):
        """Smart memory management"""
        if username in self.conversation_memory:
            current_memory = list(self.conversation_memory[username])
            if len(current_memory) >= 30:
                new_memory = current_memory[-15:]
                self.conversation_memory[username] = deque(new_memory, maxlen=30)

    def update_memory(self, username, user_message, bot_response):
        """Memory update dengan user context"""
        if username not in self.conversation_memory:
            self.conversation_memory[username] = deque(maxlen=20)

        if bot_response and len(bot_response) > 10:
            if self.conversation_memory[username]:
                last_entry = self.conversation_memory[username][-1]
                if bot_response in last_entry:
                    return

        self.conversation_memory[username].append(f"USER: {user_message}")
        self.conversation_memory[username].append(f"AI: {bot_response}")

        self.update_user_context(username, user_message, bot_response)

        if len(self.conversation_memory[username]) >= 20:
            self.cleanup_memory(username)

    def get_memory_context(self, username):
        """Memory context yang lebih focused"""
        if username not in self.conversation_memory or not self.conversation_memory[username]:
            return "TIADA HISTORY"

        memory_lines = list(self.conversation_memory[username])[-4:]

        context_lines = []
        for line in memory_lines:
            clean_line = re.sub(r'^(USER|AI):\s*', '', line)
            if len(clean_line) > 5:
                context_lines.append(clean_line)

        return " | ".join(context_lines[-3:])

    def extract_mentioned_user(self, message):
        """Extract username"""
        clean_message = re.sub(r'\b' + re.escape(self.nick) + r'\b', '', message, flags=re.IGNORECASE)
        clean_message = clean_message.strip()

        if clean_message:
            words = clean_message.split()
            if words:
                return words[0]

        return "kawan"

    def call_groq(self, prompt, timeout=10):
        """Panggil Groq AI"""
        try:
            messages = [{"role": "user", "content": prompt}]

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "max_tokens": 350,
                "temperature": 0.7,
                "top_p": 1,
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                ai_text = data['choices'][0]['message']['content'].strip()
                return ai_text
            else:
                return "🤖 Sistem sementara unavailable."

        except Exception as e:
            return "⏳ Timeout. Cuba lagi."

    def should_use_action_response(self):
        """Kurangkan frequency action response"""
        return random.random() < 0.15

    def is_math_question(self, message):
        """Mathematical reasoning detection"""
        math_keywords = ['+', '-', '*', 'x', 'darab', 'bahagi', 'tambah', 'tolak', '=', 'berapa']
        message_lower = message.lower()

        has_math_operator = any(op in message_lower for op in ['+', '-', '*', 'x', 'darab', 'bahagi'])
        has_math_keyword = any(keyword in message_lower for keyword in ['berapa', 'kira', 'hitung'])

        return has_math_operator or has_math_keyword

    def calculate_math(self, message):
        """Mathematical computation"""
        try:
            calc_msg = message.lower()
            calc_msg = calc_msg.replace('darab', '*').replace('x', '*')
            calc_msg = calc_msg.replace('tambah', '+').replace('tolak', '-')
            calc_msg = calc_msg.replace('bahagi', '/').replace('÷', '/')

            calc_msg = re.sub(r'[^\d\+\-\*\/\(\)\.\s]', ' ', calc_msg)
            calc_msg = ' '.join(calc_msg.split())

            if not calc_msg or len(calc_msg) < 3:
                return None

            result = eval(calc_msg)

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            return f"🔢 {message} = {result}"

        except:
            return None

    def enforce_hard_200_limit(self, text):
        """STRICT 180 CHARACTERS LIMIT"""
        if len(text) <= 180:
            return text

        for delimiter in ['. ', '! ', '? ', '; ']:
            pos = text[:160].rfind(delimiter)
            if pos > 60:
                return text[:pos + 1].strip()

        space_pos = text[:150].rfind(' ')
        if space_pos > 60:
            return text[:space_pos].strip() + "..."

        return text[:147].strip() + "..."

    def get_greeting_response(self, mention_message, memory_context=""):
        """Greeting response yang consistent"""
        actual_username = self.extract_mentioned_user(mention_message)
        return self.get_static_response(actual_username, "greeting_responses")

    def activate_focus(self, username):
        """Activate focus dengan timeout yang lebih pendek"""
        self.focus_users[username] = time.time() + 180
        self.silent_users.pop(username, None)
        print(f"🎯 Focus activated for {username} for 3 minutes")

    def is_in_focus(self, username):
        """Check focus"""
        if username in self.focus_users:
            if time.time() < self.focus_users[username]:
                return True
            else:
                del self.focus_users[username]
                self.silent_users.pop(username, None)
        return False

    def should_search(self, message):
        """Determine response type"""
        message_lower = message.lower().strip()

        current_user = getattr(self, 'current_processing_user', None)
        if current_user and self.is_in_focus(current_user):
            print(f"🎯 User {current_user} in focus")

        if self.is_math_question(message):
            math_result = self.calculate_math(message)
            if math_result:
                return "MATH"

        if len(message_lower) < 5:
            return "CHAT"

        casual_phrases = ['ta de pe', 'dah tade org', 'uhuks', 'diam jap', 'ok', 'okay', 'baik', 'haha', 'hehe', 'lol']
        if any(phrase in message_lower for phrase in casual_phrases):
            return "CHAT"

        search_triggers = [
            'cari', 'carikan', 'search', 'google', 'berita', 'news', 'terkini',
            'cuaca', 'weather', 'harga', 'price', 'fakta', 'fact', 'data',
            'maklumat', 'information', 'info', '!cari', 'siapa', 'apa', 'bila'
        ]

        if any(trigger in message_lower for trigger in search_triggers):
            return "SEARCH"

        return "CHAT"

    def google_search(self, query, timeout=12):
        """Google Search dengan fallback"""
        try:
            clean_query = re.sub(r'^!cari\s*', '', query).strip()

            url = "https://serpapi.com/search"
            params = {
                'q': clean_query,
                'api_key': "32840e0d0a550cf542792fcbe2d453baf5fe016b943c3117c743cbfc0d2be321",
                'engine': 'google',
                'num': 3,
                'hl': 'ms',
                'gl': 'my',
            }

            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                search_results = []

                if 'knowledge_graph' in data and data['knowledge_graph']:
                    kg = data['knowledge_graph']
                    title = kg.get('title', '')
                    description = kg.get('description', '')
                    if title and description:
                        return f"📚 {title}: {description[:100]}... [!more]"

                if 'organic_results' in data and data['organic_results']:
                    for item in data['organic_results'][:2]:
                        title = item.get('title', '')
                        snippet = item.get('snippet', '')[:80]

                        if title:
                            result = f"🔍 {title}"
                            if snippet:
                                result += f" | {snippet}..."
                            search_results.append(result)

                if search_results:
                    return search_results[0]
                else:
                    fallbacks = {
                        'menteri pelajaran': '📚 Menteri Pendidikan: Fadhina Sidek [!more]',
                        'menteri pendidikan': '📚 Menteri Pendidikan Malaysia: Fadhina Sidek [!more]', 
                        'perdana menteri': '📚 Perdana Menteri: Anwar Ibrahim [!more]',
                        'ibu negara': '📚 Ibu negara: Kuala Lumpur [!more]',
                        'gaza': '🌎 Gaza: Konflik Israel-Palestin sedang berlangsung [!more]'
                    }

                    for key, value in fallbacks.items():
                        if key in clean_query.lower():
                            return value

                    return f"📡 Maklumat '{clean_query}' sedang dikemas kini. [!more]"

            return "🔍 Sistem carian sementara unavailable."

        except Exception as e:
            return "🔍 Timeout carian. Cuba lagi."

    def ai_analyze(self, user_question, search_data, memory_context=""):
        """AI analysis dengan fix"""
        if not search_data or "tidak dapat" in search_data or "ralat" in search_data or "unavailable" in search_data:
            return f"🔍 Analisis untuk '{user_question}' sedang disiapkan. [!more]"
        else:
            response = self.unified_genius_response(user_question, "SEARCH", search_data, memory_context)

        if not response or len(response.strip()) < 10:
            response = f"📡 Maklumat untuk '{user_question}' sedang diproses. [!more]"

        response = self.enforce_hard_200_limit(response)
        return response

    def handle_next_command(self, username, memory_context=""):
        """Handle !next command"""
        if username not in self.last_search_data:
            return "❌ Tiada carian aktif. Cuba `cari [topic]` dulu."

        search_data = self.last_search_data[username]
        original_query = self.last_search_query.get(username, "")

        if username not in self.used_facts:
            self.used_facts[username] = []

        response = self.unified_genius_response(original_query, "NEXT", search_data, memory_context)

        simple_response = re.sub(r'\[!more\]|\[end\]', '', response).strip()
        if any(simple_response in used for used in self.used_facts[username]):
            return "🔄 Tiada maklumat baru. [end]"

        self.used_facts[username].append(simple_response)
        response = self.enforce_hard_200_limit(response)

        return response

    def get_chat_response(self, message, memory_context=""):
        """Chat response dengan better context understanding"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['tu je?', 'jem lagi?', 'lagi?', 'next', 'sambung']):
            response = self.get_static_response(
                getattr(self, 'current_processing_user', 'default'), 
                "followup_responses"
            )
            # 🆕 AUTO-TRANSLATE STATIC RESPONSES
            return self.translate_indonesia_to_malaysia(response) if self.detect_indonesia_language(response) else response

        if 'kamu la next' in message_lower or 'you next' in message_lower:
            return "😊 Okay! Saya sedia dengan soalan seterusnya. Apa yang kamu nak tahu?"

        if any(word in message_lower for word in ['otak', 'repair', 'baiki', 'senget', 'operasi']):
            response = self.get_static_response(
                getattr(self, 'current_processing_user', 'default'), 
                "repair_responses"
            )
            return self.translate_indonesia_to_malaysia(response) if self.detect_indonesia_language(response) else response

        if any(word in message_lower for word in ['faham', 'okay', 'ok', 'baik', 'clear', 'jelas']):
            response = self.get_static_response(
                getattr(self, 'current_processing_user', 'default'),
                "general_responses" 
            )
            return self.translate_indonesia_to_malaysia(response) if self.detect_indonesia_language(response) else response

        # 🆕 GUNA SINGLE PROMPT SYSTEM
        response = self.unified_genius_response(message, "CHAT", "", memory_context)

        # 🆕 FINAL TRANSLATION CHECK
        if self.detect_indonesia_language(response):
            response = self.translate_indonesia_to_malaysia(response)

        return response

    def get_action_response(self, message, memory_context=""):
        """Action response tanpa first person"""
        neutral_actions = [
            "processing information...",
            "analyzing data...", 
            "checking systems...",
            "reviewing details...",
            "updating records...",
            "compiling report...",
            "verifying information...",
            "organizing data..."
        ]
        return random.choice(neutral_actions)

    def get_nickchange_response(self, nick_change):
        """Nick change response"""
        try:
            new_nick = nick_change.split(' to ')[1] if ' to ' in nick_change else "someone"
            responses = [
                f"noticed {new_nick} dengan identity baru! 🦸",
                f"sees {new_nick} dengan fresh look! 😎",
                f"spotted {new_nick} dalam bentuk baru! 🎭",
                f"welcome {new_nick} dengan new vibes! 🌟"
            ]
            return random.choice(responses)
        except:
            return "noticed someone dengan new identity! 🎭"

    def process_message(self, username, message, channel=None):
        """Smart message processing dengan user conversation detection"""
        current_time = time.time()

        if hasattr(self, 'current_processing_user') and self.current_processing_user != username:
            self.current_processing = None

        self.current_processing_user = username

        # 🆕 FIX: Handle translation commands first
        translation_result = self.handle_translation_commands(username, channel or "", message)
        if translation_result:
            return translation_result

        # 🆕 FIX: Handle commands properly - JANGAN treat sebagai greeting
        if message.strip() in ['!more', '!next']:
            if username not in self.last_search_data:
                return "❌ Tiada carian aktif. Cuba `cari [topic]` dulu."

            self.last_response_time[username] = current_time
            self.current_processing = "NEXT"

            memory_context = self.get_memory_context(username)
            next_response = self.handle_next_command(username, memory_context)
            return f"NEXT|{next_response}"

        is_for_bot = self.is_message_for_bot(message, username)

        print(f"🔍 Processing: {username} | For Bot: {is_for_bot} | Message: {message[:50]}...")

        if not is_for_bot:
            print(f"⏩ Skipping {username} - message not for bot")
            return None

        if self.is_math_question(message):
            math_result = self.calculate_math(message)
            if math_result:
                return math_result

        is_bot_mentioned = self.is_mention(message)
        is_in_focus = self.is_in_focus(username)

        if is_bot_mentioned:
            self.activate_focus(username)
            return "CONNECTING"

        # 🆕 ONLY PROCESS JIKA MESSAGE UNTUK BOT
        if not is_in_focus and not is_bot_mentioned:
            message_lower = message.lower()
            direct_interactions = [
                'deep ', ' deep', '!cari',
                'bot ', ' ai ', 'assistant'
            ]

            is_direct = any(interaction in message_lower for interaction in direct_interactions)

            if is_direct:
                print(f"🎯 Direct interaction from {username}, activating focus")
                self.activate_focus(username)
                return "CONNECTING"
            else:
                print(f"⏩ Skipping {username} - not in focus and not direct interaction")
                return None

        if self.is_message_for_other_user(message) and not is_in_focus:
            print(f"⏩ Skipping {username} - message for other user")
            return None

        if self.current_processing:
            print(f"⏩ Skipping {username} - currently processing")
            return None

        message_hash = f"{username}:{message}"
        if message_hash in self.processed_messages:
            print(f"⏩ Skipping {username} - duplicate message")
            return None

        if username in self.last_response_time:
            time_since_last = current_time - self.last_response_time[username]
            if time_since_last < 2:
                print(f"⏩ Skipping {username} - too soon since last response")
                return None

        self.last_response_time[username] = current_time
        self.processed_messages.add(message_hash)

        if len(self.processed_messages) > 100:
            self.processed_messages.clear()

        if self.is_in_focus(username):
            self.focus_users[username] = time.time() + 180

            if message.lower() in ['diam', 'senyap', 'shut up', 'stop']:
                self.silent_users[username] = True
                return "🔇 Okay, saya diam."

            if message.lower() in ['boleh cakap', 'cakap', 'speak']:
                self.silent_users.pop(username, None)
                return "🔊 Baik, saya sedia bantu!"

            if username in self.silent_users:
                return None

            memory_context = self.get_memory_context(username)

            action = self.should_search(message)

            self.current_processing = action

            if action in ["SEARCH", "ANALYSIS"]:
                self.last_search_query[username] = message
                if username in self.used_facts:
                    self.used_facts[username] = []

            if action == "SEARCH":
                return f"SEARCH|{memory_context}"
            elif action == "MATH":
                return None
            else:
                return f"CHAT|{memory_context}"

        return None

# ==================== IRC CLIENT ====================  
class IRCClient:
    def __init__(self):
        self.sock = None
        self.bot = GeniusAIBot()
        self.last_global_response = 0
        self.kicked_channels = {}

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(300)
            self.sock.connect((SERVER, PORT))
            self.send_raw(f"NICK {NICK}")
            self.send_raw(f"USER seek 0 * :I'm your future, past and present, I'm the fine line")
            print("✅ Connected!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def send_raw(self, message):
        try:
            self.sock.send(f"{message}\r\n".encode())
        except Exception as e:
            print(f"❌ Send error: {e}")

    def send_message(self, target, message):
        if message and len(message) > 400:
            message = message[:397] + "..."
        self.send_raw(f"PRIVMSG {target} :{message}")

    def send_action(self, target, action):
        self.send_raw(f"PRIVMSG {target} :\x01ACTION {action}\x01")

    def send_smart_response(self, channel, response):
        """Smart response system - 1-2 lines maximum"""
        response = response.replace('"', '').strip()

        if len(response) <= 120:
            self.send_message(channel, response)
            return

        words = response.split()
        if len(words) <= 12:
            self.send_message(channel, response)
            return

        mid_point = len(words) // 2
        line1 = " ".join(words[:mid_point])
        line2 = " ".join(words[mid_point:])

        self.send_message(channel, line1)
        time.sleep(0.3)
        self.send_message(channel, line2)

    def join_channels(self):
        for channel in CHANNELS:
            self.send_raw(f"JOIN {channel}")
            time.sleep(2)
        print("✅ Joined all channels!")

    def identify_nickserv(self):
        if PASSWORD:
            self.send_raw(f"PRIVMSG NickServ :IDENTIFY {PASSWORD}")
            time.sleep(1)
            print("✅ Identified with NickServ")

    def handle_nick_change(self, old_nick, new_nick):
        """Better nick change handling"""
        print(f"🎭 Nick change: {old_nick} → {new_nick}")

        self.bot.nick_history[new_nick] = old_nick

        action_response = self.bot.get_nickchange_response(f"{old_nick} to {new_nick}")

        for channel in CHANNELS:
            self.send_action(channel, action_response)
        print(f"✅ Nick change announced: {action_response}")

    def handle_kick(self, channel, kicked_nick, kicker, reason):
        """Handle kick - auto rejoin 30s"""
        if kicked_nick == NICK:
            print(f"🚨 Bot kicked from {channel} by {kicker}")
            self.kicked_channels[channel] = time.time() + 30
            print(f"🔄 Auto-rejoining {channel} in 30 seconds...")

    def check_auto_rejoin(self):
        """Auto rejoin check"""
        current_time = time.time()
        channels_to_rejoin = []

        for channel, rejoin_time in self.kicked_channels.items():
            if current_time >= rejoin_time:
                channels_to_rejoin.append(channel)

        for channel in channels_to_rejoin:
            print(f"🔄 Rejoining {channel}...")
            self.send_raw(f"JOIN {channel}")
            del self.kicked_channels[channel]
            time.sleep(2)

    def handle_action_message(self, nick, channel, action_text):
        """Handle /me action"""
        result = self.bot.process_message(nick, action_text, channel)

        if result == "CONNECTING":
            self.send_action(channel, "is connecting... ⚡")
            time.sleep(1)
            memory_context = self.bot.get_memory_context(nick)
            ai_response = self.bot.get_greeting_response(action_text, memory_context)
            self.bot.update_memory(nick, action_text, ai_response)
            self.send_smart_response(channel, ai_response)
            self.bot.current_processing = None
            self.bot.current_processing_user = None

        elif result and "|" in result:
            action_type, data = result.split("|", 1)

            if action_type == "SEARCH":
                self.send_action(channel, "is searching... 🔍")
                time.sleep(1)
                search_data = self.bot.google_search(action_text)
                self.bot.last_search_data[nick] = search_data
                self.send_action(channel, "is analyzing data... 📊")
                time.sleep(1)
                ai_response = self.bot.ai_analyze(action_text, search_data, data)
                self.bot.update_memory(nick, action_text, ai_response)
                self.send_smart_response(channel, ai_response)
                self.bot.current_processing = None
                self.bot.current_processing_user = None

            elif action_type == "NEXT":
                self.send_action(channel, "getting more info... 📡")
                time.sleep(1)
                self.send_smart_response(channel, data)
                self.bot.update_memory(nick, action_text, data)
                self.bot.current_processing = None
                self.bot.current_processing_user = None

            elif action_type == "CHAT":
                if self.bot.should_use_action_response():
                    action_response = self.bot.get_action_response(action_text, data)
                    self.send_action(channel, action_response)
                    self.bot.update_memory(nick, action_text, f"ACTION: {action_response}")
                    time.sleep(0.5)
                    follow_up_response = self.bot.get_chat_response(action_text, data)
                    self.bot.update_memory(nick, action_text, follow_up_response)
                    self.send_smart_response(channel, follow_up_response)
                else:
                    self.send_action(channel, "is thinking... 🤔")
                    time.sleep(1)
                    response = self.bot.get_chat_response(action_text, data)
                    self.bot.update_memory(nick, action_text, response)
                    self.send_smart_response(channel, response)
                self.bot.current_processing = None
                self.bot.current_processing_user = None

        elif result:
            self.bot.update_memory(nick, action_text, result)
            self.send_smart_response(channel, result)
            self.bot.current_processing = None
            self.bot.current_processing_user = None

    def handle_normal_message(self, nick, channel, message):
        """Handle normal message dengan proper action follow-up"""
        current_time = time.time()

        print(f"📨 Received from {nick} in {channel}: {message}")

        if self.bot.current_processing:
            print(f"⏩ Skipping {nick} - bot currently processing")
            return

        self.bot.current_processing_user = nick

        is_bot_mentioned = self.bot.is_mention(message)
        is_in_focus = self.bot.is_in_focus(nick)

        print(f"🔍 {nick} - Mentioned: {is_bot_mentioned}, In Focus: {is_in_focus}")

        if is_bot_mentioned:
            print(f"🎯 {nick} mentioned bot, activating focus")
            self.bot.activate_focus(nick)

        result = self.bot.process_message(nick, message, channel)

        if result == "CONNECTING":
            if not self.bot.is_in_focus(nick):
                self.send_action(channel, "is connecting... ⚡")
                time.sleep(1)
            memory_context = self.bot.get_memory_context(nick)
            ai_response = self.bot.get_greeting_response(message, memory_context)
            self.bot.update_memory(nick, message, ai_response)
            self.send_smart_response(channel, ai_response)
            self.bot.current_processing = None
            self.bot.current_processing_user = None

        elif result and "|" in result:
            action_type, data = result.split("|", 1)

            if action_type == "SEARCH":
                self.send_action(channel, "is searching... 🔍")
                time.sleep(1)
                search_data = self.bot.google_search(message)
                self.bot.last_search_data[nick] = search_data
                self.send_action(channel, "is analyzing data... 📊")
                time.sleep(1)
                ai_response = self.bot.ai_analyze(message, search_data, data)
                self.bot.update_memory(nick, message, ai_response)
                self.send_smart_response(channel, ai_response)
                self.bot.current_processing = None
                self.bot.current_processing_user = None

            elif action_type == "NEXT":
                self.send_action(channel, "getting more info... 📡")
                time.sleep(1)
                self.send_smart_response(channel, data)
                self.bot.update_memory(nick, message, data)
                self.bot.current_processing = None
                self.bot.current_processing_user = None

            elif action_type == "CHAT":
                if self.bot.should_use_action_response():
                    action_response = self.bot.get_action_response(message, data)
                    self.send_action(channel, action_response)
                    self.bot.update_memory(nick, message, f"ACTION: {action_response}")
                    time.sleep(0.5)
                    follow_up_response = self.bot.get_chat_response(message, data)
                    self.bot.update_memory(nick, message, follow_up_response)
                    self.send_smart_response(channel, follow_up_response)
                else:
                    self.send_action(channel, "is thinking... 🤔")
                    time.sleep(1)
                    response = self.bot.get_chat_response(message, data)
                    self.bot.update_memory(nick, message, response)
                    self.send_smart_response(channel, response)
                self.bot.current_processing = None
                self.bot.current_processing_user = None

        elif result:
            self.bot.update_memory(nick, message, result)
            self.send_smart_response(channel, result)
            self.bot.current_processing = None
            self.bot.current_processing_user = None

        elif self.bot.is_in_focus(nick) and not self.bot.current_processing:
            memory_context = self.bot.get_memory_context(nick)

            action = self.bot.should_search(message)

            if action == "SEARCH":
                self.send_action(channel, "is searching... 🔍")
                time.sleep(1)
                search_data = self.bot.google_search(message)
                self.bot.last_search_data[nick] = search_data
                self.send_action(channel, "is analyzing data... 📊")
                time.sleep(1)
                ai_response = self.bot.ai_analyze(message, search_data, memory_context)
                self.bot.update_memory(nick, message, ai_response)
                self.send_smart_response(channel, ai_response)

            else:
                if self.bot.should_use_action_response():
                    action_response = self.bot.get_action_response(message, memory_context)
                    self.send_action(channel, action_response)
                    self.bot.update_memory(nick, message, f"ACTION: {action_response}")
                    time.sleep(0.5)
                    chat_response = self.bot.get_chat_response(message, memory_context)
                    self.bot.update_memory(nick, message, chat_response)
                    self.send_smart_response(channel, chat_response)
                else:
                    self.send_action(channel, "is thinking... 🤔")
                    time.sleep(1)
                    response = self.bot.get_chat_response(message, memory_context)
                    self.bot.update_memory(nick, message, response)
                    self.send_smart_response(channel, response)

        self.bot.current_processing = None
        self.bot.current_processing_user = None

    def run(self):
        while True:
            if self.connect():
                time.sleep(3)
                self.identify_nickserv()
                self.join_channels()
                print("🤖 GENIUS AI BOT STARTED!")
                print("🎭 Nick Change Detection: ACTIVE")
                print("📝 Smart Response: ENABLED (1-2 lines)")
                print("🔧 Static Response System: ACTIVE")
                print("🔄 Action Follow-up: ENABLED")
                print("🧠 Smart Conversation Detection: ACTIVE")
                print("🎯 Advanced Nick Detection: ACTIVE")
                print("🔤 Google Translate System: ACTIVE")

                buffer = ""
                while True:
                    try:
                        self.check_auto_rejoin()

                        data = self.sock.recv(1024).decode('utf-8', errors='ignore')
                        if not data:
                            break

                        buffer += data
                        lines = buffer.split('\r\n')
                        buffer = lines.pop()

                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue

                            if line.startswith(':'):
                                parts = line.split()

                                if len(parts) >= 3 and parts[1] == 'NICK':
                                    old_nick = parts[0][1:].split('!')[0]
                                    new_nick = parts[2][1:] if parts[2].startswith(':') else parts[2]

                                    if old_nick != NICK:
                                        self.handle_nick_change(old_nick, new_nick)
                                    continue

                            if 'PRIVMSG' in line:
                                try:
                                    parts = line.split(' ', 3)
                                    if len(parts) >= 4:
                                        nick = parts[0][1:].split('!')[0]
                                        channel = parts[2]
                                        message = parts[3][1:]

                                        if message.startswith('\x01ACTION ') and message.endswith('\x01'):
                                            action_text = message[8:-1]
                                            self.handle_action_message(nick, channel, action_text)
                                        else:
                                            self.handle_normal_message(nick, channel, message)

                                except Exception as e:
                                    print(f"Error: {e}")

                            if line.startswith('PING'):
                                self.send_raw(f"PONG :{line.split(':')[1]}")
                                continue

                    except Exception as e:
                        print(f"❌ Error: {e}")
                        break

            print("🔄 Reconnecting in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    client = IRCClient()
    client.run()
