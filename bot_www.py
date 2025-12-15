#!/usr/bin/env python3
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
import time
import socket
import threading
import select
import random
import json
import re
from datetime import datetime, timedelta
# Selepas imports, tambah:
import random

def _post_with_retry(payload, headers, timeout=10, max_retries=3):
    backoff = 1
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)

            # Log rate limit headers
            if 'x-ratelimit-remaining' in response.headers:
                print(f"Rate limit: {response.headers['x-ratelimit-remaining']} remaining")

            if response.status_code != 429:
                return response

            wait = backoff + random.random()
            print(f"429 received, waiting {wait:.1f}s...")
            time.sleep(wait)
            backoff *= 2

        except Exception as e:
            print(f"Retry {attempt} failed: {e}")

    return response
# ==================== CONFIG ====================
SERVER = "irc.kampungchat.org"
PORT = 6668
CHANNELS = ["#bro", "#ace", "#alamanda", "#amboi", "#desa", "#kampungchat", "#movie", "#meow","#zumba" ]
CHANNELSx = ["#ace"]
NICK = "www"
PASSWORD = "fai5zul"
IDENT = "highlander"
REALNAME = "╱╲╱╳╲╱╲Bukti Jadi Sejarah 🇲🇾❤🇵🇸╱╲╱╳╲╱╲"

# Files
PASSWORD_FILE = "sweet_password.txt"
KNOWLEDGE_FILE = "notepad.txt"
PROMPT_FILE = "prompt.txt"

# API URLs
CUACA_API = "https://api.open-meteo.com/v1/forecast"
SOLAT_API = "https://api.waktusolat.app/solat"
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"

# Groq API Configuration
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

# Other configs
MALAYSIA_UTC_OFFSET = 8
MAX_MESSAGE_LENGTH = 400
HOURLY_TRIGGER_MINUTE = 0
QUOTE_TRIGGER_MINUTES = [0, 15, 30, 45]  # Every 15 minutes
MAX_RETRIES = 9999
RETRY_DELAY = 30

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
                line_items.append(f"⛈️ {data['hujan']}mm (hujan ribut)")
            elif data['hujan'] >= 10: 
                line_items.append(f"🌧️💦 {data['hujan']}mm (hujan lebat)")
            elif data['hujan'] >= 5: 
                line_items.append(f"🌧️ {data['hujan']}mm (sedang hujan)")
            elif data['hujan'] >= 1: 
                line_items.append(f"🌦️ {data['hujan']}mm (hujan gerimis)")
            else: 
                line_items.append(f"🌦️ {data['hujan']}mm (hujan rintik)")
        elif data['peluang_hujan'] > 70:
            line_items.append(f"☔ {data['peluang_hujan']}% (berpeluang hujan)")
        elif data['peluang_hujan'] > 40:
            line_items.append(f"🌂 {data['peluang_hujan']}% (mungkin hujan)")
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
            if hour >= 2 and hour < 12:
                tip_display = "💡 pagi yang ceria! 🌅"
            elif hour >= 12 and hour < 14:
                tip_display = "💡 rehat tengahari 😴"
            elif hour >= 14 and hour < 19:
                tip_display = "💡 waktu petang 🌇"
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

# ==================== COMBINED BOT ====================
class WWWBotCombined:
    """WWW Bot Combined - Weather, Prayer, Ping, AI, Auto-quotes"""

    def __init__(self):
        # ==================== BASIC ATTRIBUTES ====================
        self.nick = NICK
        self.password = PASSWORD
        self.sock = None
        self.running = True
        self.motd_received = False
        self.connected = False
        self.retry_count = 0

        # ==================== STATISTICS COUNTERS ====================
        # ⭐⭐⭐ INITIALIZE STATS DICTIONARY PERTAMA ⭐⭐⭐
        self.stats = {
            # Message counters
            'messages_processed': 0,
            'messages_received': 0,
            'messages_sent': 0,
            'ignored_messages': 0,
            'pings_processed': 0,  # ⬅️ INI PENTING UNTUK CTCP

            # Command counters  
            'commands_processed': 0,
            'commands_unknown': 0,
            'help_responses': 0,

            # AI counters
            'ai_queries': 0,
            'ai_responses': 0,
            'ai_success': 0,
            'ai_failed': 0,
            'critical_questions': 0,
            'normal_questions': 0,

            # Feature counters
            'maideen_replies': 0,
            'ping_requests_sent': 0,  # ⬅️ GANTI NAMA (untuk elak conflict)
            'weather_queries': 0,
            'prayer_queries': 0,
            'jokes_told': 0,
            'auto_quotes': 0,

            # System counters
            'errors': 0,
            'warnings': 0,
            'connections': 0,
            'reconnects': 0,
            'timeouts': 0,
            'rate_limits': 0,
            'api_calls': 0,

            # Timing
            'start_time': time.time(),
        }

        # ==================== DATA PROVIDERS ====================
        self.data = DataProviderFixed()
        self.display = DisplayFixed()

        # ==================== PING/CTCP SYSTEM ====================
        # ⭐⭐⭐ HAPUS: self.stats['pings_processed'] = 0 ⭐⭐⭐ (sudah ada di atas)

        # Ping system (from bot)
        self.ping_requests = {}  # Untuk track CTCP ping requests
        self.znc_detected = set()
        self.message_index = 0

        # Load cap ayam messages
        self.load_cap_ayam_messages()

        # ==================== AI SYSTEM ====================
        self.prompt = self.load_prompt()
        self.knowledge_base = self.load_knowledge()
        self.last_response_time = {}
        self.last_api_call = 0
        self.rate_limit_delay = 2.0

        # ==================== NOTIFICATIONS ====================
        self.last_solat_notif = {}
        self.last_hourly = -1
        self.last_quote_minute = -1
        self.joined_channels = set()

        # Initialize last_solat_notif untuk setiap channel
        for channel in CHANNELS:
            self.last_solat_notif[channel] = {}
            self.joined_channels.add(channel)

        # ==================== MESSAGE MANAGEMENT ====================
        self.last_messages = {}
        self.duplicate_window = 60
        self.MESSAGE_DELAY = 1.5
        self.MAX_LINES_PER_COMMAND = 10

        # Anti-spam & repeat system
        self.repeat_tracker = {}
        self.spam_detection = {}
        self.temp_ignore_list = {}
        self.max_repeats = 2
        self.repeat_time_window = 5
        self.ignore_duration = 2
        self.welcome_cooldown = {}
        print("✅ Welcome system ready (.wc & .wb commands)")

        # ==================== BOT PERSONALITY ====================

        # Jokes database for Maideen
        self.MAIDEEN_JOKES = [
            "alo incik , apa mau minum? 🍵",
            "saya pun sudah banyak penat la .. tarak larat mau cakap lagi la 😴",
            "jangan kacau sama saya la , aiyoooo 😫",
            "ini macam kalu, saya bisnes ada kasi tutup la .. worang tarak 😔",
            "2 ringgit je boss! 💸",
            "sikit jam tunggu la deiiii ⏳",
            "saya masa tarak la 😓",
            "saya tarak boleh tahan la deiii .. badan banyak letih 😩",
            "saya sini malaysia juga duduk , sana India sudah lama tarak balik 🇮🇳➡️🇲🇾",
            "Sometime in the near future. Ask again tomorrow. 📅",
            "wokeh , teh tarik siap! ☕",
            "roti canai ada, tambah telur? 🥚",
            "kopi 'O' panas satu? 🔥",
            "mee goreng mamak special! 🍜",
            "ais kacang mau? ais pun ada! 🍧",
            "boss, nasi lemak sudah habis, nasi minyak mau? 🍚",
            "maggi goreng double telur, best! 😋",
            "air limau ais, fresh sikit! 🍹",
            "tosai crispy, mau sambal extra? 🌶️",
            "murtabak ayam special, confirm sedap! 🥘",
        ]

        # WWW replies to Maideen
        self.WWW_TO_MAIDEEN_REPLIES = [
            "Wei Maideen, roti canai satu! 🥞",
            "Maideen, teh tarik kurang manis! ☕",
            "Bro Maideen, jangan mengada! 😆",
            "Maideen, badan penat jangan complain! 💪",
            "Oi Maideen, India balik belum? 🇮🇳",
            "Maideen, bisnes baik ke? 💰",
            "Weh Maideen, jangan malas! 🏃‍♂️",
            "Maideen, saya pun penat gak! 😅",
            "Bro, Maideen lagi sibuk! 📱",
            "Maideen, tarak rehat ke? 😴",
        ]

        # Ignore bots list
        # Tambah dalam __init__:
        self.IGNORED_BOTS = {
            'ChanServ', 'NickServ', 'MemoServ', 'OperServ',
            'Q', 'L', 'Global', 'Aizudin',

            # ⭐⭐⭐ TAMBAH BOTS YANG ANDA PERLU IGNORE ⭐⭐⭐
            'themstudio', 'z-bot', 'zumbabot', 'zumbaquiz',
            'movie', 'kucing_gemuk', 'lovefmradio',
            'minah', 'maya_karin', 'quiz', 'radio', 'Maideen',

            # Generic bot patterns
            'serv', 'bot', '-bot', '_bot', '.bot'
        }

        # Critical question keywords
        self.CRITICAL_KEYWORDS = [
            'maksud', 'erti', 'definisi', 'pengertian', 'konsep',
            'falsafah', 'hikmah', 'pemikiran', 'kenapa', 'mengapa',
            'bagaimana', 'jelaskan', 'huraikan', 'bincangkan', 'analisis',
            'kehidupan', 'mati', 'cinta', 'iman', 'takwa', 'dunia',
            'akhirat', 'syurga', 'neraka', 'meaning', 'define', 'explain',
            'why', 'how', 'philosophy', 'wisdom', 'life', 'death',
            'pendapat anda', 'apa pandangan', 'bagaimana pendapat',
        ]

        # Dramatic timing delays
        self.DRAMATIC_DELAYS = [1.5, 2.5, 2.5, 3.0]

        # API Configuration
        self.GROQ_MODEL = "llama-3.1-8b-instant"
        self.GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

        # ==================== INITIALIZE COMPONENTS ====================
        # Maideen bot integration
        self.maideen = self._create_maideen_bot()

        # Command aliases system
        self.COMMAND_ALIASES = {}
        self.setup_aliases()

        # Untuk track channel join times (grace period)
        self._channel_joins = {}

        # ==================== DISPLAY STARTUP INFO ====================
        print("="*70)
        print(f"🤖 WWW BOT COMBINED - ALL FEATURES")
        print("="*70)
        print(f"🔧 NICK: {self.nick}")
        print(f"🔧 SERVER: {SERVER}:{PORT}")
        print(f"🔧 CHANNELS: {', '.join(CHANNELS)}")
        print(f"🔧 AI MODEL: {self.GROQ_MODEL}")
        print(f"🔧 IGNORED BOTS: {len(self.IGNORED_BOTS)} bots")
        print(f"🔧 MAIDEEN JOKES: {len(self.MAIDEEN_JOKES)} jokes loaded")
        print(f"🔧 STATS COUNTERS: {len(self.stats)} metrics initialized")
        print("="*70)

        # Show prompt summary
        if self.prompt:
            lines = self.prompt.split('\n')
            non_empty = [line for line in lines if line.strip()]
            print(f"🔧 PROMPT: {len(non_empty)} lines loaded")
        else:
            print("⚠️  NO PROMPT LOADED!")

        print("="*70)
    
    def is_repeat_spam(self, nick, message, channel=None):
        """SIMPLE VERSION: Detect 2x repeat, PER CHANNEL"""
        try:
            # Initialize jika belum ada
            if not hasattr(self, 'repeat_tracker'):
                self.repeat_tracker = {}
                self.log("✅ Initialized repeat_tracker")

            current_time = time.time()
            msg_clean = message.strip().lower()

            # Skip bots
            bot_keywords = ['serv', 'bot', 'nickserv', 'chanserv', 'memoserv']
            if any(x in nick.lower() for x in bot_keywords):
                return False

            # ⭐⭐⭐ GUNA CHANNEL-SPECIFIC TRACKING ⭐⭐⭐
            # Key: channel:nick
            track_key = f"{channel}:{nick}" if channel else nick

            if track_key not in self.repeat_tracker:
                self.repeat_tracker[track_key] = {
                    'last_msg': '',
                    'last_time': 0,
                    'count': 0
                }

            data = self.repeat_tracker[track_key]

            # Check jika message sama
            if msg_clean == data['last_msg']:
                time_diff = current_time - data['last_time']

                # Jika dalam 10 saat DAN CHANNEL SAMA
                if time_diff <= 10:
                    data['count'] += 1

                    # JIKA 2x REPEAT - SHOW ACTION DI CHANNEL SAMA
                    if data['count'] == 2:
                        # Show action message DI CHANNEL YANG SAMA
                        if channel:
                            # self.send_action(channel, f"nampak {nick} 2x repeat malas layan..")
                            self.log(f"⚠️ ACTION in {channel}: nampak {nick} 2x repeat malas layan..")

                        # Set ignore timestamp (10 saat dari sekarang)
                        data['ignore_until'] = current_time + 5
                        self.log(f"🚫 {nick} in {channel}: 2x repeat - ignoring for 5s")
                        return True

                    # Jika lebih dari 2x, check ignore period
                    elif data['count'] > 2:
                        if current_time < data.get('ignore_until', 0):
                            return True
                else:
                    # Lewat 10 saat, reset count
                    data['count'] = 1
            else:
                # Message berbeza, reset semua
                data['last_msg'] = msg_clean
                data['count'] = 1

            # Update last time
            data['last_time'] = current_time

            # Check ignore period
            if current_time < data.get('ignore_until', 0):
                return True

            return False

        except Exception as e:
            self.log(f"⚠️ Repeat check error: {e}")
            return False
    
    def _init_all_stats(self):
        """Initialize all possible statistics counters"""
        all_stats = [
            # Message counters
            'messages_received', 'messages_processed', 'messages_sent',
            'messages_ignored', 'messages_duplicate',

            # Command counters
            'commands_processed', 'commands_unknown', 'commands_error',

            # AI counters
            'ai_queries', 'ai_success', 'ai_failed', 'ai_timeout',
            'critical_questions', 'normal_questions',

            # Feature counters
            'maideen_replies', 'ping_requests', 'weather_queries',
            'prayer_queries', 'quote_posted', 'notifications_sent',

            # System counters
            'errors', 'warnings', 'connections', 'reconnects',
            'timeouts', 'rate_limits', 'api_calls',
        ]

        self.stats = {stat: 0 for stat in all_stats}

    def should_ignore(self, nick):
        """Check jika nick perlu diignore"""
        if not nick:
            return True

        # Clean nick dari IRC prefixes
        nick_clean = nick.lower().strip('@+%&~')

        # Check dalam ignore list
        if nick_clean in self.IGNORED_BOTS:
            self.update_stats('ignored_messages')
            return True

        # Additional checks jika diperlukan
        if 'serv' in nick_clean.lower() or nick_clean.endswith('bot'):
            return True

        return False
    
    def update_stats(self, stat_name, increment=1):
        """Safely update statistics counter"""
        # Jika key tidak wujud, create dulu
        if stat_name not in self.stats:
            print(f"📊 Creating new stat key: {stat_name}")
            self.stats[stat_name] = 0

        # Increment
        self.stats[stat_name] += increment
        return self.stats[stat_name]
    
    def safe_increment(self, stat_name, increment=1):
        """Safely increment a statistic counter"""
        # Jika stat tidak wujud dalam dict, create dulu
        if stat_name not in self.stats:
            self.stats[stat_name] = 0

        # Increment
        self.stats[stat_name] += increment

        # Return new value (optional)
        return self.stats[stat_name]
    
    def _create_maideen_bot(self):
        """Create Maideen bot instance"""
        class SimpleMaideen:
            def __init__(self, jokes_db):
                self.jokes_db = jokes_db

            def generate_reply(self, message, sender):
                """Simple Maideen reply"""
                import random
                message_lower = message.lower()

                # Check for direct mention
                if 'maideen' in message_lower:
                    replies = [
                        f"ya {sender}, panggil saya? 📢",
                        f"saya sini {sender}, jangan bising! 🤫",
                        f"apa mau {sender}? order? 📝",
                    ]
                    return random.choice(replies)

                # Default: random joke
                return random.choice(self.jokes_db)

        # SEKARANG self.MAIDEEN_JOKES sudah wujud!
        return SimpleMaideen(self.MAIDEEN_JOKES)

    def setup_aliases(self):
        """Setup semua command aliases"""
        # Define handler functions
        def handle_prompts(nick, args):
            return self.handle_prompt_command(nick, args)

        def handle_help(nick, args):
            return self.show_help(nick)

        def handle_status(nick, args):
            return f"{nick}: Bot WWW & Maideen aktif! 🤖"

        def handle_ignore_bot(nick, args):
            return self.toggle_ignore_bot(nick, args)

        # Register aliases
        self.COMMAND_ALIASES = {
            # prompts command dengan multiple aliases
            'prompts': handle_prompts,
            'backuprompt': handle_prompts,
            'bprompt': handle_prompts,
            'setprompt': handle_prompts,
            'prompt': handle_prompts,

            # help command
            'help': handle_help,
            'bantuan': handle_help,
            'tolong': handle_help,

            # status command  
            'status': handle_status,
            'stats': handle_status,
            'botstatus': handle_status,

            # ignore bot command
            'ignorebot': handle_ignore_bot,
            'blockbot': handle_ignore_bot,
            'skipbot': handle_ignore_bot,
        }

        print(f"✅ Aliases setup complete: {len(self.COMMAND_ALIASES)} commands registered")

    def check_and_post_auto_updates(self):
        """Check dan post semua auto-updates - ENABLE QUOTES"""
        try:
            now = DisplayFixed.get_malaysia_time()

            # 1. HOURLY WEATHER (boleh kekal)
            if now.minute == 0 and now.second <= 10:
                if now.hour != self.last_hourly:
                    self.log(f"🕐 Auto: Posting hourly weather at {now.hour}:00")
                    cuaca_data = self.data.get_cuaca_detail("Kuala Lumpur")
                    if cuaca_data:
                        lines = self.display.format_cuaca_jelas(cuaca_data)
                        for channel in self.joined_channels:
                            if channel:
                                for line in lines:
                                    self.send(channel, line)
                                    time.sleep(1)
                                time.sleep(2)
                    self.last_hourly = now.hour

            # 2. ⭐⭐ ENABLE AUTO-QUOTES ⭐⭐ (pada minit 15, 30, 45)
            if now.minute in [15, 30, 45] and now.second <= 10:
                if now.minute != self.last_quote_minute:
                    self.log(f"💭 Auto: Posting quote at {now.hour}:{now.minute:02d}")
                    quote = self.get_ai_quote()
                    if not quote:
                        quote = self.get_fallback_quote()
                    if quote:
                        for channel in self.joined_channels:
                            if channel:
                                self.send(channel, f"💭 {quote}")
                                time.sleep(2)
                    self.last_quote_minute = now.minute

            # 3. SOLAT NOTIFICATION (boleh kekal)
            current_time_str = now.strftime("%I:%M%p").lower().lstrip('0')
            solat_data = self.data.get_solat("Kuala Lumpur")
            if solat_data and 'error' not in solat_data:
                prayers = [
                    ('subuh', '🌅🕌 subuh', solat_data.get('subuh')),
                    ('zohor', '🕌🕰️ zohor', solat_data.get('zohor')),
                    ('asar', '⛅📿 asar', solat_data.get('asar')),
                    ('maghrib', '🌇🌙 maghrib', solat_data.get('maghrib')),
                    ('isyak', '🌃🌟 isyak', solat_data.get('isyak'))
                ]

                for channel in self.joined_channels:
                    if not channel:
                        continue
                    for prayer_key, prayer_name, prayer_time in prayers:
                        if not prayer_time or prayer_time == "--:--":
                            continue
                        prayer_clean = DisplayFixed.convert_to_12h(prayer_time)
                        prayer_clean = prayer_clean.replace(":00", "")
                        if prayer_clean == current_time_str:
                            today = now.strftime("%Y%m%d")
                            last_notif = self.last_solat_notif.get(channel, {}).get(prayer_key)
                            if last_notif != today:
                                msg = f"⏰ Sekarang telah masuknya waktu • {prayer_name} • {prayer_time} bagi Kuala Lumpur dan kawasan yang sewaktu dengannya."
                                self.send(channel, msg)
                                if channel not in self.last_solat_notif:
                                    self.last_solat_notif[channel] = {}
                                self.last_solat_notif[channel][prayer_key] = today
                                self.log(f"✅ Solat notification for {prayer_name} posted")

        except Exception as e:
            self.log(f"⚠️ Auto-update check error: {e}")

    def post_hourly_weather(self, waktu):
        """Post hourly weather ke semua channel"""
        try:
            cuaca = self.data.get_cuaca_detail("Kuala Lumpur")
            if not cuaca:
                self.log("❌ Failed to get weather data")
                return

            lines = self.display.format_cuaca_jelas(cuaca)

            for channel in self.joined_channels:
                if channel:  # Pastikan channel valid
                    for line in lines:
                        self.send(channel, line)
                        time.sleep(1)

                    self.log(f"✅ Posted hourly weather to {channel}")
                    time.sleep(2)  # Delay antara channel

            self.update_stats('weather_queries')

        except Exception as e:
            self.log(f"❌ Hourly weather error: {e}")

    def post_auto_quote(self):
        """Post auto quote ke semua channel"""
        try:
            quote = self.get_ai_quote()
            if not quote:
                quote = self.get_fallback_quote()  # Fallback

            if quote:
                for channel in self.joined_channels:
                    if channel:
                        self.send(channel, f"💭 {quote}")
                        self.log(f"✅ Posted quote to {channel}")
                        time.sleep(2)  # Delay antara channel

                self.stats['auto_quotes'] += 1

        except Exception as e:
            self.log(f"❌ Auto quote error: {e}")

    def check_solat_notification(self, now):
        """Check dan post solat notification"""
        try:
            current_time_str = now.strftime("%I:%M%p").lower().lstrip('0')

            # Dapatkan data solat KL (default)
            solat_data = self.data.get_solat("Kuala Lumpur")
            if not solat_data or 'error' in solat_data:
                return

            # Check setiap waktu solat
            prayers = [
                ('subuh', '🌅🕌 subuh', solat_data.get('subuh')),
                ('zohor', '🕌🕰️ zohor', solat_data.get('zohor')),
                ('asar', '⛅📿 asar', solat_data.get('asar')),
                ('maghrib', '🌇🌙 maghrib', solat_data.get('maghrib')),
                ('isyak', '🌃🌟 isyak', solat_data.get('isyak'))
            ]

            for channel in self.joined_channels:
                if not channel:
                    continue

                for prayer_key, prayer_name, prayer_time in prayers:
                    if not prayer_time or prayer_time == "--:--":
                        continue

                    # Clean time format
                    prayer_clean = DisplayFixed.convert_to_12h(prayer_time)
                    prayer_clean = prayer_clean.replace(":00", "")

                    # Compare dengan current time
                    if prayer_clean == current_time_str:
                        today = now.strftime("%Y%m%d")
                        last_notif = self.last_solat_notif.get(channel, {}).get(prayer_key)

                        if last_notif != today:
                            self.send(channel, f"⏰ Sekarang telah masuknya waktu • {prayer_name} • {prayer_time} bagi Kuala Lumpur dan kawasan yang sewaktu dengannya.")
                            # Update last notification
                            if channel not in self.last_solat_notif:
                                self.last_solat_notif[channel] = {}
                            self.last_solat_notif[channel][prayer_key] = today
                            self.update_stats('prayer_queries')

        except Exception as e:
            self.log(f"❌ Solat notification error: {e}")
    
    def add_to_memory(self, nick, message, channel):
        """Add message to memory - WITH UNIVERSAL BOT CLEANING"""
        # Check jika message dari bot
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

        # Skip jika tidak perlu
        skip_conditions = [
            not clean_message,
            len(clean_message.strip()) < 2,
            clean_message.startswith('ACTION'),
            nick.lower() == self.nick.lower(),
            clean_message.lower() in ['ping', 'pong', 'test', 'hello', 'hi'],
        ]

        if any(skip_conditions):
            return

        # Add to memory
        self.conversation_memory.append({
            'nick': nick,
            'message': clean_message,
            'channel': channel,
            'timestamp': time.time(),
            'time_str': time.strftime('%I:%M%p', time.localtime()).lower(),
            'is_bot': is_bot  # Flag untuk bot messages
        })

        # Memory management
        if len(self.conversation_memory) > 30:
            removed = self.conversation_memory[:15]
            self.conversation_memory = self.conversation_memory[15:]

            # Log jenis messages yang dibuang
            bot_count = sum(1 for msg in removed if msg.get('is_bot', False))
            human_count = len(removed) - bot_count
            print(f"🧹 Memory: Removed {len(removed)} messages ({bot_count} bots, {human_count} humans)")

        # Print memory status
        bot_in_memory = sum(1 for msg in self.conversation_memory if msg.get('is_bot', False))
        print(f"🧠 Memory: {len(self.conversation_memory)}/30 ({bot_in_memory} bot messages)")

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
            'MEMOSERV', 'OPERSERV', 'STATS', 'INFO', 'Z-Bot',

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
    
    # ==================== CRITICAL QUESTION DETECTION ====================
    def _is_critical_question(self, text):
        """Detect jika soalan kritikal"""
        if not text:
            return False

        text_lower = text.lower()

        # Check keywords
        if any(keyword in text_lower for keyword in self.CRITICAL_KEYWORDS):
            return True

        # Check length
        if len(text) > 80:
            return True

        # Check jika ada tanda soalan kompleks
        if '?' in text and text.count(' ') > 8:
            return True

        return False

    # ==================== MESSAGE SPLITTING FUNCTIONS ====================
    def _split_for_critical_mode(self, text):
        """Split untuk MODE KRITIKAL: max 4 lines, dengan word boundaries yang baik"""
        if not text:
            return ["..."]

        text = text.strip()

        # Jika cukup pendek, return 1 line
        if len(text) <= 175:
            return [text]

        print(f"📊 KRITIKAL MODE SPLITTING: {len(text)} chars")

        # ⭐⭐⭐ IMPROVED SPLITTING ⭐⭐⭐
        lines = []
        current_line = ""
        words = text.split()

        for i, word in enumerate(words):
            # Check jika tambah word ini akan exceed limit
            test_length = len(current_line) + len(word) + (1 if current_line else 0)

            if test_length <= 175:
                # Masih muat dalam line semasa
                current_line = f"{current_line} {word}" if current_line else word
            else:
                # Line dah penuh, simpan dan start baru
                if current_line:
                    lines.append(current_line)

                # Start new line dengan current word
                current_line = word

                # Check jika dah capai max lines (4)
                if len(lines) >= 4:
                    break

        # Add last line jika belum capai limit
        if current_line and len(lines) < 4:
            lines.append(current_line)

        # ⭐⭐⭐ FIX: Jika ada baki words yang tak muat ⭐⭐⭐
        if len(lines) == 4 and current_line != words[-1]:
            # Ada baki text yang tak muat
            # Cari last space dalam line ke-4 untuk split yang natural
            last_line = lines[3]
            if len(last_line) > 160:  # Jika hampir penuh
                # Cari last natural break point
                last_space = last_line.rfind(' ')
                if last_space > 140:  # Jika jumpa space yang ok
                    # Split line ke-4
                    lines[3] = last_line[:last_space]
                    # Baki text (jika ada) akan hilang atau...
                    # Boleh tambah "..." jika nak indicate ada continuation
                    if not lines[3].endswith(('.', '!', '?', '...')):
                        lines[3] += '...'

        print(f"📊 Split into {len(lines)} lines")
        return lines[:4]

    def _split_for_normal_mode(self, text):
        """Split untuk MODE BIASA: max 2 lines"""
        if not text:
            return ["..."]

        text = text.strip()

        if len(text) <= 120:
            return [text]

        # Try to split at natural points
        mid = len(text) // 2

        # Cari punctuation
        for i in range(mid, len(text)):
            if text[i] in '.!?;,':
                line1 = text[:i+1].strip()
                line2 = text[i+1:].strip()
                if line1 and line2:
                    return [line1, line2]

        # Cari space
        for i in range(mid, len(text)):
            if text[i] == ' ':
                line1 = text[:i].strip()
                line2 = text[i+1:].strip()
                if line1 and line2:
                    return [line1, line2]

        # Force split
        return [text[:mid].strip(), text[mid:].strip()]

    def update_stats(self, stat_name, increment=1):
        """Update statistics counter"""
        # Jika key tidak wujud, create dulu
        if stat_name not in self.stats:
            self.stats[stat_name] = 0

        self.stats[stat_name] += increment

    # Atau dalam __init__, tambah semua potential stats keys:
    POTENTIAL_STATS = [
        'messages_processed', 'messages_received', 'commands_processed',
        'ai_queries', 'errors', 'maideen_replies', 'ignored_messages',
        'ping_requests', 'weather_queries', 'prayer_queries',
        'connections', 'reconnects', 'timeouts', 'api_calls',
        'critical_questions', 'normal_questions', 'jokes_told',
    ]

    def print_stats(self):
        """Print current statistics"""
        print("\n📊 CURRENT STATISTICS:")
        print("-" * 40)
        for stat, value in self.stats.items():
            print(f"  {stat.replace('_', ' ').title()}: {value}")
        print("-" * 40)
    
    # ==================== HELPER FUNCTIONS ====================
    def should_ignore(self, nick):
        """Check jika nick perlu diignore"""
        nick_lower = nick.lower().strip('@+%&~')  # Remove IRC prefixes
        return nick_lower in self.IGNORED_BOTS

    def toggle_ignore_bot(self, nick, args):
        """Toggle ignore untuk bot tertentu"""
        if not args:
            bot_list = ", ".join(sorted(self.IGNORED_BOTS))
            return f"{nick}: Bots diignore: {bot_list}"

        bot_name = args.strip().lower()

        if bot_name in self.IGNORED_BOTS:
            self.IGNORED_BOTS.remove(bot_name)
            return f"{nick}: ✅ Bot '{bot_name}' dikeluarkan dari ignore list"
        else:
            self.IGNORED_BOTS.add(bot_name)
            return f"{nick}: ✅ Bot '{bot_name}' ditambah ke ignore list"

    def show_help(self, nick):
        """Show help message"""
        help_msg = f"""{nick}: **BOT WWW & MAIDEEN HELP** 🚀

**Commands:**
!prompts <message>  - Chat dengan WWW bot
!help / !bantuan    - Tunjukkan mesej ini
!status             - Check bot status
!ignorebot <name>   - Toggle ignore bot

**Alias support:** !backuprompt, !bprompt, !setprompt (semua sama)

**Auto-features:**
• Maideen auto-reply dengan lawak 1 line
• Auto-ignore bots dalam IGNORED_BOTS list
• Format strict: YES X → message → ACTION:

Contoh: !prompts apa khabar?
"""
        return help_msg

    # Note: Functions lain seperti query_groq_ai, parse_ai_output, 
    # process_message, dll akan ditambah selepas __init__

        # Show prompt summary
        if self.prompt:
            lines = self.prompt.split('\n')
            non_empty = [line for line in lines if line.strip()]
            print(f"🔧 PROMPT: {len(non_empty)} lines loaded")
            print(f"🔧 PROMPT PREVIEW:")
            for i, line in enumerate(non_empty[:5], 1):
                print(f"   {i:2d}. {line[:70]}..." if len(line) > 70 else f"   {i:2d}. {line}")
            if len(non_empty) > 5:
                print(f"   ... and {len(non_empty)-5} more lines")
        else:
            print("⚠️  NO PROMPT LOADED!")

        print("="*70)

        for channel in CHANNELS:
            self.last_solat_notif[channel] = {}
            self.joined_channels.add(channel)

        # Messages
        self.cap_ayam_messages = [
            "Quantum sweet processing activated 🍬⚛️",
            "Candy-coated latency measurement 🍭📡",
            "Sweet fiber network routing 🍫🌐",
            "Sugar-powered quantum computation 🍡🧠",
            "Caramel latency optimization 🍯⚡",
            "Chocolate hyperspeed achieved 🍫🚀",
            "Gummy bear network confirmed 🐻🌌",
            "Lollipop routing excellence 🍭🎯",
            "Cotton candy cloud computing 🍬☁️",
            "WWW neural network computed 🧁🧠"
        ]

        self.greeting_responses = []

        # Stats
        self.stats = {
            'pings_processed': 0,
            'ai_responses': 0,
            'help_responses': 0,
            'greeting_responses': 0,
            'weather_requests': 0,
            'prayer_requests': 0,
            'auto_quotes': 0,
            'errors': 0,
            'kicks': 0,
            'rejoins': 0,
            'messages_received': 0,
            'start_time': time.time()
        }

        print("="*70)
        print(f"🤖 WWW BOT COMBINED - ALL FEATURES")
        print("="*70)
        print(f"🔧 NICK: {self.nick}")
        print(f"🔧 SERVER: {SERVER}:{PORT}")
        print(f"🔧 CHANNELS: {', '.join(CHANNELS)}")
        print(f"🔧 WEATHER: Global support via geocoding")
        print(f"🔧 SOLAT: Malaysia with proper zone mapping")
        print(f"🔧 PING: CTCP with sweet messages")
        print(f"🔧 AI: Groq LLM with smart detection")
        print(f"🔧 AUTO: Hourly weather + 15min quotes")
        print("="*70)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{timestamp} {message}")

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def get_time_pretty(self):
        now = datetime.now()
        hour_12 = now.strftime("%I").lstrip("0") or "12"
        minute = now.strftime("%M")
        second = now.strftime("%S")
        am_pm = now.strftime("%p").lower()
        return f"{hour_12}:{minute}:{second}{am_pm}"

    # ========== TAMBAH FUNCTIONS BARU DALAM CLASS ==========

    def process_message(self, nick, message, channel=None):
        """Process message - DENGAN LENGTH LIMIT"""
        try:
            # self.log(f"🔍 Processing: {nick} -> '{message[:50]}...'")

            # ⭐⭐⭐ REJECT MESSAGES > 200 CHARACTERS ⭐⭐⭐
            if len(message) > 200:
                self.log(f"🚫 Message too long from {nick}: {len(message)} chars")
                return None

            # ⭐⭐⭐ REJECT MESSAGES DENGAN BANYAK LINES ⭐⭐⭐
            newline_count = message.count('\n')
            if newline_count > 2:
                self.log("🚫 Too many lines from {}: {} lines".format(nick, newline_count))
                return None

            # ⭐⭐⭐ IMPORT THREADING DALAM FUNCTION ⭐⭐⭐
            import threading
            import time
            import random
            import re

            # ⭐⭐⭐ SKIP SEMUA MESSAGES 75 SAAT PERTAMA ⭐⭐⭐
            JOIN_GRACE_PERIOD = 75  # 75 saat

            if hasattr(self, '_channel_joins') and channel:
                join_time = self._channel_joins.get(channel, 0)
                if join_time > 0:
                    time_since_join = time.time() - join_time
                    if time_since_join < JOIN_GRACE_PERIOD:
                        self.log(f"⏳ Channel grace period: {channel} ({time_since_join:.1f}s/{JOIN_GRACE_PERIOD}s)")
                        return None

            # ⭐⭐⭐ TAMBAH PROTECTION FLAG ⭐⭐⭐
            msg_key = f"{nick}:{channel}:{message[:50]}"
            current_time = time.time()

            if not hasattr(self, '_processing_messages'):
                self._processing_messages = {}

            if msg_key in self._processing_messages:
                if current_time - self._processing_messages[msg_key] < 3:
                    self.log(f"🚫 Skipping duplicate processing: {msg_key[:50]}")
                    return None

            self._processing_messages[msg_key] = current_time

            # Clean up old entries
            for key in list(self._processing_messages.keys()):
                if current_time - self._processing_messages[key] > 30:
                    del self._processing_messages[key]

            # Repeat spam check
            if self.is_repeat_spam(nick, message, channel):
                self.log(f"🚫 Repeat spam blocked: {nick}")
                return None

            self.update_stats('messages_processed')

            # Ignore bots
            if self.should_ignore(nick):
                self.update_stats('ignored_messages')
                return None

            responses = []

            # ⭐⭐ MENTION CHECK - COMPREHENSIVE ⭐⭐
            message_lower = message.lower().strip()
            words = message_lower.split()

            self.log(f"🔍 Words: {words}")
            self.log(f"🔍 Word count: {len(words)}")

            # Pattern 1: "www" sahaja
            if message_lower == 'www':
                self.log(f"✅ Exact single word 'www'")
                threading.Thread(
                    target=self.handle_ai_request,
                    args=(nick, channel, "hello"),
                    daemon=True
                ).start()
                return None

            # Pattern 2: "@www" sahaja
            elif message_lower == '@www':
                self.log(f"✅ Exact single word '@www'")
                threading.Thread(
                    target=self.handle_ai_request,
                    args=(nick, channel, "hello"),
                    daemon=True
                ).start()
                return None

            # Pattern 3: Ada "www" sebagai standalone word
            for i, word in enumerate(words):
                clean_word = re.sub(r'\x03\d{0,2}(,\d{0,2})?', '', word)
                clean_word = re.sub(r'[\x00-\x1F\x7F]', '', clean_word)

                if clean_word in ['www', '@www']:
                    self.log(f"✅ Found 'www' as word #{i+1}: '{word}'")

                    if i == len(words) - 1:
                        before_www = ' '.join(words[:i])
                        ai_text = before_www if before_www else "hello"
                    else:
                        after_www = ' '.join(words[i+1:])
                        ai_text = after_www if after_www else "hello"

                    threading.Thread(
                        target=self.handle_ai_request,
                        args=(nick, channel, ai_text),
                        daemon=True
                    ).start()
                    return None

            # Pattern 4: "www:" atau "www,"
            for word in words:
                clean_word = re.sub(r'\x03\d{0,2}(,\d{0,2})?', '', word)
                clean_word = re.sub(r'[\x00-\x1F\x7F]', '', clean_word)

                if clean_word.startswith('www:') or clean_word.startswith('www,'):
                    self.log(f"✅ Found 'www:' or 'www,' word: '{word}'")
                    if ':' in clean_word:
                        text = clean_word.split(':', 1)[1]
                    elif ',' in clean_word:
                        text = clean_word.split(',', 1)[1]
                    else:
                        text = ""

                    ai_text = text if text else "hello"
                    threading.Thread(
                        target=self.handle_ai_request,
                        args=(nick, channel, ai_text),
                        daemon=True
                    ).start()
                    return None

            # Pattern 5: "@www" sebagai part of word
            for word in words:
                clean_word = re.sub(r'\x03\d{0,2}(,\d{0,2})?', '', word)
                clean_word = re.sub(r'[\x00-\x1F\x7F]', '', clean_word)

                if clean_word.startswith('@www'):
                    self.log(f"✅ Found '@www' word: '{word}'")
                    if ':' in clean_word:
                        text = clean_word.split(':', 1)[1]
                    elif ',' in clean_word:
                        text = clean_word.split(',', 1)[1]
                    elif len(clean_word) > 4:
                        text = clean_word[4:]
                    else:
                        text = ""

                    ai_text = text if text else "hello"
                    threading.Thread(
                        target=self.handle_ai_request,
                        args=(nick, channel, ai_text),
                        daemon=True
                    ).start()
                    return None

            # Pattern 6: Commands dengan !
            if message.startswith('!'):
                parts = message[1:].split(' ', 1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                self.log(f"🔍 Command detected: {cmd}")

                # AI commands
                ai_commands = ['prompts', 'ai', 'backuprompt', 'bprompt', 'setprompt', 'prompt']
                if cmd in ai_commands:
                    self.log(f"✅ AI command: {cmd}")
                    threading.Thread(
                        target=self.handle_ai_request,
                        args=(nick, channel, args if args else "hello"),
                        daemon=True
                    ).start()
                    return None

                # Other commands
                handler = self.COMMAND_ALIASES.get(cmd)
                if handler:
                    response = handler(nick, args)
                    if response:
                        responses.append(('www', response))
                        self.update_stats('commands_processed')

            # Maideen auto-reply
            elif 'maideen' in message_lower:
                if random.random() < 0.7:
                    if not self.is_repeat_spam(nick, f"maideen:{message}", channel):
                        maideen_reply = self.maideen.generate_reply(message, nick)
                        responses.append(('maideen', maideen_reply))
                        self.update_stats('maideen_replies')

            # Jika ada responses, return
            if responses:
                return responses
            else:
                return None

        except Exception as e:
            self.log(f"❌ process_message error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def is_proper_mention(self, message):
        """Check jika message benar-benar mention bot (elak false positive)"""
        import re

        message_lower = message.lower()
        bot_nick = self.nick.lower()  # "www"

        # ⭐⭐ LIST FALSE POSITIVES ⭐⭐
        # Words yang mengandungi "www" tapi bukan mention
        false_positives = [
            'wowww', 'swww', 'twww', 'awww', 'ewww', 'owww',
            'wwws', 'wwww', 'wwwe', 'wwwa', 'wwwt', 'wwwl',
            'ywww', 'kwww', 'mwww', 'nwww', 'pwww'
        ]

        # Check untuk false positives
        for fp in false_positives:
            if fp in message_lower:
                return False

        # ⭐⭐ VALID MENTION PATTERNS ⭐⭐
        patterns = [
            # @www atau @WWW
            r'@' + re.escape(bot_nick) + r'(\s|$|[:,!?])',

            # www: atau www, (dengan punctuation)
            r'\b' + re.escape(bot_nick) + r'[:,](\s|$)',

            # www dengan spaces (sebagai word)
            r'(\s|^)' + re.escape(bot_nick) + r'(\s|$|[:,!?])',

            # www diawal ayat
            r'^' + re.escape(bot_nick) + r'\s+',
        ]

        # Check setiap pattern
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return True

        # Special case: "www" sahaja (exact word)
        if message_lower.strip() == bot_nick:
            return True

        return False
    
    def handle_prompt_command(self, nick, args):
        """Handle prompts command (utama & semua aliases)"""
        self.update_stats('commands_processed')

        if not args:
            return f"{nick}: Syntax: !prompts <message>"

        # Check rate limit
        import time
        current_time = time.time()
        if current_time - self.last_api_call < 1.0:
            return f"{nick}: Slow down bro! Tunggu sikit. ⏳"

        # Get AI response
        ai_response = self.query_groq_ai(args, nick)

        # Parse response untuk format
        decision, regular_lines, action_lines = self.parse_ai_output(ai_response)

        # Format response untuk return
        if regular_lines:
            # Build response string
            response_lines = [f"{nick}: {regular_lines[0]}"]
            for line in regular_lines[1:]:
                response_lines.append(line)

            if action_lines:
                response_lines.append(f"ACTION: {action_lines[0]}")

            return "\n".join(response_lines)

        return f"{nick}: {ai_response}"  # Fallback
    
    def split_into_sentences(self, text):
        """Split text kepada sentences secara natural - FIXED VERSION"""
        import re

        if not text or len(text) < 20:
            return [text] if text else []

        text = text.strip()

        # Strategy 1: Split pada natural sentence boundaries
        sentences = []
        current = ""

        for i, char in enumerate(text):
            current += char

            # Check untuk end of sentence
            if char in '.!?':
                # Ensure bukan abbreviation atau decimal
                if i > 0 and text[i-1].isdigit():
                    # Decimal number seperti "1.5", "2.3"
                    continue

                # Check jika ada space selepas atau end of string
                if i == len(text) - 1 or text[i+1] in ' \t\n':
                    # Ini adalah end of sentence sebenar
                    if len(current.strip()) > 15:  # Minimum length
                        sentences.append(current.strip())
                        current = ""

        # Add any remaining text
        if current.strip():
            sentences.append(current.strip())

        # Strategy 2: Jika tak jumpa sentences, split pada comma atau semicolon
        if len(sentences) <= 1 and len(text) > 150:
            sentences = []
            current = ""

            for char in text:
                current += char

                if char in ',;:' and len(current) > 50:
                    sentences.append(current.strip())
                    current = ""

            if current.strip():
                sentences.append(current.strip())

        # Strategy 3: Jika masih satu piece, split by length dengan word boundaries
        if len(sentences) <= 1 and len(text) > 120:
            words = text.split()
            sentences = []
            current_sentence = ""

            for word in words:
                if len(current_sentence) + len(word) + 1 <= 120:
                    if current_sentence:
                        current_sentence += " " + word
                    else:
                        current_sentence = word
                else:
                    if current_sentence:
                        sentences.append(current_sentence)
                    current_sentence = word

            if current_sentence:
                sentences.append(current_sentence)

        # Clean up: remove empty, ensure min length
        sentences = [s for s in sentences if s and len(s) > 10]

        # Jika masih kosong, return original
        if not sentences:
            return [text[:150] + "..." if len(text) > 150 else text]

        return sentences

    def send_notepad_full_slow(self, channel, nick, lines):
        """Send notepad FULL LENGTH dengan slow reading (5 saat delay)"""
        try:
            self.send(channel, f"📖 {nick}: MEMBACA NOTEPAD ({len(lines)} entries)...")
            time.sleep(3)

            max_entries = min(5, len(lines))

            for i in range(max_entries):
                original_line = lines[i]
                if not original_line:
                    continue

                line = original_line
                if len(line) > 3 and line[0].isdigit() and line[1] == '.' and line[2] == ' ':
                    line = line[3:]

                line = ' '.join(line.split())

                # Jika panjang, split kepada sentences
                if len(line) > 250:
                    sentences = self.split_into_sentences(line)

                    if len(sentences) > 1:
                        self.send(channel, f"📖 {nick}: Entry {i+1}/{max_entries}:")
                        time.sleep(2)

                        for j, sentence in enumerate(sentences):
                            if sentence.strip():
                                prefix = f"  {i+1}.{j+1} "
                                self.send(channel, prefix + sentence.strip())

                                # ⏱️ DELAY 5 SAAT
                                if j < len(sentences) - 1:
                                    time.sleep(5)

                        if i < max_entries - 1:
                            time.sleep(5)
                        continue

                # Line biasa
                prefix = f"📖 {nick}: [{i+1}/{max_entries}] "
                self.send(channel, prefix + line)

                # ⏱️ DELAY 5 SAAT
                if i < max_entries - 1:
                    time.sleep(5)

            time.sleep(3)
            if len(lines) > max_entries:
                remaining = len(lines) - max_entries
                self.send(channel, f"📖 {nick}: ... dan {remaining} entries lagi.")
            else:
                self.send(channel, f"📖 {nick}: Tamat membaca. 📚✨")

        except Exception as e:
            self.send(channel, f"❌ {nick}: Error: {str(e)}")

    def handle_read_notepad_full(self, nick, channel):
        """Handle !read notepad.txt full (FULL LENGTH)"""
        try:
            if not os.path.exists(KNOWLEDGE_FILE):
                return [f"❌ {nick}: File notepad.txt tidak ditemukan."]

            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]

            if not lines:
                return [f"📄 {nick}: notepad.txt kosong."]

            import threading
            thread = threading.Thread(
                target=self.send_notepad_full_slow,
                args=(channel, nick, lines)
            )
            thread.daemon = True
            thread.start()

            return None

        except Exception as e:
            return [f"❌ {nick}: Error: {str(e)}"]

    def handle_read_notepad_short(self, nick, channel):
        """Handle !read notepad.txt (SHORT VERSION)"""
        try:
            if not os.path.exists(KNOWLEDGE_FILE):
                return [f"❌ {nick}: File notepad.txt tidak ditemukan."]

            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]

            if not lines:
                return [f"📄 {nick}: notepad.txt kosong."]

            import threading
            thread = threading.Thread(
                target=self.send_notepad_with_delay,  # ⬅️ Fungsi yang sedia ada
                args=(channel, nick, lines)
            )
            thread.daemon = True
            thread.start()

            return None

        except Exception as e:
            return [f"❌ {nick}: Error: {str(e)}"]

    def should_inject_knowledge(self, message):
        """Check jika soalan perlu knowledge base"""
        message_lower = message.lower()

        keywords_for_kb = [
            'mirc', 'irc', 'kampungchat', 'server', 'port',
            'nick', 'identify', 'register', 'channel', 'mode',
            'ctcp', 'ping', 'action', 'script', 'bot',
            'cuaca', 'solat', 'waktu', 'command', 'syntax'
        ]

        return any(keyword in message_lower for keyword in keywords_for_kb)

    def handle_read_notepad(self, nick, channel):
        """Handle !read notepad.txt DENGAN DELAY"""
        try:
            if not os.path.exists(KNOWLEDGE_FILE):
                return [f"❌ {nick}: File notepad.txt tidak ditemukan."]

            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]

            if not lines:
                return [f"📄 {nick}: notepad.txt kosong."]

            # ⚠️ JANGAN return list (kita akan handle dalam thread)
            # Start dalam thread supaya tak block bot main thread
            import threading
            thread = threading.Thread(
                target=self.send_notepad_with_delay,
                args=(channel, nick, lines)
            )
            thread.daemon = True
            thread.start()

            return None  # Jangan return apa-apa

        except Exception as e:
            return [f"❌ {nick}: Error membaca file: {str(e)}"]

    def send_notepad_with_delay(self, channel, nick, lines):
        """Send notepad content - SUPER SIMPLE"""
        try:
            self.send(channel, f"📚 {nick}: notepad.txt ({len(lines)} entries):")
            time.sleep(1.5)

            max_lines = min(8, len(lines))

            for i in range(max_lines):
                line = lines[i]
                if line:
                    # ✅ Remove numbering "1. ", "2. ", etc
                    if len(line) > 3 and line[0].isdigit() and line[1] == '.' and line[2] == ' ':
                        line = line[3:]

                    # ✅ Fixed length + ellipsis
                    if len(line) > 65:
                        line = line[:65] + "..."

                    prefix = f"[{i+1}/{max_lines}] "
                    self.send(channel, prefix + line)

                    if i < max_lines - 1:
                        time.sleep(2)

            if len(lines) > max_lines:
                time.sleep(1)
                remaining = len(lines) - max_lines
                self.send(channel, f"📚 {nick}: ... dan {remaining} entries lagi.")

        except Exception as e:
            self.send(channel, f"❌ {nick}: Error: {str(e)}")

    def load_prompt(self):
        """Load ALL lines from prompt.txt - NO LIMIT"""
        prompt_text = ""
        try:
            if os.path.exists(PROMPT_FILE):
                print(f"📝 Reading prompt file: {PROMPT_FILE}")

                # Read ALL content
                with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
                    prompt_text = f.read().strip()

                # Count lines
                lines = [line.strip() for line in prompt_text.split('\n') if line.strip()]
                non_comment_lines = [line for line in lines if not line.startswith('#')]

                print(f"   Total lines: {len(lines)}")
                print(f"   Non-comment lines: {len(non_comment_lines)}")
                print(f"   File size: {len(prompt_text)} characters")

                if not prompt_text:
                    print("⚠️  Prompt file is empty, using default")
                    prompt_text = self.create_default_prompt()

            else:
                print(f"❌ {PROMPT_FILE} not found, creating with your WWW PERSONALITY")
                prompt_text = """# WWW PERSONALITY - PEMBERI HIKMAH
ANDA WWW - PEMBERI HIKMAH DAN PENASIHAT
Anda adalah WWW, pemberi hikmah dan nasihat bijaksana di IRC.
Gunakan Bahasa Malaysia beradat, lembut dan penuh hormat.
Berikan nasihat kehidupan, syair, kata-kata hikmah.
Gunakan gaya bahasa yang indah, puitis dan bermakna.
Fokus pada pengajaran hidup dan kebijaksanaan.
Jawab dalam 1-2 baris sahaja. MAX 150 karakter.
Gunakan emoji sederhana: 🌿 (alam), ✨ (hikmah), 🙏 (syukur), 💎 (nilai).

FORMAT WAJIB:
<DECISION>YES/NO</DECISION>
<RESPONSE>nasihat bijaksana anda di sini</RESPONSE>

CONTOH:
<DECISION>YES</DECISION>
<RESPONSE>Kesabaran itu kunci kebahagiaan. 🌿</RESPONSE>"""

                with open(PROMPT_FILE, 'w', encoding='utf-8') as f:
                    f.write(prompt_text)

                print("✅ Created prompt.txt with WWW PERSONALITY")

            return prompt_text

        except Exception as e:
            print(f"❌ Error loading prompt: {e}")
            import traceback
            traceback.print_exc()
            return self.create_default_prompt()

    def create_default_prompt(self):
        """Create default prompt jika ada error"""
        return """ANDA WWW - PEMBERI HIKMAH DAN PENASIHAT
Anda adalah WWW, pemberi hikmah dan nasihat bijaksana di IRC.
Gunakan Bahasa Malaysia beradat, lembut dan penuh hormat.
Berikan nasihat kehidupan, syair, kata-kata hikmah.
FORMAT: <DECISION>YES/NO</DECISION><RESPONSE>nasihat anda</RESPONSE>"""

    def load_knowledge(self):
        """Load knowledge from notepad.txt"""
        knowledge = []
        try:
            if os.path.exists(KNOWLEDGE_FILE):
                with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
                    knowledge = [line.strip() for line in f if line.strip()]

                self.log(f"📚 Loaded {len(knowledge)} lines from {KNOWLEDGE_FILE}")
            else:
                self.log(f"⚠️ {KNOWLEDGE_FILE} not found, creating default")
                with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
                    f.write("mIRC adalah program chatting popular untuk IRC.\n")
                knowledge = ["mIRC adalah program chatting popular untuk IRC."]
        except Exception as e:
            self.log(f"❌ Error loading knowledge: {e}")
            knowledge = ["Error loading knowledge base."]

        return knowledge

    def search_knowledge(self, query):
        """Search knowledge base untuk relevant info"""
        try:
            if not hasattr(self, 'knowledge_base') or not self.knowledge_base:
                return []

            query_lower = query.lower().strip()

            # Jika query terlalu pendek
            if len(query_lower) < 2:
                return []

            results = []

            for line in self.knowledge_base:
                line_lower = line.lower()

                # Simple matching - check jika query words ada dalam line
                query_words = query_lower.split()
                match_score = 0

                for word in query_words:
                    if len(word) >= 3:  # Ignore short words
                        if word in line_lower:
                            match_score += 1
                        # Bonus untuk exact phrase match
                        if query_lower in line_lower:
                            match_score += 3

                if match_score > 0:
                    results.append((match_score, line))

            # Sort by match score
            results.sort(key=lambda x: x[0], reverse=True)

            # Return top 3 results
            return [line for score, line in results[:3]]

        except Exception as e:
            print(f"❌ Knowledge search error: {e}")
            return []

    def read_and_send_with_delay(self, channel, filename, nick, delay=2):
        """Baca file dan send dengan delay antara lines"""
        try:
            if not os.path.exists(filename):
                return [f"❌ {nick}: File '{filename}' tidak ditemukan."]

            with open(filename, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]

            if not lines:
                return [f"📄 {nick}: File '{filename}' kosong."]

            # Kirim info dulu
            self.send(channel, f"📄 {nick}: File '{filename}' ({len(lines)} baris):")
            time.sleep(1)

            # Kirim lines dengan DELAY
            for i, line in enumerate(lines[:10]):  # Max 10 baris
                if line:
                    # Format: [1/10] line content
                    prefix = f"[{i+1}/{min(10, len(lines))}] "
                    self.send(channel, prefix + (line[:80] + "..." if len(line) > 80 else line))

                    # DELAY antara lines (kecuali last line)
                    if i < min(9, len(lines)-1):  # 0-8 (9 lines)
                        time.sleep(delay)  # ⏱️ DELAY 2 SAAT

            # Jika ada lebih dari 10 lines, beritahu
            if len(lines) > 10:
                time.sleep(1)
                self.send(channel, f"📄 {nick}: ... dan {len(lines)-10} baris lagi. Gunakan .find untuk search.")

            return True

        except Exception as e:
            self.send(channel, f"❌ {nick}: Error: {str(e)}")
            return False

    # ========== NOTEPAD UNLIMITED READING FUNCTIONS ==========

    def handle_read_all_notepad(self, nick, channel):
        """Handle !readall - baca SEMUA entries berterusan"""
        try:
            if not os.path.exists(KNOWLEDGE_FILE):
                return [f"❌ {nick}: File notepad.txt tidak ditemukan."]

            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as file:
                all_lines = [line.strip() for line in file if line.strip()]

            if not all_lines:
                return [f"📄 {nick}: notepad.txt kosong."]

            # Start dalam thread untuk baca SEMUA
            import threading
            thread = threading.Thread(
                target=self.send_all_notepad_continuous,
                args=(channel, nick, all_lines)
            )
            thread.daemon = True
            thread.start()

            return [f"📚 {nick}: MEMBACA SEMUA {len(all_lines)} ENTRIES BERTERUSAN..."]

        except Exception as e:
            return [f"❌ {nick}: Error: {str(e)}"]

    def send_all_notepad_continuous(self, channel, nick, all_lines):
        """Baca SEMUA entries berterusan dengan delay"""
        try:
            total_entries = len(all_lines)

            self.send(channel, f"📚 {nick}: MEMULAKAN PEMBACAAN {total_entries} ENTRIES...")
            time.sleep(2)

            for i, original_line in enumerate(all_lines):
                line = original_line

                # Remove numbering "1. ", "2. ", etc
                if len(line) > 3 and line[0].isdigit() and line[1] == '.' and line[2] == ' ':
                    line = line[3:]

                # Clean line
                line = ' '.join(line.split())
                entry_num = i + 1

                # Progress indicator setiap 5 entries
                if entry_num % 5 == 0:
                    progress = (entry_num * 100) // total_entries
                    self.send(channel, f"📚 {nick}: Progress: {progress}% ({entry_num}/{total_entries})...")
                    time.sleep(2)

                # Jika line panjang, truncate
                if len(line) > 200:
                    # Cari natural break point
                    trunc_pos = 200
                    for pos in range(200, 180, -1):
                        if pos < len(line) and line[pos] in '.!?;,':
                            trunc_pos = pos + 1
                            break

                    line = line[:trunc_pos]
                    if not line.endswith(('...', '.', '!', '?')):
                        line += '...'

                # Send entry
                self.send(channel, f"[{entry_num}] {line}")

                # ⏱️ DELAY 5 SAAT antara entries (kecuali entry terakhir)
                if entry_num < total_entries:
                    time.sleep(5)

            # Tamat
            time.sleep(2)
            self.send(channel, f"📚 {nick}: ✅ TAMAT MEMBACA {total_entries} ENTRIES! 📖✨")

        except Exception as e:
            self.send(channel, f"❌ {nick}: Error: {str(e)}")

    def handle_read_from(self, nick, channel, start_entry):
        """Handle !readfrom X - baca dari entry X hingga akhir"""
        try:
            if not os.path.exists(KNOWLEDGE_FILE):
                return [f"❌ {nick}: File notepad.txt tidak ditemukan."]

            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as file:
                all_lines = [line.strip() for line in file if line.strip()]

            if not all_lines:
                return [f"📄 {nick}: notepad.txt kosong."]

            # Validate start entry
            if start_entry < 1:
                start_entry = 1
            if start_entry > len(all_lines):
                return [f"📄 {nick}: Entry {start_entry} tidak wujud. Hanya ada {len(all_lines)} entries."]

            start_idx = start_entry - 1
            lines_to_read = all_lines[start_idx:]

            # Start thread
            import threading
            thread = threading.Thread(
                target=self.send_from_entry_continuous,
                args=(channel, nick, lines_to_read, start_entry)
            )
            thread.daemon = True
            thread.start()

            return [f"📚 {nick}: MEMBACA DARI ENTRY {start_entry} ({len(lines_to_read)} entries)..."]

        except Exception as e:  # ⚠️ INI YANG HILANG!
            return [f"❌ {nick}: Error: {str(e)}"]

    def send_from_entry_continuous(self, channel, nick, lines, start_num):
        """Baca dari entry tertentu - SPLIT JIKA PANJANG"""
        try:
            total_to_read = len(lines)
            self.send(channel, f"📚 {nick}: MEMBACA {total_to_read} ENTRIES DARI #{start_num}...")
            time.sleep(2)

            for i, original_line in enumerate(lines):
                line = original_line

                # Remove numbering
                if len(line) > 3 and line[0].isdigit() and line[1] == '.' and line[2] == ' ':
                    line = line[3:]

                line = ' '.join(line.split())
                entry_num = start_num + i

                # ✅ JIKA SANGAT PANJANG, SPLIT KE MULTIPLE MESSAGES
                if len(line) > 200:
                    # Split kepada sentences
                    sentences = self.split_into_sentences(line)

                    if len(sentences) > 1:
                        # Send first sentence dengan entry number
                        self.send(channel, f"[{entry_num}] {sentences[0]}")
                        time.sleep(1)

                        # Send remaining sentences
                        for j in range(1, min(3, len(sentences))):  # Max 3 sentences
                            self.send(channel, f"   {sentences[j][:120]}...")
                            if j < min(3, len(sentences)) - 1:
                                time.sleep(3)
                    else:
                        # Fallback: truncate
                        self.send(channel, f"[{entry_num}] {line[:180]}...")
                else:
                    # Line pendek, send terus
                    self.send(channel, f"[{entry_num}] {line}")

                # ⏱️ DELAY 5 SAAT antara entries
                if i < len(lines) - 1:
                    time.sleep(5)

            # Tamat
            time.sleep(2)
            self.send(channel, f"📚 {nick}: ✅ TAMAT MEMBACA {total_to_read} ENTRIES! 📖")

        except Exception as e:
            self.send(channel, f"❌ {nick}: Error: {str(e)}")

    def send_raw(self, msg):
        if self.sock:
            try:
                self.sock.send(f"{msg}\r\n".encode())
                return True
            except Exception as e:
                self.log(f"❌ Send error: {e}")
                self.stats['errors'] += 1
                return False
        return False

    def send(self, target, msg):
        """Kirim message ke channel"""
        if len(msg) > MAX_MESSAGE_LENGTH:
            msg = msg[:MAX_MESSAGE_LENGTH-3] + "..."
        self.send_raw(f"PRIVMSG {target} :{msg}")

    # TAMBAH METHOD INI JIKA BELUM ADA
    def send_action(self, target, action_text):
        """Kirim CTCP ACTION (/me) ke target"""
        return self.send_raw(f"PRIVMSG {target} :\x01ACTION {action_text}\x01")

    def send_multiple(self, target, lines):
        """Kirim semua line dalam list"""
        for i, line in enumerate(lines[:3]):
            if line.strip():
                self.send(target, line)
                if i < len(lines[:3]) - 1:
                    time.sleep(1.5)

    def wait_for_motd(self, timeout=30):
        """Tunggu sampai MOTD selesai"""
        self.log("⏳ Waiting for MOTD...")
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
                                    self.log("✅ MOTD received!")
                                    self.motd_received = True
                                    return True
            except:
                pass

        self.log("❌ Timeout waiting for MOTD")
        return False

    def connect(self):
        """Main connect method - MODE -T SUDAH DIHANTAR DALAM connect_to_server()"""
        if self.connect_to_server():  # ⭐ MODE -T sudah dihantar di sini
            if self.wait_for_motd():
                self.identify()
                time.sleep(3)
                self.join_channels()
                # ⭐ JANGAN hantar MODE -T lagi di sini (sudah dihantar)
                self.connected = True
                return True
        return False
    
    def connect_to_server(self):
        """Connect ke server"""
        try:
            self.log(f"🔗 Connecting to {SERVER}:{PORT}...")

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            self.sock.connect((SERVER, PORT))

            # Send registration
            self.log(f"📤 Registering as {self.nick}...")
            self.send_raw(f"NICK {self.nick}")
            self.send_raw(f"USER {IDENT} 0 * :{REALNAME}")

            return True

        except Exception as e:
            self.log(f"❌ Connection error: {e}")
            if self.sock:
                self.sock.close()
                self.sock = None
            return False

    def identify(self):
        """Identify dengan NickServ"""
        if self.password:
            self.log("🔑 Identifying to NickServ...")
            identify_cmd = f"PRIVMSG NickServ :IDENTIFY {self.password}"
            self.send_raw(identify_cmd)
            time.sleep(2)  # Kurangkan dari 3 ke 2 saat

        # ⭐⭐⭐ LETAK DI SINI - SELEPAS SERVER KENAL NICK ANDA ⭐⭐⭐
        self.log("🚨 SENDING MODE -T NOW (critical for CTCP)...")
        for i in range(2):  # Hantar 2 kali untuk pastikan
            self.send_raw(f"MODE {self.nick} -T")
            time.sleep(0.5)

        self.log("✅ Mode -T commands sent (CTCP should work now)")

    def join_channels(self):
        """Join semua channels"""
        self.log("📤 Joining channels...")
        for channel in self.joined_channels:
            try:
                self.send_raw(f"JOIN {channel}")
                self.log(f"✅ Joined {channel}")

                # ⭐⭐⭐ RECORD JOIN TIME ⭐⭐⭐
                self._channel_joins[channel] = time.time()
                self.log(f"⏰ Recorded join time for {channel}")

                time.sleep(1.5)  # Delay untuk avoid flood
            except Exception as e:
                self.log(f"❌ Failed to join {channel}: {e}")

    def connect(self):
        """Main connect method"""
        if self.connect_to_server():
            if self.wait_for_motd():
                self.identify()
                time.sleep(3)
                self.join_channels()
                self.send_raw(f"MODE {self.nick} -T")
                self.connected = True
                return True
        return False

    def auto_rejoin(self):
        """Auto-rejoin system"""
        while self.running and self.retry_count < MAX_RETRIES:
            if not self.connected:
                self.log(f"🔄 Attempting to reconnect... (Attempt {self.retry_count + 1}/{MAX_RETRIES})")

                if self.connect_to_server():
                    if self.wait_for_motd():
                        self.identify()
                        time.sleep(3)
                        self.join_channels()
                        self.connected = True
                        self.send_raw(f"MODE {self.nick} -T")
                        self.retry_count = 0

                        # Send welcome message
                        if CHANNELS:
                            self.send(CHANNELS[0], f"🤖 {self.nick} reconnected •")

                        self.log("✅ Reconnected successfully!")
                        return True

                self.retry_count += 1
                self.log(f"⏳ Waiting {RETRY_DELAY} seconds before retry...")
                time.sleep(RETRY_DELAY)

        if self.retry_count >= MAX_RETRIES:
            self.log(f"❌ Max retries reached ({MAX_RETRIES})")
            self.running = False

        return False

    def handle_ping_request(self, nick, channel, hostmask):
        """Handle ping request (from SweetServ)"""
        self.log(f"🎯 Ping from {nick}")

        if nick in self.ping_requests:
            self.send(channel, f"⏳ {nick} - Wait")
            return

        is_znc = False
        if hostmask and ('znc.in' in hostmask.lower() or '/znc' in hostmask.lower()):
            is_znc = True
            self.znc_detected.add(nick)

        if not is_znc and 'znc.in' not in hostmask.lower() and 'znc' not in hostmask.lower():
            # self.send(channel, f"💡 {nick}: /mode {nick} -T")
            time.sleep(1)

        current_time = time.time()

        self.ping_requests[nick] = {
            'tick': current_time,
            'channel': channel,
            'is_znc': is_znc
        }

        ctcp_ping = f"\x01PING {int(current_time * 1000)}\x01"
        self.send_raw(f"PRIVMSG {nick} :{ctcp_ping}")
        self.stats['ping_requests_sent'] = self.stats.get('ping_requests_sent', 0) + 1

        self.log(f"📡 CTCP PING sent to {nick}")
        # self.send(channel, f"📡 Measuring lag for {nick}...")

    def lag_status(self, ms):
        ms_int = int(ms)
        if ms_int <= 100: return "SUPER FAST 💎 Excellent Connection"
        elif ms_int <= 300: return "FAST ⚡ Very good" 
        elif ms_int <= 600: return "NORMAL 🌟 Standard IRC"
        elif ms_int <= 999: return "🌀 Stable"
        elif ms_int <= 2000: return "🌊 Moderate"
        elif ms_int <= 3500: return "⚠️ Lagging"
        elif ms_int <= 5000: return "🛑 Heavy Lag"
        else: return "💀 Timeout"

    def angka_ke_kata(self, number_str):
        digit_to_word = {
            '0': 'kosong', '1': 'satu', '2': 'dua', '3': 'tiga',
            '4': 'empat', '5': 'lima', '6': 'enam', '7': 'tujuh',
            '8': 'lapan', '9': 'sembilan'
        }

        result = []
        for char in number_str:
            if char == '.':
                result.append('perpuluhan • ')
            else:
                result.append(digit_to_word.get(char, char) + ' • ')

        output = ''.join(result).strip()
        if output.endswith('•'):
            output = output[:-1].strip()

        return f"-=₪۩۞{output}۞۩₪=-"

    def handle_ctcp_reply(self, line):
        """Handle CTCP PING reply - FIXED DELETE ISSUE"""
        try:
            # Debug log
            # self.log(f"🔍 CTCP checking line: {line[:100]}...")

            if "NOTICE" in line and self.nick in line and "\x01PING" in line:
                self.log("🎯 CTCP REPLY DETECTED!")

                # Extract nick dari hostmask
                parts = line.split()
                if not parts:
                    return False

                hostmask = parts[0]
                if hostmask.startswith(":"):
                    hostmask = hostmask[1:]

                # Extract nick dari hostmask (format: nick!user@host)
                if "!" in hostmask:
                    nick = hostmask.split("!")[0]
                else:
                    nick = hostmask

                self.log(f"🔍 Extracted nick: {nick}")
                self.log(f"🔍 Current ping_requests keys: {list(self.ping_requests.keys())}")

                # Check jika nick ada dalam ping_requests
                if nick in self.ping_requests:
                    self.log(f"✅ Found {nick} in ping_requests, processing...")

                    data = self.ping_requests[nick]
                    start_time = data['tick']
                    channel = data.get('channel', '#unknown')
                    is_znc = data.get('is_znc', False)

                    end_time = time.time()
                    lag_seconds = end_time - start_time
                    lag_ms = lag_seconds * 1000

                    self.log(f"⏱️ Lag calculation: {lag_seconds:.3f}s ({lag_ms:.1f}ms)")

                    # ⭐⭐⭐ DELETE DARI PING_REQUESTS SEBELUM APA-APA ⭐⭐⭐
                    # Ini penting untuk elak timeout!
                    try:
                        del self.ping_requests[nick]
                        self.log(f"🗑️ DELETED {nick} from ping_requests")
                    except KeyError:
                        self.log(f"⚠️ {nick} already deleted from ping_requests")

                    # Get cap ayam message
                    cap_msg = "Sweet processing 🍬"
                    if hasattr(self, 'cap_ayam_messages') and self.cap_ayam_messages:
                        try:
                            if not hasattr(self, 'message_index'):
                                self.message_index = 0
                            cap_msg = self.cap_ayam_messages[self.message_index % len(self.cap_ayam_messages)]
                            self.message_index = (self.message_index + 1) % len(self.cap_ayam_messages)
                        except:
                            cap_msg = "Network sweet 🍭"

                    # Angka ke kata
                    angka_kata = ""
                    if hasattr(self, 'angka_ke_kata'):
                        try:
                            lag_str = f"{lag_seconds:.3f}"
                            angka_kata = self.angka_ke_kata(lag_str)
                        except:
                            angka_kata = f"{lag_seconds:.3f}s"
                    else:
                        angka_kata = f"{lag_seconds:.3f}s"

                    # Lag status
                    status = "Measured"
                    if hasattr(self, 'lag_status'):
                        try:
                            status = self.lag_status(lag_ms)
                        except:
                            status = f"{lag_ms:.1f}ms"

                    # Build response
                    znc_note = " [ZNC]" if is_znc else ""
                    response = f"• P✸NG • {nick}{znc_note} {lag_seconds:.3f}s ({lag_ms:.1f}ms) {status} ({angka_kata}) \"{cap_msg}\" 🐔Cap(*'∇'*)Ayam🐥🐤"

                    self.log(f"📤 Sending CTCP ACTION: {response[:80]}...")

                    # Send ACTION response
                    self.send_raw(f"PRIVMSG {channel} :\x01ACTION {response}\x01")

                    # Update stats dengan safety check
                    if 'pings_processed' in self.stats:
                        self.stats['pings_processed'] = self.stats.get('pings_processed', 0) + 1
                    else:
                        self.stats['pings_processed'] = 1
                        self.log("📊 Created pings_processed stat counter")

                    self.log(f"✅ CTCP reply completed for {nick}")
                    return True
                else:
                    self.log(f"⚠️ {nick} not found in ping_requests")
                    return False

        except Exception as e:
            self.log(f"❌ CTCP error: {e}")
            import traceback
            self.log(f"❌ Traceback: {traceback.format_exc()}")
            return False

    # ==================== AI SYSTEM ====================

    def query_groq_ai(self, user_message, nick):
        """Query Groq AI API"""
        self.update_stats('ai_queries')

        import time
        import requests

        # Rate limiting
        current_time = time.time()
        if current_time - self.last_api_call < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - (current_time - self.last_api_call)
            time.sleep(wait_time)

        self.last_api_call = time.time()

        try:
            # API configuration
            from config import GROQ_API_KEY  # Import dari config file

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            # Build prompt
            full_prompt = f"""{self.prompt}

    **🎯 FORMAT RESPONSE TETAP:**

    YES <1-4>
    <dialog_line_1>
    <dialog_line_2> (jika YES >= 2)
    <dialog_line_3> (jika YES >= 3)  
    <dialog_line_4> (jika YES = 4)
    ACTION: <action_dengan_emoji>

    **PERATURAN:**
    1. YES HARUS di AWAL
    2. ANGKA = 1,2,3,4 SAHAJA
    3. ACTION: HARUS di AKHIR

    **CONTOH:**
    YES 2
    Wei apa khabar?
    Lama tak jumpa!
    ACTION: senyum 😊
    """

            payload = {
                "model": self.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": f"{nick}: {user_message}"}
                ],
                "temperature": 0.4,
                "max_tokens": 120,
                "stream": False
            }

            print(f"🤖 Querying AI: {user_message[:50]}...")

            response = requests.post(self.GROQ_API_URL, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()

                if 'choices' in result and result['choices']:
                    ai_text = result['choices'][0]['message']['content'].strip()
                    print(f"🤖 AI Response: {ai_text[:100]}...")
                    return ai_text
                else:
                    return f"{nick}: AI return kosong"

            else:
                print(f"❌ API error: {response.status_code}")
                return f"{nick}: API error {response.status_code}"

        except requests.exceptions.Timeout:
            return f"{nick}: AI timeout"
        except Exception as e:
            print(f"❌ AI error: {e}")
            return f"{nick}: Sistem error"
    
    def backupquery_groq_ai(self, user_message, nick):
        """Query Groq AI dan update stats"""
        self.update_stats('ai_queries')
        if not hasattr(self, 'last_api_call'):
            self.last_api_call = 0

        current_time = time.time()
        if current_time - self.last_api_call < 2.0:
            wait_time = 2.0 - (current_time - self.last_api_call)
            time.sleep(wait_time)

        self.last_api_call = time.time()

        try:
            # Search knowledge base untuk relevant info
            kb_results = self.search_knowledge(user_message)

            # Build enhanced prompt dengan knowledge
            base_prompt = self.prompt if self.prompt else "You are a helpful assistant."

            if kb_results:
                knowledge_text = "\n".join(kb_results[:3])  # Max 3 lines knowledge
                enhanced_prompt = f"{base_prompt}\n\n**KNOWLEDGE BASE:**\n{knowledge_text}"
            else:
                enhanced_prompt = base_prompt

            # Short timeout untuk faster response
            timeout = 8

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            # ====================================================
            # KHAS UNTUK 8B-INSTANT: FORMAT YANG LEBIH MUDAH
            # ====================================================
            strict_instruction = """

            **🎯 FORMAT RESPONSE TETAP:**

            YES <1-4>
            <dialog_line_1>
            <dialog_line_2> (jika YES >= 2)
            <dialog_line_3> (jika YES >= 3)  
            <dialog_line_4> (jika YES = 4)
            ACTION: <action_dengan_emoji>

            **PERATURAN MUDAH:**
            1. YES HARUS di AWAL
            2. ANGKA = 1,2,3,4 SAHAJA
            3. ACTION: HARUS di AKHIR
            4. Dialog BOLEH PANJANG untuk soalan kritikal

            **CONTOH BIASA:**
            YES 2
            Wei apa khabar?
            Lama tak jumpa!
            ACTION: senyum 😊

            **CONTOH KRITIKAL:**
            YES 3
            Falsafah kehidupan mengajar kita...
            Setiap detik adalah peluang...
            Dengan kesedaran, kita hidup bermakna.
            ACTION: renung dalam 🧠
            """

            full_prompt = enhanced_prompt + strict_instruction

            payload = {
                "model": "llama-3.1-8b-instant",  # PASTIKAN MODEL BETUL
                "messages": [
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": f"{user_message}"}
                ],
                "temperature": 0.4,  # TURUNKAN DARI 0.7 KE 0.4
                "max_tokens": 180,   # KURANGKAN DARI 150 KE 120
                "stream": False
            }

            # DEBUG
            print(f"\n🤖 [8B-DEBUG] Querying llama-3.1-8b-instant:")
            print(f"   Knowledge results: {len(kb_results)} lines")
            print(f"   User: {user_message[:50]}...")

            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)

            if response.status_code == 200:
                result = response.json()

                # DEBUG: Tampilkan response raw
                print(f"🤖 [8B-DEBUG] Raw API response: {response.text[:200]}...")

                if 'choices' not in result:
                    print(f"❌ No 'choices' key in response: {result}")
                    return f"{nick}: Tiada jawapan dari AI"

                if not result['choices']:
                    print(f"❌ Empty 'choices' list")
                    return f"{nick}: AI return kosong"

                first_choice = result['choices'][0]
                if 'message' not in first_choice:
                    print(f"❌ No 'message' in choice: {first_choice}")
                    return f"{nick}: Format response AI tidak betul"

                if 'content' not in first_choice['message']:
                    print(f"❌ No 'content' in message: {first_choice['message']}")
                    return f"{nick}: AI content missing"

                ai_text = first_choice['message']['content'].strip()
                print(f"🤖 [8B-DEBUG] AI raw response: '{ai_text}'")

                if not ai_text:
                    return f"{nick}: AI return kosong"

                # ====================================================
                # POST-PROCESSING KHAS UNTUK 8B-INSTANT
                # ====================================================
                ai_text = self.fix_8b_format(ai_text)
                print(f"🤖 [8B-DEBUG] Fixed response: '{ai_text}'")

                return ai_text

            else:
                print(f"❌ API error: {response.status_code}")
                if hasattr(response, 'text'):
                    print(f"❌ Error text: {response.text[:200]}")

                    # Check jika rate limit
                    if response.status_code == 429:
                        return f"{nick}: Rate limit reached! Tunggu reset tengah malam UTC. 😅"

                return f"{nick}: Gangguan teknikal"

        except requests.exceptions.Timeout:
            return f"{nick}: AI timeout (lebih 8 saat)"
        except Exception as e:
            print(f"❌ AI error: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"{nick}: Sistem sementara tak berfungsi"

    def fix_8b_format(self, ai_text):
        """Fix format untuk model 8b-instant yang kurang patuh"""
        ai_text = ai_text.strip()

        # Jika kosong
        if not ai_text:
            return "YES 1\n...\nACTION: confused 🤔"

        # Debug original
        print(f"🔧 [8B-FIX] Original: '{ai_text}'")

        # Case 1: Jika ada quotes, remove
        if (ai_text.startswith('"') and ai_text.endswith('"')) or \
           (ai_text.startswith("'") and ai_text.endswith("'")):
            ai_text = ai_text[1:-1].strip()

        # Split lines
        lines = [line.strip() for line in ai_text.split('\n') if line.strip()]

        # Jika takda lines langsung
        if not lines:
            return "YES 1\n...\nACTION: confused 🤔"

        # Cari YES line
        yes_index = -1
        for i, line in enumerate(lines):
            if line.upper().startswith('YES'):
                yes_index = i
                break

        # Jika takda YES, tambah di depan
        if yes_index == -1:
            # Cari ACTION lines
            action_indices = []
            dialog_lines = []

            for i, line in enumerate(lines):
                if line.upper().startswith('ACTION:'):
                    action_indices.append(i)
                else:
                    dialog_lines.append(line)

            # Ambil maksimum 2 dialog lines
            dialog_to_keep = dialog_lines[:2]

            # Ambil last ACTION line sahaja
            action_line = "ACTION: tersenyum 😊"
            if action_indices:
                action_line = lines[action_indices[-1]]

            # Reconstruct dengan YES
            new_lines = [f"YES {len(dialog_to_keep)}"] + dialog_to_keep + [action_line]
            return '\n'.join(new_lines)

        # Jika YES bukan di line pertama, pindah ke atas
        if yes_index > 0:
            yes_line = lines.pop(yes_index)
            lines.insert(0, yes_line)

        # Fix YES count
        if lines[0].upper().startswith('YES'):
            # Count actual dialog lines (bukan ACTION)
            dialog_count = 0
            for line in lines[1:]:
                if not line.upper().startswith('ACTION:'):
                    dialog_count += 1
                else:
                    break  # Stop counting selepas ACTION

            # Limit dialog count to 2
            dialog_count = min(dialog_count, 2)

            # Update YES line
            parts = lines[0].split()
            if len(parts) >= 2:
                try:
                    current_num = int(parts[1])
                    if current_num != dialog_count:
                        lines[0] = f"YES {dialog_count}"
                except:
                    lines[0] = f"YES {dialog_count}"
            else:
                lines[0] = f"YES {dialog_count}"

        # Pastikan hanya 1 ACTION line dan di akhir
        action_lines = [i for i, line in enumerate(lines) if line.upper().startswith('ACTION:')]

        if len(action_lines) > 1:
            # Keep last ACTION sahaja
            last_action = lines[action_lines[-1]]
            # Remove semua ACTION lines
            lines = [line for i, line in enumerate(lines) 
                    if not line.upper().startswith('ACTION:')]
            # Add back last ACTION
            lines.append(last_action)
        elif len(action_lines) == 0:
            # Tambah ACTION jika tiada
            lines.append("ACTION: tersenyum 😊")
        else:
            # Pastikan ACTION di akhir
            action_idx = action_lines[0]
            if action_idx != len(lines) - 1:
                action_line = lines.pop(action_idx)
                lines.append(action_line)

        # Limit total lines to 4 (YES + max 2 dialog + ACTION)
        if len(lines) > 4:
            lines = lines[:4]
            # Update YES count
            if lines[0].upper().startswith('YES'):
                dialog_count = sum(1 for line in lines[1:] 
                                 if not line.upper().startswith('ACTION:'))
                lines[0] = f"YES {dialog_count}"

        result = '\n'.join(lines)
        print(f"🔧 [8B-FIX] Fixed: '{result}'")
        return result

    def parse_ai_output(self, ai_text):
        """Parse AI output - FIXED ACTION SEPARATION BUG"""
        try:
            if not ai_text or ai_text.strip() == "":
                return "YES", ["..."], []

            ai_text = ai_text.strip()
            print(f"🔍 PARSING AI OUTPUT: {ai_text[:200]}...")

            # Deteksi mode kritikal DARI TEXT ASAL (bukan dialog sahaja)
            is_critical = self._is_critical_question(ai_text)

            # Default values
            decision = "YES"
            regular_lines = []
            action_lines = []

            # ⭐⭐ FIX 1: Split lines dengan betul
            lines = []
            for line in ai_text.split('\n'):
                line = line.strip()
                if line:  # Skip empty lines
                    lines.append(line)

            if not lines:
                return decision, ["..."], []

            # Check if follows format: YES X\n[lines]\nACTION:
            if lines[0].upper().startswith("YES"):
                # Parse YES line
                first_line = lines[0].upper()

                # ⭐⭐ FIX 2: Process lines dengan logic yang lebih jelas
                dialog_lines = []
                in_action_section = False
                current_action_text = ""

                for line in lines[1:]:
                    line_upper = line.upper()

                    # Check for ACTION: 
                    if line_upper.startswith("ACTION:") or ' ACTION:' in line_upper:
                        in_action_section = True
                        # Extract action text
                        if 'ACTION:' in line_upper:
                            # Cari position ACTION:
                            action_idx = line_upper.find('ACTION:')
                            # Jika ada text sebelum ACTION:, itu dialog
                            if action_idx > 0:
                                dialog_part = line[:action_idx].strip()
                                if dialog_part:
                                    dialog_lines.append(dialog_part)

                            action_part = line[action_idx + 7:].strip()  # 7 = len("ACTION:")
                            if action_part:
                                action_lines.append(action_part)
                        else:
                            # Line hanya mengandungi ACTION:
                            pass
                    elif in_action_section:
                        # Lines selepas ACTION: juga action
                        action_lines.append(line)
                    else:
                        # Dialog lines
                        dialog_lines.append(line)

                # Gabungkan dialog lines untuk splitting
                if dialog_lines:
                    dialog_text = " ".join(dialog_lines)

                    # ⭐⭐ FIX 3: Bersihkan sisa "ACTION:" jika ada
                    import re
                    dialog_text = re.sub(r'\s*ACTION:.*$', '', dialog_text, flags=re.IGNORECASE)

                    if dialog_text.strip():
                        if is_critical:
                            regular_lines = self._split_for_critical_mode(dialog_text)
                        else:
                            regular_lines = self._split_for_normal_mode(dialog_text)

            else:
                # Fallback: AI tak ikut format
                # ⭐⭐ FIX 4: Cari dan extract ACTION: dari mana-mana bahagian
                import re

                # Cari semua ACTION: occurrences
                action_matches = list(re.finditer(r'ACTION:\s*(.+?)(?=\n|$)', ai_text, re.IGNORECASE))

                if action_matches:
                    # Extract action texts
                    for match in action_matches:
                        action_text = match.group(1).strip()
                        if action_text:
                            action_lines.append(action_text)

                    # Remove ACTION: parts dari ai_text untuk dapat dialog
                    dialog_text = re.sub(r'ACTION:.*?(?=\n|$)', '', ai_text, flags=re.IGNORECASE)
                    dialog_text = dialog_text.strip()
                else:
                    dialog_text = ai_text

                # Split dialog text
                if dialog_text:
                    if is_critical:
                        regular_lines = self._split_for_critical_mode(dialog_text)
                    else:
                        regular_lines = self._split_for_normal_mode(dialog_text)

                # Jika tiada action lines, tambah default
                if not action_lines:
                    action_lines = ["tersenyum 😊"]

            # ⭐⭐ FIX 5: Clean up - pastikan ACTION: tiada dalam regular lines
            cleaned_regular = []
            for line in regular_lines:
                # Remove any ACTION: text
                clean_line = re.sub(r'\s*ACTION:.*$', '', line, flags=re.IGNORECASE).strip()
                if clean_line:
                    cleaned_regular.append(clean_line)

            regular_lines = cleaned_regular

            print(f"✅ PARSED: {len(regular_lines)} regular lines, {len(action_lines)} action lines")

            return decision, regular_lines, action_lines

        except Exception as e:
            print(f"❌ Parse error: {e}")
            import traceback
            traceback.print_exc()
            return "YES", ["..."], ["tersenyum 😊"]

    def _split_long_message(self, text, max_chars=300):
        """Split long messages untuk readability (DESIGN AWAK)"""
        if len(text) <= max_chars:
            return [text]

        # Smart splitting pada punctuation
        sentences = []
        current = ""

        # Split by sentences
        for char in text:
            current += char
            if len(current) >= max_chars and char in '.!?,;:':
                sentences.append(current.strip())
                current = ""

        if current:
            sentences.append(current.strip())

        # Jika masih terlalu panjang, split by words
        if not sentences or any(len(s) > max_chars * 1.5 for s in sentences):
            words = text.split()
            chunks = []
            current_chunk = ""

            for word in words:
                if len(current_chunk) + len(word) + 1 <= max_chars:
                    current_chunk += " " + word if current_chunk else word
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = word

            if current_chunk:
                chunks.append(current_chunk)

            return chunks

        return sentences

    def _is_critical_question(self, text):
        """Detect jika soalan kritikal (perlu jawapan panjang)"""
        if not text:
            return False

        text_lower = text.lower()

        # Keywords untuk soalan kritikal
        critical_keywords = [
            # Falsafah & makna
            'maksud', 'erti', 'definisi', 'pengertian', 'konsep',
            'falsafah', 'hikmah', 'falsafah', 'pemikiran',

            # Soalan kompleks
            'kenapa', 'mengapa', 'bagaimana', 'boleh terangkan',
            'jelaskan', 'huraikan', 'bincangkan', 'analisis',

            # Topik berat
            'kehidupan', 'mati', 'cinta', 'iman', 'takwa',
            'dunia', 'akhirat', 'syurga', 'neraka',

            # English equivalents
            'meaning', 'define', 'explain', 'why', 'how',
            'philosophy', 'wisdom', 'life', 'death',

            # Pattern soalan panjang
            'pendapat anda', 'apa pandangan', 'bagaimana pendapat',
        ]

        # Check jika text mengandungi keyword kritikal
        for keyword in critical_keywords:
            if keyword in text_lower:
                return True

        # Check panjang soalan (soalan panjang biasanya kritikal)
        if len(text) > 80:  # Soalan lebih dari 80 karakter
            return True

        # Check jika ada tanda soalan kompleks
        if '?' in text and text.count(' ') > 8:  # Soalan panjang dengan banyak words
            return True

        return False

    def _split_for_critical_mode(self, text):
        """Split untuk MODE KRITIKAL: max 4 lines, 175 chars per line"""
        if not text:
            return ["..."]

        text = text.strip()

        # Jika dah cukup pendek
        if len(text) <= 175:
            return [text]

        print(f"📊 KRITIKAL MODE SPLITTING: {len(text)} chars")

        # Simple splitting untuk test dulu
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= 175:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

                # Jika dah cukup 4 lines
                if len(lines) >= 4:
                    # Gabung baki dalam last line
                    remaining = ' '.join([current_line] + words[words.index(word)+1:])
                    if remaining:
                        # Potong jika terlalu panjang
                        if len(remaining) > 200:
                            remaining = remaining[:197] + "..."
                        lines.append(remaining)
                    return lines[:4]

        # Tambah last line jika ada
        if current_line and len(lines) < 4:
            lines.append(current_line)

        return lines[:4]

    def _split_for_normal_mode(self, text):
        """Split untuk MODE BIASA: max 2 lines, lebih pendek"""
        if not text:
            return ["..."]

        text = text.strip()

        if len(text) <= 120:
            return [text]

        # Try split pada natural point
        mid = len(text) // 2

        # Cari punctuation untuk split yang natural
        for i in range(mid, len(text)):
            if text[i] in '.!?;,':
                line1 = text[:i+1].strip()
                line2 = text[i+1:].strip()
                if line1 and line2:
                    return [line1, line2][:2]

        # Cari space
        for i in range(mid, len(text)):
            if text[i] == ' ':
                line1 = text[:i].strip()
                line2 = text[i+1:].strip()
                if line1 and line2:
                    return [line1, line2][:2]

        # Split di tengah exact
        return [text[:mid].strip(), text[mid:].strip()][:2]
    
    def backupquery_groq_ai(self, user_message, nick):
        """Query Groq AI dengan knowledge base"""
        if not hasattr(self, 'last_api_call'):
            self.last_api_call = 0

        current_time = time.time()
        if current_time - self.last_api_call < 2.0:
            wait_time = 2.0 - (current_time - self.last_api_call)
            time.sleep(wait_time)

        self.last_api_call = time.time()

        try:
            # Search knowledge base untuk relevant info
            kb_results = self.search_knowledge(user_message)

            # Build enhanced prompt dengan knowledge
            base_prompt = self.prompt if self.prompt else "You are a helpful assistant."

            if kb_results:
                knowledge_text = "\n".join(kb_results[:3])  # Max 3 lines knowledge
                enhanced_prompt = f"{base_prompt}\n\n**KNOWLEDGE BASE:**\n{knowledge_text}"
            else:
                enhanced_prompt = base_prompt

            # Short timeout untuk faster response
            timeout = 8

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            # Tambah instruction untuk FORMAT TEPAT
            strict_instruction = "\n\n**🎯 FORMAT RESPONSE WAJIB:**\nYES <line_count>\n<regular_message_line_1>\n<regular_message_line_2>\nACTION: <action_text>"

            full_prompt = enhanced_prompt + strict_instruction

            payload = {
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": f"{user_message}"}
                ],
                "temperature": 0.7,
                "max_tokens": 150,
                "stream": False
            }

            # DEBUG
            print(f"\n🤖 DEBUG - Prompt with knowledge:")
            print(f"   Knowledge results: {len(kb_results)} lines")
            print(f"   Enhanced prompt length: {len(full_prompt)} chars")
            print(f"   User: {user_message[:50]}...")

            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)

            if response.status_code == 200:
                result = response.json()

                # DEBUG: Tampilkan response raw
                print(f"🤖 DEBUG - Raw API response: {response.text[:200]}...")

                if 'choices' not in result:
                    print(f"❌ No 'choices' key in response: {result}")
                    return f"{nick}: Tiada jawapan dari AI"

                if not result['choices']:
                    print(f"❌ Empty 'choices' list")
                    return f"{nick}: AI return kosong"

                first_choice = result['choices'][0]
                if 'message' not in first_choice:
                    print(f"❌ No 'message' in choice: {first_choice}")
                    return f"{nick}: Format response AI tidak betul"

                if 'content' not in first_choice['message']:
                    print(f"❌ No 'content' in message: {first_choice['message']}")
                    return f"{nick}: AI content missing"

                ai_text = first_choice['message']['content'].strip()
                print(f"🤖 DEBUG - AI raw response: '{ai_text}'")

                if not ai_text:
                    return f"{nick}: AI return kosong"

                return ai_text

            else:
                print(f"❌ API error: {response.status_code}")
                if hasattr(response, 'text'):
                    print(f"❌ Error text: {response.text[:200]}")

                    # Check jika rate limit
                    if response.status_code == 429:
                        return f"{nick}: Rate limit reached! Dah guna 99.5% token harian. Tunggu reset tengah malam UTC. 😅"

                return f"{nick}: Gangguan teknikal"

        except requests.exceptions.Timeout:
            return f"{nick}: AI timeout (lebih 8 saat)"
        except Exception as e:
            print(f"❌ AI error: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"{nick}: Sistem sementara tak berfungsi"

    def backupparse_ai_output(self, ai_text):
        """Parse AI output DAN split messages dengan limit prompt asal"""
        try:
            if not ai_text or ai_text.strip() == "":
                return "YES", ["..."], []  # decision, regular_lines, action_lines

            ai_text = ai_text.strip()
            print(f"🔍 PARSING AI: {ai_text[:200]}...")

            # Default values
            decision = "YES"
            regular_lines = []
            action_lines = []

            # Tentukan jika soalan kritikal (berdasarkan prompt asal)
            is_critical = len(ai_text) > 150 or any(word in ai_text.lower() for word in 
                                                   ['complex', 'explain', 'detail', 'how to', 'why', 'what if'])

            # FORMAT: YES X\nlines\nACTION:
            if ai_text.startswith("YES"):
                lines = [line.strip() for line in ai_text.split('\n') if line.strip()]

                # First line: "YES X"
                first_line = lines[0].upper()
                if ' ' in first_line:
                    parts = first_line.split()
                    if len(parts) > 1 and parts[1].isdigit():
                        requested_lines = int(parts[1])

                # Process other lines
                in_action_section = False
                temp_regular_text = ""

                for line in lines[1:]:
                    if not line:
                        continue

                    if line.upper().startswith("ACTION:"):
                        in_action_section = True
                        action_text = line[7:].strip()
                        if action_text:
                            action_lines.append(action_text)
                    else:
                        if in_action_section:
                            # Line selepas ACTION: juga dianggap action
                            if line and line not in action_lines:
                                action_lines.append(line)
                        else:
                            # Accumulate regular text untuk splitting
                            if temp_regular_text:
                                temp_regular_text += " " + line
                            else:
                                temp_regular_text = line

                # Split regular text mengikut limit prompt asal
                if temp_regular_text:
                    if is_critical:
                        # KRITIKAL: MAX 4 lines total (regular + action)
                        max_regular_lines = max(0, 4 - len(action_lines))
                        regular_lines = self._split_text_with_limit(temp_regular_text, 
                                                                  max_lines=max_regular_lines, 
                                                                  chars_per_line=100)
                    else:
                        # BIASA: 1-2 lines total
                        max_regular_lines = max(0, 2 - len(action_lines))
                        regular_lines = self._split_text_with_limit(temp_regular_text,
                                                                  max_lines=max_regular_lines,
                                                                  chars_per_line=80)

            # FALLBACK: Direct text
            else:
                # Apply splitting berdasarkan jenis soalan
                if is_critical:
                    regular_lines = self._split_text_with_limit(ai_text, max_lines=4, chars_per_line=100)
                else:
                    regular_lines = self._split_text_with_limit(ai_text, max_lines=2, chars_per_line=80)

            # Apply FINAL limits berdasarkan prompt asal
            total_lines = len(regular_lines) + len(action_lines)

            if is_critical:
                # KRITIKAL: MAX 4 lines
                if total_lines > 4:
                    print(f"⚠️ Critical: {total_lines} lines, reducing to 4")
                    # Kurangkan action dulu, kemudian regular
                    while total_lines > 4 and action_lines:
                        action_lines.pop()
                        total_lines -= 1
                    while total_lines > 4 and regular_lines:
                        regular_lines.pop()
                        total_lines -= 1
            else:
                # BIASA: 1-2 lines  
                if total_lines > 2:
                    print(f"⚠️ Normal: {total_lines} lines, reducing to 2")
                    if len(regular_lines) > 1:
                        regular_lines = regular_lines[:1]
                    if len(action_lines) > 1:
                        action_lines = action_lines[:1]

            print(f"✅ PARSED (Critical: {is_critical}):")
            print(f"   Regular: {len(regular_lines)} lines")
            print(f"   Action: {len(action_lines)} lines")
            print(f"   TOTAL: {len(regular_lines) + len(action_lines)} lines")

            return decision, regular_lines, action_lines

        except Exception as e:
            print(f"❌ Parse error: {e}")
            import traceback
            traceback.print_exc()
            return "YES", ["..."], []

    def get_ai_quote(self):
        """Get inspirational quote from AI - FIXED SPLITTING"""
        try:
            self.log("🤖 Getting AI quote...")

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            # ⭐⭐⭐ SYSTEM PROMPT YANG LEBIH KETAT ⭐⭐⭐
            system_prompt = """You are a wisdom quote generator. Create SHORT, COMPLETE quotes.

    STRICT RULES:
    1. MAXIMUM 20-25 words (4-5 sentences MAX)
    2. MUST be a COMPLETE thought - jangan terputus!
    3. Language: 100% Bahasa Malaysia
    4. Format: SINGLE short paragraph sahaja
    5. End dengan natural ending (., !, ?)
    6. Add 1 relevant emoji di akhir
    7. DO NOT exceed 120 characters total
    8. Complete the final sentence properly

    BAD EXAMPLE (TERPUTUS): "Pengalaman adalah guru yang paling berharga, kerana melalui kesilapan dan kegagalan, kita dapat memperoleh pengetahuan dan kebijaksanaan untuk menjadi lebih berani dan bijak dal..."
    GOOD EXAMPLE: "Pengalaman mengajar kita melalui kesilapan. Kegagalan adalah peluang untuk belajar. Terus berani dan bijak! 🌟"
    """

            # Themes yang sangat pendek
            import random
            quote_themes = [
                "kesabaran",
                "kegagalan sebagai guru",
                "kebijaksanaan dari pengalaman",
                "keberanian menghadapi cabaran",
                "sederhana dalam hidup"
            ]

            user_prompt = f"Buat satu petikan hikmah yang SANGAT PENDEK dan LENGKAP tentang: {random.choice(quote_themes)}"

            payload = {
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 50,  # ⭐ KURANGKAN LAGI! DARI 60 KE 50 ⭐
                "stream": False
            }

            self.log(f"📤 Requesting quote (max_tokens: {payload['max_tokens']})...")

            response = _post_with_retry(payload, headers, timeout=8)

            if response.status_code == 200:
                result = response.json()

                if not result.get('choices'):
                    self.log("❌ No choices in response")
                    return self.get_fallback_quote()

                first_choice = result['choices'][0]
                if 'message' not in first_choice or 'content' not in first_choice['message']:
                    self.log("❌ Invalid response format")
                    return self.get_fallback_quote()

                quote = first_choice['message']['content'].strip()

                if not quote:
                    self.log("❌ Empty quote response")
                    return self.get_fallback_quote()

                # ⭐⭐⭐ FIX SPLITTING - PASTIKAN QUOTE LENGKAP ⭐⭐⭐
                quote = self._validate_quote_completeness(quote)

                # Jika masih panjang, split dengan betul
                if len(quote) > 140:
                    quote = self._split_quote_properly(quote)

                # Add emoji jika kurang
                import re
                emoji_pattern = re.compile("["
                    u"\U0001F600-\U0001F64F"
                    u"\U0001F300-\U0001F5FF" 
                    u"\U0001F680-\U0001F6FF"
                    "]+", flags=re.UNICODE)

                if not emoji_pattern.search(quote):
                    emojis = ['✨', '🌟', '💎', '🌿', '💫']
                    quote += f" {random.choice(emojis)}"

                # Format
                formats = ['💭 {}', '🗨️ {}', '💎 {}', '🌟 {}']
                formatted = random.choice(formats).format(quote)

                self.log(f"✅ Quote ({len(quote)} chars): {quote[:60]}...")
                return formatted

            else:
                self.log(f"❌ Quote API error: {response.status_code}")
                return self.get_fallback_quote()

        except Exception as e:
            self.log(f"❌ Quote error: {e}")
            return self.get_fallback_quote()

    def _validate_quote_completeness(self, quote):
        """Validate dan pastikan quote lengkap"""
        if not quote:
            return "Hikmah datang dengan kesabaran. ✨"

        quote = quote.strip()

        # 1. Remove trailing ellipsis (...)
        quote = quote.rstrip('.…')

        # 2. Cari last proper sentence ending
        last_period = quote.rfind('.')
        last_excl = quote.rfind('!')
        last_quest = quote.rfind('?')

        last_end = max(last_period, last_excl, last_quest)

        # 3. Jika ada proper ending, potong di sana
        if last_end > 0:
            # Jika ending dalam 80% akhir text, gunakan
            if last_end > len(quote) * 0.7:
                return quote[:last_end + 1]
            # Jika ending terlalu awal, tambah punctuation
            else:
                # Cari last space untuk split yang natural
                last_space = quote.rfind(' ')
                if last_space > len(quote) * 0.8:
                    return quote[:last_space] + "..."
                else:
                    return quote + "."
        else:
            # Tiada punctuation, tambah
            return quote + "."

    def _split_quote_properly(self, quote, max_length=140):
        """Split quote dengan betul - TIDAK POTONG TENGAH AYAT"""
        if len(quote) <= max_length:
            return quote

        self.log(f"✂️ Splitting long quote: {len(quote)} chars")

        # Cari natural break point
        ideal_cut = max_length

        # Priority 1: Cari punctuation (., !, ?)
        for i in range(max_length - 10, max_length):
            if i < len(quote) and quote[i] in '.!?':
                ideal_cut = i + 1  # Include punctuation
                break

        # Priority 2: Cari comma atau semicolon
        if ideal_cut == max_length:
            for i in range(max_length - 5, max_length):
                if i < len(quote) and quote[i] in ',;':
                    ideal_cut = i + 1
                    break

        # Priority 3: Cari space
        if ideal_cut == max_length:
            for i in range(max_length - 1, max_length - 20, -1):
                if i < len(quote) and quote[i] == ' ':
                    ideal_cut = i
                    break

        result = quote[:ideal_cut].strip()

        # Pastikan ada punctuation di akhir
        if result and result[-1] not in '.!?':
            result += "..."

        self.log(f"✅ After split: {len(result)} chars")
        return result

    def get_fallback_quote(self):
        """Return fallback quote jika API gagal"""
        fallback_quotes = [
            "Hidup bagai roda, kadang di atas kadang di bawah. Yang penting terus berputar. 🔄",
            "Air yang tenang jangan disangka tiada buaya. Dalam diam ada kekuatan. 🌊",
            "Seperti padi, semakin berisi semakin tunduk. Rendah hati itu indah. 🌾",
            "Bukan kapal yang tenggelam kerana air di luar, tapi air yang masuk ke dalam. ⛵",
            "Setiap hujan pasti berhenti, setiap malam pasti subuh. Sabar menunggu waktu. 🌧️🌅",
            "Ilmu yang bermanfaat lebih baik dari harta yang berlimpah. 📚✨",
            "Kesabaran itu kunci segala hikmah dan kebahagiaan. 🔑",
            "Bersyukur dengan yang sedikit membawa ketenangan yang banyak. 🙏",
            "Perjalanan seribu batu bermula dengan satu langkah. 👣",
            "Masa yang dihabiskan untuk memberi nasihat tidak pernah sia-sia. 💭"
        ]

        import random
        quote = random.choice(fallback_quotes)

        # Random format
        formats = ['💭 {}', '🗨️ {}', '📜 {}', '💎 {}']
        formatted = random.choice(formats).format(quote)

        self.log(f"📝 Simple quote: {formatted[:60]}...")
        return formatted

    def should_use_ai(self, message):
        """Check if message should use AI - FIXED FALSE POSITIVES"""
        message_lower = message.lower()

        # Check untuk !ai command
        if '!ai' in message_lower:
            return True

        # ⭐⭐ FIX: Check untuk MENTION yang BETUL ⭐⭐
        # Pattern matching yang lebih tepat
        import re

        # Pattern untuk mention: @www, www: , www, 
        mention_patterns = [
            r'@' + re.escape(self.nick.lower()) + r'\b',  # @www
            r'\b' + re.escape(self.nick.lower()) + r'[:,]?\s',  # www: atau www,
            r'\b' + re.escape(self.nick.lower()) + r'\b',  # www (sebagai word)
        ]

        for pattern in mention_patterns:
            if re.search(pattern, message_lower):
                return True

        # Check untuk direct questions dengan tanda tanya
        if '?' in message:
            # Check jika address ke bot secara spesifik
            bot_keywords = [self.nick.lower(), 'www', 'serv', 'bot', 'ai']
            for keyword in bot_keywords:
                # Gunakan word boundary untuk elak false positive
                if re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                    return True

        return False

    def handle_ai_request(self, nick, channel, message):
        """Handle AI request - DENGAN REPEAT CHECK AWAL"""
        try:
            # ⭐⭐ CHECK REPEAT SPAM FIRST - SEBELUM APA-APA ⭐⭐
            if self.is_repeat_spam(nick, message, channel):
                self.log(f"🚫 AI REQUEST BLOCKED: {nick} - repeat spam detected")
                return  # ⭐ LANGSUNG TAK PROCEED!

            self.log(f"🤖 AI request from {nick}: '{message[:30]}...'")

            # Update stats
            self.update_stats('ai_queries')

            # Rate limiting
            current_time = time.time()
            if nick in self.last_response_time:
                if current_time - self.last_response_time[nick] < 0.5:
                    self.log(f"⏰ Rate limited: {nick}")
                    # self.send(channel, f"{nick}: Tunggu 2 saat sebelum tanya lagi")
                    return

            self.last_response_time[nick] = current_time

            # Clean message
            cleaned_msg = message
            triggers = ['!ai', 'ai:', '.ai', f'@{self.nick.lower()}', self.nick.lower(), 'www']
            for trigger in triggers:
                cleaned_msg = cleaned_msg.replace(trigger, '').strip()

            if not cleaned_msg or len(cleaned_msg) < 2:
                self.log(f"⚠️ Empty AI request from {nick}")
                import random
                responses = [
                    f"{nick}: Ya? {nick} pciter?",
                    f"{nick}: ya boleh saya bantu?",
                    f"{nick}: Ada apa tu?"
                ]
                response = random.choice(responses)
                self.send(channel, response)
                return

            # Record start time
            start_time = time.time()
            self.log(f"🤖 Processing AI request: '{cleaned_msg[:100]}...'")

            # ⭐⭐ DETECT CRITICAL QUESTION (untuk stats sahaja) ⭐⭐
            is_critical = self._is_critical_question(cleaned_msg)
            if is_critical:
                self.log(f"🧠 CRITICAL QUESTION DETECTED")
                self.update_stats('critical_questions')
            else:
                self.log(f"💬 NORMAL QUESTION")
                self.update_stats('normal_questions')

            # MINIMUM THINKING TIME: 3 saat
            elapsed_time = time.time() - start_time
            if elapsed_time < 3.0:
                time.sleep(3.0 - elapsed_time)

            # SEARCH KNOWLEDGE BASE jika relevant
            kb_context = ""
            if self.should_inject_knowledge(cleaned_msg):
                kb_results = self.search_knowledge(cleaned_msg)
                if kb_results:
                    kb_context = "\nRelevant knowledge: " + " | ".join(kb_results[:2])
                    self.log(f"📚 Injecting knowledge: {kb_context}")

            # Modify user message dengan context
            enhanced_message = cleaned_msg
            if kb_context:
                enhanced_message = f"{cleaned_msg}\n\nContext:{kb_context}"

            # Dapatkan response dari AI dengan enhanced message
            response_text = self.query_groq_ai(enhanced_message, nick)

            # Calculate total processing time
            total_time = time.time() - start_time
            self.log(f"⏱️ AI processed in {total_time:.2f} seconds")

            if not response_text or response_text.strip() == "":
                self.send(channel, f"{nick}: Maaf, tak dapat jawapan sekarang.")
                self.update_stats('ai_failed')
                return

            # ⭐⭐ GUNA parse_ai_output() ASAL ANDA ⭐⭐
            # (yang dah ada logic split 4 lines dengan dramatic timing)
            decision, regular_lines, action_lines = self.parse_ai_output(response_text)

            # Jika decision NO
            if decision == "NO":
                self.log(f"🤖 Decision: NO for '{cleaned_msg[:50]}...'")
                import random
                responses = [
                    f"{nick}: Maaf, itu di luar bidang saya.",
                    f"{nick}: Saya fokus pada hikmah dan nasihat kehidupan sahaja.",
                    f"{nick}: Cuba tanya soalan tentang kehidupan atau hikmah."
                ]
                self.send(channel, random.choice(responses))
                self.update_stats('ai_failed')
                return

            # Log parsing result
            self.log(f"📝 Parsed: {len(regular_lines)} regular, {len(action_lines)} action lines")

            # ⭐⭐ SEND ACTION LINES - DRAMATIC TIMING ⭐⭐
            # (Kekalkan timing dramatic asal anda)
            for action_text in action_lines:
                if action_text:
                    self.send_action(channel, action_text)
                    if len(action_lines) > 1:
                        time.sleep(1.5)

            # ⭐⭐ SEND REGULAR LINES - DRAMATIC TIMING ASAL ⭐⭐
            # (Kekalkan dramatic delays asal anda)
            for i, line in enumerate(regular_lines):
                if line:
                    self.send(channel, line)
                    # ⭐⭐ GUNA DRAMATIC DELAYS ASAL ANDA ⭐⭐
                    if i < len(regular_lines) - 1:
                        # Gunakan self.DRAMATIC_DELAYS jika ada, atau default
                        if hasattr(self, 'DRAMATIC_DELAYS') and i < len(self.DRAMATIC_DELAYS):
                            time.sleep(self.DRAMATIC_DELAYS[i])
                        else:
                            # Default dramatic delays
                            delays = [1.5, 2.5, 2.5, 3.0]
                            delay = delays[i] if i < len(delays) else 2.0
                            time.sleep(delay)

            # Update success stats
            self.update_stats('ai_responses')
            self.update_stats('ai_success')

        except Exception as e:
            self.log(f"❌ AI handler error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.update_stats('errors')
            self.send(channel, f"{nick}: Error memproses permintaan")

    def split_ai_response(self, text, max_lines=4, chars_per_line=100):
        """Split AI response kepada multiple lines yang kemas"""
        try:
            # CHECK 1: Pastikan text bukan None
            if text is None:
                self.log("⚠️ split_ai_response received None text")
                return ["Maaf, tiada response."]

            text = str(text).strip()  # Convert ke string jika perlu

            # CHECK 2: Jika text kosong
            if text == "":
                self.log("⚠️ split_ai_response received empty text")
                return ["..."]

            # Remove sweet emojis dari text
            sweet_emojis = ['🍬', '🍭', '🍫', '🍡', '🧁', '🍪', '🍯']
            for emoji in sweet_emojis:
                text = text.replace(emoji, '')

            # Jika text pendek, return 1 line sahaja
            if len(text) <= chars_per_line or max_lines == 1:
                return [text.strip()]

            # Split kepada ayat-ayat semula jadi
            sentences = re.split(r'(?<=[.!?])\s+', text)

            # CHECK 3: Jika tak dapat split sentences
            if not sentences or len(sentences) == 0:
                # Simple split by length
                lines = []
                for i in range(0, len(text), chars_per_line):
                    lines.append(text[i:i+chars_per_line].strip())
                return lines[:max_lines]

            lines = []
            current_line = ""

            for sentence in sentences:
                if not sentence.strip():
                    continue

                # Jika sentence sahaja dah lebih panjang dari chars_per_line
                if len(sentence) > chars_per_line:
                    # Split manual
                    words = sentence.split()
                    temp_line = ""
                    for word in words:
                        if len(temp_line) + len(word) + 1 <= chars_per_line:
                            if temp_line:
                                temp_line += " " + word
                            else:
                                temp_line = word
                        else:
                            if temp_line:
                                lines.append(temp_line)
                                temp_line = word
                            else:
                                lines.append(word)
                    if temp_line:
                        current_line = temp_line
                else:
                    # Normal case
                    if len(current_line) + len(sentence) + 1 <= chars_per_line:
                        if current_line:
                            current_line += " " + sentence
                        else:
                            current_line = sentence
                    else:
                        lines.append(current_line)
                        current_line = sentence

                # Jika dah cukup lines
                if len(lines) >= max_lines - 1:
                    if current_line:
                        lines.append(current_line)
                    break

            # Add remaining text
            if current_line and len(lines) < max_lines:
                lines.append(current_line)
            elif current_line and len(lines) >= max_lines:
                # Gabung ke line terakhir
                if len(lines) > 0:
                    last_line = lines[-1]
                    if len(last_line) + len(current_line) + 3 <= chars_per_line * 1.5:
                        lines[-1] = last_line + " ... " + current_line
                    else:
                        lines[-1] = last_line + " ..."

            # Pastikan maksimum lines
            lines = lines[:max_lines]

            # CHECK 4: Jika lines masih kosong
            if not lines or len(lines) == 0:
                return [text[:chars_per_line].strip()]

            # Trim setiap line
            lines = [line[:chars_per_line].strip() for line in lines]

            return lines

        except Exception as e:
            self.log(f"❌ Split error: {e}")
            import traceback
            self.log(f"❌ Traceback: {traceback.format_exc()}")
            # Fallback: simple split
            text_str = str(text) if text else "Maaf, ada error."
            if len(text_str) <= chars_per_line:
                return [text_str.strip()]
            return [text_str[:chars_per_line].strip(), text_str[chars_per_line:chars_per_line*2].strip()]

    def _split_text_with_limit(self, text, max_lines=4, chars_per_line=100):
        """Split text dengan word boundaries dan limit lines - HELPER FUNCTION"""
        try:
            import re

            if not text or not isinstance(text, str):
                return ["..."]

            text = text.strip()

            # Jika text kosong atau sangat pendek
            if len(text) < 2:
                return ["..."]

            # Jika cukup pendek untuk satu line
            if len(text) <= chars_per_line or max_lines == 1:
                return [text]

            # Split dengan intelligent word boundaries (lebih baik dari split_ai_response)
            words = text.split()
            lines = []
            current_line = ""

            for i, word in enumerate(words):
                # Check jika tambah word ini akan melebihi limit
                test_line = current_line + (" " if current_line else "") + word

                if len(test_line) <= chars_per_line:
                    current_line = test_line
                else:
                    # Save current line jika bukan kosong
                    if current_line:
                        lines.append(current_line)

                    # Start new line dengan current word
                    current_line = word

                    # Check jika dah capai max lines
                    if len(lines) >= max_lines:
                        # Jika dah capai limit, tambah ... dan break
                        if current_line and len(lines) < max_lines:
                            lines.append(current_line + "...")
                        elif lines and not lines[-1].endswith("..."):
                            lines[-1] = lines[-1] + "..."
                        break

            # Add last line jika belum capai limit
            if current_line and len(lines) < max_lines:
                lines.append(current_line)

            # Ensure kita tak lebih dari max_lines
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                # Ensure last line ends properly
                if lines and not lines[-1].endswith("..."):
                    lines[-1] = lines[-1] + "..."

            # Clean up: Remove empty lines
            lines = [line for line in lines if line and line.strip()]

            # Jika masih kosong
            if not lines:
                return [text[:chars_per_line] + "..." if len(text) > chars_per_line else text]

            return lines

        except Exception as e:
            print(f"❌ _split_text_with_limit error: {e}")
            # Fallback: simple split
            if len(text) > chars_per_line:
                return [text[:chars_per_line-3] + "..."]
            return [text]

    def check_hourly_weather(self, current_time):
        """Check and post hourly weather if needed"""
        try:
            import time
            from datetime import datetime

            # Get current hour
            current_hour = datetime.fromtimestamp(current_time).hour

            # Jika last_hourly belum diset atau sudah lepas 1 jam
            if self.last_hourly == -1 or current_hour != self.last_hourly:
                # Post weather untuk Kuala Lumpur (default)
                weather_info = self.data.get_cuaca_detail("Kuala Lumpur")

                if weather_info:
                    # Format message
                    message = f"🕒 {current_hour:02d}:00 | Cuaca KL: {weather_info['lokasi']} {weather_info['suhu']}°C, {weather_info['keterangan']}"

                    # Post ke semua channel
                    for channel in self.joined_channels:
                        self.send_message(channel, message)

                    # Update last hourly
                    self.last_hourly = current_hour
                    print(f"✅ Posted hourly weather: {message[:50]}...")

                    # Update stats
                    self.update_stats('weather_queries')

        except Exception as e:
            print(f"❌ Error in check_hourly_weather: {e}")
    
    def handle_command(self, nick, channel, command):
        """Handle commands - UPDATED VERSION"""
        try:
            cmd = command.lower().strip()

            # Debug log
            self.log(f"🔧 Processing command: '{cmd}' from {nick}")

            # ⭐⭐⭐ PING COMMAND - HANDLED IN RUN() ⭐⭐⭐
            if cmd == '.ping':
                self.log(f"🎯 .ping command forwarded to run() handler")
                return None  # Biar run() handle CTCP ping

            # ⭐⭐⭐ WEATHER COMMAND ⭐⭐⭐
            elif cmd.startswith("!cuaca"):
                parts = cmd.split()
                lokasi = "Kuala Lumpur" if len(parts) < 2 else ' '.join(parts[1:])

                if lokasi.lower() in ['afrika', 'africa', 'eropah', 'europe', 'asia', 'amerika', 'america']:
                    return [f"❌ '{lokasi}' terlalu umum. Sila nyatakan bandar atau negara yang spesifik (cth: Cairo, London, Tokyo)"]

                cuaca = self.data.get_cuaca_detail(lokasi)
                if cuaca:
                    self.update_stats('weather_queries')
                    return self.display.format_cuaca_jelas(cuaca)
                else:
                    return [f"❌ tak dapat data cuaca untuk '{lokasi}'. Cuba nama bandar yang lebih spesifik."]

            # ⭐⭐⭐ PRAYER TIME COMMAND ⭐⭐⭐
            elif cmd.startswith("!wsolat") or cmd == "!solat":
                parts = cmd.split()
                lokasi = "Kuala Lumpur" if len(parts) < 2 else ' '.join(parts[1:])

                solat = self.data.get_solat(lokasi)
                if solat:
                    self.update_stats('prayer_queries')
                    if 'error' in solat:
                        return [f"❌ {solat['error']}"]
                    else:
                        return self.display.format_solat_fixed(solat)
                else:
                    return [f"❌ tak dapat data solat {lokasi}"]

            # ⭐⭐⭐ CURRENT TIME COMMAND ⭐⭐⭐
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
                elif 12 <= hour < 14:  # ⭐ UPDATED: 12pm-1:59pm sahaja
                    greeting = "☀️ selamat tengahari"
                elif 14 <= hour < 19:  # ⭐ UPDATED: 2:00pm-6:59pm petang
                    greeting = "⛅ selamat petang"
                else:
                    greeting = "🌃 selamat malam"

                return [f"🕐 {waktu} • {greeting} • {hari}, {tarikh}"]

            # ⭐⭐⭐ AI COMMANDS - THREADED ⭐⭐⭐
            elif cmd.startswith('!ai') or cmd.startswith('!prompts'):
                parts = cmd.split(' ', 1)
                ai_query = parts[1] if len(parts) > 1 else "hello"

                # Handle dalam thread
                import threading
                threading.Thread(
                    target=self.handle_ai_request,
                    args=(nick, channel, ai_query),
                    daemon=True
                ).start()

                return [f"🤖 {nick}: Processing AI request..."]  # Immediate feedback

            # ⭐⭐⭐ HELP COMMANDS ⭐⭐⭐
            elif cmd.startswith('.help') or cmd.startswith('!help'):
                query = cmd[5:].strip() if len(cmd) > 5 else ""

                if not query:
                    help_msg = [
                        f"{nick}: **🤖 WWW BOT COMMANDS**",
                        "**Cuaca:** !cuaca [lokasi] (global support)",
                        "**Solat:** !wsolat [lokasi] (Malaysia only)",
                        "**Masa:** !waktu (current Malaysia time)",
                        "**AI:** !ai [soalan] atau mention 'www'",
                        "**Ping:** .ping (CTCP lag test)",
                        "**Notepad:** !read notepad.txt [full]",
                        "**Stats:** .stats (bot statistics)",
                        "**Lain:** !bantuan, !info, .find, !files"
                    ]
                    return help_msg

                # Search knowledge base untuk specific help
                results = self.search_knowledge(query)
                if results:
                    self.update_stats('help_responses')
                    formatted = [f"🔍 {nick}: Help results untuk '{query}':"]
                    for i, line in enumerate(results[:3], 1):
                        formatted.append(f"  {i}. {line}")
                    return formatted
                else:
                    # Forward ke AI jika tak jumpa
                    threading.Thread(
                        target=self.handle_ai_request,
                        args=(nick, channel, query),
                        daemon=True
                    ).start()
                    return [f"🤖 {nick}: Mencari jawapan untuk '{query}'..."]

            # ⭐⭐⭐ STATISTICS COMMAND ⭐⭐⭐
            elif cmd in ['.stats', '!stats']:
                import time
                uptime = time.time() - self.stats.get('start_time', time.time())
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)

                stats_msg = [
                    f"📊 **{nick}: BOT STATISTICS**",
                    f"• ⏱️ Uptime: {hours}h {minutes}m",
                    f"• 🤖 AI: {self.stats.get('ai_queries', 0)} queries, {self.stats.get('ai_responses', 0)} responses",
                    f"• 🌤️ Weather: {self.stats.get('weather_queries', 0)} requests",
                    f"• 🕌 Prayer: {self.stats.get('prayer_queries', 0)} requests",
                    f"• 📡 Ping: {self.stats.get('pings_processed', 0)} tests",
                    f"• 💭 Quotes: {self.stats.get('auto_quotes', 0)} posted",
                    f"• 📨 Messages: {self.stats.get('messages_processed', 0)} processed"
                ]
                return stats_msg

            # ⭐⭐⭐ NOTEPAD READING COMMANDS ⭐⭐⭐
            elif cmd.startswith('!read'):
                parts = cmd.split()
                if len(parts) >= 2:
                    filename = parts[1]

                    if filename == 'notepad.txt':
                        is_full = len(parts) >= 3 and parts[2] == 'full'

                        if is_full:
                            return self.handle_read_notepad_full(nick, channel)
                        else:
                            return self.handle_read_notepad_short(nick, channel)
                    else:
                        allowed_files = ['prompt.txt', 'reply.txt']
                        if filename in allowed_files:
                            return self.handle_read_other_file(nick, filename)
                        else:
                            return [f"❌ {nick}: Hanya boleh baca: notepad.txt, prompt.txt, reply.txt"]
                else:
                    return [f"❌ {nick}: Format: !read <filename> [full]"]

            elif cmd == '!readall':
                return self.handle_read_all_notepad(nick, channel)

            elif cmd.startswith('!readfrom'):
                parts = cmd.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    start_entry = int(parts[1])
                    return self.handle_read_from(nick, channel, start_entry)
                else:
                    return [f"❌ {nick}: Format: !readfrom <entry_number>"]

            # ⭐⭐⭐ SEARCH COMMAND ⭐⭐⭐
            elif cmd.startswith('.find'):
                search_term = cmd[6:].strip() if len(cmd) > 6 else ""
                if not search_term:
                    return [f"❌ {nick}: Format: .find <keyword>"]

                results = []
                for line in self.knowledge_base:
                    if search_term.lower() in line.lower():
                        results.append(line)

                if not results:
                    return [f"🔍 {nick}: Tiada results untuk '{search_term}'"]

                # Handle dalam thread dengan delay
                import threading
                threading.Thread(
                    target=self.send_search_results,
                    args=(channel, nick, search_term, results)
                ).daemon = True
                threading.Thread.start()

                return [f"🔍 {nick}: Mencari '{search_term}'... ({len(results)} results)"]

            # ⭐⭐⭐ FILE MANAGEMENT COMMANDS ⭐⭐⭐
            elif cmd == '!reload':
                self.knowledge_base = self.load_knowledge()
                return [f"✅ {nick}: Knowledge base reloaded! {len(self.knowledge_base)} lines."]

            elif cmd == '!files':
                import os
                files = [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.')]
                files = sorted(files)[:10]

                if files:
                    return [f"📁 {nick}: Files: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}"]
                else:
                    return [f"📁 {nick}: Tiada file dalam folder."]

            # ⭐⭐⭐ INFO & HELP COMMANDS ⭐⭐⭐
            elif cmd == "!bantuan":
                return [
                    f"🛠️ **{nick}: BANTUAN CEPAT**",
                    "• !cuaca [lokasi] - Info cuaca global",
                    "• !wsolat [lokasi] - Waktu solat Malaysia",
                    "• !waktu - Masa Malaysia terkini",
                    "• !ai [soalan] - Chat dengan AI",
                    "• .ping - Test connection lag",
                    "• .stats - Bot statistics",
                    "• !help - Detailed help"
                ]

            elif cmd == "!info":
                return [
                    f"🤖 **{nick}: WWW BOT INFO**",
                    "• Cuaca: Global support via geocoding API",
                    "• Solat: Malaysia dengan zone mapping betul",
                    "• AI: Groq LLM dengan smart detection",
                    "• Ping: CTCP dengan sweet messages",
                    "• Auto: Hourly weather + 15min quotes",
                    "• Commands: !help untuk senarai lengkap"
                ]

            # ⭐⭐⭐ TEST & DEBUG COMMANDS ⭐⭐⭐
            elif cmd == '!testctcp':
                # Test CTCP functionality
                self.send_raw(f"MODE {self.nick} -T")
                return [f"🔧 {nick}: MODE -T sent. Try .ping now"]

            elif cmd == '!testweather':
                # Test weather API
                cuaca = self.data.get_cuaca_detail("Kuala Lumpur")
                if cuaca:
                    return [f"✅ {nick}: Weather API OK - {cuaca['lokasi']} {cuaca['suhu']}°C"]
                else:
                    return [f"❌ {nick}: Weather API failed"]

            elif cmd == '!testquote':
                # Test quote generation
                quote = self.get_ai_quote()
                if not quote:
                    quote = self.get_fallback_quote()
                return [f"💭 {nick}: Test quote: {quote}"]

            # ⭐⭐⭐ UNKNOWN COMMAND ⭐⭐⭐
            else:
                self.update_stats('commands_unknown')
                self.log(f"❓ Unknown command: '{cmd}' from {nick}")

                # Suggest help
                # return [f"❓ {nick}: Command '{cmd.split()[0]}' tak dikenali. Cuba !help"]

        except Exception as e:
            self.log(f"❌ handle_command error: {e}")
            import traceback
            traceback.print_exc()
            return [f"❌ {nick}: Error processing command"]

    def load_cap_ayam_messages(self):
        """Load cap ayam messages dari reply.txt"""
        try:
            reply_file = "reply.txt"

            if os.path.exists(reply_file):
                self.log(f"📖 Loading cap ayam messages from {reply_file}")

                with open(reply_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Cari bahagian CAP AYAM dalam file
                # Format mungkin: [CAP_AYAM] atau ## CAP AYAM ##
                messages = []

                # Pattern 1: Cari bahagian antara [CAP_AYAM] tags
                if '[CAP_AYAM]' in content:
                    start = content.find('[CAP_AYAM]') + len('[CAP_AYAM]')
                    end = content.find('[/CAP_AYAM]')
                    if end > start:
                        section = content[start:end].strip()
                        messages = [line.strip() for line in section.split('\n') if line.strip()]

                # Pattern 2: Cari lines yang ada 🍬 atau 🍭 emoji
                if not messages:
                    lines = content.split('\n')
                    sweet_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and any(emoji in line for emoji in ['🍬', '🍭', '🍫', '🍡', '🧁']):
                            sweet_lines.append(line)

                    if sweet_lines:
                        messages = sweet_lines[:20]  # Ambil 20 pertama

                # Pattern 3: Jika masih tak jumpa, ambil semua lines
                if not messages:
                    messages = [line.strip() for line in content.split('\n') 
                               if line.strip() and len(line.strip()) > 10][:15]

                # Jika dapat messages, simpan
                if messages:
                    self.cap_ayam_messages = messages
                    self.log(f"✅ Loaded {len(messages)} cap ayam messages")

                    # Debug: Show first 3 messages
                    for i, msg in enumerate(messages[:3], 1):
                        self.log(f"   {i}. {msg[:50]}...")
                else:
                    # Fallback messages
                    self.cap_ayam_messages = [
                        "Quantum sweet processing activated 🍬⚛️",
                        "Candy-coated latency measurement 🍭📡",
                        "Sweet fiber network routing 🍫🌐",
                        "Sugar-powered quantum computation 🍡🧠",
                    ]
                    self.log(f"⚠️ No messages found in {reply_file}, using defaults")

            else:
                # File tidak wujud, guna default
                self.log(f"❌ {reply_file} not found, using default messages")
                self.cap_ayam_messages = [
                    "Quantum sweet processing activated 🍬⚛️",
                    "Candy-coated latency measurement 🍭📡",
                    "Sweet fiber network routing 🍫🌐",
                    "Sugar-powered quantum computation 🍡🧠",
                ]

            # Initialize message index
            self.message_index = 0

        except Exception as e:
            self.log(f"❌ Error loading cap ayam messages: {e}")
            self.cap_ayam_messages = ["Sweet network processing 🍬"]
            self.message_index = 0
    
    def handle_read_other_file(self, nick, filename):
        """Handle reading other files like prompt.txt, reply.txt"""
        try:
            if not os.path.exists(filename):
                return [f"❌ {nick}: File '{filename}' tidak ditemukan."]

            with open(filename, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]

            if not lines:
                return [f"📄 {nick}: '{filename}' kosong."]

            # Return first 5 lines sahaja
            preview = []
            preview.append(f"📄 {nick}: {filename} ({len(lines)} lines):")

            for i, line in enumerate(lines[:5], 1):
                if len(line) > 80:
                    line = line[:77] + "..."
                preview.append(f"  {i}. {line}")

            if len(lines) > 5:
                preview.append(f"  ... dan {len(lines)-5} lines lagi")

            return preview

        except Exception as e:
            return [f"❌ {nick}: Error reading {filename}: {str(e)}"]
    
    def send_search_results(self, channel, nick, search_term, results):
        """Send search results dengan delay"""
        try:
            self.send(channel, f"🔍 {nick}: Results untuk '{search_term}' ({len(results)} found):")
            time.sleep(1.5)

            max_results = min(8, len(results))

            for i, line in enumerate(results[:max_results], 1):
                # Clean and truncate
                if len(line) > 3 and line[0].isdigit() and line[1] == '.' and line[2] == ' ':
                    line = line[3:]

                if len(line) > 65:
                    line = line[:62] + "..."

                prefix = f"[{i}/{max_results}] "
                self.send(channel, prefix + line)

                if i < max_results:
                    time.sleep(2)

            if len(results) > max_results:
                time.sleep(1)
                remaining = len(results) - max_results
                self.send(channel, f"🔍 {nick}: ... dan {remaining} results lagi.")

        except Exception as e:
            self.send(channel, f"❌ {nick}: Search error: {str(e)}")
    
    def start_services(self):
        """Start background services - SIMPLIFIED VERSION"""
        import threading

        def keepalive():
            while self.running:
                time.sleep(60)
                try:
                    if self.connected:
                        self.send_raw("PING :keepalive")
                except:
                    self.connected = False

        def auto_updates_loop():
            """Loop untuk semua auto-updates: weather, quote, solat"""
            self.log("🔄 Auto-updates loop started")
            while self.running:
                try:
                    # Hanya check jika connected dan ada channel
                    if self.connected and self.joined_channels:
                        self.check_and_post_auto_updates()  # ⭐ GUNA FUNGSI INI

                    # Check setiap 10 saat (bukan terlalu kerap)
                    time.sleep(10)

                except Exception as e:
                    self.log(f"❌ Auto-updates loop error: {e}")
                    time.sleep(30)  # Tunggu lebih lama jika error
        
        def monitor_connection():
            """Monitor connection dan auto-rejoin"""
            while self.running:
                if not self.connected:
                    self.auto_rejoin()
                time.sleep(10)

        def cleanup_timeouts(self):
            """Cleanup ping timeouts - FIXED VERSION"""
            while self.running:
                current_time = time.time()

                # Buat copy of keys untuk elak modification during iteration
                nicks_to_check = list(self.ping_requests.keys())

                for nick in nicks_to_check:
                    if nick in self.ping_requests:  # Double-check masih ada
                        data = self.ping_requests[nick]
                        if current_time - data['tick'] > 10:
                            # ⭐⭐⭐ LOG SEBELUM DELETE ⭐⭐⭐
                            self.log(f"⏰ Ping timeout for {nick} ({(current_time - data['tick']):.1f}s)")

                            channel = data.get('channel')

                            try:
                                del self.ping_requests[nick]
                                self.log(f"🗑️ Timeout: Deleted {nick} from ping_requests")
                            except KeyError:
                                self.log(f"⚠️ {nick} already deleted during timeout check")

                            # Send timeout message
                            if channel:
                                self.send(channel, f"⏰ 10s {nick} - Timeout 1st type /mode {nick} -T")

                time.sleep(5)  # Check setiap 5 saat

        # Start semua threads
        threading.Thread(target=keepalive, daemon=True).start()
        threading.Thread(target=auto_updates_loop, daemon=True).start()  # INI YANG UTAMA
        threading.Thread(target=monitor_connection, daemon=True).start()
        threading.Thread(target=cleanup_timeouts, daemon=True).start()

        self.log("🔄 Services started (unified auto-updates)")

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

        def start_services(self):
            """Start background services"""
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

            def quote_announce():  # ⬅️ INI 8 SPACES (dalam start_services)
                """Auto quote every 15 minutes"""
                while self.running:
                    now = DisplayFixed.get_malaysia_time()

                    if now.minute in QUOTE_TRIGGER_MINUTES and now.second <= 10:
                        if now.minute != self.last_quote_minute:
                            if self.connected:
                                self.do_quote_announce()
                                self.last_quote_minute = now.minute
                            time.sleep(60)  # ⚠️ MASALAH DI SINI!

                    time.sleep(1)  # ⚠️ DAN INI JUGA

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

            def cleanup_timeouts():
                """Cleanup ping timeouts"""
                while self.running:
                    current_time = time.time()
                    for nick, data in list(self.ping_requests.items()):
                        if current_time - data['tick'] > 10:
                            del self.ping_requests[nick]
                            self.log(f"⏰ Ping timeout for {nick}")
                            if 'channel' in data:
                                self.send(data['channel'], f"⏰ {nick} - Timeout (10s)")
                    time.sleep(5)

            threading.Thread(target=keepalive, daemon=True).start()
            threading.Thread(target=hourly_announce, daemon=True).start()
            threading.Thread(target=quote_announce, daemon=True).start()  # ⬅️ INI DIPANGGIL
            threading.Thread(target=solat_notification, daemon=True).start()
            threading.Thread(target=monitor_connection, daemon=True).start()
            threading.Thread(target=cleanup_timeouts, daemon=True).start()

            self.log("🔄 Services started")

    def do_hourly_announce(self, waktu):
        """Hourly weather announcement"""
        self.log(f"🕐 hourly: {waktu.hour}:00")

        for channel in CHANNELS:
            if channel in self.joined_channels:
                cuaca = self.data.get_cuaca_detail("Kuala Lumpur")
                if cuaca:
                    lines = self.display.format_cuaca_jelas(cuaca)
                    self.send_multiple(channel, lines)
                    time.sleep(3)

    def do_quote_announce(self):
        """15-minute quote announcement - DEBUG VERSION"""
        try:
            self.log("="*60)
            self.log("💭💭💭 DO_QUOTE_ANNOUNCE STARTED 💭💭💭")

            # Debug 1: Check connection status
            self.log(f"🔌 Connection status: {self.connected}")
            self.log(f"🔌 Socket exists: {self.sock is not None}")

            # Debug 2: Check joined channels
            self.log(f"📊 Joined channels count: {len(self.joined_channels)}")
            self.log(f"📊 Joined channels list: {list(self.joined_channels)}")

            # Debug 3: Check jika ada channel
            if not self.joined_channels:
                self.log("❌ CRITICAL: No channels joined!")
                # Cuba join semula
                for channel in CHANNELS:
                    try:
                        self.send_raw(f"JOIN {channel}")
                        self.joined_channels.add(channel)
                        self.log(f"🔄 Re-joined {channel}")
                        time.sleep(1)
                    except Exception as e:
                        self.log(f"❌ Failed to join {channel}: {e}")

            # Get quote
            self.log("🤖 Getting AI quote...")
            quote = self.get_ai_quote()

            if not quote:
                self.log("❌ No quote generated, using fallback")
                quote = self.get_fallback_quote()

            self.log(f"✅ Quote ready: {quote[:80]}...")

            # Post to channels
            success_count = 0
            failed_count = 0

            for channel in list(self.joined_channels):
                try:
                    if not channel or not channel.startswith('#'):
                        self.log(f"⚠️ Skipping invalid channel: {channel}")
                        continue

                    self.log(f"📤 Attempting to post to {channel}...")

                    # Test connection dulu dengan PING
                    try:
                        self.send_raw(f"PING :{channel}_test")
                    except Exception as e:
                        self.log(f"❌ Socket test failed for {channel}: {e}")
                        continue

                    # Post quote
                    full_message = f"💭 {quote}"

                    # Trim jika terlalu panjang
                    if len(full_message) > MAX_MESSAGE_LENGTH:
                        full_message = full_message[:MAX_MESSAGE_LENGTH-3] + "..."

                    self.log(f"📝 Message to send: {full_message[:50]}...")

                    # Send message
                    result = self.send(channel, full_message)

                    if result:
                        self.log(f"✅ SUCCESS: Posted to {channel}")
                        success_count += 1
                    else:
                        self.log(f"❌ FAILED: Send() returned False for {channel}")
                        failed_count += 1

                    # Delay antara channel
                    time.sleep(2)

                except Exception as e:
                    self.log(f"❌ ERROR posting to {channel}: {str(e)}")
                    failed_count += 1

            # Summary
            self.log(f"📊 SUMMARY: Success={success_count}, Failed={failed_count}")

            if success_count > 0:
                self.stats['auto_quotes'] += 1
                self.log(f"✅ Auto quote completed, posted to {success_count} channel(s)")
            else:
                self.log("❌ Auto quote FAILED - No channels received quote")

            self.log("="*60)

        except Exception as e:
            self.log(f"❌ CRITICAL ERROR in do_quote_announce: {str(e)}")
            import traceback
            self.log(f"❌ Traceback: {traceback.format_exc()}")

    def handle_kick(self, channel, kicked_nick):
        """Handle kick dari channel"""
        if kicked_nick == self.nick:
            self.log(f"⚠️ Kicked from {channel}")
            self.joined_channels.discard(channel)
            self.stats['kicks'] += 1

            # Auto rejoin selepas delay
            time.sleep(RETRY_DELAY)
            if self.connected:
                self.send_raw(f"JOIN {channel}")
                self.log(f"🔄 Rejoined {channel}")
                self.joined_channels.add(channel)
                self.stats['rejoins'] += 1

    def send(self, target, msg):
        """Kirim message ke channel - RETURN STATUS"""
        try:
            if len(msg) > MAX_MESSAGE_LENGTH:
                msg = msg[:MAX_MESSAGE_LENGTH-3] + "..."

            # Debug log
            self.log(f"📤 SEND: PRIVMSG {target} :{msg[:50]}...")

            # Check socket
            if not self.sock:
                self.log("❌ SEND ERROR: No socket")
                self.connected = False
                return False

            # Send menggunakan send_raw
            success = self.send_raw(f"PRIVMSG {target} :{msg}")

            if success:
                self.log(f"✅ SEND SUCCESS to {target}")
            else:
                self.log(f"❌ SEND FAILED to {target}")

            return success

        except Exception as e:
            self.log(f"❌ SEND EXCEPTION: {str(e)}")
            return False
    
    def is_duplicate_message(self, nick, channel, message):
        """Check jika message sama dari user yang sama dalam window time"""
        try:
            # Clean message untuk comparison
            clean_msg = message.strip().lower()

            # Initialize structures jika belum ada
            if channel not in self.last_messages:
                self.last_messages[channel] = {}

            current_time = time.time()

            # Check jika nick ada dalam history
            if nick in self.last_messages[channel]:
                last_msg, last_time = self.last_messages[channel][nick]

                # Check jika masih dalam window time dan message sama
                if (current_time - last_time) < self.duplicate_window:
                    if clean_msg == last_msg.lower():
                        self.log(f"🚫 Duplicate message from {nick}: '{message[:30]}...'")
                        return True

            # Update history
            self.last_messages[channel][nick] = (clean_msg, current_time)

            # Clean old entries
            self.clean_message_history()

            return False

        except Exception as e:
            self.log(f"⚠️ Duplicate check error: {e}")
            return False

    def clean_message_history(self):
        """Clean old message history"""
        try:
            current_time = time.time()

            for channel in list(self.last_messages.keys()):
                for nick in list(self.last_messages[channel].keys()):
                    _, msg_time = self.last_messages[channel][nick]

                    # Remove jika lebih lama dari window
                    if (current_time - msg_time) > self.duplicate_window:
                        del self.last_messages[channel][nick]

                # Remove empty channels
                if not self.last_messages[channel]:
                    del self.last_messages[channel]

        except Exception as e:
            self.log(f"⚠️ Clean history error: {e}")

    def handle_greeting(self, nick, channel, message):
        """Handle greetings dengan deduplication"""
        try:
            # Check duplicate message dulu
            if self.is_duplicate_message(nick, channel, message):
                return False  # Skip duplicate

            message_lower = message.lower().strip()

            if not message_lower:
                return False

            words = message_lower.split()
            if not words:
                return False

            first_word = words[0]

            # Greeting words
            greeting_words = ['hi', 'hello', 'hey', 'halo', 'hai', 'salam']

            if first_word in greeting_words:
                # Check jika greeting kepada bot
                if self.nick.lower() in message_lower:
                    # Simple reply dengan delay random
                    time.sleep(random.uniform(0.5, 1.5))

                    responses = [
                        f"Hai {nick}",
                        f"Hello {nick}",
                        f"Salam {nick}"
                    ]
                    import random
                    response = random.choice(responses)
                    self.send(channel, response)
                    self.stats['greeting_responses'] += 1
                    return False # kalau nak enable AI response, guna True

            return False

        except Exception as e:
            self.log(f"❌ Greeting error: {e}")
            return False

        def handle_mention(self, nick, channel, message):
            """Handle mentions - FIXED untuk elak false positives"""
            try:
                import re

                # ⭐⭐ FIX: Gunakan regex untuk exact mention ⭐⭐
                message_lower = message.lower()
                nick_lower = self.nick.lower()

                # Pattern untuk detect mention yang betul
                # 1. @www (dengan prefix @)
                # 2. www: atau www, (dengan punctuation)
                # 3. www (sebagai standalone word)
                # 4. Diawal ayat: "www apa khabar?"

                mention_patterns = [
                    r'^@' + re.escape(nick_lower) + r'\b',      # @www diawal
                    r'\s@' + re.escape(nick_lower) + r'\b',     # @www ditengah
                    r'^' + re.escape(nick_lower) + r'[:,]?\s',  # www: diawal
                    r'\s' + re.escape(nick_lower) + r'[:,]?\s', # www: ditengah
                    r'\b' + re.escape(nick_lower) + r'\b',      # www sebagai word
                ]

                is_mention = False
                for pattern in mention_patterns:
                    if re.search(pattern, message_lower):
                        is_mention = True
                        break

                # ⭐⭐ SPECIAL CASE: Elak false positive untuk "wowww", "swww", etc ⭐⭐
                # Jika message mengandungi "www" tapi bukan sebagai standalone word
                if nick_lower in message_lower and not is_mention:
                    # Check jika "www" adalah substring dari word lain
                    words = message_lower.split()
                    for word in words:
                        if nick_lower in word and nick_lower != word:
                            # Contoh: "wowww" mengandungi "www" tapi bukan "www" sahaja
                            self.log(f"⚠️ False positive detected: '{word}' contains '{nick_lower}' but is not a mention")
                            return False

                if not is_mention:
                    return False

                # ⭐⭐ CHECK REPEAT DENGAN CHANNEL PARAMETER ⭐⭐
                if self.is_repeat_spam(nick, message, channel):  # Pass channel!
                    self.log(f"🚫 Anti-repeat blocked reply to {nick}")
                    return False  # Tidak reply apa-apa

                # Rate limiting check (existing)
                current_time = time.time()
                if nick in self.last_response_time:
                    if current_time - self.last_response_time[nick] < 2.5:
                        self.log(f"⏰ Mention rate limited: {nick}")
                        self.send(channel, f"{nick}: Tunggu sebentar")
                        return True

                self.last_response_time[nick] = current_time

                # Record start time
                start_time = time.time()

                # Clean message untuk AI (remove bot name)
                cleaned_msg = message
                cleaned_msg = cleaned_msg.replace(self.nick.lower(), '').replace(self.nick, '')
                cleaned_msg = cleaned_msg.replace('@', '').strip()

                # Jika message kosong selepas remove bot name
                if not cleaned_msg or len(cleaned_msg) < 2:
                    cleaned_msg = "hello"  # Default prompt

                self.log(f"🤖 Processing mention: '{cleaned_msg[:100]}...'")

                # Show thinking message dengan CTCP ACTION
                thinking_action = f" is typing..."
                self.send_action(channel, thinking_action)

                # MINIMUM THINKING TIME: 3 saat
                elapsed_time = time.time() - start_time
                if elapsed_time < 3.0:
                    time.sleep(3.0 - elapsed_time)

                # Get AI response
                response_text = self.query_groq_ai(cleaned_msg, nick)

                # Calculate total processing time
                total_time = time.time() - start_time
                self.log(f"⏱️ Mention processed in {total_time:.2f} seconds")

                if not response_text or response_text.strip() == "":
                    response_text = f"{nick}: Ya?"

                # Clean sweet emojis jika ada
                sweet_emojis = ['🍬', '🍭', '🍫', '🍡', '🧁', '🍪']
                for emoji in sweet_emojis:
                    response_text = response_text.replace(emoji, '')

                # Split jika panjang
                lines = self.split_ai_response(response_text, max_lines=2, chars_per_line=100)

                # Send response
                if len(lines) == 1:
                    self.send(channel, lines[0])
                else:
                    for i, line in enumerate(lines):
                        self.send(channel, line)
                        if i < len(lines) - 1:
                            time.sleep(2)

                self.update_stats('ai_responses')
                return True

            except Exception as e:
                self.log(f"❌ Mention handler error: {e}")
                self.send(channel, f"{nick}: Ya?")
                return True

    def is_valid_mention(self, message):
        """Check jika message benar-benar mention bot"""
        import re

        message_lower = message.lower()
        bot_nick = self.nick.lower()

        # List of common false positives
        false_positives = [
            'wowww', 'swww', 'twww', 'awww', 'ewww', 'owww',
            'wwws', 'wwww', 'wwwe', 'wwwa', 'wwwt'
        ]

        # Check jika message mengandungi false positive
        for fp in false_positives:
            if fp in message_lower:
                return False

        # Pattern untuk valid mention
        patterns = [
            # @www
            r'@' + re.escape(bot_nick) + r'(\s|$|[:,!?])',
            # www: atau www,
            r'\b' + re.escape(bot_nick) + r'[:,](\s|$)',
            # www (sebagai word dengan spaces atau punctuation)
            r'(\s|^)' + re.escape(bot_nick) + r'(\s|$|[:,!?])',
        ]

        for pattern in patterns:
            if re.search(pattern, message_lower):
                return True

        return False
    
    def join_channels_backup(self):
        """Backup method untuk join channels"""
        self.log("🔄 Backup: Joining channels...")

        for channel in CHANNELS:
            try:
                self.send_raw(f"JOIN {channel}")
                self.log(f"  🔄 Backup join {channel}")
                time.sleep(1)
            except Exception as e:
                self.log(f"  ❌ Backup join failed for {channel}: {e}")

    def run(self):
        """Main run method - GABUNGAN DENGAN UPDATES"""
        if not self.connect():
            return

        self.start_services()

        self.log(f"🚀 Bot running! Press Ctrl+C to stop")
        self.log("="*60)

        # ⭐⭐⭐ BACKUP AUTO-JOIN - jika connect() gagal join ⭐⭐⭐
        if self.connected and not self.joined_channels:
            self.log("⚠️ Connected but no channels joined, attempting backup join...")
            self.join_channels_backup()

        # Test API dulu
        self.log("🔍 Testing APIs...")
        cuaca_test = self.data.get_cuaca_detail("Kuala Lumpur")
        solat_kl_test = self.data.get_solat("Kuala Lumpur")

        if cuaca_test:
            self.log(f"✅ Cuaca API (KL): {cuaca_test['lokasi']} {cuaca_test['suhu']}°C")
        else:
            self.log("❌ Cuaca API (KL) failed")

        if solat_kl_test:
            self.log(f"✅ Solat API (KL): {solat_kl_test['lokasi']} Maghrib={solat_kl_test['maghrib']}")
        else:
            self.log("❌ Solat API (KL) failed")

        self.log("="*60)

        buffer = ""

        try:
            while self.running:
                try:
                    ready, _, _ = select.select([self.sock], [], [], 5)

                    if ready:
                        data = self.sock.recv(4096).decode('utf-8', errors='ignore')
                        if not data:
                            self.log("⚠️ Connection closed by server")
                            self.connected = False
                            break

                        buffer += data
                        self.stats['messages_received'] += 1

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

                            # Handle CTCP reply
                            if self.handle_ctcp_reply(line):
                                continue

                            # ⭐⭐⭐ AUTO-JOIN LOGIC YANG SEBENAR ⭐⭐⭐
                            # Check jika sudah registered/connected
                            if not self.motd_received:
                                # Server messages yang indicate ready
                                if any(x in line for x in [' 001 ', ' 002 ', ' 003 ', ' 004 ', ' 005 ', ' 376 ', ' 422 ']):
                                    self.motd_received = True
                                    self.log("✅ Server ready, joining channels...")

                                    # ⭐⭐⭐ ACTUALLY JOIN CHANNELS ⭐⭐⭐
                                    for channel in CHANNELS:
                                        self.send_raw(f"JOIN {channel}")
                                        self.log(f"  → Joining {channel}")
                                        time.sleep(1)  # Delay untuk avoid flood
                                    continue

                            # Handle KICK
                            if "KICK" in line and self.nick in line:
                                parts = line.split()
                                if len(parts) >= 4:
                                    channel = parts[2]
                                    kicked_nick = parts[3]
                                    if kicked_nick == self.nick:
                                        self.handle_kick(channel, kicked_nick)
                                continue

                            # Handle PRIVMSG (commands)
                            if "PRIVMSG" in line:
                                try:
                                    # Simple parsing untuk IRC message
                                    # Format: :nick!user@host PRIVMSG #channel :message

                                    # Cari position PRIVMSG
                                    privmsg_index = line.find(" PRIVMSG ")
                                    if privmsg_index == -1:
                                        continue

                                    # Bahagian sebelum PRIVMSG
                                    prefix = line[:privmsg_index]
                                    if prefix.startswith(":"):
                                        prefix = prefix[1:]

                                    # Dapatkan nick
                                    nick_end = prefix.find("!")
                                    if nick_end > 0:
                                        nick = prefix[:nick_end]
                                    else:
                                        nick = prefix

                                    # Bahagian selepas PRIVMSG
                                    after_privmsg = line[privmsg_index + 9:]  # " PRIVMSG " = 9 chars

                                    # Dapatkan channel dan message
                                    channel_end = after_privmsg.find(" :")
                                    if channel_end > 0:
                                        target = after_privmsg[:channel_end]
                                        message = after_privmsg[channel_end + 2:]  # Skip " :"
                                    else:
                                        # Jika tiada message
                                        target = after_privmsg.strip()
                                        message = ""

                                    # Skip jika message dari bot sendiri
                                    if nick == self.nick:
                                        continue

                                    # Jika message ke channel
                                    if target in CHANNELS:
                                        self.log(f"📨 {nick} -> {target}: '{message[:50]}...'")

                                        # ⭐⭐⭐ GUNA process_message() UNTUK SEMUA MESSAGE PROCESSING ⭐⭐⭐
                                        # Ini untuk elak duplicate logic
                                        responses = self.process_message(nick, message, target)

                                        # Jika ada responses dari process_message(), kirim
                                        if responses:
                                            self.log(f"📤 Sending {len(responses)} responses from process_message...")
                                            for bot_type, response in responses:
                                                if response and response.strip():
                                                    self.send(target, response)

                                        # ⭐⭐⭐ TAPI KITA MASIH PERLU HANDLE .PING DI SINI ⭐⭐⭐
                                        # Kerana process_message() anda mungkin skip .ping
                                        elif message.strip().lower() in ['.ping']:
                                            self.log(f"🎯 .ping command from {nick} (handled in run())")
                                            hostmask = prefix
                                            self.handle_ping_request(nick, target, hostmask)

                                        # ⭐⭐⭐ TAMBAH .wc & .wb DI SINI ⭐⭐⭐
                                        elif message.lower().startswith('.wc') or message.lower().startswith('.wb'):
                                            try:
                                                parts = message.strip().split()
                                                cmd = parts[0].lower()
                                                target_nick = parts[1] if len(parts) > 1 else nick

                                                # ⭐⭐⭐ COOLDOWN HANYA UNTUK .wc/.wb ⭐⭐⭐
                                                # Guna key yang spesifik untuk command ini sahaja
                                                key = f"welcome_cmd:{nick}:{target_nick}"
                                                if not hasattr(self, 'welcome_cooldown'):
                                                    self.welcome_cooldown = {}

                                                current_time = time.time()
                                                if key in self.welcome_cooldown:
                                                    time_diff = current_time - self.welcome_cooldown[key]
                                                    if time_diff < 2:  # 2 saat cooldown
                                                        self.send(target, f"⏳ {nick}: Tunggu {2-time_diff:.1f} saat sebelum tanya lagi")
                                                        continue

                                                self.welcome_cooldown[key] = current_time

                                                # ⭐⭐⭐ BACA WC/WB DENGAN SEQUENCE ⭐⭐⭐
                                                f1 = 'wb.txt' if cmd == '.wb' else 'wc.txt'
                                                msg = ""

                                                # Initialize counter jika belum ada
                                                if not hasattr(self, 'wc_counter'):
                                                    self.wc_counter = 0
                                                if not hasattr(self, 'wb_counter'):
                                                    self.wb_counter = 0

                                                try:
                                                    with open(f1, 'r', encoding='utf-8') as f:
                                                        lines = f.readlines()
                                                        if lines:
                                                            if cmd == '.wb':
                                                                current_line = lines[self.wb_counter % len(lines)]
                                                                self.wb_counter += 1
                                                            else:
                                                                current_line = lines[self.wc_counter % len(lines)]
                                                                self.wc_counter += 1
                                                            msg = current_line.strip().replace('$nick', target_nick)
                                                        else:
                                                            msg = f"{target_nick}! 🎉 Akhirnya kamu kembali!"
                                                except Exception as e:
                                                    print(f"❌ Error reading {f1}: {e}")
                                                    msg = f"{target_nick}! 🎉 Akhirnya kamu kembali!"

                                                # ⭐⭐⭐ TIMER 1.5 SAAT SEBELUM RESPON ⭐⭐⭐
                                                time.sleep(1.5)  # Delay 1.5 saat
                                                
                                                # ⭐⭐⭐ BACA MOTIVASI DENGAN SEQUENCE ⭐⭐⭐
                                                motiv = ""
                                                if not hasattr(self, 'motiv_counter'):
                                                    self.motiv_counter = 0

                                                try:
                                                    with open('motivasi.txt', 'r', encoding='utf-8') as f:
                                                        motiv_lines = f.readlines()
                                                        if motiv_lines:
                                                            current_motiv = motiv_lines[self.motiv_counter % len(motiv_lines)]
                                                            self.motiv_counter += 1
                                                            motiv = current_motiv.strip()
                                                except:
                                                    motiv = "Teruskan perjuangan, pasti ada cahaya di hujungnya! 🌅"

                                                # ⭐⭐⭐ BORDER ⭐⭐⭐
                                                border = ""
                                                try:
                                                    with open('border.txt', 'r', encoding='utf-8') as f:
                                                        border_line = f.readline().strip()
                                                        if border_line:
                                                            border = border_line.replace('{text}', target_nick)
                                                        else:
                                                            border = f"✰❄ {target_nick} ❄★"
                                                except:
                                                    border = f"✰❄ {target_nick} ❄★"

                                                # ⭐⭐⭐ FORMAT OUTPUT ⭐⭐⭐
                                                response = f"welcome {target_nick} {msg} {motiv} {border}"
                                                self.send(target, response.strip())

                                            except Exception as e:
                                                print(f"❌ Welcome error: {e}")
                                                self.send(target, f"Welcom {target_nick if 'target_nick' in locals() else nick}")

                                        # ⭐⭐ FALLBACK: Jika process_message() return None dan bukan .ping
                                        # Kita mungkin nak handle mentions atau AI di sini
                                        elif self.should_use_ai(message):
                                            self.log(f"🤖 AI trigger for message from {nick}")
                                            self.handle_ai_request(nick, target, message)

                                        # Optional: Handle other commands secara langsung
                                        elif message.startswith('!') and not responses:
                                            response = self.handle_command(nick, target, message)
                                            if response:
                                                if isinstance(response, list):
                                                    for line in response[:3]:
                                                        if line and line.strip():
                                                            self.send(target, line)
                                                            time.sleep(1.5)
                                                else:
                                                    if response and response.strip():
                                                        self.send(target, response)

                                except Exception as e:
                                    self.log(f"⚠️ Parse error: {e}")
                                    self.stats['errors'] += 1

                    # ⭐⭐⭐ JANGAN PANGGIL AUTO-UPDATES DI SINI ⭐⭐⭐
                    # if self.connected:
                    #     self.check_and_post_auto_updates()
                    # ⭐⭐⭐ SUDAH ADA DALAM THREAD auto_updates_loop() ⭐⭐⭐

                except Exception as e:
                    self.log(f"⚠️ Loop error: {e}")
                    self.stats['errors'] += 1
                    time.sleep(5)

        except KeyboardInterrupt:
            self.log("⏹️ Stopping bot...")
        finally:
            self.running = False
            if self.sock:
                self.send_raw("QUIT :Goodbye!")
                time.sleep(1)
                self.sock.close()
            self.log("👋 Bot stopped")

if __name__ == "__main__":
    print("🤖 WWW BOT COMBINED - ALL FEATURES")
    print("="*70)
    print("🔧 FEATURES:")
    print("• Weather: Global support via geocoding API")
    print("• Prayer: Malaysia dengan zone mapping yang betul")
    print("• Ping: CTCP with sweet messages")
    print("• AI: Groq LLM with smart question detection")
    print("• Auto: Hourly weather + 15min quotes")
    print("• Commands: !cuaca !wsolat !waktu !ai .ping .help .stats")
    print("="*70)
    print("\n🚀 Starting bot...")

    bot = WWWBotCombined()
    bot.run()
