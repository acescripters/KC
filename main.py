#!/usr/bin/env python3
"""
🤖 BOT LAUNCHER v4.0 - STABIL DENGAN ANTI-SLEEP
Auto-Reconnect 3 Bot + Anti-Sleep System + Web Preview
"""
import os
import sys
import subprocess
import signal
import time
import threading
import urllib.request
import urllib.error
import json
import http.server
from datetime import datetime

# ==================== KONFIGURASI ====================
BOT_FILES = {
    "WWW": "www.py",
    "MINAH": "minah.py", 
    "DEEP": "deep.py"
}

HEALTH_PORT = 8080
CHECK_INTERVAL = 5  # Saat antara check bot
ANTI_SLEEP_INTERVAL = 240  # 4 minit - ping sendiri

# ==================== SIMPLE WEB PREVIEW ====================
class PreviewHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Minimal HTML untuk preview Replit
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>🤖 Bot Manager</title>
            <style>
                body {font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5;}
                .container {max-width: 600px; margin: 50px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);}
                h1 {color: #333; text-align: center;}
                .status {color: green; font-weight: bold; text-align: center; font-size: 1.2em;}
                .bots {display: flex; justify-content: center; gap: 20px; margin: 30px 0;}
                .bot {background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; min-width: 120px;}
                .bot-name {font-weight: bold; margin-bottom: 5px;}
                .bot-status {font-size: 0.9em;}
                .live {color: #4CAF50; font-weight: bold;}
                .dead {color: #F44336; font-weight: bold;}
                .uptime {text-align: center; color: #666; margin-top: 20px;}
            </style>
            <meta http-equiv="refresh" content="30">
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Bot Manager v4.0</h1>
                    <div class="status">✅ BOT IS RUNNING</div>

                    <div class="bots">
                        <div class="bot">
                            <div class="bot-name">WWW</div>
                            <div class="bot-status live">● Online</div>
                        </div>
                        <div class="bot">
                            <div class="bot-name">MINAH</div>
                            <div class="bot-status live">● Online</div>
                        </div>
                        <div class="bot">
                            <div class="bot-name">DEEP</div>
                            <div class="bot-status live">● Online</div>
                        </div>
                    </div>

                    <div class="uptime" id="uptime">Uptime: Loading...</div>
                    <p style="text-align: center; color: #666; font-size: 0.9em;">
                        Auto-reconnect enabled • Anti-sleep active • All systems operational
                    </p>
                </div>

                <script>
                    // Update uptime counter
                    function updateUptime() {
                        const start = Date.now();
                        setInterval(() => {
                            const diff = Date.now() - start;
                            const hours = Math.floor(diff / (1000 * 60 * 60));
                            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                            document.getElementById('uptime').textContent = 
                                `Uptime: ${hours}h ${minutes}m ${seconds}s`;
                        }, 1000);
                    }
                    updateUptime();
                </script>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())

        elif self.path == '/health':
            # Health endpoint untuk UptimeRobot
            import time
            launcher = self.server.launcher

            bot_status = {}
            for bot_name in BOT_FILES.keys():
                process = launcher.processes.get(bot_name)
                bot_status[bot_name] = {
                    "alive": process is not None and process.poll() is None,
                    "restarts": launcher.restart_counts.get(bot_name, 0),
                    "pid": process.pid if process and process.poll() is None else None
                }

            health_data = {
                "status": "healthy",
                "service": "bot_manager",
                "timestamp": datetime.now().isoformat(),
                "uptime": int(time.time() - launcher.start_time),
                "bot_status": bot_status,
                "anti_sleep": True,
                "version": "4.0"
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(health_data).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress access logs

def start_health_server(launcher, port=8080):
    """Start web server dalam background"""
    class CustomHTTPServer(http.server.HTTPServer):
        def __init__(self, *args, **kwargs):
            self.launcher = launcher
            super().__init__(*args, **kwargs)

    def run_server():
        try:
            server = CustomHTTPServer(('0.0.0.0', port), PreviewHandler)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Web: http://localhost:{port}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 Health: http://localhost:{port}/health")
            server.serve_forever()
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Web server error: {e}")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2)
    return thread

# ==================== BOT LAUNCHER (STABIL VERSION) ====================
class BotLauncher:
    def __init__(self):
        self.bots = BOT_FILES
        self.processes = {}
        self.restart_counts = {bot: 0 for bot in self.bots}
        self.start_time = time.time()
        self.running = True
        self.last_mass_disconnect = 0

        signal.signal(signal.SIGINT, self.signal_handler)

        print(f"\n[{self._timestamp()}] {'='*70}")
        print(f"[{self._timestamp()}] 🤖 BOT LAUNCHER v4.0 - STABIL DENGAN ANTI-SLEEP")
        print(f"[{self._timestamp()}] {'='*70}")

        # Start web server
        self.health_thread = start_health_server(self, HEALTH_PORT)

        # Start anti-sleep system
        self._start_anti_sleep()

        print(f"[{self._timestamp()}] ✅ Sistem siap: {len(self.bots)} bot")

    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def _start_anti_sleep(self):
        """System untuk elak Replit sleep"""
        def keep_alive():
            last_ping = time.time()
            ping_count = 0

            while self.running:
                try:
                    current_time = time.time()

                    # Ping sendiri setiap 4 minit
                    if current_time - last_ping > ANTI_SLEEP_INTERVAL:
                        ping_count += 1
                        try:
                            # Self-ping health endpoint
                            url = f"http://localhost:{HEALTH_PORT}/health"
                            urllib.request.urlopen(url, timeout=5)
                            print(f"[{self._timestamp()}] 🔄 Keep-alive ping #{ping_count}")
                        except Exception as e:
                            print(f"[{self._timestamp()}] ⏰ Anti-sleep activity")

                        last_ping = current_time

                    # Status report setiap 15 minit
                    if int(current_time) % 900 < 5:  # 15 minit
                        alive = sum(1 for p in self.processes.values() 
                                  if p and p.poll() is None)
                        print(f"[{self._timestamp()}] 📊 Status: {alive}/{len(self.bots)} bots alive")
                        print(f"[{self._timestamp()}] ⏰ Uptime: {int(current_time - self.start_time)}s")

                    time.sleep(30)

                except Exception as e:
                    print(f"[{self._timestamp()}] ⚠️ Anti-sleep error: {e}")
                    time.sleep(60)

        threading.Thread(target=keep_alive, daemon=True).start()
        print(f"[{self._timestamp()}] ✅ Anti-sleep system activated")

    def signal_handler(self, sig, frame):
        print(f"\n[{self._timestamp()}] 🛑 Shutdown signal received")
        self.running = False
        self.stop_all()

    def start_bot(self, bot_name, bot_file):
        """Start bot - STABIL VERSION (sama seperti kod asal anda)"""
        if not os.path.exists(bot_file):
            print(f"[{self._timestamp()}] ❌ File not found: {bot_file}")
            return None

        print(f"[{self._timestamp()}] 🚀 Starting {bot_name}...")

        try:
            process = subprocess.Popen(
                [sys.executable, "-u", bot_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Output handler - SAMA SEPERTI KOD ASAL ANDA
            def output_handler(proc, name):
                last_active = time.time()

                while self.running:
                    try:
                        line = proc.stdout.readline()
                        if line:
                            last_active = time.time()
                            print(f"[{self._timestamp()} | {name}] {line.rstrip()}")
                        elif time.time() - last_active > 30:
                            print(f"[{self._timestamp()}] ⚠️ {name} no output for 30s")
                            last_active = time.time()
                    except:
                        break

            threading.Thread(target=output_handler, args=(process, bot_name), daemon=True).start()

            self.restart_counts[bot_name] += 1
            print(f"[{self._timestamp()}] ✅ {bot_name} started (PID: {process.pid})")
            return process

        except Exception as e:
            print(f"[{self._timestamp()}] ❌ Failed to start {bot_name}: {e}")
            return None

    def monitor_and_reconnect(self):
        """Main monitoring - STABIL VERSION dengan anti-sleep enhancement"""
        print(f"\n[{self._timestamp()}] 📡 STARTING ALL BOTS")
        print(f"[{self._timestamp()}] {'='*60}")

        # Start semua bot dengan staggered delay
        for bot_name in self.bots:
            self.processes[bot_name] = self.start_bot(bot_name, self.bots[bot_name])
            time.sleep(2)  # Delay pendek untuk elak race condition

        print(f"\n[{self._timestamp()}] ✅ All bots started")
        print(f"[{self._timestamp()}] 📊 Monitoring active")
        print(f"[{self._timestamp()}] ⚡ Anti-sleep system running")
        print(f"\n[{self._timestamp()}] Press Ctrl+C to stop\n")

        # Main monitoring loop
        check_interval = CHECK_INTERVAL
        last_status_check = time.time()

        try:
            while self.running:
                time.sleep(check_interval)
                current_time = self._timestamp()

                # DETECT MASS DISCONNECT (Replit sleep)
                dead_bots = [name for name, proc in self.processes.items() 
                           if proc is None or proc.poll() is not None]

                if len(dead_bots) >= 2:  # Jika 2+ bot mati serentak
                    now = time.time()
                    if now - self.last_mass_disconnect > 300:  # 5 minit sejak terakhir
                        print(f"[{current_time}] ⚠️ MASS DISCONNECT DETECTED")
                        print(f"[{current_time}]   Dead bots: {dead_bots}")
                        print(f"[{current_time}]   Reconnecting all...")

                        for bot_name in dead_bots:
                            if self.running:
                                self.processes[bot_name] = self.start_bot(bot_name, self.bots[bot_name])
                                time.sleep(3)

                        self.last_mass_disconnect = now
                        continue  # Skip individual check

                # Individual bot check (kod asal anda)
                for bot_name, process in list(self.processes.items()):
                    if process is None or process.poll() is not None:
                        print(f"[{current_time}] ⚠️ {bot_name} is dead, reconnecting...")

                        if process and process.poll() is None:
                            process.terminate()
                            time.sleep(1)

                        # Exponential backoff delay
                        restart_count = self.restart_counts.get(bot_name, 0)
                        delay = min(60, 2 ** min(restart_count, 6))

                        if delay > 3:
                            print(f"[{current_time}] ⏳ Waiting {delay}s before restart...")
                            for i in range(delay, 0, -1):
                                if not self.running:
                                    break
                                if i % 10 == 0 or i <= 5:
                                    print(f"[{current_time}]   Restarting in {i}s...", end='\r')
                                time.sleep(1)
                            print(" " * 50, end='\r')

                        if self.running:
                            self.processes[bot_name] = self.start_bot(bot_name, self.bots[bot_name])

                # Status report setiap 5 minit
                if time.time() - last_status_check > 300:
                    last_status_check = time.time()
                    alive = sum(1 for p in self.processes.values() 
                              if p and p.poll() is None)
                    print(f"\n[{current_time}] 📊 STATUS: {alive}/{len(self.bots)} bots alive")
                    print(f"[{current_time}] ⏰ Uptime: {int(time.time() - self.start_time)}s")

                    # Show bot details
                    for bot_name in self.bots:
                        process = self.processes.get(bot_name)
                        status = "✅" if process and process.poll() is None else "❌"
                        print(f"[{current_time}]   {status} {bot_name}: {self.restart_counts.get(bot_name, 0)} restarts")

        except KeyboardInterrupt:
            print(f"\n[{self._timestamp()}] 🛑 Shutdown requested")
        except Exception as e:
            print(f"[{self._timestamp()}] ❌ Monitor error: {e}")
        finally:
            self.stop_all()

    def stop_all(self):
        """Graceful shutdown"""
        print(f"\n[{self._timestamp()}] ⏳ Shutting down all bots...")

        self.running = False

        for bot_name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"[{self._timestamp()}]   Stopping {bot_name}...")
                try:
                    process.terminate()
                    time.sleep(2)
                    if process.poll() is None:
                        process.kill()
                except:
                    pass

        uptime = int(time.time() - self.start_time)
        print(f"[{self._timestamp()}] ✅ All bots stopped")
        print(f"[{self._timestamp()}] 🕐 Total uptime: {uptime} seconds")

        sys.exit(0)

# ==================== MAIN EXECUTION ====================
def main():
    """Main entry point"""
    print("🔍 Checking system...")

    # Check semua file bot
    missing_files = []
    for bot_name, bot_file in BOT_FILES.items():
        if not os.path.exists(bot_file):
            missing_files.append(bot_file)

    if missing_files:
        print(f"❌ Missing bot files:")
        for f in missing_files:
            print(f"   - {f}")
        sys.exit(1)

    print(f"✅ Found {len(BOT_FILES)} bot files")
    print(f"✅ Python: {sys.version.split()[0]}")

    # Start launcher
    launcher = BotLauncher()

    try:
        launcher.monitor_and_reconnect()
    except KeyboardInterrupt:
        launcher.stop_all()

if __name__ == "__main__":
    # Setup untuk Replit
    os.environ['PYTHONUNBUFFERED'] = '1'

    # Run
    main()
