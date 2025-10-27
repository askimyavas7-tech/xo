import asyncio
import time
import platform
from datetime import datetime
import psutil  # Bu kütüphanenin yüklü olduğundan emin olun (pip install psutil)

from pyrogram.enums import ParseMode
from HasiiMusic import app
from HasiiMusic.utils.database import (
    get_served_chats,
    is_on_off,
    get_active_chats,
    get_active_video_chats
)
from config import LOG, LOGGER_ID

async def play_logs(message):
    """
    Yeni oynatma günlüklerini (loglarını) yapılandırılan LOG grubuna gönderir.
    (Gizli gruplar için davet linki oluşturmayı deneyecek şekilde güncellendi)
    """
    
    # --- 1. Zamanlama ve Ping Başlangıcı ---
    ping_start = time.time()
    now = datetime.now()
    tarih = now.strftime("%d %B %Y")
    saat = now.strftime("%H:%M:%S")
    gun = now.strftime("%A")

    # --- 2. Sistem İstatistikleri (psutil) ---
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_cores = psutil.cpu_count(logical=True)
    os_info = f"{platform.system()} {platform.release()}"
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    boot_time_timestamp = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time_timestamp)
    # Uptime'ı HH:MM:SS formatına çevir
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    if uptime_seconds > 86400: # Eğer 1 günden fazlaysa
        uptime_days = uptime_seconds // 86400
        uptime_str = f"{uptime_days} Gün, {uptime_str}"
    net_io = psutil.net_io_counters()
    net_sent_mb = f"{net_io.bytes_sent / (1024 * 1024):.2f}MB"
    net_recv_mb = f"{net_io.bytes_recv / (1024 * 1024):.2f}MB"
    cpu_temp = "N/A" # CPU sıcaklığı çoğu sunucuda N/A olarak döner

    # --- 3. Async Veri Toplama (API ve DB Çağrıları) ---
    try:
        results = await asyncio.gather(
            is_on_off(LOG),
            app.get_chat_members_count(message.chat.id),
            get_served_chats(),
            get_active_chats(),
            get_active_video_chats(),
            app.get_me() # Ping için API çağrısı
        )
        
        log_is_on, member_count, served_chats, active_chats, active_video_chats, _ = results
        # Ping'i hesapla
        ping_ms = f"{(time.time() - ping_start) * 1000:.0f} ms"

    except Exception as e:
        print(f"[play_logs] Veri toplama hatası: {e}")
        return # Hata varsa fonksiyondan çık

    # Loglama kapalıysa veya mesaj zaten log grubundansa çık
    if not log_is_on or message.chat.id == LOGGER_ID:
        return

    # --- 4. Verileri Hazırlama (GÜNCELLENDİ) ---
    total_chats = len(served_chats)
    active_voice_count = len(active_chats)
    active_video_count = len(active_video_chats)

    # Grup Linki (Gizli grup için davet linki denemesi eklendi)
    if message.chat.username:
        chat_tag = f"@{message.chat.username}"
    else:
        # Gizli grup ise davet linki oluşturmayı dene
        try:
            chat_tag = await app.export_chat_invite_link(message.chat.id)
            if not chat_tag: # Bazen None dönebilir
                 chat_tag = "Özel Grup (Link Alınamadı)"
        except Exception as e:
            # Bot admin değilse veya link oluşturma yetkisi yoksa
            print(f"[play_logs] Davet linki oluşturulamadı: {e}")
            chat_tag = "Özel Grup (Link Yetkisi Yok)"

    # Kullanıcı Adı
    user_username = f"@{message.from_user.username}" if message.from_user.username else "Yok"
    
    kaynak = "Komut" # Varsayılan

    # --- 5. Log Metnini Oluşturma (İstenen Formatta) ---
    logger_text = f"""🔊 **Yeni Müzik Oynatıldı**

🕒 **Tarih/Saat:**
📅 {tarih}
⏰ {saat} ({gun})

📚 **Grup:** {message.chat.title} [`{message.chat.id}`]
🔗 **Grup Linki:** {chat_tag}
👥 **Üye Sayısı:** {member_count}

👤 **Kullanıcı:** {message.from_user.mention}
✨ **Kullanıcı Adı:** {user_username}
🔢 **Kullanıcı ID:** `{message.from_user.id}`
🔍 **Kaynak:** {kaynak}

🔎 **Sorgu:** {message.text}

💻 **Sistem Durumu**
├ 🧩 Sistem: {os_info} | {cpu_cores} Çekirdek
├ 🖥️ CPU : {cpu_percent}% ✅
├ 🧠 RAM : {ram_percent}% ✅
├ 💾 Disk: {disk_percent}% ✅
├ 🌡️ CPU Sıcaklığı: {cpu_temp}
├ 🌐 Ağ Kullanımı : ⬆️ {net_sent_mb} / ⬇️ {net_recv_mb}
└ ⏳ Uptime: {uptime_str}

⚡ **Ping:** {ping_ms}

📊 **Genel Durum**
├ 🌐 Toplam Grup : {total_chats}
├ 🔊 Aktif Ses   : {active_voice_count}
└ 🎥 Aktif Video : {active_video_count}
"""

    # --- 6. Log Gönderme ve Başlık Güncelleme ---
    try:
        await app.send_message(
            LOGGER_ID,
            text=logger_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True, # Linkin önizlemesini log grubunda göstermez
        )
        
        # Log grubu başlığını güncelle
        await app.set_chat_title(LOGGER_ID, f"🔊 Aktif Ses: {active_voice_count} | 🎥 Video: {active_video_count}")
        
    except Exception as e:
        print(f"[play_logs] Log gönderilemedi veya başlık güncellenemedi: {e}")
