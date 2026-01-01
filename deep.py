import re
import socket
import time
import random
import requests
import datetime as dt
from collections import deque

# ===== VERIFIED SEARCH ENGINE =====
class VerifiedSearchEngine:
    def __init__(self):
        self.sources = {
            'wikipedia_ms': {
                'name': 'Wikipedia Bahasa Malaysia',
                'url': 'https://ms.wikipedia.org/w/api.php',
                'verified': True
            },
            'wikipedia_en': {
                'name': 'Wikipedia English',
                'url': 'https://en.wikipedia.org/w/api.php', 
                'verified': True
            },
            'weather_gov': {
                'name': 'OpenWeatherMap',
                'url': 'https://api.openweathermap.org/data/2.5/weather',
                'verified': True,
                'api_key': '00d5ea501cfab4ca390219973dd4c9f9'  # Anda perlu dapatkan API key
            },
            'news_api': {
                'name': 'NewsAPI',
                'url': 'https://newsapi.org/v2/everything',
                'verified': True,
                'api_key': '0a4985db05f24db892bb1588f153a148'  # Anda perlu dapatkan API key
            },
            'bmkg': {
                'name': 'BMKG Indonesia',
                'url': 'https://data.bmkg.go.id/',
                'verified': True
            },
            'gov_my': {
                'name': 'Portal Data Terbuka Malaysia',
                'url': 'https://data.gov.my/',
                'verified': True
            }
        }

        print("🔍 Verified Search Engine Initialized")
        print("📚 Sources: Wikipedia, BMKG, OpenWeatherMap, NewsAPI")

    def search_wikipedia(self, query, lang='ms'):
        """🔍 Search Wikipedia dengan source verification"""
        try:
            source = self.sources['wikipedia_ms'] if lang == 'ms' else self.sources['wikipedia_en']

            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': 5,
                'srprop': 'snippet|timestamp',
                'utf8': 1
            }

            response = requests.get(source['url'], params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get('query', {}).get('search', [])

                verified_results = []
                for result in results:
                    verified_results.append({
                        'title': result['title'],
                        'snippet': self.clean_html(result['snippet']),
                        'source': source['name'],
                        'timestamp': result.get('timestamp', ''),
                        'url': f"https://{lang}.wikipedia.org/wiki/{result['title'].replace(' ', '_')}",
                        'verified': True
                    })

                return verified_results

        except Exception as e:
            print(f"❌ Wikipedia search error: {e}")

        return []

    def get_weather(self, location):
        """🌤️ Get weather data from verified source"""
        try:
            # Untuk Malaysia/Indonesia, kita boleh guna OpenWeatherMap atau BMKG
            if 'kuala lumpur' in location.lower() or 'kl' in location.lower():
                # Contoh untuk Kuala Lumpur
                params = {
                    'q': 'Kuala Lumpur, MY',
                    'appid': self.sources['weather_gov']['api_key'],
                    'units': 'metric',
                    'lang': 'ms'
                }

                response = requests.get(
                    self.sources['weather_gov']['url'], 
                    params=params, 
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        'location': data['name'],
                        'temp': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'description': data['weather'][0]['description'],
                        'source': self.sources['weather_gov']['name'],
                        'timestamp': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'verified': True
                    }

        except Exception as e:
            print(f"❌ Weather API error: {e}")

        return None

    def search_news(self, query, country='my'):
        """📰 Search news from verified sources"""
        try:
            if not self.sources['news_api']['api_key']:
                return []

            params = {
                'q': query,
                'apiKey': self.sources['news_api']['api_key'],
                'pageSize': 5,
                'language': 'ms' if country == 'my' else 'en',
                'sortBy': 'relevancy'
            }

            response = requests.get(
                self.sources['news_api']['url'],
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])

                verified_articles = []
                for article in articles:
                    # Filter untuk sumber yang verified
                    source_name = article.get('source', {}).get('name', '')
                    if self.is_verified_news_source(source_name):
                        verified_articles.append({
                            'title': article['title'],
                            'description': article['description'],
                            'url': article['url'],
                            'source': source_name,
                            'published': article['publishedAt'],
                            'verified': True
                        })

                return verified_articles

        except Exception as e:
            print(f"❌ News API error: {e}")

        return []

    def is_verified_news_source(self, source_name):
        """✅ Check if news source is verified"""
        verified_sources = [
            'Bernama', 'Astro Awani', 'Utusan Malaysia', 'The Star',
            'New Straits Times', 'Malay Mail', 'Free Malaysia Today',
            'BBC', 'CNN', 'Reuters', 'Al Jazeera'
        ]

        return any(vs.lower() in source_name.lower() for vs in verified_sources)

    def clean_html(self, text):
        """🧹 Clean HTML from snippets"""
        if not text:
            return ""

        # Simple HTML tag removal
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def search_all_sources(self, query):
        """🔍 Search across all verified sources - FIXED"""
        results = {
            'wikipedia': [],
            'news': [],
            'weather': None,
            'total_sources': 0,
            'verified_count': 0
        }

        try:
            # 1. Search Wikipedia
            print(f"🔍 DEBUG: Searching Wikipedia...")
            wiki_results = self.search_wikipedia(query)
            results['wikipedia'] = wiki_results
            results['total_sources'] += 1
            results['verified_count'] += 1 if wiki_results else 0
            print(f"🔍 DEBUG: Wikipedia results: {len(wiki_results)}")

            # 2. Search News
            news_keywords = ['berita', 'isu', 'terkini', 'viral', 'trending', 'hari ini']
            if any(keyword in query.lower() for keyword in news_keywords):
                print(f"🔍 DEBUG: Searching news...")
                news_results = self.search_news(query)
                results['news'] = news_results
                results['total_sources'] += 1
                results['verified_count'] += len(news_results)
                print(f"🔍 DEBUG: News results: {len(news_results)}")

            # 3. Check Weather
            weather_keywords = ['cuaca', 'weather', 'hujan', 'panas', 'suhu']
            if any(keyword in query.lower() for keyword in weather_keywords):
                print(f"🔍 DEBUG: Getting weather...")
                weather_data = self.get_weather(query)
                results['weather'] = weather_data
                if weather_data:
                    results['total_sources'] += 1
                    results['verified_count'] += 1
                    print(f"🔍 DEBUG: Weather data: {weather_data.get('location', 'N/A')}")

            print(f"🔍 DEBUG: Total sources: {results['total_sources']}, Verified: {results['verified_count']}")
            return results

        except Exception as e:
            print(f"❌ Search error in search_all_sources: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return results  # Return empty results jika error
            
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

class DeepBot:
    def __init__(self):
        # ==================== IRC CONFIG ====================
        self.server = "irc.kampungchat.org"
        self.port = 6668
        self.nick = "deep"
        self.username = "seek"
        self.nickserv_password = "ace:123456"
        self.realname = "I'm your future, past and present, I'm the fine line 🧠"

        # Channels list
        self.channels = ['#amboi','#ace', '#zumba', '#alamanda', '#bro', '#desa', '#purple', "#amboi", "#movie", "#meow", "#love"]

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

        # ==================== SEARCH ENGINE ====================
        self.search_engine = VerifiedSearchEngine()
        self.last_cleanup_time = 0
        self.cleanup_interval = 86400

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

            # 👇 BAIKI SINI: Tukar } kepada )
            self.sock.connect((self.server, self.port)) 

            self.send_raw(f"NICK {self.nick}")
            self.send_raw(f"USER {self.username} 0 * :{self.realname}")

            # Tunggu server register nick
            time.sleep(3)

            # IDENTIFY ke NickServ
            if self.nickserv_password:
                print(f"🔐 Sending Identify command...")
                # Format standard: Nick + Password
                self.send_raw(f"PRIVMSG NickServ :IDENTIFY {self.nick} {self.nickserv_password}")
                time.sleep(5) # Tunggu balasan dari server

            # Join channel
            print("🚀 Joining channels...")
            for channel in self.channels:
                self.send_raw(f"JOIN {channel}")
                print(f"✅ Attempting to Join {channel}")
                time.sleep(1)

            self.connected = True
            print("✅ Connection sequence sent!")

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

        focus_message = f"auto reply activated buat {user} tanpa mention {self.nick} lagi. Taip '.clear' untuk bersihkan."
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

        # !ask command - Search web
        if message.startswith('!ask '):
            query = message[5:].strip()
            if query:
                self.send_action(channel, f"searching for '{query}'... 🔍")
                threading.Thread(
                    target=self.handle_ask_command,
                    args=(query, nick, channel),
                    daemon=True
                ).start()
                return True

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

    def handle_ask_command(self, query, nick, channel):
        """Handle !ask command - search web using VerifiedSearchEngine"""
        try:
            # Try Wikipedia Malay first
            result = self.search_engine.search_wikipedia(query, lang='ms')
            
            if result and result != "Tiada hasil ditemui.":
                self.send_message(channel, f"{nick}: {result}")
                return
            
            # Try Wikipedia English
            result = self.search_engine.search_wikipedia(query, lang='en')
            
            if result and result != "No results found.":
                self.send_message(channel, f"{nick}: {result}")
                return
            
            # Try news search
            result = self.search_engine.search_news(query)
            
            if result and "Error" not in result:
                self.send_message(channel, f"{nick}: {result}")
                return
            
            # No results found
            self.send_message(channel, f"{nick}: Maaf, tiada hasil ditemui untuk '{query}'. Cuba topik lain.")
            
        except Exception as e:
            print(f"❌ Error in !ask command: {e}")
            self.send_message(channel, f"{nick}: Maaf, ada masalah semasa mencari. Cuba lagi.")

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
        print("🚀 Starting DeepBot with Enhanced Language Support...")

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

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    print("="*60)
    print("🤖 Deep v4.2 - LANGUAGE DETECTION FIXED")
    print("🌐 Enhanced Malay + English + Mixed Language Support")
    print("🔧 Fixed AI Response Parsing")
    print("💾 Auto-expiry Log System")
    print("="*60)

    bot = DeepBot()

    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot crashed: {e}")
        import traceback
        traceback.print_exc()
