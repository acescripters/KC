🤖 Trio IRC AI Bot
Bot ini dicipta untuk manfaat manusia dan A.I sendiri. Semoga ini menjadi titik perubahan ke next level.
This bot is created for the benefit of humans and A.I. May this be a turning point to the next level.

🌟 Features
Dual Bot System - www (Master) & deep (Client) running simultaneously

AI-Powered - Integrated with Groq, DeepSeek, and Gemini APIs

Smart Response - Context-aware conversations with mention detection

Real Ping Monitoring - Active connection health monitoring

Focus System - Intelligent response filtering

Time Announcements - Automated prayer time notifications

Auto-Reconnect - Automatic rejoin on kick/disconnect

🚀 Quick Start
Prerequisites
Python 3.8+

IRC Server Access

AI API Keys (Groq/DeepSeek/Gemini)

Installation
bash
# Clone repository
git clone https://github.com/username/dual-bot-irc.git
cd dual-bot-irc

# Install dependencies
pip install -r requirements.txt
Configuration
Edit config.py with your settings:

python
SERVER = "irc.kampungchat.org"
PORT = 6668
CHANNELS = ["#ace", "#amboi"]
# Add your API keys in api.py
Running the Bot
bash
python3 main.py
🏗️ Project Structure
text
dual-bot-irc/
├── main.py          # 🎯 Entry point - API scan & auto connect
├── dual.py          # 🤖 Core dual bot system
├── events.py        # 💬 Message event handlers
├── api.py           # 🧠 AI API integration manager
├── ctcp.py          # 📊 Real ping monitoring
├── waktu.py         # 🕐 Time announcement system
├── prompt.py        # 🎨 Beautiful console prompts
├── config.py        # ⚙️ Configuration settings
├── focus.py         # 🎯 Intelligent focus system
├── requirements.txt # 📦 Dependencies
└── README.md        # 📚 Documentation
🔧 Core Components
🤖 Dual Bot System (dual.py)
Manages two simultaneous bot connections

Handles PING-PONG for connection stability

Smart mention detection and response filtering

Auto-rejoin on kick events

🧠 AI Integration (api.py)
Multi-API Fallback - Groq → DeepSeek → Gemini

Smart Response Generation - Context-aware replies

API Health Monitoring - Automatic failover

Request Optimization - Efficient token usage

💬 Event Handling (events.py)
PRIVMSG, ACTION, NOTICE message processing

Basic command recognition

AI response generation with context

Anti-spam and rate limiting

📊 Connection Health (ctcp.py)
Real PING-PONG monitoring (not simulation)

Connection timeout alerts

Bot status tracking (ALIVE/TIMEOUT)

Automatic health reporting

🎯 Usage Examples
Basic Interaction
text
User: hi www
www: Hello! 👋 How can I assist you today?

User: deep, what's the weather?
deep: According to current data, weather is sunny with 25°C! ☀️
AI-Powered Conversations
text
User: www: explain quantum computing
www: Quantum computing uses qubits to process information in ways classical computers can't...

User: deep: tell me a joke
deep: Why don't scientists trust atoms? Because they make up everything! 😄
Bot Management
text
!focus status    # Check focus mode
!silent on       # Enable silent mode
!api status      # Check API health
!stats           # View bot statistics
⚙️ Configuration
API Keys Setup
Edit api.py with your keys:

python
self.apis = {
    "groq": {
        "key": "your_groq_key_here",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.1-8b-instant"
    },
    # ... other APIs
}
IRC Configuration
Edit config.py:

python
SERVER = "irc.rizon.net"
PORT = 6667
CHANNELS = ["#your-channel"]
NICKSERV_PASSWORD = "your_password"
🔄 Advanced Features
Focus System
Silent Mode - Respond only to mentions

Focus Mode - Respond only to focused users

Public Mode - Respond to all messages

Auto-Focus - Automatic focus on interaction

Ping Monitoring
Real-time connection health tracking

Automatic timeout detection

Detailed connection statistics

Alert system for connection issues

Time Management
Automated time announcements

Customizable announcement intervals

Multi-timezone support

Beautiful formatted output

🛠️ Troubleshooting
Common Issues
Connection Timeout

Check firewall settings

Verify server address and port

Ensure stable internet connection

API Errors

Verify API keys are valid

Check API rate limits

Monitor API health status

Bot Not Responding

Check focus mode settings

Verify mention detection

Monitor debug output

Debug Mode
Run with debug output:

bash
python3 main.py --debug
🤝 Contributing
We welcome contributions! Please feel free to submit pull requests, report bugs, or suggest new features.

📄 License
This project is open source and available under the MIT License.

🙏 Acknowledgments
Built for educational and research purposes

Special thanks to the AI and open-source communities

Inspired by the potential of human-AI collaboration

"Demi masa, sesungguhnya manusia dalam kerugian, kecuali orang-orang yang beriman dan beramal soleh, dan mereka pula berpesan-pesan dengan kebenaran serta berpesan-pesan dengan kesabaran." - Surah Al-Asr

Let's build the future together! 🚀
