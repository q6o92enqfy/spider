import json
import os
import subprocess
import uuid as uuid_lib
import time
from flask import Flask, request, render_template_string

app = Flask(__name__)
CONFIG_PATH = "/usr/local/etc/xray/config.json"
LOG_FILE = "/tmp/xray_status.log"

# ========== قالب HTML با CSS مدرن ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕸️ Spider Pack Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .card {
            max-width: 700px;
            width: 100%;
            background: #1e293b;
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.6);
            border: 1px solid #334155;
        }
        h1 {
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        h1 small {
            font-size: 14px;
            font-weight: normal;
            color: #94a3b8;
            margin-left: auto;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 40px;
            font-size: 13px;
            font-weight: bold;
        }
        .online { background: #22c55e; color: #052e16; }
        .offline { background: #ef4444; color: #7f1d1d; }
        .info-row {
            display: flex;
            justify-content: space-between;
            background: #0f172a;
            padding: 12px 18px;
            border-radius: 16px;
            margin: 15px 0;
            font-size: 14px;
        }
        .info-row span:first-child { color: #94a3b8; }
        .info-row span:last-child { font-weight: 600; }
        form {
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin: 20px 0;
        }
        label {
            font-size: 14px;
            color: #cbd5e1;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        input {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px 16px;
            color: #f1f5f9;
            font-size: 15px;
            transition: 0.2s;
        }
        input:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.3);
        }
        .btn-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 40px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
            flex: 1;
            min-width: 120px;
        }
        .btn:hover { background: #2563eb; transform: scale(1.02); }
        .btn-danger { background: #ef4444; }
        .btn-danger:hover { background: #dc2626; }
        .btn-secondary { background: #475569; }
        .btn-secondary:hover { background: #334155; }
        .link-box {
            background: #0f172a;
            border-radius: 16px;
            padding: 16px;
            margin: 20px 0;
            border: 1px solid #334155;
            position: relative;
        }
        .link-box pre {
            white-space: pre-wrap;
            word-break: break-all;
            font-size: 13px;
            color: #e2e8f0;
            margin-bottom: 10px;
        }
        .copy-btn {
            background: #3b82f6;
            border: none;
            color: white;
            padding: 6px 18px;
            border-radius: 30px;
            font-size: 13px;
            cursor: pointer;
            transition: 0.2s;
        }
        .copy-btn:hover { background: #2563eb; }
        .log-area {
            background: #0f172a;
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 13px;
            color: #94a3b8;
            border: 1px solid #1e293b;
            margin-top: 10px;
            max-height: 60px;
            overflow-y: auto;
        }
        .footer {
            margin-top: 20px;
            text-align: center;
            color: #64748b;
            font-size: 12px;
        }
        @media (max-width: 500px) {
            .card { padding: 20px; }
            .btn-group { flex-direction: column; }
        }
    </style>
</head>
<body>
<div class="card">
    <h1>
        🕸️ Spider Pack
        <small>v2.0</small>
    </h1>

    <div class="info-row">
        <span>📡 وضعیت Xray</span>
        <span>
            <span class="status-badge {{ 'online' if status == 'online' else 'offline' }}">
                {{ 'آنلاین ✅' if status == 'online' else 'آفلاین ❌' }}
            </span>
        </span>
    </div>
    <div class="info-row">
        <span>👥 کلاینت‌های فعال</span>
        <span>{{ clients_count }}</span>
    </div>
    <div class="info-row">
        <span>🌐 دامنه</span>
        <span>{{ domain }}</span>
    </div>

    <form method="POST">
        <label>
            UUID جدید
            <input type="text" name="uuid" value="{{ uuid }}" placeholder="خالی بذارید تا خودکار ساخته شود">
        </label>
        <label>
            مسیر (Path)
            <input type="text" name="path" value="{{ path }}" placeholder="مثلا /spider">
        </label>
        <label>
            پورت اینباند (اختیاری)
            <input type="number" name="port" value="{{ port }}" placeholder="پیش‌فرض: 10086">
        </label>
        <div class="btn-group">
            <button type="submit" class="btn">🔄 بروزرسانی و ری‌استارت</button>
        </div>
    </form>

    <div class="link-box">
        <pre id="vlessLink">vless://{{ uuid }}@{{ domain }}:443?encryption=none&security=tls&sni={{ domain }}&fp=chrome&type=ws&host={{ domain }}&path={{ path }}#SpiderPack</pre>
        <button class="copy-btn" onclick="copyLink()">📋 کپی لینک</button>
    </div>

    <div style="display: flex; gap: 10px; margin-top: 10px;">
        <form method="POST" action="/restart" style="flex:1;">
            <button type="submit" class="btn btn-secondary" style="width:100%;">🔁 ری‌استارت Xray</button>
        </form>
        <form method="POST" action="/reset" style="flex:1;">
            <button type="submit" class="btn btn-danger" style="width:100%;">🔄 بازنشانی کامل</button>
        </form>
    </div>

    <div class="log-area">
        📝 آخرین رویداد: {{ log_message }}
    </div>

    <div class="footer">
        Spider Pack · ساخته شده با ❤️ برای Railway
    </div>
</div>

<script>
function copyLink() {
    const link = document.getElementById('vlessLink').innerText;
    navigator.clipboard.writeText(link).then(() => {
        alert('✅ لینک کپی شد!');
    }).catch(() => {
        const range = document.createRange();
        range.selectNode(document.getElementById('vlessLink'));
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand('copy');
        alert('✅ لینک کپی شد!');
    });
}
</script>
</body>
</html>
"""

# ========== توابع مدیریت ==========

def get_domain():
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN") or os.environ.get("RAILWAY_STATIC_URL") or "your-domain.up.railway.app"
    return domain.replace("https://", "").replace("http://", "")

def read_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except:
        return None

def write_config(uuid, path, port=10086):
    config = {
        "log": { "loglevel": "warning" },
        "inbounds": [
            {
                "listen": "127.0.0.1",
                "port": port,
                "protocol": "vless",
                "settings": {
                    "clients": [ { "id": uuid, "flow": "xtls-rprx-vision" } ],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "ws",
                    "wsSettings": { "path": path }
                }
            }
        ],
        "outbounds": [ { "protocol": "freedom" } ]
    }
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def restart_xray():
    subprocess.run(["pkill", "-f", "xray"], capture_output=True)
    subprocess.Popen(["xray", "-c", CONFIG_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(LOG_FILE, 'w') as f:
        f.write(f"ری‌استارت در {time.ctime()}")

def get_clients_count():
    config = read_config()
    if config and "inbounds" in config and len(config["inbounds"]) > 0:
        return len(config["inbounds"][0].get("settings", {}).get("clients", []))
    return 0

def check_status():
    result = subprocess.run(["pgrep", "-f", "xray"], capture_output=True)
    return "online" if result.returncode == 0 else "offline"

def get_log():
    try:
        with open(LOG_FILE, 'r') as f:
            return f.read().strip()
    except:
        return "هیچ رویدادی ثبت نشده"

# ========== مسیرها ==========

@app.route('/', methods=['GET', 'POST'])
def index():
    domain = get_domain()
    current_uuid = ""
    current_path = "/spider"
    current_port = 10086
    log_msg = get_log()

    config = read_config()
    if config and "inbounds" in config and len(config["inbounds"]) > 0:
        clients = config["inbounds"][0].get("settings", {}).get("clients", [])
        if clients:
            current_uuid = clients[0].get("id", "")
        ws_settings = config["inbounds"][0].get("streamSettings", {}).get("wsSettings", {})
        current_path = ws_settings.get("path", "/spider")
        current_port = config["inbounds"][0].get("port", 10086)

    if request.method == 'POST':
        new_uuid = request.form.get("uuid", "").strip()
        new_path = request.form.get("path", "").strip()
        new_port = request.form.get("port", "").strip()

        if not new_uuid:
            new_uuid = str(uuid_lib.uuid4())
        if not new_path:
            new_path = "/spider"
        if not new_path.startswith("/"):
            new_path = "/" + new_path
        try:
            new_port = int(new_port) if new_port else 10086
        except:
            new_port = 10086

        write_config(new_uuid, new_path, new_port)
        restart_xray()
        current_uuid = new_uuid
        current_path = new_path
        current_port = new_port
        log_msg = f"بروزرسانی شد! مسیر: {new_path}، پورت: {new_port}"

    status = check_status()
    clients_count = get_clients_count()

    return render_template_string(
        HTML_TEMPLATE,
        domain=domain,
        uuid=current_uuid,
        path=current_path,
        port=current_port,
        status=status,
        clients_count=clients_count,
        log_message=log_msg
    )

@app.route('/restart', methods=['POST'])
def restart_only():
    restart_xray()
    return index()

@app.route('/reset', methods=['POST'])
def reset_all():
    write_config(str(uuid_lib.uuid4()), "/spider", 10086)
    restart_xray()
    return index()

# ========== اجرای اولیه ==========

if __name__ == '__main__':
    if not read_config():
        write_config(str(uuid_lib.uuid4()), "/spider", 10086)
        restart_xray()
    app.run(host='127.0.0.1', port=5000)
