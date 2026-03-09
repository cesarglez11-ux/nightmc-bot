"""
╔══════════════════════════════════════════════════════════════════╗
  ███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗███╗   ███╗ ██████╗
  ████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝████╗ ████║██╔════╝
  ██╔██╗ ██║██║██║  ███╗███████║   ██║   ██╔████╔██║██║
  ██║╚██╗██║██║██║   ██║██╔══██║   ██║   ██║╚██╔╝██║██║
  ██║ ╚████║██║╚██████╔╝██║  ██║   ██║   ██║ ╚═╝ ██║╚██████╗
  ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝ ╚═════╝
                  Bot de Tickets — NightMc Network v2.1
  Token  →  Railway › Variables › DISCORD_TOKEN
  Deploy →  Railway › Deployments › Redeploy
╚══════════════════════════════════════════════════════════════════╝
"""
import discord
from discord import ui
from discord.ext import commands
import asyncio
import datetime
import io
import os

TOKEN = os.getenv("DISCORD_TOKEN")

# ╔═══════════════════════════════════════════════════════════════╗
#   ⚙️  CONFIGURACIÓN
# ╚═══════════════════════════════════════════════════════════════╝
COOLDOWN_SEGUNDOS = 60

CAT_SOPORTE      = "🛠️ SOPORTE"
CAT_REPORTE      = "🚫 REPORTES"
CAT_APELACION    = "⚖️ APELACIONES"
CAT_PAGOS        = "💰 Pagos Tienda"
CAT_POSTULACION  = "📋 Postulaciones Staff"
CAT_ALIANZA      = "🤝 Alianzas"
CAT_EVENTO       = "🎉 Eventos"
CAT_TRANSFER     = "🔄 TRANSFERIDOS"
LOGS_CANAL       = "ticket-logs"

CATEGORIAS_TICKET = {
    "soporte":      CAT_SOPORTE,
    "reporte":      CAT_REPORTE,
    "apelacion":    CAT_APELACION,
    "pagos_tienda": CAT_PAGOS,
    "postulacion":  CAT_POSTULACION,
    "alianza":      CAT_ALIANZA,
    "evento":       CAT_EVENTO,
}
ROLES_TICKET = {
    "soporte":      (None,                        True),
    "reporte":      ("--------Low staff--------",    True),
    "apelacion":    ("--------Medium Staff--------", True),
    "pagos_tienda": ("--------Head staff--------",   False),
    "postulacion":  ("--------Medium Staff--------", True),
    "alianza":      ("--------Head staff--------",   False),
    "evento":       ("--------Low staff--------",    True),
}
MSG_SIN_PERMISOS = "❌  Aún no tienes los suficientes permisos para responder en este ticket."
TRANSFER_SUBS = {
    "ganadores-eventos":   ("--------Head staff--------",  CAT_TRANSFER, "🎖️  Ganadores de Eventos"),
    "unregister":          ("--------Head staff--------",  CAT_TRANSFER, "🔐  Unregister"),
    "reembolso":           ("--------Head staff--------",  CAT_TRANSFER, "💸  Reembolso"),
    "staff-report":        ("--------Head staff--------",  CAT_TRANSFER, "🚨  Staff Report"),
    "error-config":        ("--------Head staff--------",  CAT_TRANSFER, "⚠️  Error de Configuración"),
    "revives":             ("--------High Staff--------", CAT_TRANSFER, "💊  Revives"),
    "cambio-nick":         ("--------High Staff--------", CAT_TRANSFER, "✏️  Cambio de Nick"),
}
STAFF_TEAM        = "--------Staff team--------"
ROL_SOPORTE       = "| Soporte"
TODOS_ROLES_STAFF = ["--------Low staff--------", "--------Medium Staff--------", "--------High Staff--------", "--------Head staff--------", "--------Staff team--------"]
ROLES_SUPERIORES  = ["--------High Staff--------", "--------Head staff--------"]

# ╔═══════════════════════════════════════════════════════════════╗
#   🎨  ESTÉTICA
# ╚═══════════════════════════════════════════════════════════════╝
BANNER_URL   = "https://i.imgur.com/uhYEbZj.png"
COLOR_BASE   = 0x2b2d31
COLOR_OK     = 0x57f287
COLOR_DANGER = 0xed4245
COLOR_WARN   = 0xfee75c
COLOR_BLUE   = 0x5865f2
FOOTER       = "NightMc.me"
SEP          = "──────────────────────────────"

def _footer(e, guild):
    e.set_footer(text=FOOTER, icon_url=guild.icon.url if guild.icon else None)
    return e

# ── Embeds de ticket ─────────────────────────────────────────────
def embed_ticket_soporte(guild, user, rol_tag, campos):
    e = discord.Embed(color=COLOR_BASE)
    e.set_author(name="SISTEMA DE TICKETS — NIGHTMC", icon_url=guild.icon.url if guild.icon else None)
    e.title = "🛠️  Soporte general de NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu ticket pronto será atendido por algún miembro de {rol_tag}.\n"
        f"Le pedimos que tenga paciencia.\n\n"
        f"*Bienvenido al sistema de Soporte Técnico de NightMC.*\n"
        f"Por favor, espera pacientemente mientras el equipo revisa tu solicitud."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable", value=f"> {rol_tag}",                    inline=False)
    e.add_field(name="🎮  Nick en Minecraft", value=f"```{campos.get('Nick','—')}```", inline=True)
    e.add_field(name="❓  Duda o consulta",   value=f"```{campos.get('Duda','—')}```", inline=False)
    e.add_field(name=SEP, value=(
        "> ⚠️  Las solicitudes que no sigan el formato serán rechazadas.\n"
        "> 💬  Recibirás respuesta una vez el staff revise tu caso.\n"
        "> 🙏  Gracias por contactar con el **Staff Team de NightMC Network**."
    ), inline=False)
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_ticket_reporte(guild, user, rol_tag, campos):
    e = discord.Embed(color=COLOR_BASE)
    e.set_author(name="SISTEMA DE TICKETS — NIGHTMC", icon_url=guild.icon.url if guild.icon else None)
    e.title = "🚫  Reporte a Usuario — NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu reporte será revisado por el {rol_tag}.\n"
        f"Le pedimos que tenga paciencia mientras el equipo evalúa las pruebas."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable",  value=f"> {rol_tag}",                                 inline=False)
    e.add_field(name="🎮  Tu nick",            value=f"```{campos.get('Nick','—')}```",              inline=True)
    e.add_field(name="🎯  Usuario reportado",  value=f"```{campos.get('Usuario reportado','—')}```", inline=True)
    e.add_field(name="🔗  Pruebas",            value=f"```{campos.get('Pruebas','—')}```",           inline=False)
    e.add_field(name=SEP, value=(
        "> ⚠️  Los reportes sin pruebas válidas serán cerrados automáticamente.\n"
        "> 🔍  El equipo verificará la evidencia antes de tomar acción.\n"
        "> 🙏  Gracias por ayudar a mantener la comunidad de **NightMC Network**."
    ), inline=False)
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_ticket_apelacion(guild, user, rol_tag, campos):
    e = discord.Embed(color=COLOR_BASE)
    e.set_author(name="SISTEMA DE TICKETS — NIGHTMC", icon_url=guild.icon.url if guild.icon else None)
    e.title = "⚖️  Apelación de Sanción — NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu apelación será revisada por {rol_tag}.\n"
        f"El proceso puede tomar tiempo. Le pedimos paciencia y respeto."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable",            value=f"> {rol_tag}",                                            inline=False)
    e.add_field(name="🎮  Cuenta sancionada",            value=f"```{campos.get('Nick sancionado','—')}```",              inline=True)
    e.add_field(name="🛡️  Staff que sancionó",           value=f"```{campos.get('Staff que sancionó','—')}```",           inline=True)
    e.add_field(name="📋  Razón de la sanción",          value=f"```{campos.get('Razón de la sanción','—')}```",          inline=False)
    e.add_field(name="💬  ¿Por qué retirar la sanción?", value=f"```{campos.get('¿Por qué retirar la sanción?','—')}```", inline=False)
    e.add_field(name=SEP, value=(
        "> ⚠️  Las apelaciones falsas o irrespetuosas serán rechazadas.\n"
        "> ⏳  El proceso puede demorar, sé paciente por favor.\n"
        "> 🙏  Gracias por contactar con el **Staff Team de NightMC Network**."
    ), inline=False)
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_ticket_pagos(guild, user, rol_tag, campos):
    e = discord.Embed(color=COLOR_BASE)
    e.set_author(name="SISTEMA DE TICKETS — NIGHTMC", icon_url=guild.icon.url if guild.icon else None)
    e.title = "💰  Soporte Pagos Tienda — NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu solicitud de compra será atendida por {rol_tag}.\n"
        f"Por favor adjunta toda la información para agilizar el proceso."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable", value=f"> {rol_tag}",                              inline=False)
    e.add_field(name="🎮  Nick de compra",    value=f"```{campos.get('Nick de compra','—')}```", inline=True)
    e.add_field(name="🧾  ID de compra",      value=f"```{campos.get('ID de compra','—')}```",   inline=True)
    e.add_field(name="⚠️  Problema",          value=f"```{campos.get('Problema','—')}```",       inline=False)
    e.add_field(name=SEP, value=(
        "> 📧  Revisa tu correo de Tebex para encontrar el ID de transacción.\n"
        "> ⚠️  Sin ID de compra válido no se puede procesar la solicitud.\n"
        "> 🙏  Gracias por apoyar a **NightMC Network** con tu compra."
    ), inline=False)
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_ticket_postulacion(guild, user, rol_tag, campos):
    e = discord.Embed(color=COLOR_BASE)
    e.set_author(name="SISTEMA DE TICKETS — NIGHTMC", icon_url=guild.icon.url if guild.icon else None)
    e.title = "📋  Postulación Staff — NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu postulación será evaluada por {rol_tag}.\n"
        f"Revisaremos tu solicitud con atención. Sé paciente."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable",  value=f"> {rol_tag}", inline=False)
    e.add_field(name="🎮  Nick", value=f"```{campos.get('Nick','—')}```", inline=True)
    e.add_field(name="💬  Duda", value=f"```{campos.get('Duda','—')}```", inline=False)
    e.add_field(name=SEP, value=(
        "> ⚠️  Las postulaciones falsas o con datos incorrectos serán rechazadas.\n"
        "> ⏳  El proceso de evaluación puede tomar varios días.\n"
        "> 🙏  Gracias por tu interés en **NightMC Network**."
    ), inline=False)
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_ticket_alianza(guild, user, rol_tag, campos):
    e = discord.Embed(color=COLOR_BASE)
    e.set_author(name="SISTEMA DE TICKETS — NIGHTMC", icon_url=guild.icon.url if guild.icon else None)
    e.title = "🤝  Propuesta de Alianza — NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu propuesta será revisada por {rol_tag}.\n"
        f"Evaluaremos la colaboración con atención."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable",   value=f"> {rol_tag}", inline=False)
    e.add_field(name="🏷️  Nombre del servidor", value=f"```{campos.get('Servidor','—')}```", inline=True)
    e.add_field(name="👥  Miembros aprox.",      value=f"```{campos.get('Miembros','—')}```", inline=True)
    e.add_field(name="💡  Propuesta",            value=f"```{campos.get('Propuesta','—')}```", inline=False)
    e.add_field(name=SEP, value=(
        "> 📋  Toda alianza debe beneficiar a ambas comunidades.\n"
        "> ⏳  Nos pondremos en contacto a la brevedad.\n"
        "> 🙏  Gracias por contactar con **NightMC Network**."
    ), inline=False)
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_ticket_evento(guild, user, rol_tag, campos):
    e = discord.Embed(color=COLOR_BASE)
    e.set_author(name="SISTEMA DE TICKETS — NIGHTMC", icon_url=guild.icon.url if guild.icon else None)
    e.title = "🎉  Soporte de Eventos — NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu solicitud de evento será atendida por {rol_tag}.\n"
        f"Verificaremos tu participación y el premio correspondiente."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable",  value=f"> {rol_tag}", inline=False)
    e.add_field(name="🎮  Nick",               value=f"```{campos.get('Nick','—')}```", inline=True)
    e.add_field(name="🎪  Nombre del evento",  value=f"```{campos.get('Evento','—')}```", inline=True)
    e.add_field(name="🏆  Premio esperado",    value=f"```{campos.get('Premio','—')}```", inline=False)
    e.add_field(name="📋  Descripción",        value=f"```{campos.get('Descripcion','—')}```", inline=False)
    e.add_field(name=SEP, value=(
        "> 📸  Adjunta pruebas de participación si las tienes.\n"
        "> ⏳  Verificaremos los registros del evento.\n"
        "> 🙏  Gracias por participar en **NightMC Network**."
    ), inline=False)
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

EMBED_TICKET = {
    "soporte":      embed_ticket_soporte,
    "reporte":      embed_ticket_reporte,
    "apelacion":    embed_ticket_apelacion,
    "pagos_tienda": embed_ticket_pagos,
    "postulacion":  embed_ticket_postulacion,
    "alianza":      embed_ticket_alianza,
    "evento":       embed_ticket_evento,
}

def embed_claimed(user, guild):
    e = discord.Embed(
        description=f"🔑  **{user.mention}** tomó el control de este ticket.\nEl canal fue renombrado correctamente.",
        color=COLOR_OK)
    e.set_footer(text="NightMc Network  ✦  Soporte activo")
    return e

def embed_transfer_msg(label, guild):
    e = discord.Embed(color=0x5865f2)
    e.set_author(name="NightMc Network  ✦  Transferencia de Ticket",
                 icon_url=guild.icon.url if guild.icon else None)
    e.title = "🔄  Ticket Redirigido"
    e.description = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Tu ticket ha sido escalado a\n"
        f"**{label}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    e.add_field(name="⏳  Estado",      value="> El equipo especializado revisará tu caso.",  inline=False)
    e.add_field(name="💬  ¿Qué sigue?", value="> Un miembro del staff se pondrá en contacto contigo en breve.\n> Por favor, **no abras otro ticket** sobre el mismo tema.", inline=False)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_transfer_menu(guild):
    e = discord.Embed(color=COLOR_WARN)
    e.set_author(name="NightMc Network  ✦  Escalación Interna",
                 icon_url=guild.icon.url if guild.icon else None)
    e.title = "🔄  Transferir Expediente"
    e.description = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Selecciona el tipo de gestión que necesitas.\n"
        "El ticket será redirigido al equipo correcto.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑  **Head staff** — Gestiones críticas\n"
        "🔰  **Hight staff** — Gestiones avanzadas\n"
        "🛡️  **Staff team** — Gestiones generales"
    )
    e.set_footer(text="NightMc Network  ✦  Solo staff puede usar esta función")
    return e

def embed_close(guild):
    e = discord.Embed(
        title="🔒  Cerrando Ticket",
        description=("Este ticket será eliminado en **5 segundos**.\n\n"
                     "*Gracias por contactar al soporte de NightMc.*\n"
                     "✦  Hasta pronto."),
        color=COLOR_DANGER)
    return _footer(e, guild)

def embed_setup(guild):
    e = discord.Embed(color=0x2b2d31)
    e.set_author(name="NightMc Network  ✦  Sistema de Soporte",
                 icon_url=guild.icon.url if guild.icon else None)
    e.title = "🎫  ¿Necesitas ayuda?"
    e.description = (
        "\n"
        "Bienvenido al **Centro de Soporte** de NightMc Network.\n"
        "Estamos aquí para ayudarte con cualquier problema o duda.\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "┃  🛠️  **Soporte General** — Dudas, ayuda general\n"
        "┃  🚫  **Reportes** — Jugadores, bugs, hacks\n"
        "┃  ⚖️  **Apelaciones** — Bans, mutes, sanciones\n"
        "┃  💰  **Pagos Tienda** — Compras, rangos, problemas\n"
        "┃  📋  **Postulaciones Staff** — Aplicar para ser staff\n"
        "┃  🤝  **Alianzas** — Propuestas de colaboración\n"
        "┃  🎉  **Eventos** — Premios no recibidos, participación\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    e.add_field(name="📋  Normas del ticket", value=(
        "> 🔹 Sé respetuoso con el staff en todo momento\n"
        "> 🔹 Proporciona información clara y verídica\n"
        "> 🔹 No abuses del sistema de tickets\n"
        "> 🔹 Un ticket por asunto, no acumules consultas"
    ), inline=False)
    e.add_field(name="⏱️  Tiempo de respuesta",
                value="> Nuestro equipo te atenderá **lo antes posible**.", inline=False)
    e.add_field(name="🎙️  ¿Prefieres atención por voz?", value=(
        "> También ofrecemos soporte en **canales de voz**.\n"
        "> Entra en **┋ Sala de Espera** y un miembro del\n"
        "> **Staff Team** te atenderá cuando esté disponible.\n"
        "> *No garantizamos atención 24/7 por voz, pero siempre lo intentamos.*"
    ), inline=False)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

ERR_NO_STAFF     = "❌  Solo el staff puede realizar esta acción."
ERR_YA_RECLAMADO = "⚠️  Este ticket ya está siendo atendido por otro miembro del staff."
ERR_YA_TUYO      = "ℹ️  Ya tienes este ticket reclamado."
ERR_PROPIO       = "❌  No puedes reclamar tu propio ticket."
ERR_NO_CAT       = "❌  No se pudo crear la categoría. Revisa los permisos del bot."
ERR_DUPLICADO    = "❌  Ya tienes un ticket abierto. Ciérralo antes de abrir otro."
ERR_COOLDOWN     = "⏳  Espera un momento antes de abrir otro ticket."

# ╔═══════════════════════════════════════════════════════════════╗
#   🤖  BOT
# ╚═══════════════════════════════════════════════════════════════╝
class NightBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self._ticket_msg_ids: dict[int, int] = {}
        self._claimed_channels: dict[int, int] = {}
        self._last_rename: dict[int, float] = {}

    async def setup_hook(self):
        self.add_view(TicketLauncher())
        self.add_view(TicketControl())
        print("✦  Bot de Tickets listo. Usa !sync para registrar los comandos slash.")

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="NightMc Network 🌙"))
        print(f"✦  Online  ·  {self.user}  ·  {self.user.id}")

bot = NightBot()

tickets_abiertos: dict[int, int]               = {}
cooldowns:        dict[int, datetime.datetime]  = {}

# ╔═══════════════════════════════════════════════════════════════╗
#   🔧  UTILIDADES
# ╚═══════════════════════════════════════════════════════════════╝
def es_staff(m: discord.Member) -> bool:
    return any(r.name in TODOS_ROLES_STAFF for r in m.roles)

def en_cooldown(uid: int) -> bool:
    return uid in cooldowns and \
        (datetime.datetime.now() - cooldowns[uid]).total_seconds() < COOLDOWN_SEGUNDOS

def leer_topic(canal: discord.TextChannel, clave: str) -> str:
    if not canal.topic:
        return ""
    for parte in canal.topic.split("|"):
        parte = parte.strip()
        if parte.startswith(f"{clave}:"):
            return parte[len(clave)+1:].strip()
    return ""

def _get_owner_id_from_topic(canal) -> int:
    try:
        return int(leer_topic(canal, "ownerid"))
    except Exception:
        return 0

async def get_o_crear_cat(guild, nombre):
    cat = discord.utils.get(guild.categories, name=nombre)
    if not cat:
        try:
            cat = await guild.create_category(nombre, overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
            })
        except discord.Forbidden:
            return None
    return cat

async def get_o_crear_logs(guild):
    canal = discord.utils.get(guild.text_channels, name=LOGS_CANAL)
    if canal:
        return canal
    try:
        cat = discord.utils.get(guild.categories, name="📋 LOGS")
        if not cat:
            cat = await guild.create_category("📋 LOGS")
        rol_st = discord.utils.get(guild.roles, name=STAFF_TEAM)
        perms  = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if rol_st:
            perms[rol_st] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        return await guild.create_text_channel(LOGS_CANAL, category=cat, overwrites=perms)
    except Exception:
        return None

async def enviar_log(guild, embed, file=None):
    c = await get_o_crear_logs(guild)
    if c:
        try:
            await c.send(embed=embed, file=file) if file else await c.send(embed=embed)
        except Exception:
            pass

async def hacer_transcript(canal: discord.TextChannel) -> io.BytesIO:
    lineas = [f"=== TRANSCRIPT #{canal.name} ===\n\n"]
    async for msg in canal.history(limit=500, oldest_first=True):
        ts   = msg.created_at.strftime("%d/%m/%Y %H:%M")
        cont = msg.content or ""
        for emb in msg.embeds:
            if emb.title:
                cont += f" [EMBED: {emb.title}]"
        lineas.append(f"[{ts}] {msg.author.display_name}: {cont}\n")
    return io.BytesIO("".join(lineas).encode("utf-8"))

async def rename_robusto(canal: discord.TextChannel, nuevo_nombre: str):
    import time
    nuevo_nombre = nuevo_nombre[:50].lower().replace(" ", "-")
    if canal.name == nuevo_nombre:
        return True
    try:
        await canal.edit(name=nuevo_nombre)
        bot._last_rename[canal.id] = time.monotonic()
        return True
    except discord.HTTPException as e:
        if e.status == 429:
            wait = float(getattr(e, "retry_after", 600))
            await asyncio.sleep(wait + 2)
            try:
                await canal.edit(name=nuevo_nombre)
                bot._last_rename[canal.id] = time.monotonic()
                return True
            except Exception:
                return False
        return False
    except Exception:
        return False

async def calcular_base_nombre(canal: discord.TextChannel) -> str:
    base = canal.name
    if base.endswith("-pendiente"):
        base = base[:-10]
    partes = base.split("-")
    if len(partes) >= 3 and 2 <= len(partes[-1]) <= 15:
        base = "-".join(partes[:-1])
    return base

async def cerrar_ticket(canal: discord.TextChannel, guild: discord.Guild,
                        cerrado_por: discord.Member, owner_id: int):
    for uid, cid in list(tickets_abiertos.items()):
        if cid == canal.id:
            del tickets_abiertos[uid]
            break
    bot._ticket_msg_ids.pop(canal.id, None)
    bot._claimed_channels.pop(canal.id, None)
    owner = guild.get_member(owner_id)
    nombre_t = f"transcript-{canal.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    log_e = discord.Embed(title="📤  Ticket Cerrado", color=COLOR_DANGER, timestamp=datetime.datetime.now())
    log_e.add_field(name="Canal",       value=f"#{canal.name}",    inline=True)
    log_e.add_field(name="Cerrado por", value=cerrado_por.mention, inline=True)
    if owner:
        log_e.add_field(name="Dueño", value=owner.mention, inline=True)
    log_e.set_footer(text=FOOTER)
    arch = await hacer_transcript(canal)
    await enviar_log(guild, log_e, file=discord.File(arch, filename=nombre_t))
    await asyncio.sleep(5)
    try:
        await canal.delete()
    except discord.NotFound:
        pass

def _tiene_claim_button(msg: discord.Message) -> bool:
    for row in msg.components:
        for child in row.children:
            if getattr(child, "custom_id", None) == "claim_t":
                return True
    return False

async def resetear_claim_en_canal(canal: discord.TextChannel, nombre_canal: str, owner_id: int):
    bot._claimed_channels.pop(canal.id, None)
    nuevo_view = TicketControl(nombre_canal=nombre_canal, owner_id=owner_id)
    mid = bot._ticket_msg_ids.get(canal.id)
    if mid:
        try:
            msg = await canal.fetch_message(mid)
            await msg.edit(view=nuevo_view)
            return
        except Exception:
            pass
    try:
        async for m in canal.history(limit=50, oldest_first=True):
            if m.author.id == canal.guild.me.id and _tiene_claim_button(m):
                await m.edit(view=nuevo_view)
                bot._ticket_msg_ids[canal.id] = m.id
                return
    except Exception:
        pass

# ╔═══════════════════════════════════════════════════════════════╗
#   🎫  CREAR TICKET
# ╚═══════════════════════════════════════════════════════════════╝
async def crear_ticket(interaction: discord.Interaction,
                       tipo: str, campos: dict, nombre_canal: str):
    guild = interaction.guild
    user  = interaction.user
    await interaction.response.defer(ephemeral=True)
    if en_cooldown(user.id):
        return await interaction.followup.send(ERR_COOLDOWN, ephemeral=True)
    if user.id in tickets_abiertos:
        existe = guild.get_channel(tickets_abiertos[user.id])
        if existe:
            return await interaction.followup.send(ERR_DUPLICADO, ephemeral=True)
        del tickets_abiertos[user.id]
    cat = await get_o_crear_cat(guild, CATEGORIAS_TICKET.get(tipo, CAT_SOPORTE))
    if not cat:
        return await interaction.followup.send(ERR_NO_CAT, ephemeral=True)
    nombre_rol_esp, usar_st = ROLES_TICKET.get(tipo, (None, True))
    rol_esp = discord.utils.get(guild.roles, name=nombre_rol_esp) if nombre_rol_esp else None
    rol_st  = discord.utils.get(guild.roles, name=STAFF_TEAM)
    perms = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        user:               discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
    }
    if rol_esp:            perms[rol_esp] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if usar_st and rol_st: perms[rol_st]  = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    rol_solo_lectura = discord.utils.get(guild.roles, name=ROL_SOPORTE)
    if rol_solo_lectura:   perms[rol_solo_lectura] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
    try:
        canal = await guild.create_text_channel(
            name=f"{nombre_canal}-pendiente",
            category=cat, overwrites=perms,
            topic=f"tipo:{tipo} | ownerid:{user.id}")
    except discord.Forbidden:
        return await interaction.followup.send("❌  Sin permisos para crear canales.", ephemeral=True)
    tickets_abiertos[user.id] = canal.id
    cooldowns[user.id]        = datetime.datetime.now()
    rol_tag = (rol_st.mention  if usar_st and rol_st else
               rol_esp.mention if rol_esp else f"@{STAFF_TEAM}")
    view = TicketControl(nombre_canal=nombre_canal, owner_id=user.id)
    msg  = await canal.send(
        content=f"{user.mention}  {rol_tag}",
        embed=EMBED_TICKET[tipo](guild, user, rol_tag, campos),
        view=view)
    bot._ticket_msg_ids[canal.id] = msg.id
    await interaction.followup.send(f"✅  Tu ticket fue abierto en {canal.mention}", ephemeral=True)
    log_e = discord.Embed(title="📥  Ticket Abierto", color=COLOR_OK, timestamp=datetime.datetime.now())
    log_e.add_field(name="Usuario",   value=user.mention,                             inline=True)
    log_e.add_field(name="Canal",     value=canal.mention,                            inline=True)
    log_e.add_field(name="Categoría", value=CATEGORIAS_TICKET.get(tipo, CAT_SOPORTE), inline=True)
    log_e.set_footer(text=FOOTER)
    await enviar_log(guild, log_e)

# ╔═══════════════════════════════════════════════════════════════╗
#   🎮  BOTONES DEL TICKET
# ╚═══════════════════════════════════════════════════════════════╝
class TicketControl(ui.View):
    def __init__(self, nombre_canal: str = "ticket", owner_id: int = 0):
        super().__init__(timeout=None)
        self.nombre_canal  = nombre_canal
        self.owner_id      = owner_id

    def _get_owner_id(self, canal):
        if self.owner_id:
            return self.owner_id
        try:
            val = leer_topic(canal, "ownerid")
            return int(val) if val else 0
        except Exception:
            return 0

    @ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="🔑", custom_id="claim_t")
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        if not es_staff(interaction.user):
            if any(r.name == ROL_SOPORTE for r in interaction.user.roles):
                return await interaction.response.send_message(MSG_SIN_PERMISOS, ephemeral=True)
            return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
        canal_id = interaction.channel.id
        owner_id = self._get_owner_id(interaction.channel)
        if interaction.user.id == owner_id:
            return await interaction.response.send_message(ERR_PROPIO, ephemeral=True)
        claimed = bot._claimed_channels.get(canal_id)
        if claimed and claimed != interaction.user.id:
            return await interaction.response.send_message(ERR_YA_RECLAMADO, ephemeral=True)
        if claimed == interaction.user.id:
            return await interaction.response.send_message(ERR_YA_TUYO, ephemeral=True)
        bot._claimed_channels[canal_id] = interaction.user.id
        button.label    = f"Claimed  ·  {interaction.user.display_name}"
        button.emoji    = None
        button.disabled = True
        await interaction.response.edit_message(view=self)
        base = await calcular_base_nombre(interaction.channel)
        asyncio.create_task(rename_robusto(interaction.channel, f"{base}-{interaction.user.name[:12].lower()}"))
        await interaction.channel.send(embed=embed_claimed(interaction.user, interaction.guild))

    @ui.button(label="Transferir", style=discord.ButtonStyle.primary, emoji="🔄", custom_id="transfer_t")
    async def transfer_btn(self, interaction: discord.Interaction, button: ui.Button):
        if not es_staff(interaction.user):
            if any(r.name == ROL_SOPORTE for r in interaction.user.roles):
                return await interaction.response.send_message(MSG_SIN_PERMISOS, ephemeral=True)
            return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
        owner_id = self._get_owner_id(interaction.channel)
        await interaction.response.send_message(
            embed=embed_transfer_menu(interaction.guild),
            view=TransferView(owner_id=owner_id), ephemeral=True)

    @ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="close_t")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        if not es_staff(interaction.user):
            if any(r.name == ROL_SOPORTE for r in interaction.user.roles):
                return await interaction.response.send_message(MSG_SIN_PERMISOS, ephemeral=True)
            return await interaction.response.send_message(
                "❌  Solo el personal autorizado puede cerrar este expediente.", ephemeral=True)
        owner_id = self._get_owner_id(interaction.channel)
        await interaction.response.send_message(embed=embed_close(interaction.guild))
        await cerrar_ticket(interaction.channel, interaction.guild, interaction.user, owner_id)

# ╔═══════════════════════════════════════════════════════════════╗
#   🔄  MENÚ DE TRANSFERENCIA
# ╚═══════════════════════════════════════════════════════════════╝
class TransferView(ui.View):
    def __init__(self, owner_id: int = 0):
        super().__init__(timeout=180)
        self.owner_id = owner_id

    @ui.select(placeholder="✦  Selecciona el tipo de gestión...", options=[
        discord.SelectOption(label="Ganadores de Eventos",    value="ganadores-eventos",
            emoji="🎖️", description="👑 Head staff — Premio no entregado"),
        discord.SelectOption(label="Unregister",              value="unregister",
            emoji="🔐", description="👑 Head staff — Recuperación de cuenta"),
        discord.SelectOption(label="Reembolso",               value="reembolso",
            emoji="💸", description="👑 Head staff — Reembolso tienda"),
        discord.SelectOption(label="Staff Report",            value="staff-report",
            emoji="🚨", description="👑 Head staff — Reportar a un staff"),
        discord.SelectOption(label="Error de Configuración",  value="error-config",
            emoji="⚠️", description="👑 Head staff — Error de config/permisos"),
        discord.SelectOption(label="Revives",                 value="revives",
            emoji="💊", description="🔰 Hight staff — Recuperar inventario"),
        discord.SelectOption(label="Cambio de Nick",          value="cambio-nick",
            emoji="✏️", description="🔰 Hight staff — Cambiar nick vinculado"),
    ])
    async def select_callback(self, interaction: discord.Interaction, select: ui.Select):
        destino  = select.values[0]
        sub      = TRANSFER_SUBS.get(destino)
        if not sub:
            return await interaction.response.send_message("❌  Subcategoría no encontrada.", ephemeral=True)
        nombre_rol, cat_nombre, label = sub
        rol_nuevo  = discord.utils.get(interaction.guild.roles, name=nombre_rol)
        canal      = interaction.channel
        guild      = interaction.guild
        owner_id   = self.owner_id or _get_owner_id_from_topic(canal)
        cat_t = await get_o_crear_cat(guild, cat_nombre)
        if cat_t and canal.category != cat_t:
            try: await canal.edit(category=cat_t)
            except (discord.Forbidden, discord.HTTPException): pass
        asyncio.create_task(rename_robusto(canal, destino + "-pendiente"))
        roles_quitar = [STAFF_TEAM] + [n for n, _ in ROLES_TICKET.values() if n]
        for target in list(canal.overwrites):
            if isinstance(target, discord.Role) and target.name in roles_quitar:
                try: await canal.set_permissions(target, overwrite=None)
                except discord.Forbidden: pass
        if rol_nuevo:
            try: await canal.set_permissions(rol_nuevo, read_messages=True, send_messages=True)
            except discord.Forbidden: pass
        if owner_id:
            owner = guild.get_member(owner_id)
            if owner:
                try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
                except discord.Forbidden: pass
        await resetear_claim_en_canal(canal, destino, owner_id)
        mention = rol_nuevo.mention if rol_nuevo else f"@{nombre_rol}"
        await interaction.response.send_message(embed=embed_transfer_msg(label, guild))
        await canal.send(f"{mention}  ✦  Se requiere atención en este ticket — **{label}**.")
        log_e = discord.Embed(title="🔄  Ticket Transferido", color=COLOR_WARN, timestamp=datetime.datetime.now())
        log_e.add_field(name="Canal",   value=canal.mention,            inline=True)
        log_e.add_field(name="Destino", value=label,                    inline=True)
        log_e.add_field(name="Rol",     value=nombre_rol,               inline=True)
        log_e.add_field(name="Staff",   value=interaction.user.mention, inline=True)
        log_e.set_footer(text=FOOTER)
        await enviar_log(guild, log_e)

# ╔═══════════════════════════════════════════════════════════════╗
#   📝  MODALES
# ╚═══════════════════════════════════════════════════════════════╝
class GeneralModal(ui.Modal, title="NightMc  ·  Soporte General"):
    nick     = ui.TextInput(label="Nick", placeholder="Tu nick en Minecraft")
    consulta = ui.TextInput(label="Duda", placeholder="¿Cuál es tu duda o consulta?",
                            style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "soporte", {"Nick": self.nick.value, "Duda": self.consulta.value}, "soporte")

class ReporteModal(ui.Modal, title="NightMc  ·  Reportar Usuario"):
    nick    = ui.TextInput(label="Nick",                 placeholder="Tu nick en Minecraft")
    acusado = ui.TextInput(label="Usuario que reportas", placeholder="Nick del usuario a reportar")
    pruebas = ui.TextInput(label="Pruebas",              placeholder="Link de imgur, YouTube, etc.",
                           style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "reporte",
            {"Nick": self.nick.value, "Usuario reportado": self.acusado.value,
             "Pruebas": self.pruebas.value}, "reporte")

class ApelacionModal(ui.Modal, title="NightMc  ·  Apelar Sanción"):
    nick  = ui.TextInput(label="Nick",                                   placeholder="Nick de Minecraft (cuenta sancionada)")
    staff = ui.TextInput(label="Staff que te sancionó",                  placeholder="¿Qué staff aplicó la sanción?")
    razon = ui.TextInput(label="Razón de la sanción",                    placeholder="¿Por qué razón te sancionaron?",
                         style=discord.TextStyle.paragraph)
    unban = ui.TextInput(label="¿Por qué debería retirarse tu sanción?", placeholder="Explica tu caso",
                         style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "apelacion",
            {"Nick sancionado": self.nick.value, "Staff que sancionó": self.staff.value,
             "Razón de la sanción": self.razon.value,
             "¿Por qué retirar la sanción?": self.unban.value}, "apelacion")

class PagosTiendaModal(ui.Modal, title="NightMc  ·  Soporte Pagos Tienda"):
    nick    = ui.TextInput(label="Nick",         placeholder="Nick con el que hiciste la compra")
    id_pago = ui.TextInput(label="ID de compra", placeholder="ID de tu transacción en Tebex (revisa tu correo)")
    error   = ui.TextInput(label="Problema",     placeholder="¿Qué sucedió con tu compra?",
                           style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "pagos_tienda",
            {"Nick de compra": self.nick.value, "ID de compra": self.id_pago.value,
             "Problema": self.error.value}, "pagos-tienda")

class PostulacionModal(ui.Modal, title="NightMc  ·  Postulación Staff"):
    nick  = ui.TextInput(label="Nick", placeholder="Tu nick en Minecraft")
    duda  = ui.TextInput(label="Duda", placeholder="¿Qué clase de duda tienes?",
                         style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "postulacion",
            {"Nick": self.nick.value, "Duda": self.duda.value}, "postulacion")

class AlianzaModal(ui.Modal, title="NightMc  ·  Propuesta de Alianza"):
    servidor  = ui.TextInput(label="Nombre del servidor", placeholder="¿Cómo se llama tu servidor?")
    miembros  = ui.TextInput(label="Miembros aproximados", placeholder="Ej: 500 miembros")
    propuesta = ui.TextInput(label="Propuesta de colaboración",
                             placeholder="¿Qué tipo de alianza propones?",
                             style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "alianza",
            {"Servidor": self.servidor.value, "Miembros": self.miembros.value,
             "Propuesta": self.propuesta.value}, "alianza")

class EventoModal(ui.Modal, title="NightMc  ·  Soporte de Eventos"):
    nick   = ui.TextInput(label="Nick",              placeholder="Tu nick en Minecraft")
    evento = ui.TextInput(label="Nombre del evento", placeholder="¿En qué evento participaste?")
    premio = ui.TextInput(label="Premio esperado",   placeholder="¿Qué premio te corresponde?")
    desc   = ui.TextInput(label="Descripción",       placeholder="Explica el problema con detalle",
                          style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "evento",
            {"Nick": self.nick.value, "Evento": self.evento.value,
             "Premio": self.premio.value, "Descripcion": self.desc.value}, "evento")

# ╔═══════════════════════════════════════════════════════════════╗
#   🎡  MENÚ PRINCIPAL — Dropdown
# ╚═══════════════════════════════════════════════════════════════╝
class TicketLauncher(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.select(custom_id="main_sel",
               placeholder="✦  ¿En qué podemos ayudarte?",
               options=[
                   discord.SelectOption(label="Soporte General",      value="general",
                       emoji="🛠️", description="Dudas, ayuda general"),
                   discord.SelectOption(label="Reportes",             value="reporte",
                       emoji="🚫", description="Jugadores, bugs, hacks"),
                   discord.SelectOption(label="Apelaciones",          value="apelacion",
                       emoji="⚖️", description="Bans, mutes, sanciones"),
                   discord.SelectOption(label="Pagos Tienda",         value="pagos_tienda",
                       emoji="💰", description="Compras, rangos, problemas"),
                   discord.SelectOption(label="Postulaciones Staff",  value="postulacion",
                       emoji="📋", description="Aplicar para ser staff"),
                   discord.SelectOption(label="Alianzas",             value="alianza",
                       emoji="🤝", description="Propuestas de colaboración"),
                   discord.SelectOption(label="Eventos",              value="evento",
                       emoji="🎉", description="Premios no recibidos, participación"),
               ])
    async def callback(self, interaction: discord.Interaction, select: ui.Select):
        modales = {
            "general":      GeneralModal(),
            "reporte":      ReporteModal(),
            "apelacion":    ApelacionModal(),
            "pagos_tienda": PagosTiendaModal(),
            "postulacion":  PostulacionModal(),
            "alianza":      AlianzaModal(),
            "evento":       EventoModal(),
        }
        await interaction.response.send_modal(modales[select.values[0]])

# ╔═══════════════════════════════════════════════════════════════╗
#   ⚡  SLASH COMMANDS
# ╚═══════════════════════════════════════════════════════════════╝
@bot.tree.command(name="transfer", description="Deriva este ticket a otro equipo de staff")
async def transfer_slash(interaction: discord.Interaction):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    owner_id = _get_owner_id_from_topic(interaction.channel)
    await interaction.response.send_message(
        embed=embed_transfer_menu(interaction.guild),
        view=TransferView(owner_id=owner_id), ephemeral=True)

@bot.tree.command(name="close", description="Cierra este ticket")
async def close_slash(interaction: discord.Interaction):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    owner_id = _get_owner_id_from_topic(interaction.channel)
    await interaction.followup.send(embed=embed_close(interaction.guild))
    await cerrar_ticket(interaction.channel, interaction.guild, interaction.user, owner_id)

@bot.tree.command(name="claim", description="Reclama este ticket")
async def claim_slash(interaction: discord.Interaction):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    owner_id = _get_owner_id_from_topic(interaction.channel)
    if interaction.user.id == owner_id:
        return await interaction.followup.send(ERR_PROPIO, ephemeral=True)
    base = await calcular_base_nombre(interaction.channel)
    asyncio.create_task(rename_robusto(interaction.channel, f"{base}-{interaction.user.name[:12].lower()}"))
    await interaction.followup.send(embed=embed_claimed(interaction.user, interaction.guild))

@bot.tree.command(name="transcript", description="Genera el transcript de este ticket")
async def transcript_slash(interaction: discord.Interaction):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    arch   = await hacer_transcript(interaction.channel)
    nombre = f"transcript-{interaction.channel.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    await interaction.followup.send("📄  Transcript generado:",
        file=discord.File(arch, filename=nombre), ephemeral=True)
    arch2 = await hacer_transcript(interaction.channel)
    log_e = discord.Embed(title="📄  Transcript Generado", color=COLOR_WARN, timestamp=datetime.datetime.now())
    log_e.add_field(name="Canal", value=interaction.channel.mention, inline=True)
    log_e.add_field(name="Staff", value=interaction.user.mention,    inline=True)
    log_e.set_footer(text=FOOTER)
    lc = await get_o_crear_logs(interaction.guild)
    if lc:
        try: await lc.send(embed=log_e, file=discord.File(arch2, filename=nombre))
        except Exception: pass

@bot.tree.command(name="add", description="Añade a un usuario al ticket")
@discord.app_commands.describe(usuario="Usuario a añadir")
async def add_slash(interaction: discord.Interaction, usuario: discord.Member):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    try:
        await interaction.channel.set_permissions(usuario, read_messages=True, send_messages=True)
        await interaction.followup.send(f"✅  {usuario.mention} fue añadido al ticket.")
    except discord.Forbidden:
        await interaction.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="remove", description="Elimina a un usuario del ticket")
@discord.app_commands.describe(usuario="Usuario a eliminar")
async def remove_slash(interaction: discord.Interaction, usuario: discord.Member):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    try:
        await interaction.channel.set_permissions(usuario, overwrite=None)
        await interaction.followup.send(f"🚫  {usuario.mention} fue eliminado del ticket.")
    except discord.Forbidden:
        await interaction.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="rename", description="Renombra el canal del ticket")
@discord.app_commands.describe(nombre="Nuevo nombre (sin espacios)")
async def rename_slash(interaction: discord.Interaction, nombre: str):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.channel.edit(name=nombre.lower().replace(" ", "-")[:50])
        await interaction.followup.send("✏️  Canal renombrado.", ephemeral=True)
    except (discord.Forbidden, discord.HTTPException) as e:
        await interaction.followup.send(f"❌  {e}", ephemeral=True)

@bot.tree.command(name="slowmode", description="Activa o desactiva el modo lento")
@discord.app_commands.describe(segundos="Segundos (0 para desactivar)")
async def slowmode_slash(interaction: discord.Interaction, segundos: int = 0):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    segundos = max(0, min(segundos, 21600))
    try:
        await interaction.channel.edit(slowmode_delay=segundos)
        msg = f"🐢  Slowmode: **{segundos}s**." if segundos else "✅  Slowmode desactivado."
        await interaction.followup.send(msg)
    except discord.Forbidden:
        await interaction.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="specifictag_staff", description="Transfiere este ticket a un staff específico")
@discord.app_commands.describe(staff="Miembro del staff al que transferir")
async def specifictag_staff(interaction: discord.Interaction, staff: discord.Member):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    if not es_staff(staff):
        return await interaction.response.send_message("❌  El usuario no es staff.", ephemeral=True)
    if staff.id == interaction.user.id:
        return await interaction.response.send_message("❌  No puedes transferirte el ticket a ti mismo.", ephemeral=True)
    await interaction.response.defer()
    canal    = interaction.channel
    guild    = interaction.guild
    owner_id = _get_owner_id_from_topic(canal)
    for target in list(canal.overwrites):
        if isinstance(target, discord.Role) and target.name in TODOS_ROLES_STAFF:
            try: await canal.set_permissions(target, overwrite=None)
            except discord.Forbidden: pass
    for nombre_rol in ROLES_SUPERIORES:
        rol = discord.utils.get(guild.roles, name=nombre_rol)
        if rol:
            try: await canal.set_permissions(rol, read_messages=True, send_messages=True)
            except discord.Forbidden: pass
    try: await canal.set_permissions(staff, read_messages=True, send_messages=True)
    except discord.Forbidden: pass
    if owner_id:
        owner = guild.get_member(owner_id)
        if owner:
            try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
            except discord.Forbidden: pass
    cat_t = await get_o_crear_cat(guild, CAT_TRANSFER)
    if cat_t and canal.category != cat_t:
        try: await canal.edit(category=cat_t)
        except (discord.Forbidden, discord.HTTPException): pass
    nombre_destino = f"staff-{staff.name[:12].lower()}"
    await resetear_claim_en_canal(canal, nombre_destino, owner_id)
    asyncio.create_task(rename_robusto(canal, f"{nombre_destino}-pendiente"))
    e = discord.Embed(title="👤  Ticket Transferido a Staff", color=COLOR_BLUE)
    e.description = (f"Este ticket fue asignado a {staff.mention}.\n\n"
                     f"Solo **{staff.display_name}** y roles a partir de **Hight staff** pueden verlo.\n"
                     f"**Agradecemos tu paciencia.**")
    e.set_image(url=BANNER_URL)
    _footer(e, guild)
    await interaction.followup.send(embed=e)
    await canal.send(f"{staff.mention}  ✦  Se te ha asignado este ticket.")
    log_e = discord.Embed(title="👤  Ticket → Staff Específico", color=COLOR_BLUE, timestamp=datetime.datetime.now())
    log_e.add_field(name="Canal",    value=canal.mention,            inline=True)
    log_e.add_field(name="Asignado", value=staff.mention,            inline=True)
    log_e.add_field(name="Por",      value=interaction.user.mention, inline=True)
    log_e.set_footer(text=FOOTER)
    await enviar_log(guild, log_e)

@bot.tree.command(name="specifictag_role", description="Transfiere este ticket a un rol específico")
@discord.app_commands.describe(rol="Rol al que transferir el ticket")
async def specifictag_role(interaction: discord.Interaction, rol: discord.Role):
    if not es_staff(interaction.user):
        return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    canal    = interaction.channel
    guild    = interaction.guild
    owner_id = _get_owner_id_from_topic(canal)
    for target in list(canal.overwrites):
        if isinstance(target, discord.Role) and target.name in TODOS_ROLES_STAFF:
            try: await canal.set_permissions(target, overwrite=None)
            except discord.Forbidden: pass
    for nombre_rol in ROLES_SUPERIORES:
        r = discord.utils.get(guild.roles, name=nombre_rol)
        if r:
            try: await canal.set_permissions(r, read_messages=True, send_messages=True)
            except discord.Forbidden: pass
    try: await canal.set_permissions(rol, read_messages=True, send_messages=True)
    except discord.Forbidden: pass
    if owner_id:
        owner = guild.get_member(owner_id)
        if owner:
            try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
            except discord.Forbidden: pass
    cat_t = await get_o_crear_cat(guild, CAT_TRANSFER)
    if cat_t and canal.category != cat_t:
        try: await canal.edit(category=cat_t)
        except (discord.Forbidden, discord.HTTPException): pass
    nombre_destino = rol.name[:20].lower().replace(" ", "-")
    await resetear_claim_en_canal(canal, nombre_destino, owner_id)
    asyncio.create_task(rename_robusto(canal, f"{nombre_destino}-pendiente"))
    e = discord.Embed(title="🎭  Ticket Transferido a Rol", color=COLOR_BLUE)
    e.description = (f"Este ticket fue asignado al rol {rol.mention}.\n\n"
                     f"Solo **{rol.name}** y roles a partir de **Hight staff** pueden verlo.\n"
                     f"**Agradecemos tu paciencia.**")
    e.set_image(url=BANNER_URL)
    _footer(e, guild)
    await interaction.followup.send(embed=e)
    await canal.send(f"{rol.mention}  ✦  Se requiere atención en este ticket.")
    log_e = discord.Embed(title="🎭  Ticket → Rol Específico", color=COLOR_BLUE, timestamp=datetime.datetime.now())
    log_e.add_field(name="Canal", value=canal.mention,            inline=True)
    log_e.add_field(name="Rol",   value=rol.mention,              inline=True)
    log_e.add_field(name="Por",   value=interaction.user.mention, inline=True)
    log_e.set_footer(text=FOOTER)
    await enviar_log(guild, log_e)

def _build_help(guild):
    e = discord.Embed(title="📋  Comandos — NightMc Tickets", color=COLOR_BLUE)
    e.set_author(name="NightMc Network", icon_url=guild.icon.url if guild.icon else None)
    e.description = "Todos los comandos funcionan con `/` **y** con `!` indistintamente.\n" + SEP
    e.add_field(name="🎫  Tickets", value=(
        "`/claim` `!claim` — Reclamar el ticket\n"
        "`/close` `!close` — Cerrar el ticket\n"
        "`/transcript` `!transcript` — Generar transcript"
    ), inline=False)
    e.add_field(name="👥  Usuarios", value=(
        "`/add @usuario` — Añadir al ticket\n"
        "`/remove @usuario` — Eliminar del ticket"
    ), inline=False)
    e.add_field(name="⚙️  Canal", value=(
        "`/rename <nombre>` — Renombrar canal\n"
        "`/slowmode [seg]` — Modo lento (0 = off)"
    ), inline=False)
    e.add_field(name="🔄  Transferir", value=(
        "`/transfer` — Derivar a Rol Discord\n"
        "`/specifictag_staff @staff` — Asignar a 1 staff\n"
        "`/specifictag_role @rol` — Asignar a un rol"
    ), inline=False)
    e.add_field(name="🛠️  Admin", value=(
        "`!setup` — Publicar panel de soporte\n"
        "`!sync` — Registrar slash commands"
    ), inline=False)
    e.set_footer(text=FOOTER)
    return e

def _build_ip_embed():
    e = discord.Embed(title="👑  NightMc Network — Conexión", color=COLOR_BLUE)
    e.description = "¡Bienvenido a **NightMc Network**!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    e.add_field(name="☕  Java Edition",  value="> **IP:** `NightMc.me`\n> **Versiones:** 1.16+", inline=True)
    e.add_field(name="🟩  Bedrock",       value="> ⏳ **Próximamente...**",                       inline=True)
    e.add_field(name="\u200b", value="\u200b", inline=False)
    e.add_field(name="🎮  Modalidades",   value="> ⚔️  **ClashBox** — Disponible\n> 🗡️  **FullPvP** — Próximamente", inline=True)
    e.add_field(name="🔗  Redes",         value="> 💬  [Discord](https://discord.gg/2r2byXBgsv)\n> 🔴  [YouTube](https://www.youtube.com/@NightMCNetwork-me)", inline=True)
    e.set_image(url="https://i.imgur.com/WxEp4MV.png")
    e.set_footer(text="© Powered by NightMC")
    return e

@bot.tree.command(name="help", description="Muestra todos los comandos disponibles")
async def help_slash(interaction: discord.Interaction):
    await interaction.response.send_message(embed=_build_help(interaction.guild), ephemeral=True)

@bot.tree.command(name="ip", description="Muestra las IPs para conectarte al servidor")
async def ip_slash(interaction: discord.Interaction):
    await interaction.response.send_message(embed=_build_ip_embed())

# ╔═══════════════════════════════════════════════════════════════╗
#   🛠️  COMANDOS DE PREFIJO
# ╚═══════════════════════════════════════════════════════════════╝
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await ctx.send(embed=embed_setup(ctx.guild), view=TicketLauncher())
    try: await ctx.message.delete()
    except discord.Forbidden: pass

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    msg = await ctx.send("⏳  Registrando comandos...")
    try:
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await msg.edit(content=f"✅  **{len(synced)} comandos** registrados en **{ctx.guild.name}**.\n💡  Si no aparecen haz **Ctrl+R**.")
        for cmd in synced:
            print(f"  · /{cmd.name}")
    except Exception as e:
        await msg.edit(content=f"❌  Error: {e}")

@bot.command(name="claim")
async def claim_prefix(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    owner_id = _get_owner_id_from_topic(ctx.channel)
    if ctx.author.id == owner_id: return await ctx.send(ERR_PROPIO)
    base = await calcular_base_nombre(ctx.channel)
    asyncio.create_task(rename_robusto(ctx.channel, f"{base}-{ctx.author.name[:12].lower()}"))
    await ctx.send(embed=embed_claimed(ctx.author, ctx.guild))

@bot.command(name="close")
async def close_prefix(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    owner_id = _get_owner_id_from_topic(ctx.channel)
    await ctx.send(embed=embed_close(ctx.guild))
    await cerrar_ticket(ctx.channel, ctx.guild, ctx.author, owner_id)

@bot.command(name="transfer")
async def transfer_prefix(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    await ctx.send("🔄  Usa el **botón Transferir** del ticket o el comando `/transfer`.")

@bot.command(name="transcript")
async def transcript_prefix(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    msg = await ctx.send("⏳  Generando...")
    arch   = await hacer_transcript(ctx.channel)
    nombre = f"transcript-{ctx.channel.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    await msg.delete()
    await ctx.send("📄  Transcript:", file=discord.File(arch, filename=nombre))

@bot.command(name="add")
async def add_prefix(ctx, usuario: discord.Member = None):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    if not usuario: return await ctx.send("❌  Uso: `!add @usuario`")
    try:
        await ctx.channel.set_permissions(usuario, read_messages=True, send_messages=True)
        await ctx.send(f"✅  {usuario.mention} fue añadido.")
    except discord.Forbidden:
        await ctx.send("❌  Sin permisos.")

@bot.command(name="remove")
async def remove_prefix(ctx, usuario: discord.Member = None):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    if not usuario: return await ctx.send("❌  Uso: `!remove @usuario`")
    try:
        await ctx.channel.set_permissions(usuario, overwrite=None)
        await ctx.send(f"🚫  {usuario.mention} eliminado.")
    except discord.Forbidden:
        await ctx.send("❌  Sin permisos.")

@bot.command(name="rename")
async def rename_prefix(ctx, *, nombre: str = None):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    if not nombre: return await ctx.send("❌  Uso: `!rename nuevo-nombre`")
    try:
        await ctx.channel.edit(name=nombre.lower().replace(" ", "-")[:50])
        await ctx.send("✏️  Canal renombrado.")
    except (discord.Forbidden, discord.HTTPException) as e:
        await ctx.send(f"❌  {e}")

@bot.command(name="slowmode")
async def slowmode_prefix(ctx, segundos: int = 0):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    segundos = max(0, min(segundos, 21600))
    try:
        await ctx.channel.edit(slowmode_delay=segundos)
        await ctx.send(f"🐢  Slowmode: **{segundos}s**." if segundos else "✅  Slowmode desactivado.")
    except discord.Forbidden:
        await ctx.send("❌  Sin permisos.")

@bot.command(name="help", aliases=["ayuda"])
async def help_prefix(ctx):
    await ctx.send(embed=_build_help(ctx.guild))

@bot.command(name="ip")
async def ip_prefix(ctx):
    await ctx.send(embed=_build_ip_embed())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("❌  Sin permisos.")
    raise error

# ╔═══════════════════════════════════════════════════════════════╗
#   🚀  ARRANQUE
# ╚═══════════════════════════════════════════════════════════════╝
if not TOKEN:
    print("\n❌  ERROR: No se encontró DISCORD_TOKEN")
    print("   Railway → Variables → añade DISCORD_TOKEN\n")
    exit(1)

bot.run(TOKEN)
