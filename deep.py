import re
import socket
import time
import random
import requests
from collections import deque

# ===== MEMORY SYSTEM =====
class MemorySystem:
    def __init__(self):
        self.conversations = {}
        self.search_sessions = {}
        self.message_queues = {}
        self.user_states = {}

    def save_chat(self, user, user_msg, bot_response):
        if user not in self.conversations:
            self.conversations[user] = deque(maxlen=3)

        self.conversations[user].append({
            'user': user_msg,
            'bot': bot_response,
            'time': time.time()
        })

    def get_recent_chats(self, user):
        if user not in self.conversations:
            return ""

        recent = []
        for chat in list(self.conversations[user])[-2:]:
            recent.append(f"User: {chat['user']}")
            recent.append(f"Assistant: {chat['bot']}")

        return "\n".join(recent)

    def clear_search_session(self, user):
        if user in self.search_sessions:
            del self.search_sessions[user]
        if user in self.message_queues:
            del self.message_queues[user]
        if user in self.user_states:
            del self.user_states[user]

    def save_message_queue(self, user, messages):
        self.message_queues[user] = {
            'messages': messages,
            'index': 0,
            'timestamp': time.time()
        }

    def get_next_message(self, user):
        if user in self.message_queues:
            queue = self.message_queues[user]
            if queue['index'] < len(queue['messages']):
                message = queue['messages'][queue['index']]
                queue['index'] += 1
                return message
            else:
                del self.message_queues[user]
                return "(🧠:end)"
        return None

    def has_more_messages(self, user):
        if user in self.message_queues:
            return self.message_queues[user]['index'] < len(self.message_queues[user]['messages'])
        return False

    def set_user_state(self, user, state):
        self.user_states[user] = state

    def get_user_state(self, user):
        return self.user_states.get(user, None)

# ===== WEB SPY WITH MEDIA LINKS =====
class WebSpy:
    def __init__(self):
        print("🔍 Web Spy Ready!")
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']

    def baca_website(self, url, nick):
        try:
            # Check untuk direct image links
            if self.is_image_url(url):
                return f"🖼️ {nick}: Image Link → {url}"

            # Check untuk direct video links  
            if self.is_video_url(url):
                return f"🎥 {nick}: Video Link → {url}"

            # Normal website
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE)
                title = title_match.group(1) if title_match else "No Title"

                # Cari image links dalam page
                image_links = self.extract_image_links(response.text)
                if image_links:
                    return f"📖 {nick}: {title} 🖼️{len(image_links)}images → {', '.join(image_links[:2])}"

                return f"📖 {nick}: {title} 🔗"
            else:
                return f"❌ Failed: HTTP {response.status_code}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def is_image_url(self, url):
        url_lower = url.lower()
        return any(url_lower.endswith(ext) for ext in self.image_extensions)

    def is_video_url(self, url):
        url_lower = url.lower()
        return any(url_lower.endswith(ext) for ext in self.video_extensions)

    def extract_image_links(self, html_content):
        img_pattern = r'<img[^>]+src="([^">]+)"'
        images = re.findall(img_pattern, html_content)

        valid_images = []
        for img in images:
            if any(img.lower().endswith(ext) for ext in self.image_extensions):
                if img.startswith('//'):
                    img = 'https:' + img
                valid_images.append(img)

        return valid_images[:3]  # Max 3 image links

# ===== MAIN BOT =====
class DeepGenius:
    def __init__(self):
        # IRC Config
        self.server = "irc.kampungchat.org"
        self.port = 6668
        self.nick = "deep"
        self.alt_nicks = ["DeepG", "DeepG_", "DeGen"]  # Alternate nicks
        self.channels = ["#ace", "#amboi", "#desa", "#alamanda", "#love"]

        # NickServ credentials (ganti dengan yang betul)
        self.nickserv_password = "ace:123456"  # Password yang betul

        # API Config
        self.api_key = "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"  # Isi dengan API key anda
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        # Systems
        self.memory = MemorySystem()
        self.web_spy = WebSpy()

        # Connection
        self.last_ping = time.time()
        self.last_message_time = 0
        self.message_delay = 1.0
        self.current_nick = self.nick
        self.identified = False
        self.join_attempts = 0

        # ==================== MEMORY SYSTEM ====================
        self.conversation_memory = []
        self.max_messages = 30
        self.cleanup_threshold = 10  # Padam 10 apabila penuh 30

        # ==================== INITIALIZATION ====================
        print(f"🧠 Memory system: max={self.max_messages}, auto-cleanup={self.cleanup_threshold}")
        print("🧠 Deep Genius - MEDIA LINKS + (🧠:end)!")
        print("🔍 Web Spy: Ready")
        print("🎯 Dramatic Search: Activated")
        print("📖 Complete Articles: Guaranteed")
        print(f"🎯 Nick: {self.nick}, Password: {self.nickserv_password}")

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
    
    def strip_ctrl_codes(self, text):
        """
        🧹 Strip semua control code formatting (bold, underline, italic, color, etc.)
        dari text sebelum dihantar ke AI server.
        """
        if not text:
            return text

        # Remove color codes
        text = re.sub(r'\x03\d{1,2}(?:,\d{1,2})?', '', text)

        # Remove other control characters
        control_chars = [
            '\x02',  # Bold
            '\x1D',  # Italic
            '\x1F',  # Underline
            '\x16',  # Reverse
            '\x0F',  # Reset
            '\x11',  # Monospace
            '\x1E',  # Strikethrough
        ]

        for char in control_chars:
            text = text.replace(char, '')

        # Clean up
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def connect(self):
        """🔗 Connect to IRC Server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(300)
            self.sock.connect((self.server, self.port))

            # Login sequence
            print(f"🔗 Connecting as {self.current_nick}...")
            self.send_raw(f"NICK {self.current_nick}")
            self.send_raw(f"USER seek 0 * :I'm your future, past and present, I'm the fine line 🧠")
            time.sleep(2)

            # Wait for initial connection
            self.receive_messages(timeout=5)

            # Try to identify with NickServ
            self.identify_with_nickserv()

            # Join channels after identification
            time.sleep(3)
            self.join_channels()

            print("🎉 Bot is ONLINE and READY!")

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            time.sleep(10)
            self.reconnect()

    def reconnect(self):
        """Try to reconnect with alternate nick if needed"""
        if self.current_nick == self.nick:
            # Try alternate nick
            alt_index = self.join_attempts % len(self.alt_nicks)
            self.current_nick = self.alt_nicks[alt_index]
            self.join_attempts += 1
            print(f"🔄 Trying alternate nick: {self.current_nick}")
        else:
            # Rotate back to main nick
            self.current_nick = self.nick
            print(f"🔄 Trying main nick: {self.current_nick}")

        self.connect()

    def identify_with_nickserv(self):
        """🔐 Identify with NickServ using proper IRC protocol"""
        try:
            print(f"🔐 Identifying with NickServ as {self.current_nick}...")

            # Wait a bit for NickServ to recognize us
            time.sleep(3)

            # Send IDENTIFY command (standard format)
            identify_cmd = f"PRIVMSG NickServ :IDENTIFY {self.nickserv_password}"
            self.send_raw(identify_cmd)
            print(f"📤 Sent: {identify_cmd}")

            # Alternative method: Use NICKSERV command
            nickserv_cmd = f"NICKSERV IDENTIFY {self.nickserv_password}"
            self.send_raw(nickserv_cmd)
            print(f"📤 Sent: {nickserv_cmd}")

            # Check for response
            self.receive_messages(timeout=5)

            # Set identified flag
            self.identified = True
            print("✅ Identification sent")

        except Exception as e:
            print(f"⚠️ NickServ identify error: {e}")
            self.identified = False

    def join_channels(self):
        """Join all channels"""
        for channel in self.channels:
            try:
                self.send_raw(f"JOIN {channel}")
                print(f"✅ Joined {channel}")
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Failed to join {channel}: {e}")

    def receive_messages(self, timeout=5):
        """Receive and process messages for a period"""
        end_time = time.time() + timeout
        self.sock.settimeout(1)

        while time.time() < end_time:
            try:
                data = self.sock.recv(2048).decode('utf-8', errors='ignore')
                if data:
                    lines = data.strip().split('\r\n')
                    for line in lines:
                        if line:
                            print(f"📥: {line}")

                            # Check for authentication success
                            if "You are now identified" in line or "Password accepted" in line:
                                print("✅ Successfully identified with NickServ!")
                                self.identified = True

                            # Check for nick in use
                            elif "Nickname is already in use" in line:
                                print("⚠️ Nick in use, trying alternate...")
                                return False

                            # Handle PING
                            elif line.startswith("PING"):
                                ping_data = line.split(":")[1] if ":" in line else ""
                                self.send_raw(f"PONG :{ping_data}")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"⚠️ Receive error: {e}")
                break

        self.sock.settimeout(300)
        return True

    def send_raw(self, message):
        """📤 Send raw IRC command"""
        try:
            self.sock.send(f"{message}\r\n".encode())
            if not message.startswith("PONG"):
                print(f"📤: {message}")
        except Exception as e:
            print(f"❌ Send error: {e}")

    def send_message(self, target, message):
        """💬 Send message to channel/user"""
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        if time_since_last < self.message_delay:
            time.sleep(self.message_delay - time_since_last)

        self.send_raw(f"PRIVMSG {target} :{message}")
        self.last_message_time = time.time()

    def split_into_complete_chunks(self, text, max_chars=350):
        """📝 Split text into COMPLETE chunks only"""
        # Extract timing dengan 3 digits
        timing_match = re.search(r'\[\🧠[^\]]+\]', text)
        timing = timing_match.group(0) if timing_match else ""
        content = re.sub(r'\[\🧠[^\]]+\]', '', text).strip()

        if len(content) <= max_chars:
            if timing:
                content = content + " " + timing
            return [content]

        # Split into complete sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

        if not sentences:
            return [content[:max_chars] + "..."]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if not sentence.endswith(('.', '!', '?')):
                sentence = sentence + '.'

            if len(current_chunk) + len(sentence) + 1 <= max_chars:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk and len(current_chunk) > 30:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk and len(current_chunk) > 30:
            chunks.append(current_chunk)

        # Add timing to LAST chunk only
        if chunks and timing:
            last_chunk = chunks[-1]
            if len(last_chunk) + len(timing) + 1 <= max_chars:
                chunks[-1] = last_chunk + " " + timing

        return chunks if chunks else [content[:max_chars] + "..."]

    def send_paginated_response(self, target, full_response, username, focus_choice):
        """📖 Send response dengan (🧠:end) di akhir"""
        full_response = self.clean_response(full_response)

        # Untuk pilihan 1 (fakta penting), terus hantar
        if focus_choice == '1':
            self.send_message(target, full_response)
            return False

        # Split into chunks
        chunks = self.split_into_complete_chunks(full_response, max_chars=330)

        if len(chunks) <= 1:
            self.send_message(target, full_response)
            return False
        else:
            # Prepare chunks dengan !next di hujung
            formatted_chunks = []
            for i, chunk in enumerate(chunks):
                clean_chunk = chunk.strip()

                if not clean_chunk.endswith(('.', '!', '?', ')')):
                    clean_chunk += '.'

                # Jika BUKAN chunk terakhir, tambah !next di hujung
                if i < len(chunks) - 1:
                    clean_chunk += " !next"

                formatted_chunks.append(clean_chunk)

            # Hantar chunk pertama
            self.send_message(target, formatted_chunks[0])

            # Simpan remaining chunks untuk !next
            if len(formatted_chunks) > 1:
                self.memory.save_message_queue(username, formatted_chunks[1:])
                self.memory.set_user_state(username, 'pagination')

            return True

    def handle_next_command(self, nick, channel):
        """🔄 Handle !next command dengan (🧠:end)"""
        current_state = self.memory.get_user_state(nick)

        if current_state != 'pagination':
            self.send_message(channel, "(🧠:end)")
            return True

        if self.memory.has_more_messages(nick):
            next_msg = self.memory.get_next_message(nick)

            if next_msg == "(🧠:end)":
                self.send_message(channel, "(🧠:end)")
                self.memory.clear_search_session(nick)
                return True
            elif next_msg:
                self.send_message(channel, next_msg)

                if not self.memory.has_more_messages(nick):
                    self.memory.clear_search_session(nick)
                return True

        self.send_message(channel, "(🧠:end)")
        self.memory.clear_search_session(nick)
        return True

    def clean_response(self, text):
        """🧹 Clean AI response"""
        text = re.sub(r'^(Hai|Hello|Hi|Selamat|Halo)[^!]*!?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'^(Deep|AI|Bot|Assistant)[:\-\s]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Saya (gembira|senang|suka)[^.]*\.\s*', '', text, flags=re.IGNORECASE)

        text = text.strip()

        if text and not text.endswith(('.', '!', '?')) and len(text.split()) > 2:
            text += '.'

        return text

    def get_ai_response(self, message, username, is_search=False, focus_choice='2'):
        """🤖 Get AI response dengan timing 3 digits"""
        start_time = time.time()
        try:
            # 🆕 STRIP CONTROL CODES sebelum proses ke AI
            clean_message = self.strip_ctrl_codes(message)

            context = self.memory.get_recent_chats(username)

            if is_search:
                prompt_templates = {
                    '1': """You are Deep - provide KEY FACTS only in Bahasa Malaysia.
                    Provide 3-5 most important facts as bullet points.
                    Be very concise and direct. No long explanations.
                    Format: • Fact 1 • Fact 2 • Fact 3""",

                    '2': """You are Deep - provide COMPREHENSIVE information in Bahasa Malaysia.
                    CRITICAL: Write in SHORT, COMPLETE sentences only. 
                    Each sentence must finish its thought completely.
                    Maximum 15-20 words per sentence.
                    Avoid long, complex sentence structures.
                    Use simple, clear Bahasa Malaysia.""",

                    '3': """You are Deep - provide DEEP ANALYSIS in Bahasa Malaysia.
                    CRITICAL: Write in SHORT, SELF-CONTAINED paragraphs only.
                    Each paragraph must be 2-3 complete sentences maximum.
                    Finish every thought completely before moving to next.
                    No incomplete ideas or cut-off sentences.
                    Use clear, straightforward Bahasa Malaysia."""
                }

                system_content = prompt_templates.get(focus_choice, prompt_templates['2'])
            else:
                system_content = f"""You are Deep - a helpful chat assistant in IRC chat. 
                Use Bahasa Malaysia or English and Keep responses natural and complete.
                Recent context: {context}
                Borak santai 
                suka menyampuk 
                Jawapan ringkas 
                straight to the point 
                penuh dengan slanga kampung 
                dan lawak jenaka
                jangan pakai semua huruf besar sebab nanti op kick CAPS
                """

            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"{username}: {clean_message}"}
            ]

            max_tokens = {
                '1': 120,
                '2': 300,
                '3': 512
            }.get(focus_choice, 300)

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }

            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                result = response.json()
                ai_text = result['choices'][0]['message']['content'].strip()

                ai_text = self.clean_response(ai_text)

                # TIMING 3 DIGITS - Convert to milliseconds
                response_time_ms = int((time.time() - start_time) * 1000)
                timing_display = f" [🧠{response_time_ms:03d}ms]"

                if len(ai_text) < 150:
                    self.memory.save_chat(username, clean_message, ai_text)

                return ai_text + timing_display
            else:
                response_time_ms = int((time.time() - start_time) * 1000)
                return f"Maaf, API sibuk. [💔{response_time_ms:03d}ms]"

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            return f"Error: {str(e)} [💔{response_time_ms:03d}ms]"

    # ===== 🎭 DRAMATIC SEARCH ENGINE =====
    def dramatic_search_engine(self, question, nick, channel):
        """🎭 3-LINE DRAMATIC SEARCH ONLY"""
        try:
            script_lines = self.generate_dramatic_sequence(question)

            for line in script_lines:
                if line.strip():
                    self.send_raw(f"PRIVMSG {channel} :\x01ACTION {line.strip()}\x01")
                    print(f"🎭 Action: * {self.current_nick} {line.strip()}")
                    time.sleep(1.5)

            focus_question = self.generate_normal_focus_question(question)
            self.send_message(channel, focus_question)

            self.memory.search_sessions[nick] = {
                'original_question': question,
                'channel': channel, 
                'stage': 'waiting_focus',
                'search_type': self.detect_search_type(question),
                'username': nick
            }

            return True

        except Exception as e:
            self.send_message(channel, f"❌ Search failed: {str(e)}")
            return True

    def generate_dramatic_sequence(self, question):
        """🎭 GENERATE 3-LINE DRAMATIC SEQUENCE"""
        search_type = self.detect_search_type(question)
        result_count = random.randint(13, 33)

        dramatic_scripts = {
            'tech': [
                f"🔧 {question.upper()} • 📦 {result_count} sources • 💻 Tech Analysis",
                f"🔍 Code Review • 📚 Documentation • ⚙️ System Parse", 
                f"🧠 AI Processing • ✅ Verification • 🎯 Target Locked"
            ],
            'general': [
                f"🌐 {question.upper()} • 📊 {result_count} databases • 📖 Research Initiated",
                f"🔗 Cross-Reference • 🎓 Academic Sources • 💾 Data Mining",
                f"🧠 Intelligence Synthesis • ✅ Data Verified • 📋 Report Ready"
            ],
            'howto': [
                f"🛠️ {question.upper()} • 📋 {result_count} guides • 📝 Procedure Analysis",
                f"🔧 Step Extraction • 🎥 Video Reference • 📖 Manual Compilation",
                f"🧠 Method Optimization • ✅ Steps Validated • 🎯 Guide Prepared"
            ],
            'news': [
                f"📰 {question.upper()} • 🔄 {result_count} streams • 🗞️ News Monitoring", 
                f"⚡ Live Updates • 📱 Social Feed • 🌐 Blog Analysis",
                f"🧠 Trend Analysis • ✅ Facts Checked • 📊 Report Compiled"
            ]
        }

        return dramatic_scripts.get(search_type, dramatic_scripts['general'])

    def generate_normal_focus_question(self, original_question):
        return f"🎯 Pilihan: [1]Fakta penting [2]Maklumat lengkap [3]Analisis mendalam - '{original_question}'"

    def detect_search_type(self, question):
        q_lower = question.lower()

        if any(word in q_lower for word in ['code', 'programming', 'python', 'javascript', 'github', 'api']):
            return 'tech'
        elif any(word in q_lower for word in ['bagaimana', 'cara', 'tutorial', 'step', 'panduan']):
            return 'howto'
        elif any(word in q_lower for word in ['berita', 'trending', 'viral', 'isu terkini', 'hari ini']):
            return 'news'
        else:
            return 'general'

    def handle_search_focus(self, nick, channel, focus_choice):
        if nick in self.memory.search_sessions and self.memory.search_sessions[nick]['stage'] == 'waiting_focus':
            session = self.memory.search_sessions[nick]
            original_question = session['original_question']
            search_type = session['search_type']

            enhanced_query = self.enhance_search_query(original_question, focus_choice, search_type)
            search_response = self.get_ai_response(enhanced_query, nick, is_search=True, focus_choice=focus_choice)

            has_more = self.send_paginated_response(channel, search_response, nick, focus_choice)

            self.memory.search_sessions[nick]['stage'] = 'completed'
            self.memory.search_sessions[nick]['focus_choice'] = focus_choice

            return True

        return False

    def enhance_search_query(self, original_question, focus_choice, search_type):
        focus_enhancements = {
            '1': {
                'tech': f"{original_question} - berikan fakta penting dan utama sahaja",
                'howto': f"{original_question} - langkah asas dan penting sahaja", 
                'general': f"{original_question} - fakta utama dan maklumat asas",
                'news': f"{original_question} - perkara utama dan update terkini"
            },
            '2': {
                'tech': f"{original_question} - berikan penjelasan lengkap dengan contoh",
                'howto': f"{original_question} - panduan lengkap langkah demi langkah",
                'general': f"{original_question} - maklumat menyeluruh dan terperinci", 
                'news': f"{original_question} - laporan lengkap dengan context"
            },
            '3': {
                'tech': f"{original_question} - analisis mendalam dengan teknikal details",
                'howto': f"{original_question} - analisis komprehensif dengan tips lanjutan",
                'general': f"{original_question} - kajian mendalam dan analisis menyeluruh",
                'news': f"{original_question} - analisis mendalam dengan background lengkap"
            }
        }

        return focus_enhancements.get(focus_choice, {}).get(search_type, original_question)

    def handle_normal_message(self, nick, channel, message):
        if message.lower() == '!next':
            if self.handle_next_command(nick, channel):
                return True

        if nick in self.memory.search_sessions and self.memory.search_sessions[nick]['stage'] == 'waiting_focus':
            if message in ['1', '2', '3']:
                return self.handle_search_focus(nick, channel, message)

        return False

    def handle_command(self, nick, channel, message):
        if message.startswith('!baca website'):
            url = message[14:].strip()
            if url:
                result = self.web_spy.baca_website(url, nick)
                self.send_message(channel, result)
                return True

        elif message == '.help':
            help_text = "🤖 Deep: !baca website [url] | !ask [question] | !info | !next"
            self.send_message(channel, help_text)
            return True

        elif message.startswith('!ask '):
            question = message[5:].strip()
            if question:
                print(f"🎭 !ask from {nick}: {question}")
                return self.dramatic_search_engine(question, nick, channel)

        return False

    def should_respond(self, nick, message):
        if nick.lower() == self.current_nick.lower():
            return False

        if self.current_nick.lower() in message.lower():
            return True

        if random.random() < 0.03:
            return True

        return False

    def parse_message(self, line):
        if line.startswith("PING"):
            ping_data = line.split(":")[1] if ":" in line else "keepalive"
            self.send_raw(f"PONG :{ping_data}")
            return None

        parts = line.split(" ")
        if len(parts) < 2:
            return None

        if parts[1] == "PRIVMSG":
            try:
                nick = parts[0][1:].split("!")[0]
                channel = parts[2]
                message = " ".join(parts[3:])[1:]

                return {
                    "type": "message",
                    "nick": nick,
                    "channel": channel,
                    "message": message
                }
            except:
                return None

        return None

    def run(self):
        self.connect()
        buffer = ""

        while True:
            try:
                if time.time() - self.last_ping > 30:
                    self.send_raw("PING :keepalive")
                    self.last_ping = time.time()

                data = self.sock.recv(2048).decode('utf-8', errors='ignore')
                if not data:
                    print("❌ No data, reconnecting...")
                    time.sleep(5)
                    self.connect()
                    continue

                buffer += data
                lines = buffer.split("\r\n")
                buffer = lines.pop()

                for line in lines:
                    if line.strip():
                        parsed = self.parse_message(line)
                        if not parsed:
                            continue

                        if parsed["type"] == "message":
                            nick, channel, message = parsed["nick"], parsed["channel"], parsed["message"]

                            if self.handle_normal_message(nick, channel, message):
                                continue

                            if message.startswith('!'):
                                if self.handle_command(nick, channel, message):
                                    continue

                            if self.should_respond(nick, message):
                                response = self.get_ai_response(message, nick)
                                self.send_message(channel, response)

            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(5)
                self.connect()

if __name__ == "__main__":
    bot = DeepGenius()
    bot.run()
