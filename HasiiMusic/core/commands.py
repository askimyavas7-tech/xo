from pyrogram import Client
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
)

# Ana bot dosyanızdakiyle aynı log importunu kullanıyoruz
# Eğer ana dosyanız 'bot.py' ise ve 'logging.py' bir üst dizindeyse bu import doğrudur.
from ..logging import LOGGER 

PRIVATE_COMMANDS = [
    BotCommand("start", "🌟 Botu başlat ve müzik keyfine başla"),
    BotCommand("yardim", "🧠 Yardım menüsünü göster"),
]

GROUP_COMMANDS = [
    BotCommand("oynat", "🎶 Seçilen şarkıyı çalmaya başlar"),
    BotCommand("voynat", "🎬 Video oynatımını başlatır"),
    BotCommand("atla", "⏭️ Sonraki şarkıya geç"),
    BotCommand("duraklat", "⏸️ Şarkıyı duraklat"),
    BotCommand("devam", "▶️ Şarkıyı devam ettir"),
    BotCommand("son", "⛔ Oynatmayı durdur"),
    BotCommand("karistir", "🔀 Çalma listesini karıştır"),
    BotCommand("dongu", "🔁 Tekrar modunu etkinleştir"),
    BotCommand("sira", "📋 Kuyruğu göster"),
    BotCommand("ilerisar", "⏩ Şarkıyı ileri sar"),
    BotCommand("gerisar", "⏪ Şarkıyı geri sar"),
    BotCommand("playlist", "🎼 Kendi çalma listen"),
    BotCommand("bul", "🔍 Müzik ara ve indir"),
    BotCommand("ayarlar", "⚙️ Grup ayarlarını göster"),
    BotCommand("restart", "♻️ Botu yeniden başlat"),
    BotCommand("reload", "🔄 Admin önbelleğini yenile"),
]


async def set_bot_commands(client: Client):
    try:
        await client.set_bot_commands(PRIVATE_COMMANDS, scope=BotCommandScopeAllPrivateChats())
        await client.set_bot_commands(GROUP_COMMANDS, scope=BotCommandScopeAllGroupChats())
        LOGGER(__name__).info("✅ Bot komutları (özel ve grup) başarıyla ayarlandı.")
    except Exception as e:
        LOGGER(__name__).error(f"❌ Bot komutları ayarlanamadı: {e}")
