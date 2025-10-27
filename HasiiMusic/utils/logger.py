# HasiiMusic/plugins/player_commands.py
import psutil, platform, time, socket
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from HasiiMusic import app
from HasiiMusic.utils.database import get_served_chats, get_active_chats, get_active_video_chats, is_on_off
from pyrogram.enums import ParseMode

# Geolocation için
import geocoder

LOGGER_ID = 123456789  # LOG grubunun ID’sini buraya koy
BOT_START_TIME = time.time()
BOT_VERSION = "4.1 Geo & Hardware Edition 💫"

# ---------------------------- DELUXE LOG PANEL ---------------------------- #
async def send_deluxe_log(message: Message, event_type: str, extra_info: str = None):
    chat_id = message.chat.id
    uye_sayisi = await app.get_chat_members_count(chat_id)
    toplam_grup = len(await get_served_chats())
    aktif_sesli = len(await get_active_chats())
    aktif_video = len(await get_active_video_chats())

    if not await is_on_off("LOG"):
        return

    # Grup linki
    if message.chat.username:
        chat_link = f"https://t.me/{message.chat.username}"
    else:
        try:
            invite_link = await app.export_chat_invite_link(chat_id)
            chat_link = invite_link
        except Exception:
            chat_link = "🔒 Gizli Grup (Link alınamadı)"

    username = f"@{message.from_user.username}" if message.from_user.username else "🌸 Kullanıcı Adı Yok"
    tarih = message.date.strftime("%d.%m.%Y • %H:%M:%S")

    # Sistem istatistikleri
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    cpu_count = psutil.cpu_count(logical=True)

    # Uptime
    uptime_seconds = int(time.time() - BOT_START_TIME)
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

    # Ping
    start = time.time()
    await app.get_me()
    ping_ms = int((time.time() - start) * 1000)

    # Sistem bilgisi
    system = platform.system()
    release = platform.release()
    hostname = socket.gethostname()

    # Sunucu lokasyonu
    try:
        g = geocoder.ip("me")
        country = g.country or "Bilinmiyor"
        continent = g.continent or "Bilinmiyor"
        location = f"{country} / {continent}"
    except Exception:
        location = "🌐 Lokasyon alınamadı"

    # HTML log mesajı
    logger_text = f"""
<pre>╔══════════════════════════════════╗</pre>
<b>💫 𝐇𝐀𝐒𝐈𝐈 𝐌𝐔𝐒𝐈𝐂 - 𝐋𝐎𝐆 𝐏𝐀𝐍𝐄𝐋 💫</b>
<pre>╚══════════════════════════════════╝</pre>

🎛 <b>Olay Türü:</b> <code>{event_type}</code>
🏷 <b>Grup:</b> <a href="{chat_link}">{message.chat.title}</a> <code>[{message.chat.id}]</code>  
👥 <b>Üye Sayısı:</b> <code>{uye_sayisi}</code>  
👤 <b>Kullanıcı:</b> {message.from_user.mention}  
🔖 <b>Kullanıcı Adı:</b> {username}  
🆔 <b>Kullanıcı ID:</b> <code>{message.from_user.id}</code>

🎧 <b>Detay:</b> <code>{extra_info or "—"}</code>

<pre>──────────────────────────────</pre>
📊 <b>Bot Durumu</b>  
🌍 <b>Toplam Grup:</b> <code>{toplam_grup}</code>  
🎙 <b>Aktif Sesli Sohbet:</b> <code>{aktif_sesli}</code>  
📹 <b>Aktif Video Sohbet:</b> <code>{aktif_video}</code>  

<pre>──────────────────────────────</pre>
🧠 <b>Sistem Kaynakları</b>  
⚙️ <b>CPU:</b> <code>{cpu}%</code> ({cpu_count} Çekirdek)  
💾 <b>RAM:</b> <code>{ram}%</code>  
💽 <b>Disk:</b> <code>{disk}%</code>  

<pre>──────────────────────────────</pre>
🖥 <b>Sunucu Bilgisi</b>  
🌐 <b>İşletim Sistemi:</b> <code>{system} {release}</code>  
📡 <b>Host Adı:</b> <code>{hostname}</code>  
📍 <b>Sunucu Konumu:</b> <code>{location}</code>

<pre>──────────────────────────────</pre>
⏱ <b>Uptime:</b> <code>{uptime_str}</code>  
📶 <b>Ping:</b> <code>{ping_ms} ms</code>  
🧩 <b>Versiyon:</b> <code>{BOT_VERSION}</code>

<pre>──────────────────────────────</pre>
🕒 <b>Kayıt Alındı:</b> <code>{tarih}</code>  
👾 <b>Bot:</b> <a href="https://t.me/HasiiMusic">Hasii Music</a> 🎧
<pre>──────────────────────────────</pre>
💠 <i>“Müziği Hisset, Sessizliği Duy.”</i>
"""

    if message.chat.id != LOGGER_ID:
        try:
            await app.send_message(
                LOGGER_ID,
                logger_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            await app.set_chat_title(LOGGER_ID, f"🎶 Aktif Ses: {aktif_sesli}")
        except Exception as e:
            print(f"[Log Hatası] {e}")

# ---------------------------- KOMUTLAR ---------------------------- #

@app.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    query = " ".join(message.text.split()[1:]) if len(message.text.split()) > 1 else None
    if not query:
        await message.reply_text("❌ Lütfen bir şarkı adı veya linki girin.")
        return

    # 🎵 Buraya müzik oynatma mantığı gelecek
    # await play_music(query, message.chat.id)

    await send_deluxe_log(message, "🎵 Müzik Oynatma", extra_info=f"Sorgu: {query}")
    await message.reply_text(f"🎶 Oynatılıyor: {query}")


@app.on_message(filters.command("stop") & filters.group)
async def stop_command(client: Client, message: Message):
    # await stop_music(message.chat.id)
    await send_deluxe_log(message, "⏹ Müzik Durduruldu")
    await message.reply_text("⏹ Müzik durduruldu.")


@app.on_message(filters.command("skip") & filters.group)
async def skip_command(client: Client, message: Message):
    # await skip_music(message.chat.id)
    await send_deluxe_log(message, "⏭ Parça Geçildi")
    await message.reply_text("⏭ Parça atlandı.")


@app.on_message(filters.command("join") & filters.group)
async def join_command(client: Client, message: Message):
    # await join_voice_chat(message.chat.id)
    await send_deluxe_log(message, "🎙 Sesli Sohbete Katıldı")
    await message.reply_text("🎙 Sesli sohbete katıldım.")


@app.on_message(filters.command("leave") & filters.group)
async def leave_command(client: Client, message: Message):
    # await leave_voice_chat(message.chat.id)
    await send_deluxe_log(message, "🎧 Sesli Sohbetten Ayrıldı")
    await message.reply_text("🎧 Sesli sohbetten ayrıldım.")
