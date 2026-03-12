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
import json
import os

TOKEN = os.getenv("DISCORD_TOKEN")

# ╔═══════════════════════════════════════════════════════════════╗
#   ⚙️  CONFIGURACIÓN — NIVELES & SUGERENCIAS
# ╚═══════════════════════════════════════════════════════════════╝
NIVELES_FILE      = "niveles_data.json"
CANAL_SUGERENCIAS = "💡│sugerencias"

# XP por mensaje — sube con el nivel (más nivel = más difícil)
XP_MIN, XP_MAX    = 15, 25
XP_COOLDOWN_SEG   = 60   # segundos entre mensajes que dan XP

# Premios por nivel — DM al usuario
PREMIOS_NIVEL = {
    25:  ("Lunar",    "1 día"),
    50:  ("Dark",     "1 día"),
    75:  ("Eclipse",  "1 día"),
    100: ("Eclipse+", "1 semana"),
}

def _xp_para_nivel(nivel: int) -> int:
    """XP total acumulado para alcanzar `nivel`.
    Escala cuadráticamente — niveles altos son mucho más difíciles.
    Nivel 0=0, 1=100, 5=750, 10=2100, 25=10100, 50=35100, 100=130100"""
    if nivel <= 0:
        return 0
    return 100 * nivel + 20 * (nivel ** 2)

def _nivel_desde_xp(xp_total: int) -> int:
    nivel = 0
    while _xp_para_nivel(nivel + 1) <= xp_total:
        nivel += 1
    return nivel

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
CAT_BOTS         = "🤖 Soporte Bots"
CAT_BOTS_HEAD    = "⚙️ Escalación de Bots"
CAT_TRANSFER     = "🔄 TRANSFERIDOS"
LOGS_CANAL       = "logs-tickets"

CATEGORIAS_TICKET = {
    "soporte":      CAT_SOPORTE,
    "reporte":      CAT_REPORTE,
    "apelacion":    CAT_APELACION,
    "pagos_tienda": CAT_PAGOS,
    "postulacion":  CAT_POSTULACION,
    "alianza":      CAT_ALIANZA,
    "evento":       CAT_EVENTO,
    "bots":         CAT_BOTS,
}
ROLES_TICKET = {
    "soporte":      (None,           True),
    "reporte":      ("Low staff",    True),
    "apelacion":    ("Medium Staff", True),
    "pagos_tienda": ("Head staff",   False),
    "postulacion":  ("Medium Staff", True),
    "alianza":      ("Head staff",   False),
    "evento":       ("Low staff",    True),
    "bots":         ("Medium Staff", False),
}
MSG_SIN_PERMISOS = "❌  Aún no tienes los suficientes permisos para responder en este ticket."
TRANSFER_SUBS = {
    "ganadores-eventos":   ("Head staff",  "🎖️ Escalación - Ganadores de Eventos",  "🎖️  Ganadores de Eventos"),
    "unregister":          ("Head staff",  "🔐 Escalación - Unregister",             "🔐  Unregister"),
    "reembolso":           ("Head staff",  "💸 Escalación - Reembolso",              "💸  Reembolso"),
    "staff-report":        ("Head staff",  "🚨 Escalación - Staff Report",           "🚨  Staff Report"),
    "error-config":        ("Head staff",  "⚠️ Escalación - Error de Config",        "⚠️  Error de Configuración"),
    "revives":             ("High Staff",  "💊 Escalación - Revives",                "💊  Revives"),
    "cambio-nick":         ("High Staff",  "✏️ Escalación - Cambio de Nick",         "✏️  Cambio de Nick"),
    "bug-bot-critico":     ("Head staff",  CAT_BOTS_HEAD,                            "🚨  Bug Crítico de Bot"),
    "ver-owner":           ("Head staff",  None,                                     "👁️  Ver Owner del Ticket"),
}
STAFF_TEAM        = "Staff team"
ROL_SOPORTE       = "| Soporte"
TODOS_ROLES_STAFF = ["Low staff", "Medium Staff", "High Staff", "Head staff", "Staff team"]
ROLES_SUPERIORES  = ["High Staff", "Head staff"]

# ╔═══════════════════════════════════════════════════════════════╗
#   🎨  ESTÉTICA
# ╚═══════════════════════════════════════════════════════════════╝
BANNER_URL   = "https://i.imgur.com/uhYEbZj.png"
COLOR_BASE   = 0x2b2d31
COLOR_OK     = 0x57f287
COLOR_DANGER = 0xed4245
COLOR_WARN   = 0xfee75c
COLOR_BLUE   = 0x5865f2
FOOTER       = "© Powered by NightMC"
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
    e.title = "📋  Dudas sobre Postulaciones — NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu duda será atendida por {rol_tag}.\n"
        f"Revisaremos tu consulta con atención. Sé paciente."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable",  value=f"> {rol_tag}", inline=False)
    e.add_field(name="🎮  Nick", value=f"```{campos.get('Nick','—')}```", inline=True)
    e.add_field(name="💬  Duda sobre tu postulación", value=f"```{campos.get('Duda','—')}```", inline=False)
    e.add_field(name=SEP, value=(
        "> ⚠️  Si abres el ticket sin motivo, serás sancionado.\n"
        "> ⏳  Te responderemos lo antes posible.\n"
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

def embed_ticket_bots(guild, user, rol_tag, campos):
    e = discord.Embed(color=0x5865f2)
    e.set_author(name="SISTEMA DE TICKETS — NIGHTMC", icon_url=guild.icon.url if guild.icon else None)
    e.title = "🤖  Soporte de Bots — NightMC Network"
    e.description = (
        f"Buenas {user.mention}. Tu reporte ha sido recibido y será atendido por {rol_tag}.\n"
        f"Si el problema es crítico, el staff lo escalará al equipo técnico."
    )
    e.add_field(name=SEP, value="\u200b", inline=False)
    e.add_field(name="👤  Staff responsable",     value=f"> {rol_tag}",                                    inline=False)
    e.add_field(name="🤖  Bot afectado",          value=f"```{campos.get('Bot','—')}```",                  inline=True)
    e.add_field(name="🎮  Tu nick",               value=f"```{campos.get('Nick','—')}```",                 inline=True)
    e.add_field(name="⚠️  Problema",              value=f"```{campos.get('Problema','—')}```",             inline=False)
    e.add_field(name="🔁  ¿Se puede reproducir?", value=f"```{campos.get('Reproducible','—')}```",        inline=False)
    e.add_field(name=SEP, value=(
        "> 📸  Adjunta capturas o vídeos del error si los tienes.\n"
        "> 🔍  Si el bug es grave, el staff lo escalará a **Head staff**.\n"
        "> 🙏  Gracias por ayudar a mejorar **NightMC Network**."
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
    "bots":         embed_ticket_bots,
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
        "Al transferir este ticket, el equipo especializado\n"
        "recibirá acceso directo para **apoyar al usuario**.\n"
        "Selecciona la categoría que mejor describe el caso.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    e.add_field(name="👑  Head staff — Gestiones Críticas", value=(
        "> 🎖️  **Ganadores de Eventos** — Premio no entregado tras un evento\n"
        "> 🔐  **Unregister** — Recuperación o desvinculación de cuenta\n"
        "> 💸  **Reembolso** — Devolución de compra en tienda\n"
        "> 🚨  **Staff Report** — Reporte formal contra un miembro del staff\n"
        "> ⚠️  **Error de Configuración** — Fallo en permisos o ajustes del servidor"
    ), inline=False)
    e.add_field(name="🔰  High Staff — Gestiones Avanzadas", value=(
        "> 💊  **Revives** — Recuperación de inventario o estado en juego\n"
        "> ✏️  **Cambio de Nick** — Modificación del nick vinculado a la cuenta"
    ), inline=False)
    e.add_field(name="🚨  Escalación Técnica — Bots", value=(
        "> 🤖  **Bug Crítico de Bot** — Error grave que afecta el funcionamiento\n"
        "> ⚙️  El caso será revisado por **Head staff** en canal exclusivo"
    ), inline=False)
    e.add_field(name="👁️  Utilidades — Head staff", value=(
        "> 👤  **Ver Owner del Ticket** — Consulta quién abrió este ticket sin moverlo"
    ), inline=False)
    e.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value=(
        "> ⚠️  Solo transfiere si el caso **supera tus permisos**\n"
        "> 📋  El usuario será notificado del cambio automáticamente\n"
        "> 🔒  El ticket se moverá al equipo correspondiente al instante"
    ), inline=False)
    e.set_image(url=BANNER_URL)
    e.set_footer(text="NightMc Network  ✦  Solo staff puede usar esta función",
                 icon_url=guild.icon.url if guild.icon else None)
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
        "┃  📋  **Postulaciones Staff** — Dudas sobre el proceso de postulación\n"
        "┃  🤝  **Alianzas** — Propuestas de colaboración\n"
        "┃  🎉  **Eventos** — Premios no recibidos, participación\n"
        "┃  🤖  **Soporte de Bots** — Bugs o errores en los bots\n"
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
        "> Entra en <#1471893022630219920> y un miembro del\n"
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
        super().__init__(command_prefix="nm!", intents=intents, help_command=None)
        self._ticket_msg_ids: dict[int, int] = {}
        self._claimed_channels: dict[int, int] = {}
        self._last_rename: dict[int, float] = {}

    async def setup_hook(self):
        self.add_view(TicketLauncher())
        self.add_view(TicketControl())
        self.add_view(GiveawayView())
        print("✦  Bot de Tickets listo. Usa nm!sync para registrar los comandos slash.")

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
        rol_high = discord.utils.get(guild.roles, name="High Staff")
        rol_head = discord.utils.get(guild.roles, name="Head staff")
        perms  = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if rol_high:
            perms[rol_high] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        if rol_head:
            perms[rol_head] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
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
        if interaction.user.id == owner_id and not any(r.name == "Head staff" for r in interaction.user.roles):
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
        select = ui.Select(
            placeholder="✦  Selecciona el tipo de gestión...",
            options=[
                discord.SelectOption(label="Ganadores de Eventos",   value="ganadores-eventos",
                    emoji="🎖️", description="👑 Head staff — Premio no entregado"),
                discord.SelectOption(label="Unregister",             value="unregister",
                    emoji="🔐", description="👑 Head staff — Recuperación de cuenta"),
                discord.SelectOption(label="Reembolso",              value="reembolso",
                    emoji="💸", description="👑 Head staff — Reembolso tienda"),
                discord.SelectOption(label="Staff Report",           value="staff-report",
                    emoji="🚨", description="👑 Head staff — Reportar a un staff"),
                discord.SelectOption(label="Error de Configuración", value="error-config",
                    emoji="⚠️", description="👑 Head staff — Error de config/permisos"),
                discord.SelectOption(label="Revives",                value="revives",
                    emoji="💊", description="🔰 High staff — Recuperar inventario"),
                discord.SelectOption(label="Cambio de Nick",         value="cambio-nick",
                    emoji="✏️", description="🔰 High staff — Cambiar nick vinculado"),
                discord.SelectOption(label="Bug Critico de Bot",     value="bug-bot-critico",
                    emoji="🚨", description="👑 Head staff — Escalar problema grave de bot"),
                discord.SelectOption(label="Ver Owner del Ticket",   value="ver-owner",
                    emoji="🔎", description="👑 Head staff — Ver quien abrio este ticket"),
            ]
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        select  = interaction.data["values"]
        destino = select[0]

        # ── Ver Owner — solo Head staff, no mueve el ticket ──
        if destino == "ver-owner":
            if not any(r.name == "Head staff" for r in interaction.user.roles):
                return await interaction.response.send_message(
                    "❌  Solo **Head staff** puede usar esta opción.", ephemeral=True)
            owner_id = self.owner_id or _get_owner_id_from_topic(interaction.channel)
            owner    = interaction.guild.get_member(owner_id) if owner_id else None
            e = discord.Embed(color=COLOR_BLUE)
            e.set_author(name="NightMc Network  ✦  Info del Ticket",
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            e.title = "👁️  Owner del Ticket"
            if owner:
                e.add_field(name="👤  Usuario",   value=f"> {owner.mention}",       inline=True)
                e.add_field(name="🏷️  Nombre",    value=f"> `{owner.name}`",        inline=True)
                e.add_field(name="🆔  ID",         value=f"> `{owner.id}`",          inline=True)
                e.add_field(name="📅  En server",  value=f"> <t:{int(owner.joined_at.timestamp())}:D>", inline=True)
                e.set_thumbnail(url=owner.display_avatar.url)
            else:
                e.description = "> ❌  No se pudo obtener la información del owner."
            e.set_footer(text=FOOTER, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            return await interaction.response.send_message(embed=e, ephemeral=True)

        sub      = TRANSFER_SUBS.get(destino)
        if not sub:
            return await interaction.response.send_message("❌  Subcategoría no encontrada.", ephemeral=True)
        nombre_rol, cat_nombre, label = sub
        rol_nuevo  = discord.utils.get(interaction.guild.roles, name=nombre_rol)
        canal      = interaction.channel
        guild      = interaction.guild
        owner_id   = self.owner_id or _get_owner_id_from_topic(canal)

        await interaction.response.defer()

        # ── Crear o buscar la categoría destino con permisos correctos ──
        cat_t = discord.utils.get(guild.categories, name=cat_nombre)
        if not cat_t:
            overwrites_cat = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
            }
            if rol_nuevo:
                overwrites_cat[rol_nuevo] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            try:
                cat_t = await guild.create_category(cat_nombre, overwrites=overwrites_cat)
            except discord.Forbidden:
                cat_t = None

        # ── Quitar permisos de staff anterior en el canal ──
        roles_quitar = [STAFF_TEAM] + [n for n, _ in ROLES_TICKET.values() if n]
        for target in list(canal.overwrites):
            if isinstance(target, discord.Role) and target.name in roles_quitar:
                try: await canal.set_permissions(target, overwrite=None)
                except discord.Forbidden: pass

        # ── Dar permisos al nuevo rol en el canal ──
        if rol_nuevo:
            try: await canal.set_permissions(rol_nuevo, read_messages=True, send_messages=True)
            except discord.Forbidden: pass

        # ── Mantener permisos del usuario dueño del ticket ──
        if owner_id:
            owner = guild.get_member(owner_id)
            if owner:
                try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
                except discord.Forbidden: pass

        # ── Mover el canal a la nueva categoría ──
        if cat_t and canal.category != cat_t:
            try: await canal.edit(category=cat_t, sync_permissions=False)
            except (discord.Forbidden, discord.HTTPException): pass

        # ── Renombrar canal ──
        asyncio.create_task(rename_robusto(canal, destino + "-pendiente"))

        await resetear_claim_en_canal(canal, destino, owner_id)
        mention = rol_nuevo.mention if rol_nuevo else f"@{nombre_rol}"
        await interaction.followup.send(embed=embed_transfer_msg(label, guild))
        await canal.send(f"{mention}  ✦  Se requiere atención en este ticket — **{label}**.")
        log_e = discord.Embed(title="🔄  Ticket Transferido", color=COLOR_WARN, timestamp=datetime.datetime.now())
        log_e.add_field(name="Canal",    value=canal.mention,            inline=True)
        log_e.add_field(name="Destino",  value=label,                    inline=True)
        log_e.add_field(name="Rol",      value=nombre_rol,               inline=True)
        log_e.add_field(name="Staff",    value=interaction.user.mention, inline=True)
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

class PostulacionModal(ui.Modal, title="NightMc  ·  Dudas de Postulación"):
    nick  = ui.TextInput(label="Nick", placeholder="Tu nick en Minecraft")
    duda  = ui.TextInput(label="Duda sobre tu postulación", placeholder="¿Qué duda tienes sobre el proceso?",
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
class BotsModal(ui.Modal, title="NightMc  ·  Soporte de Bots"):
    bot_nombre   = ui.TextInput(label="Bot afectado",   placeholder="¿Qué bot está fallando?")
    nick         = ui.TextInput(label="Tu nick",         placeholder="Tu nick en Minecraft o Discord")
    problema     = ui.TextInput(label="Problema",        placeholder="Describe qué está pasando con detalle",
                                style=discord.TextStyle.paragraph)
    reproducible = ui.TextInput(label="¿Se puede reproducir?", placeholder="Ej: Sí, cada vez que uso /comando",
                                style=discord.TextStyle.paragraph, required=False)
    async def on_submit(self, i):
        await crear_ticket(i, "bots",
            {"Bot": self.bot_nombre.value, "Nick": self.nick.value,
             "Problema": self.problema.value,
             "Reproducible": self.reproducible.value or "No especificado"}, "bots")

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
                       emoji="📋", description="Dudas sobre el proceso de postulación"),
                   discord.SelectOption(label="Alianzas",             value="alianza",
                       emoji="🤝", description="Propuestas de colaboración"),
                   discord.SelectOption(label="Eventos",              value="evento",
                       emoji="🎉", description="Premios no recibidos, participación"),
                   discord.SelectOption(label="Soporte de Bots",      value="bots",
                       emoji="🤖", description="Bugs, errores o mal funcionamiento de bots"),
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
            "bots":         BotsModal(),
        }
        await interaction.response.send_modal(modales[select.values[0]])

# ╔═══════════════════════════════════════════════════════════════╗
#   ⚡  SLASH COMMANDS
# ╚═══════════════════════════════════════════════════════════════╝

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
    if interaction.user.id == owner_id and not any(r.name == "Head staff" for r in interaction.user.roles):
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







def _get_rango(member: discord.Member) -> str:
    roles = [r.name for r in member.roles]
    if "Head staff" in roles:       return "head"
    if "High Staff" in roles:       return "high"
    if "Medium Staff" in roles:     return "medium"
    if "Low staff" in roles:        return "low"
    if "Staff team" in roles:       return "staff"
    if "| Soporte" in roles:        return "soporte"
    return "usuario"

def _build_help(guild, member: discord.Member = None):
    rango = _get_rango(member) if member else "usuario"

    e = discord.Embed(color=COLOR_BLUE)
    e.set_author(name="NightMc Network  ✦  Centro de Comandos",
                 icon_url=guild.icon.url if guild.icon else None)
    e.title = "📋  Guía de Comandos — NightMc Network"
    e.set_image(url=BANNER_URL)

    # ── | Soporte — solo lectura ──────────────────────────────────
    if rango == "soporte":
        e.description = (
            f"Hola {member.mention}, puedes **ver** los tickets pero no interactuar con ellos.\n"
            f"{SEP}\n"
            f"> ℹ️  Para más permisos habla con un **Head staff**."
        )
        e.set_footer(text=FOOTER, icon_url=guild.icon.url if guild.icon else None)
        return e

    # ── Leyenda de colores ────────────────────────────────────────
    if rango in ("low", "medium", "staff", "high", "head"):
        e.description = (
            f"Hola {member.mention}, aquí están todos tus comandos.\n"
            f"Prefijo: `nm!`  ·  Slash: `/`\n"
            f"{SEP}\n"
            f"🟢 Todos  ·  🔵 Staff  ·  🟠 High Staff  ·  🔴 Head staff\n"
            f"{SEP}"
        )
    else:
        e.description = (
            f"Hola {member.mention if member else ''}! Aquí tienes todos los comandos disponibles.\n"
            f"{SEP}"
        )

    # ── General — todos ───────────────────────────────────────────
    e.add_field(name="🌐  General  🟢", value=(
        "> `/ip` `nm!ip` — IPs y modalidades del servidor\n"
        "> `/rank` — Ver tu nivel y XP actual\n"
        "> `/leaderboard` — Top 10 jugadores por nivel\n"
        "> `/sugerencia` — Enviar una sugerencia al equipo\n"
        "> `/rules` `nm!rules` — Reglas *(dc = Discord · mc = Minecraft)*\n"
        "> `/avatar` `/banner` `/userinfo` `/serverinfo` — Perfil\n"
        "> `/ping` `nm!ping` — Latencia del bot\n"
        "> `/help` `nm!help` — Este menú"
    ), inline=False)

    # ── Tickets — staff base ──────────────────────────────────────
    if rango in ("low", "medium", "staff", "high", "head"):
        e.add_field(name="🎫  Tickets  🔵", value=(
            "> `/claim` `nm!claim` — Reclamar el ticket\n"
            "> `/close` `nm!close` — Cerrar y eliminar el ticket\n"
            "> `/transcript` — Generar transcript del historial\n"
            "> `/add @usuario` — Añadir usuario al ticket\n"
            "> `/remove @usuario` — Eliminar usuario del ticket\n"
            "> `/rename <nombre>` — Renombrar el canal\n"
            "> `/slowmode [seg]` — Modo lento *(0 = desactivar)*\n"
            "> `/transfer` — Derivar a otro equipo de staff\n"
            "> `/specifictag_staff @staff` — Asignar a staff específico\n"
            "> `/specifictag_role @rol` — Asignar a rol específico"
        ), inline=False)

    # ── High Staff ───────────────────────────────────────────────
    if rango in ("high", "head"):
        e.add_field(name="🔎  Registros  🟠", value=(
            "> Acceso al canal **#logs-tickets**\n"
            "> Se registran apertura, cierre y transcripts de tickets"
        ), inline=False)

    # ── Head staff ───────────────────────────────────────────────
    if rango == "head":
        e.add_field(name="🎉  Sorteos  🔴", value=(
            "> `/giveaway` — Crear sorteo oficial\n"
            "> `/giveaway_end <id>` — Terminar sorteo anticipadamente\n"
            "> `/giveaway_reroll <id>` — Elegir nuevo ganador"
        ), inline=False)
        e.add_field(name="🔐  Administración  🔴", value=(
            "> `nm!setup` — Publicar panel de tickets\n"
            "> `nm!sync` — Registrar slash commands\n"
            "> ⚠️  *Requieren permiso de* ***Administrador***"
        ), inline=False)

    e.add_field(name=SEP, value=(
        "> 💡  Si un slash no responde, usa el prefijo `nm!`\n"
        "> 🎫  Para soporte abre un ticket en el canal correspondiente"
    ), inline=False)
    e.set_footer(text=FOOTER, icon_url=guild.icon.url if guild.icon else None)
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
    await interaction.response.send_message(embed=_build_help(interaction.guild, interaction.user), ephemeral=True)

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
    await ctx.send("⏳  Registrando comandos slash...")
    try:
        # Sincronizar directamente al guild — no depende de comandos globales
        synced = await bot.tree.sync(guild=ctx.guild)
        nombres = "\n".join(f"  · `/{cmd.name}`" for cmd in synced)
        await ctx.send(
            f"✅  **{len(synced)} comandos** registrados en **{ctx.guild.name}**.\n"
            f"💡  Si no aparecen haz **Ctrl+R**.\n{nombres}"
        )
        for cmd in synced:
            print(f"  · /{cmd.name}")
    except Exception as e:
        await ctx.send(f"❌  Error: `{e}`")

@bot.command(name="claim")
async def claim_prefix(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    owner_id = _get_owner_id_from_topic(ctx.channel)
    if ctx.author.id == owner_id and not any(r.name == "Head staff" for r in ctx.author.roles):
        return await ctx.send(ERR_PROPIO)
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
    try: await ctx.message.delete()
    except discord.Forbidden: pass
    await ctx.author.send(embed=_build_help(ctx.guild, ctx.author))

@bot.command(name="ip")
async def ip_prefix(ctx):
    await ctx.send(embed=_build_ip_embed())

@bot.command(name="ping")
async def ping_prefix(ctx):
    latencia = round(bot.latency * 1000)
    e = discord.Embed(color=COLOR_OK)
    e.title = "🏓  Pong!"
    e.description = f"> Latencia del bot: **{latencia}ms**"
    e.set_footer(text=FOOTER)
    await ctx.send(embed=e)

@bot.tree.command(name="ping", description="Muestra la latencia del bot")
async def ping_slash(interaction: discord.Interaction):
    latencia = round(bot.latency * 1000)
    e = discord.Embed(color=COLOR_OK)
    e.title = "🏓  Pong!"
    e.description = f"> Latencia del bot: **{latencia}ms**"
    e.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.command(name="info")
async def info_prefix(ctx):
    e = discord.Embed(title="ℹ️  NightMc Network — Info del Bot", color=COLOR_BLUE)
    e.set_author(name="NightMc Network", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
    e.description = (
        f"> **Bot:** {bot.user.mention}\n"
        f"> **Servidores:** {len(bot.guilds)}\n"
        f"> **Latencia:** {round(bot.latency * 1000)}ms\n"
        f"> **Prefijo:** `nm!`\n"
        f"> **Slash:** `/`"
    )
    e.set_footer(text=FOOTER)
    await ctx.send(embed=e)

@bot.tree.command(name="info", description="Muestra información del bot")
async def info_slash(interaction: discord.Interaction):
    e = discord.Embed(title="ℹ️  NightMc Network — Info del Bot", color=COLOR_BLUE)
    e.set_author(name="NightMc Network", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    e.description = (
        f"> **Bot:** {bot.user.mention}\n"
        f"> **Servidores:** {len(bot.guilds)}\n"
        f"> **Latencia:** {round(bot.latency * 1000)}ms\n"
        f"> **Prefijo:** `nm!`\n"
        f"> **Slash:** `/`"
    )
    e.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=e, ephemeral=True)

def _build_rules_mc(guild):
    e = discord.Embed(color=COLOR_BASE)
    e.set_author(name="NightMc Network  ✦  Reglamento", icon_url=guild.icon.url if guild.icon else None)
    e.title = "⚔️  Reglas del Servidor Minecraft — NightMC"
    e.description = f"Lee y respeta estas normas. El desconocimiento no exime de sanciones.\n{SEP}"
    e.add_field(name="1️⃣  Respeto y juego limpio", value="> No insultos, acoso, trampas ni comportamientos que afecten a otros jugadores.", inline=False)
    e.add_field(name="2️⃣  Prohibido hacks o exploits", value="> Hacks, mods ilegales o glitches serán sancionados inmediatamente.", inline=False)
    e.add_field(name="3️⃣  Protección de construcciones", value="> No destruir, robar construcciones ni cofres ajenos. Respeta las zonas protegidas.", inline=False)
    e.add_field(name="4️⃣  No publicidad", value="> Prohibido promocionar otros servidores, tiendas o servicios sin permiso del staff.", inline=False)
    e.add_field(name="5️⃣  Autoridad del staff", value="> Administradores y moderadores tienen la última palabra en disputas. Respeta sus decisiones.", inline=False)
    e.add_field(name="6️⃣  Respeto en chats y voz", value="> Lenguaje ofensivo, spam o contenido inapropiado en cualquier canal está prohibido.", inline=False)
    e.add_field(name="7️⃣  Reportes", value="> Reporta conflictos o exploits al staff de forma responsable. No difundas rumores.", inline=False)
    e.add_field(name="8️⃣  Sanciones", value="> Según la gravedad: advertencia, expulsión temporal, baneo temporal o **permanente**.", inline=False)
    e.set_image(url=BANNER_URL)
    e.set_footer(text=FOOTER, icon_url=guild.icon.url if guild.icon else None)
    return e

def _build_rules_dc(guild):
    e = discord.Embed(color=COLOR_BLUE)
    e.set_author(name="NightMc Network  ✦  Reglamento", icon_url=guild.icon.url if guild.icon else None)
    e.title = "💬  Reglas de Discord — NightMC"
    e.description = f"Lee y respeta estas normas. El desconocimiento no exime de sanciones.\n{SEP}"
    e.add_field(name="1️⃣  Respeto absoluto", value="> Prohibido insultar, acosar o discriminar por raza, género, orientación, religión u opinión.", inline=False)
    e.add_field(name="2️⃣  Uso correcto de canales", value="> Publica solo en el canal correspondiente. Evita spam, off-topic o mensajes repetitivos.", inline=False)
    e.add_field(name="3️⃣  Contenido inapropiado", value="> Prohibido contenido NSFW, violento, ilegal o que infrinja derechos de autor.", inline=False)
    e.add_field(name="4️⃣  No publicidad no autorizada", value="> No promociones servidores, productos o servicios sin autorización del staff.", inline=False)
    e.add_field(name="5️⃣  Nombres y avatares", value="> Los ofensivos o explícitos serán modificados o sancionados.", inline=False)
    e.add_field(name="6️⃣  Instrucciones del staff", value="> Respetar las indicaciones de moderadores y administradores. Incumplirlas genera sanciones.", inline=False)
    e.add_field(name="7️⃣  Privacidad", value="> No compartas información personal propia ni de terceros (dirección, teléfono, cuentas, etc.).", inline=False)
    e.add_field(name="8️⃣  Sanciones", value="> Según la gravedad: advertencia, mute temporal, expulsión o **baneo permanente**.", inline=False)
    e.set_image(url=BANNER_URL)
    e.set_footer(text=FOOTER, icon_url=guild.icon.url if guild.icon else None)
    return e

@bot.command(name="rules", aliases=["reglas"])
async def rules_prefix(ctx, tipo: str = "dc"):
    if tipo.lower() in ("mc", "minecraft"):
        await ctx.send(embed=_build_rules_mc(ctx.guild))
    else:
        await ctx.send(embed=_build_rules_dc(ctx.guild))

@bot.tree.command(name="rules", description="Muestra las reglas del servidor")
@discord.app_commands.describe(tipo="'dc' para Discord, 'mc' para Minecraft")
@discord.app_commands.choices(tipo=[
    discord.app_commands.Choice(name="Discord", value="dc"),
    discord.app_commands.Choice(name="Minecraft", value="mc"),
])
async def rules_slash(interaction: discord.Interaction, tipo: str = "dc"):
    if tipo == "mc":
        await interaction.response.send_message(embed=_build_rules_mc(interaction.guild))
    else:
        await interaction.response.send_message(embed=_build_rules_dc(interaction.guild))

# ╔═══════════════════════════════════════════════════════════════╗
#   🏆  SISTEMA DE NIVELES
# ╚═══════════════════════════════════════════════════════════════╝
import random as _random

_xp_cooldowns: dict[int, float] = {}  # uid → timestamp último mensaje con XP

def _load_niveles() -> dict:
    if os.path.exists(NIVELES_FILE):
        try:
            with open(NIVELES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_niveles(data: dict):
    with open(NIVELES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _get_user_xp(data: dict, uid: int) -> dict:
    key = str(uid)
    if key not in data:
        data[key] = {"xp": 0, "nivel": 0, "mensajes": 0}
    return data[key]

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        await bot.process_commands(message)
        return

    import time
    uid   = message.author.id
    ahora = time.time()

    # Cooldown de XP
    if ahora - _xp_cooldowns.get(uid, 0) >= XP_COOLDOWN_SEG:
        _xp_cooldowns[uid] = ahora
        data        = _load_niveles()
        u           = _get_user_xp(data, uid)
        nivel_antes = u["nivel"]

        # XP ganado: base + bonus por nivel (más nivel = más XP pero también más se necesita)
        xp_add = _random.randint(XP_MIN, XP_MAX)
        u["xp"]      += xp_add
        u["mensajes"] = u.get("mensajes", 0) + 1
        u["nivel"]    = _nivel_desde_xp(u["xp"])
        _save_niveles(data)

        # ── Subió de nivel → mensaje en canal ──
        if u["nivel"] > nivel_antes:
            nivel_nuevo = u["nivel"]
            xp_sig      = _xp_para_nivel(nivel_nuevo + 1)
            colores = [0x95a5a6, 0x2ecc71, 0x3498db, 0x9b59b6, 0xf39c12, 0xe74c3c]
            color   = colores[min(nivel_nuevo // 10, len(colores) - 1)]

            e = discord.Embed(color=color)
            e.set_author(
                name="NightMc Network  ✦  ¡Subiste de nivel!",
                icon_url=message.guild.icon.url if message.guild.icon else None
            )
            e.description = (
                f"🎉  ¡Felicidades {message.author.mention}!\n"
                f"Alcanzaste el **nivel {nivel_nuevo}** 🚀\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            e.add_field(name="⭐  XP Total",     value=f"`{u['xp']} XP`",             inline=True)
            e.add_field(name="📊  Nivel",         value=f"`{nivel_nuevo}`",              inline=True)
            e.add_field(name="🎯  Próximo nivel", value=f"`{xp_sig - u['xp']} XP`",   inline=True)
            e.set_thumbnail(url=message.author.display_avatar.url)
            e.set_footer(text=FOOTER, icon_url=message.guild.icon.url if message.guild.icon else None)
            try:
                await message.channel.send(embed=e)
            except Exception:
                pass

            # ── Premio por nivel especial → DM ──
            if nivel_nuevo in PREMIOS_NIVEL:
                rango, duracion = PREMIOS_NIVEL[nivel_nuevo]
                dm = discord.Embed(color=0xf1c40f)
                dm.set_author(
                    name="NightMc Network  ✦  ¡Ganaste un premio!",
                    icon_url=message.guild.icon.url if message.guild.icon else None
                )
                dm.title = f"🎁  ¡Felicidades, {message.author.display_name}!"
                dm.description = (
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Por tu dedicación en **NightMC Network**\n"
                    f"alcanzaste el **nivel {nivel_nuevo}** y ganaste:\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                )
                dm.add_field(name="🏆  Rango",     value=f"> **{rango}**",    inline=True)
                dm.add_field(name="⏳  Duración",  value=f"> **{duracion}**", inline=True)
                dm.add_field(
                    name="📋  ¿Cómo reclamarlo?",
                    value=(
                        "> Abre un ticket en el servidor con el tipo\n"
                        "> **Pagos Tienda** y muestra este mensaje.\n"
                        "> El staff verificará tu nivel y te dará el rango."
                    ),
                    inline=False
                )
                dm.set_thumbnail(url=message.author.display_avatar.url)
                dm.set_image(url=BANNER_URL)
                dm.set_footer(
                    text="© Powered by NightMC  ✦  ¡Gracias por jugar!",
                    icon_url=message.guild.icon.url if message.guild.icon else None
                )
                try:
                    await message.author.send(embed=dm)
                    # Aviso en el canal también
                    aviso = discord.Embed(color=0xf1c40f)
                    aviso.description = (
                        f"🎁  {message.author.mention} alcanzó el **nivel {nivel_nuevo}**\n"
                        f"y ganó el rango **{rango}** por **{duracion}**. ¡Revisa tus DMs! 📬"
                    )
                    await message.channel.send(embed=aviso)
                except discord.Forbidden:
                    # DMs cerrados — avisa en el canal
                    aviso = discord.Embed(color=0xf39c12)
                    aviso.description = (
                        f"🎁  {message.author.mention} ganó el rango **{rango}** por **{duracion}**\n"
                        f"⚠️  No pude enviarte el DM. Abre tus DMs y contacta al staff para reclamarlo."
                    )
                    await message.channel.send(embed=aviso)

    await bot.process_commands(message)

@bot.tree.command(name="rank", description="Muestra tu nivel y XP en el servidor")
@discord.app_commands.describe(usuario="Usuario a consultar (vacío = tú mismo)")
async def rank_slash(interaction: discord.Interaction, usuario: discord.Member = None):
    target = usuario or interaction.user
    data   = _load_niveles()
    u      = _get_user_xp(data, target.id)
    nivel  = u["nivel"]
    xp     = u["xp"]

    # XP dentro del nivel actual (siempre positivo ahora)
    xp_base_nivel = _xp_para_nivel(nivel)       # XP necesario para llegar al nivel actual
    xp_base_sig   = _xp_para_nivel(nivel + 1)   # XP necesario para llegar al siguiente
    xp_en_nivel   = xp - xp_base_nivel          # XP ganado dentro del nivel actual
    xp_necesario  = xp_base_sig - xp_base_nivel # XP total requerido para subir

    # Barra de progreso (12 bloques)
    pct      = max(0, min(xp_en_nivel / xp_necesario, 1.0)) if xp_necesario > 0 else 1.0
    filled   = int(pct * 12)
    barra    = "🟩" * filled + "⬛" * (12 - filled)
    pct_txt  = f"{int(pct * 100)}%"

    # Posición en ranking
    ranking = sorted(data.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
    pos     = next((i+1 for i, (k, _) in enumerate(ranking) if k == str(target.id)), "?")

    # Premio ya obtenido (más alto alcanzado)
    ultimo_premio = None
    for lvl_req, (rango, dur) in sorted(PREMIOS_NIVEL.items()):
        if nivel >= lvl_req:
            ultimo_premio = (lvl_req, rango, dur)

    # Próximo premio
    prox_premio = None
    for lvl_req, (rango, dur) in sorted(PREMIOS_NIVEL.items()):
        if nivel < lvl_req:
            prox_premio = (lvl_req, rango, dur)
            break

    # Color según nivel
    colores = [0x95a5a6, 0x2ecc71, 0x3498db, 0x9b59b6, 0xf39c12, 0xe74c3c]
    color   = colores[min(nivel // 10, len(colores) - 1)]

    e = discord.Embed(color=color)
    e.set_author(
        name=f"NightMc Network  ✦  Perfil de {target.display_name}",
        icon_url=target.display_avatar.url
    )
    e.set_thumbnail(url=target.display_avatar.url)
    e.description = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐  **Nivel {nivel}**   ·   🏆  **Ranking #{pos}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    e.add_field(
        name=f"📊  Progreso — {pct_txt}",
        value=f"{barra}\n`{xp_en_nivel}` / `{xp_necesario}` XP  ·  Faltan `{xp_necesario - xp_en_nivel}` XP",
        inline=False
    )
    e.add_field(name="✨  XP Total",  value=f"> `{xp} XP`",              inline=True)
    e.add_field(name="💬  Mensajes",  value=f"> `{u.get('mensajes', 0)}`", inline=True)

    if ultimo_premio:
        e.add_field(name="🏅  Último premio", value=f"> **{ultimo_premio[1]}** (nv. `{ultimo_premio[0]}`)", inline=True)

    if prox_premio:
        xp_falta = _xp_para_nivel(prox_premio[0]) - xp
        e.add_field(
            name="🎁  Próximo premio",
            value=f"> **{prox_premio[1]}** al nivel `{prox_premio[0]}`  ·  faltan `{max(0, xp_falta)} XP`",
            inline=False
        )

    e.set_footer(text=FOOTER, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="leaderboard", description="Top 10 jugadores con más nivel en el servidor")
async def leaderboard_slash(interaction: discord.Interaction):
    data    = _load_niveles()
    ranking = sorted(data.items(), key=lambda x: x[1].get("xp", 0), reverse=True)[:10]
    medallas = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

    e = discord.Embed(color=0xf1c40f)
    e.set_author(name="NightMc Network  ✦  Ranking de Niveles",
                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    e.title = "🏆  Top 10 — Niveles del Servidor"

    if not ranking:
        e.description = f"{SEP}\n> Todavía nadie tiene XP. ¡Sé el primero hablando en el servidor!"
    else:
        lineas = []
        for i, (uid, u) in enumerate(ranking):
            m   = interaction.guild.get_member(int(uid))
            nom = m.display_name if m else f"<@{uid}>"
            med = medallas[i] if i < len(medallas) else f"`{i+1}.`"
            lineas.append(
                f"{med}  **{nom}**  ·  Nivel `{u['nivel']}`  ·  `{u['xp']} XP`"
            )
        e.description = SEP + "\n" + "\n".join(lineas)

    # Posición del que pregunta
    pos = next((i+1 for i, (k, _) in enumerate(
        sorted(data.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
    ) if k == str(interaction.user.id)), None)
    if pos:
        mi_xp = data.get(str(interaction.user.id), {}).get("xp", 0)
        mi_nv = data.get(str(interaction.user.id), {}).get("nivel", 0)
        e.add_field(name="📍  Tu posición",
                    value=f"> **#{pos}** — Nivel `{mi_nv}` · `{mi_xp} XP`", inline=False)

    e.set_image(url=BANNER_URL)
    e.set_footer(text=FOOTER, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    await interaction.response.send_message(embed=e)

# ╔═══════════════════════════════════════════════════════════════╗
#   💡  SISTEMA DE SUGERENCIAS
# ╚═══════════════════════════════════════════════════════════════╝
class SugerenciaModal(ui.Modal, title="NightMc  ·  Enviar Sugerencia"):
    sugerencia = ui.TextInput(
        label="Tu sugerencia",
        placeholder="Describe tu idea con el mayor detalle posible...",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    def __init__(self, modalidad: str):
        super().__init__()
        self.modalidad = modalidad

    async def on_submit(self, interaction: discord.Interaction):
        guild  = interaction.guild
        canal  = discord.utils.get(guild.text_channels, name=CANAL_SUGERENCIAS)
        if not canal:
            return await interaction.response.send_message(
                f"❌  No se encontró el canal `{CANAL_SUGERENCIAS}`. Avísale al staff.", ephemeral=True)

        e = discord.Embed(color=0x5865f2, timestamp=discord.utils.utcnow())
        e.set_author(
            name="NightMc Network  ✦  Nueva Sugerencia",
            icon_url=guild.icon.url if guild.icon else None
        )
        e.title = f"💡  Sugerencia — {self.modalidad}"
        e.description = (
            f"{SEP}\n"
            f"{self.sugerencia.value}\n"
            f"{SEP}"
        )
        e.add_field(name="🎮  Modalidad", value=f"> **{self.modalidad}**", inline=True)
        e.add_field(name="👤  Enviado por", value=f"> {interaction.user.mention}", inline=True)
        e.set_thumbnail(url=interaction.user.display_avatar.url)
        e.set_footer(text=FOOTER, icon_url=guild.icon.url if guild.icon else None)

        msg = await canal.send(embed=e)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        await interaction.response.send_message(
            f"✅  ¡Tu sugerencia fue enviada a {canal.mention}! Gracias por ayudar a mejorar NightMc 💙",
            ephemeral=True
        )

@bot.tree.command(name="sugerencia", description="Envía una sugerencia para mejorar el servidor")
@discord.app_commands.describe(modalidad="Modalidad a la que va dirigida tu sugerencia")
@discord.app_commands.choices(modalidad=[
    discord.app_commands.Choice(name="⚔️  ClashBox", value="ClashBox"),
])
async def sugerencia_slash(interaction: discord.Interaction, modalidad: str):
    await interaction.response.send_modal(SugerenciaModal(modalidad=modalidad))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("❌  Sin permisos.")
    raise error

# ╔═══════════════════════════════════════════════════════════════╗
#   🎉  GIVEAWAYS
# ╚═══════════════════════════════════════════════════════════════╝
giveaways_activos: dict[int, dict] = {}  # message_id → datos

class GiveawayView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Participar", style=discord.ButtonStyle.success,
               emoji="🎉", custom_id="giveaway_join")
    async def join(self, interaction: discord.Interaction, button: ui.Button):
        mid = interaction.message.id
        if mid not in giveaways_activos:
            return await interaction.response.send_message(
                "❌  Este sorteo ya no está activo.", ephemeral=True)
        gw = giveaways_activos[mid]
        uid = interaction.user.id
        if uid in gw["participantes"]:
            gw["participantes"].discard(uid)
            await interaction.response.send_message(
                "↩️  Has **salido** del sorteo.", ephemeral=True)
        else:
            gw["participantes"].add(uid)
            await interaction.response.send_message(
                "✅  ¡Estás participando en el sorteo! Buena suerte 🍀", ephemeral=True)
        # Actualizar embed con contador
        embed = interaction.message.embeds[0]
        for i, field in enumerate(embed.fields):
            if "Participantes" in field.name:
                embed.set_field_at(i, name=field.name,
                    value=f"> **{len(gw['participantes'])}** personas participando",
                    inline=field.inline)
                break
        await interaction.message.edit(embed=embed)

def _build_giveaway_embed(guild, prize, duration_str, winners, host, ends_at):
    e = discord.Embed(color=0xf1c40f)
    e.set_author(name="🎊  NightMc Network — Sorteo Oficial",
                 icon_url=guild.icon.url if guild.icon else None)
    e.title = f"🎁  {prize}"
    e.description = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"¡Pulsa el botón 🎉 para participar!\n"
        f"Puedes salir del sorteo volviendo a pulsarlo.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    e.add_field(name="🏆  Premio",        value=f"> **{prize}**",              inline=True)
    e.add_field(name="🥇  Ganadores",     value=f"> **{winners}** ganador{'es' if winners > 1 else ''}",    inline=True)
    e.add_field(name="⏱️  Duración",      value=f"> **{duration_str}**",       inline=True)
    e.add_field(name="👥  Participantes", value="> **0** personas participando", inline=True)
    e.add_field(name="🎙️  Organizado por", value=f"> {host.mention}",          inline=True)
    e.add_field(name="⏰  Termina",       value=f"> <t:{int(ends_at.timestamp())}:R>", inline=True)
    e.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value=(
        "> 🔹 Un solo registro por persona\n"
        "> 🔹 Debes estar en el servidor al momento del sorteo\n"
        "> 🔹 El staff puede descalificar participantes"
    ), inline=False)
    e.set_image(url=BANNER_URL)
    e.set_footer(text="© Powered by NightMC  ✦  ¡Buena suerte a todos!",
                 icon_url=guild.icon.url if guild.icon else None)
    return e

class GiveawayModal(ui.Modal, title="NightMc  ·  Crear Sorteo"):
    premio    = ui.TextInput(label="Premio", placeholder="Ej: Rango VIP, 10€ tienda, etc.")
    duracion  = ui.TextInput(label="Duración", placeholder="Ej: 1h, 30m, 2d, 1h30m")
    ganadores = ui.TextInput(label="Número de ganadores", placeholder="Ej: 1", default="1")
    requisito = ui.TextInput(label="Requisito (opcional)", placeholder="Ej: Tener rango Member",
                             required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # Parsear duración
        import re
        raw = self.duracion.value.strip().lower()
        total_seconds = 0
        for valor, unidad in re.findall(r'(\d+)(d|h|m|s)', raw):
            v = int(valor)
            if unidad == 'd': total_seconds += v * 86400
            elif unidad == 'h': total_seconds += v * 3600
            elif unidad == 'm': total_seconds += v * 60
            elif unidad == 's': total_seconds += v
        if total_seconds == 0:
            return await interaction.response.send_message(
                "❌  Duración inválida. Usa formato como `1h`, `30m`, `2d`, `1h30m`.", ephemeral=True)

        try:
            num_ganadores = max(1, int(self.ganadores.value.strip()))
        except ValueError:
            num_ganadores = 1

        # Texto de duración legible
        partes = []
        d, rem = divmod(total_seconds, 86400)
        h, rem = divmod(rem, 3600)
        m, s   = divmod(rem, 60)
        if d: partes.append(f"{d}d")
        if h: partes.append(f"{h}h")
        if m: partes.append(f"{m}m")
        if s: partes.append(f"{s}s")
        dur_str = " ".join(partes)

        ends_at = datetime.datetime.now() + datetime.timedelta(seconds=total_seconds)
        embed   = _build_giveaway_embed(
            interaction.guild, self.premio.value,
            dur_str, num_ganadores, interaction.user, ends_at)

        if self.requisito.value:
            embed.add_field(name="📋  Requisito", value=f"> {self.requisito.value}", inline=False)

        await interaction.response.send_message("✅  Sorteo creado.", ephemeral=True)
        msg = await interaction.channel.send(
            content="@everyone  🎉  **¡NUEVO SORTEO EN NIGHTMC!**",
            embed=embed, view=GiveawayView())

        giveaways_activos[msg.id] = {
            "participantes": set(),
            "ganadores":     num_ganadores,
            "premio":        self.premio.value,
            "ends_at":       ends_at,
            "host":          interaction.user.id,
            "channel_id":    interaction.channel.id,
            "guild_id":      interaction.guild.id,
        }

        # Tarea que termina el sorteo automáticamente
        async def finalizar():
            await asyncio.sleep(total_seconds)
            gw = giveaways_activos.pop(msg.id, None)
            if not gw:
                return
            guild   = bot.get_guild(gw["guild_id"])
            channel = bot.get_channel(gw["channel_id"])
            if not guild or not channel:
                return
            participantes = list(gw["participantes"])
            import random
            e_final = discord.Embed(color=0xed4245)
            e_final.set_author(name="🎊  NightMc Network — Sorteo Finalizado",
                               icon_url=guild.icon.url if guild.icon else None)
            e_final.title = f"🎁  {gw['premio']}"
            if not participantes:
                e_final.description = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n❌  Nadie participó en este sorteo.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                e_final.set_image(url=BANNER_URL)
                e_final.set_footer(text="© Powered by NightMC")
                await msg.edit(embed=e_final, view=None)
                await channel.send("😢  Nadie participó en el sorteo. Se cancela.")
                return
            ganadores_ids = random.sample(participantes, min(gw["ganadores"], len(participantes)))
            menciones     = " ".join(f"<@{uid}>" for uid in ganadores_ids)
            e_final.description = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"¡El sorteo ha terminado!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            e_final.add_field(name="🏆  Premio",      value=f"> **{gw['premio']}**",                    inline=True)
            e_final.add_field(name="👥  Participaron", value=f"> **{len(participantes)}** personas",     inline=True)
            e_final.add_field(name="🥇  Ganador(es)", value=f"> {menciones}",                           inline=False)
            e_final.set_image(url=BANNER_URL)
            e_final.set_footer(text="© Powered by NightMC  ✦  ¡Felicidades!",
                               icon_url=guild.icon.url if guild.icon else None)
            await msg.edit(embed=e_final, view=None)
            await channel.send(
                f"🎉🎊  ¡Felicidades {menciones}! Ganaste **{gw['premio']}**.\n"
                f"Contacta al staff para reclamar tu premio.")

        asyncio.create_task(finalizar())

@bot.tree.command(name="giveaway", description="Crea un sorteo oficial")
async def giveaway_slash(interaction: discord.Interaction):
    if not tiene_rango_minimo(interaction.user, "Head staff"):
        return await interaction.response.send_message(
            "❌  Solo el **Head staff** puede crear sorteos.", ephemeral=True)
    await interaction.response.send_modal(GiveawayModal())

@bot.tree.command(name="giveaway_end", description="Termina un sorteo anticipadamente")
@discord.app_commands.describe(message_id="ID del mensaje del sorteo")
async def giveaway_end_slash(interaction: discord.Interaction, message_id: str):
    if not tiene_rango_minimo(interaction.user, "Head staff"):
        return await interaction.response.send_message(
            "❌  Solo el **Head staff** puede terminar sorteos.", ephemeral=True)
    try:
        mid = int(message_id)
    except ValueError:
        return await interaction.response.send_message("❌  ID inválido.", ephemeral=True)
    if mid not in giveaways_activos:
        return await interaction.response.send_message("❌  No se encontró un sorteo activo con ese ID.", ephemeral=True)
    gw      = giveaways_activos.pop(mid)
    guild   = interaction.guild
    channel = interaction.channel
    import random
    participantes = list(gw["participantes"])
    msg     = await channel.fetch_message(mid)
    e_final = discord.Embed(color=0xed4245)
    e_final.set_author(name="🎊  NightMc Network — Sorteo Finalizado",
                       icon_url=guild.icon.url if guild.icon else None)
    e_final.title = f"🎁  {gw['premio']}"
    if not participantes:
        e_final.description = "❌  Nadie participó en este sorteo."
        await msg.edit(embed=e_final, view=None)
        return await interaction.response.send_message("😢  Nadie participó.", ephemeral=True)
    ganadores_ids = random.sample(participantes, min(gw["ganadores"], len(participantes)))
    menciones     = " ".join(f"<@{uid}>" for uid in ganadores_ids)
    e_final.description = "¡El sorteo ha terminado anticipadamente!"
    e_final.add_field(name="🏆  Premio",      value=f"> **{gw['premio']}**",                inline=True)
    e_final.add_field(name="👥  Participaron", value=f"> **{len(participantes)}** personas", inline=True)
    e_final.add_field(name="🥇  Ganador(es)", value=f"> {menciones}",                       inline=False)
    e_final.set_image(url=BANNER_URL)
    e_final.set_footer(text="© Powered by NightMC  ✦  ¡Felicidades!",
                       icon_url=guild.icon.url if guild.icon else None)
    await msg.edit(embed=e_final, view=None)
    await channel.send(f"🎉  ¡Felicidades {menciones}! Ganaste **{gw['premio']}**.")
    await interaction.response.send_message("✅  Sorteo finalizado.", ephemeral=True)

@bot.tree.command(name="giveaway_reroll", description="Elige un nuevo ganador de un sorteo terminado")
@discord.app_commands.describe(message_id="ID del mensaje del sorteo terminado")
async def giveaway_reroll_slash(interaction: discord.Interaction, message_id: str):
    if not tiene_rango_minimo(interaction.user, "Head staff"):
        return await interaction.response.send_message(
            "❌  Solo el **Head staff** puede hacer reroll.", ephemeral=True)
    await interaction.response.send_message(
        "⚠️  Para hacer reroll contacta a un **Head staff** para revisar los logs del sorteo.",
        ephemeral=True)

# ╔═══════════════════════════════════════════════════════════════╗
#   👤  PERFIL — AVATAR / BANNER / USERINFO / SERVERINFO
# ╚═══════════════════════════════════════════════════════════════╝
def tiene_rango_minimo(member: discord.Member, nombre_rol_minimo: str) -> bool:
    rol_minimo = discord.utils.get(member.guild.roles, name=nombre_rol_minimo)
    if not rol_minimo:
        return False
    return member.top_role.position >= rol_minimo.position

@bot.tree.command(name="avatar", description="Muestra el avatar de un usuario")
@discord.app_commands.describe(usuario="Usuario del que ver el avatar (vacío = tú mismo)")
async def avatar_slash(interaction: discord.Interaction, usuario: discord.Member = None):
    target = usuario or interaction.user
    e = discord.Embed(color=COLOR_BLUE)
    e.set_author(name=f"🖼️  Avatar de {target.display_name}",
                 icon_url=target.display_avatar.url)
    e.description = (
        f"> 👤  **{target.display_name}** (`{target.name}`)\n"
        f"> 🆔  `{target.id}`"
    )
    formats = []
    base = target.display_avatar.url
    for fmt in ["png", "jpg", "webp"]:
        formats.append(f"[{fmt.upper()}]({target.display_avatar.with_format(fmt).url})")
    if target.display_avatar.is_animated():
        formats.append(f"[GIF]({target.display_avatar.with_format('gif').url})")
    e.add_field(name="📥  Descargar", value=" · ".join(formats), inline=False)
    e.set_image(url=target.display_avatar.with_size(1024).url)
    e.set_footer(text=FOOTER, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="banner", description="Muestra el banner de un usuario")
@discord.app_commands.describe(usuario="Usuario del que ver el banner (vacío = tú mismo)")
async def banner_slash(interaction: discord.Interaction, usuario: discord.Member = None):
    target = usuario or interaction.user
    await interaction.response.defer()
    try:
        user_fetch = await bot.fetch_user(target.id)
    except Exception:
        return await interaction.followup.send("❌  No se pudo obtener el perfil.", ephemeral=True)
    if not user_fetch.banner:
        return await interaction.followup.send(
            f"❌  **{target.display_name}** no tiene banner de perfil.", ephemeral=True)
    e = discord.Embed(color=user_fetch.accent_color or COLOR_BLUE)
    e.set_author(name=f"🎨  Banner de {target.display_name}",
                 icon_url=target.display_avatar.url)
    e.description = (
        f"> 👤  **{target.display_name}** (`{target.name}`)\n"
        f"> 🆔  `{target.id}`"
    )
    formats = []
    for fmt in ["png", "jpg", "webp"]:
        formats.append(f"[{fmt.upper()}]({user_fetch.banner.with_format(fmt).url})")
    if user_fetch.banner.is_animated():
        formats.append(f"[GIF]({user_fetch.banner.with_format('gif').url})")
    e.add_field(name="📥  Descargar", value=" · ".join(formats), inline=False)
    e.set_image(url=user_fetch.banner.with_size(1024).url)
    e.set_footer(text=FOOTER, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    await interaction.followup.send(embed=e)

@bot.tree.command(name="userinfo", description="Muestra información de un usuario")
@discord.app_commands.describe(usuario="Usuario del que ver la info (vacío = tú mismo)")
async def userinfo_slash(interaction: discord.Interaction, usuario: discord.Member = None):
    target = usuario or interaction.user
    roles  = [r.mention for r in reversed(target.roles) if r.name != "@everyone"]
    e = discord.Embed(color=target.color if target.color.value else COLOR_BLUE)
    e.set_author(name=f"👤  Información de {target.display_name}",
                 icon_url=target.display_avatar.url)
    e.set_thumbnail(url=target.display_avatar.url)
    e.add_field(name="🏷️  Nombre",        value=f"> `{target.name}`",                                        inline=True)
    e.add_field(name="🎭  Apodo",          value=f"> `{target.nick or '—'}`",                                 inline=True)
    e.add_field(name="🆔  ID",             value=f"> `{target.id}`",                                          inline=True)
    e.add_field(name="📅  Cuenta creada",  value=f"> <t:{int(target.created_at.timestamp())}:D>",             inline=True)
    e.add_field(name="📥  Entró al server",value=f"> <t:{int(target.joined_at.timestamp())}:D>",              inline=True)
    e.add_field(name="🤖  Bot",            value=f"> {'Sí' if target.bot else 'No'}",                         inline=True)
    e.add_field(name="🎨  Color del rol",  value=f"> `{str(target.color)}` " if target.color.value else "> `Sin color`", inline=True)
    e.add_field(name="⚡  Estado",         value=f"> `{str(target.status).capitalize()}`" if hasattr(target, 'status') else "> `—`", inline=True)
    if roles:
        roles_str = " ".join(roles[:15])
        if len(roles) > 15:
            roles_str += f" *+{len(roles)-15} más*"
        e.add_field(name=f"🏅  Roles ({len(roles)})", value=roles_str, inline=False)
    e.set_footer(text=FOOTER, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="serverinfo", description="Muestra información del servidor")
async def serverinfo_slash(interaction: discord.Interaction):
    guild  = interaction.guild
    total  = guild.member_count
    bots   = sum(1 for m in guild.members if m.bot)
    humanos= total - bots
    e = discord.Embed(color=COLOR_BLUE)
    e.set_author(name=f"🏰  {guild.name}",
                 icon_url=guild.icon.url if guild.icon else None)
    e.set_thumbnail(url=guild.icon.url if guild.icon else None)
    e.add_field(name="🆔  ID",             value=f"> `{guild.id}`",                                      inline=True)
    e.add_field(name="👑  Dueño",          value=f"> {guild.owner.mention}",                             inline=True)
    e.add_field(name="📅  Creado",         value=f"> <t:{int(guild.created_at.timestamp())}:D>",         inline=True)
    e.add_field(name="👥  Miembros",       value=f"> 👤 **{humanos}** humanos\n> 🤖 **{bots}** bots\n> 📊 **{total}** total", inline=True)
    e.add_field(name="📢  Canales",        value=f"> 💬 **{len(guild.text_channels)}** texto\n> 🔊 **{len(guild.voice_channels)}** voz\n> 📁 **{len(guild.categories)}** categorías", inline=True)
    e.add_field(name="🎭  Roles",          value=f"> **{len(guild.roles)}** roles",                      inline=True)
    e.add_field(name="🚀  Boost",          value=f"> Nivel **{guild.premium_tier}**\n> **{guild.premium_subscription_count}** boosts", inline=True)
    e.add_field(name="🌍  Región",         value=f"> `{str(guild.preferred_locale)}`",                   inline=True)
    e.add_field(name="🔒  Verificación",   value=f"> `{str(guild.verification_level).capitalize()}`",    inline=True)
    if guild.banner:
        e.set_image(url=guild.banner.with_size(1024).url)
    e.set_footer(text=FOOTER, icon_url=guild.icon.url if guild.icon else None)
    await interaction.response.send_message(embed=e)

# ╔═══════════════════════════════════════════════════════════════╗
#   🔧  COMANDOS DE ADMIN — TESTING & MANTENIMIENTO
# ╚═══════════════════════════════════════════════════════════════╝

@bot.command(name="clearglobal")
@commands.has_permissions(administrator=True)
async def clearglobal(ctx):
    """Elimina todos los slash commands globales duplicados."""
    await ctx.send("⏳  Limpiando comandos globales... (puede tardar ~15s por rate limit de Discord)")
    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        await ctx.send("✅  Comandos globales eliminados. Usa `nm!sync` para registrarlos en este servidor.")
    except Exception as e:
        await ctx.send(f"❌  Error: `{e}`")

@bot.command(name="givexp")
@commands.has_permissions(administrator=True)
async def givexp(ctx, usuario: discord.Member = None, cantidad: int = 100):
    """Da XP a un usuario. Uso: nm!givexp @usuario 500"""
    if not usuario:
        return await ctx.send("❌  Uso: `nm!givexp @usuario cantidad`")
    if cantidad <= 0:
        return await ctx.send("❌  La cantidad debe ser mayor a 0.")

    data  = _load_niveles()
    u     = _get_user_xp(data, usuario.id)
    nivel_antes = u["nivel"]

    u["xp"]    += cantidad
    u["nivel"]  = _nivel_desde_xp(u["xp"])
    _save_niveles(data)


    e = discord.Embed(color=0x2ecc71)
    e.set_author(name="NightMc Network  ✦  XP Añadido", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
    e.description = (
        f"✅  Se añadieron **{cantidad} XP** a {usuario.mention}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    e.add_field(name="✨  XP Total",      value=f"`{u['xp']} XP`",   inline=True)
    e.add_field(name="⭐  Nivel actual",  value=f"`{u['nivel']}`",    inline=True)
    if u["nivel"] > nivel_antes:
        e.add_field(name="🎉  Subió de nivel", value=f"`{nivel_antes}` → `{u['nivel']}`", inline=True)
    e.set_footer(text=FOOTER)
    await ctx.send(embed=e)

@bot.command(name="removexp")
@commands.has_permissions(administrator=True)
async def removexp(ctx, usuario: discord.Member = None, cantidad: int = 100):
    """Quita XP a un usuario. Uso: nm!removexp @usuario 500"""
    if not usuario:
        return await ctx.send("❌  Uso: `nm!removexp @usuario cantidad`")

    data = _load_niveles()
    u    = _get_user_xp(data, usuario.id)

    u["xp"]    = max(0, u["xp"] - cantidad)
    u["nivel"] = _nivel_desde_xp(u["xp"])
    _save_niveles(data)

    await ctx.send(f"🔻  Se quitaron **{cantidad} XP** a {usuario.mention}. Ahora tiene `{u['xp']} XP` (nivel `{u['nivel']}`).")

@bot.command(name="setrank")
@commands.has_permissions(administrator=True)
async def setrank(ctx, usuario: discord.Member = None, nivel: int = 0):
    """Establece el nivel de un usuario directamente. Uso: nm!setrank @usuario 10"""
    if not usuario:
        return await ctx.send("❌  Uso: `nm!setrank @usuario nivel`")
    if nivel < 0:
        return await ctx.send("❌  El nivel debe ser 0 o mayor.")

    data = _load_niveles()
    u    = _get_user_xp(data, usuario.id)

    # Poner XP justo al inicio del nivel pedido
    u["xp"]    = _xp_para_nivel(nivel)
    u["nivel"] = nivel
    _save_niveles(data)


    e = discord.Embed(color=0x9b59b6)
    e.set_author(name="NightMc Network  ✦  Nivel Establecido", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
    e.description = (
        f"✅  {usuario.mention} fue puesto en **nivel {nivel}**\n"
        f"> XP asignado: `{u['xp']}`\n"
        f"> Rol de nivel asignado automáticamente."
    )
    e.set_footer(text=FOOTER)
    await ctx.send(embed=e)

@bot.command(name="resetxp")
@commands.has_permissions(administrator=True)
async def resetxp(ctx, usuario: discord.Member = None):
    """Resetea el XP de un usuario a 0. Uso: nm!resetxp @usuario"""
    if not usuario:
        return await ctx.send("❌  Uso: `nm!resetxp @usuario`")

    data = _load_niveles()
    data[str(usuario.id)] = {"xp": 0, "nivel": 0, "mensajes": 0}
    _save_niveles(data)

    await ctx.send(f"🔄  XP de {usuario.mention} reseteado a 0.")

# ╔═══════════════════════════════════════════════════════════════╗
#   🚀  ARRANQUE
# ╚═══════════════════════════════════════════════════════════════╝
if not TOKEN:
    print("\n❌  ERROR: No se encontró DISCORD_TOKEN")
    print("   Railway → Variables → añade DISCORD_TOKEN\n")
    exit(1)

bot.run(TOKEN)
