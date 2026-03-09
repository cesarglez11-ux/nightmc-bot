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
import asyncio, datetime, io, os

TOKEN = os.getenv("DISCORD_TOKEN")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ⚙️  CONFIGURACIÓN  —  Solo edita esta sección
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROL_LOW   = "Low staff"
ROL_MED   = "Medium Staff"
ROL_HIGH  = "Hight staff"
ROL_HEAD  = "Head staff"
ROL_TEAM  = "Staff team"

TODOS_STAFF      = [ROL_LOW, ROL_MED, ROL_HIGH, ROL_HEAD, ROL_TEAM]
ROLES_SUPERIORES = [ROL_HIGH, ROL_HEAD]

CAT_SOPORTE     = "🛠️ SOPORTE"
CAT_REPORTE     = "🚫 REPORTES"
CAT_APELACION   = "⚖️ APELACIONES"
CAT_PAGOS       = "💰 Pagos Tienda"
CAT_JUEGO       = "🎮 Soporte de Juego"
CAT_POSTULACION = "📋 Postulaciones Staff"
CAT_ALIANZA     = "🤝 Alianzas"
CAT_EVENTO      = "🎉 Eventos"
CAT_TRANSFER    = "🔄 TRANSFERIDOS"
LOGS_CANAL      = "ticket-logs"

CATEGORIAS_TICKET = {
    "soporte":      CAT_SOPORTE,
    "reporte":      CAT_REPORTE,
    "apelacion":    CAT_APELACION,
    "pagos_tienda": CAT_PAGOS,
    "juego":        CAT_JUEGO,
    "postulacion":  CAT_POSTULACION,
    "alianza":      CAT_ALIANZA,
    "evento":       CAT_EVENTO,
}

ROLES_TICKET = {
    "soporte":      (None,    True),
    "reporte":      (ROL_LOW, True),
    "apelacion":    (ROL_MED, True),
    "pagos_tienda": (ROL_HEAD, False),
    "juego":        (ROL_LOW, True),
    "postulacion":  (ROL_MED, True),
    "alianza":      (ROL_HEAD, False),
    "evento":       (ROL_LOW, True),
}

TRANSFER_SUBS = {
    "ganadores-eventos": (ROL_HEAD, CAT_TRANSFER, "🎖️  Ganadores de Eventos"),
    "unregister":        (ROL_HEAD, CAT_TRANSFER, "🔐  Unregister"),
    "reembolso":         (ROL_HEAD, CAT_TRANSFER, "💸  Reembolso"),
    "staff-report":      (ROL_HEAD, CAT_TRANSFER, "🚨  Staff Report"),
    "error-config":      (ROL_HEAD, CAT_TRANSFER, "⚠️  Error de Configuración"),
    "revives":           (ROL_HIGH, CAT_TRANSFER, "💊  Revives"),
    "cambio-nick":       (ROL_HIGH, CAT_TRANSFER, "✏️  Cambio de Nick"),
}

BANNER_URL   = "https://i.imgur.com/uhYEbZj.png"
BANNER_IP    = "https://i.imgur.com/WxEp4MV.png"
FOOTER_TXT   = "NightMc Network  ✦  nightmc.me"
COOLDOWN_SEG = 60

C_DEFAULT = 0x1a1d21
C_GREEN   = 0x2ecc71
C_RED     = 0xe74c3c
C_YELLOW  = 0xf1c40f
C_BLUE    = 0x5865f2

COLORES_TICKET = {
    "soporte":      0x5865f2,
    "reporte":      0xe74c3c,
    "apelacion":    0xf1c40f,
    "pagos_tienda": 0x2ecc71,
    "juego":        0x1abc9c,
    "postulacion":  0xe91e8c,
    "alianza":      0xe67e22,
    "evento":       0x9b59b6,
}

ERR_NO_STAFF     = "❌  No tienes permisos para hacer esto."
ERR_YA_RECLAMADO = "⚠️  Este ticket ya lo está atendiendo otro miembro del staff."
ERR_YA_TUYO      = "ℹ️  Este ticket ya está reclamado por ti."
ERR_PROPIO       = "❌  No puedes reclamar tu propio ticket."
ERR_NO_CAT       = "❌  No se pudo crear la categoría. Verifica los permisos del bot."
ERR_DUPLICADO    = "❌  Ya tienes un ticket abierto. Ciérralo antes de abrir uno nuevo."
ERR_COOLDOWN     = "⏳  Espera un momento antes de abrir otro ticket."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🎨  EMBEDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIV = "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌"

def _ico(guild):
    return guild.icon.url if guild.icon else None

def _footer(e, guild):
    e.set_footer(text=FOOTER_TXT, icon_url=_ico(guild))
    return e

def _campo(v):
    return f"```\n{v or '—'}\n```"

TICKET_META = {
    "soporte": {
        "emoji": "🛠️", "titulo": "Soporte General",
        "desc": "Tu solicitud será atendida a la brevedad.\nMientras tanto, asegúrate de haber incluido toda la información necesaria.",
        "campos": [("🎮  Nick en Minecraft", "Nick"), ("❓  Consulta", "Duda")],
        "tip": "Sé claro y detallado · El staff te responderá pronto",
    },
    "reporte": {
        "emoji": "🚫", "titulo": "Reporte de Usuario",
        "desc": "Tu reporte ha sido recibido. El staff revisará las pruebas con atención.\nLos reportes sin evidencia válida serán archivados.",
        "campos": [("🎮  Tu nick", "Nick"), ("🎯  Nick del reportado", "Usuario reportado"), ("🔗  Pruebas", "Pruebas")],
        "tip": "Adjunta capturas o vídeos como prueba",
    },
    "apelacion": {
        "emoji": "⚖️", "titulo": "Apelación de Sanción",
        "desc": "Tu apelación ha sido registrada. El equipo la evaluará con imparcialidad.\nEl proceso puede tomar tiempo — sé paciente.",
        "campos": [
            ("🎮  Cuenta sancionada",             "Nick sancionado"),
            ("🛡️  Staff que sancionó",             "Staff que sancionó"),
            ("📋  Razón de la sanción",            "Razón de la sanción"),
            ("💬  Motivo para retirar la sanción", "¿Por qué retirar la sanción?"),
        ],
        "tip": "Las apelaciones irrespetuosas serán rechazadas",
    },
    "pagos_tienda": {
        "emoji": "💰", "titulo": "Soporte Pagos Tienda",
        "desc": "Tu solicitud ha sido recibida.\nAdjunta el ID de transacción de Tebex para agilizar el proceso.",
        "campos": [("🎮  Nick de compra", "Nick de compra"), ("🧾  ID de transacción", "ID de compra"), ("⚠️  Descripción del problema", "Problema")],
        "tip": "Revisa tu correo de Tebex para el ID de compra",
    },
    "juego": {
        "emoji": "🎮", "titulo": "Soporte de Juego",
        "desc": "Tu reporte ha sido recibido.\nCuanta más información aportes, más rápido podremos resolverlo.",
        "campos": [("🎮  Nick", "Nick"), ("🐛  Bug o error", "Bug"), ("📍  Ubicación", "Ubicacion")],
        "tip": "Adjunta capturas si es posible",
    },
    "postulacion": {
        "emoji": "📋", "titulo": "Postulación Staff",
        "desc": "Tu postulación ha sido registrada correctamente.\nEl equipo de administración la revisará en los próximos días.",
        "campos": [("🎮  Nick", "Nick"), ("💬  Consulta", "Duda")],
        "tip": "El proceso puede tardar varios días · Sé paciente",
    },
    "alianza": {
        "emoji": "🤝", "titulo": "Propuesta de Alianza",
        "desc": "Tu propuesta ha sido recibida.\nLa evaluaremos para ver si encaja con la visión del servidor.",
        "campos": [("🏷️  Servidor", "Servidor"), ("👥  Miembros aprox.", "Miembros"), ("💡  Propuesta", "Propuesta")],
        "tip": "Toda alianza debe beneficiar a ambas comunidades",
    },
    "evento": {
        "emoji": "🎉", "titulo": "Soporte de Eventos",
        "desc": "Tu solicitud relacionada con un evento ha sido registrada.\nVerificaremos tu participación y el premio correspondiente.",
        "campos": [("🎮  Nick", "Nick"), ("🎪  Evento", "Evento"), ("🏆  Premio esperado", "Premio"), ("📋  Descripción", "Descripcion")],
        "tip": "Adjunta pruebas de participación si las tienes",
    },
}

def build_ticket_embed(tipo, guild, user, rol_tag, campos):
    meta  = TICKET_META[tipo]
    e = discord.Embed(color=COLORES_TICKET.get(tipo, C_DEFAULT))
    e.set_author(name=f"NightMc Network  ·  {meta['titulo']}", icon_url=_ico(guild))
    e.title = f"{meta['emoji']}  {meta['titulo']}"
    e.description = (
        f"> {user.mention}, bienvenido al sistema de soporte.\n"
        f"> {meta['desc']}\n\n"
        f"{DIV}"
    )
    e.add_field(name="👤  Atendido por", value=f"> {rol_tag}", inline=False)
    e.add_field(name=DIV, value="", inline=False)
    for label, key in meta["campos"]:
        e.add_field(name=label, value=_campo(campos.get(key)), inline=False)
    e.add_field(name=DIV, value=(
        "> 💬  Responde en este canal con información adicional.\n"
        "> ⏳  El staff te atenderá lo antes posible.\n"
        "> 🙏  Gracias por contactar con **NightMc Network**."
    ), inline=False)
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    e.set_footer(text=f"NightMc Network  ·  {meta['tip']}", icon_url=_ico(guild))
    return e

def embed_setup(guild):
    e = discord.Embed(color=C_DEFAULT)
    e.set_author(name="Centro de Soporte  ·  NightMc Network", icon_url=_ico(guild))
    e.title = "🎫  ¿En qué podemos ayudarte?"
    e.description = (
        "\n"
        "> Bienvenido al **Sistema de Soporte** de NightMc Network.\n"
        "> Selecciona la categoría que mejor describe tu consulta.\n"
        f"\n{DIV}\n"
    )
    cats = [
        ("🛠️", "Soporte General",     "Dudas, preguntas y ayuda general"),
        ("🚫", "Reportes",            "Reportar jugadores, hacks o comportamiento"),
        ("⚖️", "Apelaciones",         "Apelar bans, mutes y sanciones"),
        ("💰", "Pagos Tienda",        "Problemas con compras, rangos o Tebex"),
        ("🎮", "Soporte de Juego",    "Bugs in-game, glitches y errores"),
        ("📋", "Postulaciones Staff", "Aplicar para unirte al equipo de staff"),
        ("🤝", "Alianzas",            "Propuestas de colaboración o alianza"),
        ("🎉", "Eventos",             "Premios de eventos no recibidos"),
    ]
    e.add_field(
        name="📂  Categorías disponibles",
        value="\n".join(f"> {em}  **{t}** — {d}" for em, t, d in cats),
        inline=False
    )
    e.add_field(name=DIV, value=(
        "> 🔹  Sé respetuoso con el staff en todo momento.\n"
        "> 🔹  Proporciona información clara y verídica.\n"
        "> 🔹  Abre solo un ticket por asunto.\n"
        "> 🔹  No abuses del sistema de soporte."
    ), inline=False)
    e.add_field(name="⏱️  Tiempo de respuesta",
                value="> El equipo te atenderá **lo antes posible**.", inline=False)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_claimed(user, guild):
    e = discord.Embed(color=C_GREEN)
    e.description = (
        f"**{user.mention}** ha tomado el control de este ticket.\n"
        f"> ✦  {user.display_name} se encargará de tu caso."
    )
    e.set_footer(text="NightMc Network  ✦  Ticket en atención", icon_url=_ico(guild))
    return e

def embed_close(guild):
    e = discord.Embed(
        title="🔒  Cerrando Ticket",
        description=(
            "> Este ticket será eliminado en **5 segundos**.\n\n"
            "> Gracias por contactar con **NightMc Network**.\n"
            "> ✦  ¡Hasta pronto!"
        ),
        color=C_RED
    )
    return _footer(e, guild)

def embed_transfer_menu(guild):
    e = discord.Embed(color=C_YELLOW)
    e.set_author(name="NightMc Network  ·  Escalación Interna", icon_url=_ico(guild))
    e.title = "🔄  Transferir Expediente"
    e.description = (
        f"{DIV}\n"
        "> Selecciona el tipo de gestión que necesita este ticket.\n"
        f"{DIV}\n\n"
        f"👑  **{ROL_HEAD}** — Gestiones críticas y administrativas\n"
        f"🔰  **{ROL_HIGH}** — Gestiones avanzadas in-game\n"
    )
    e.set_footer(text="Solo el staff puede usar esta función", icon_url=_ico(guild))
    return e

def embed_transfer_done(label, guild):
    e = discord.Embed(color=C_BLUE)
    e.set_author(name="NightMc Network  ·  Ticket Transferido", icon_url=_ico(guild))
    e.title = "🔄  Expediente Escalado"
    e.description = f"{DIV}\n> Tu ticket ha sido escalado a\n> **{label}**\n{DIV}"
    e.add_field(name="⏳  Estado",    value="> El equipo especializado revisará tu caso.", inline=False)
    e.add_field(name="💬  ¿Qué sigue?", value="> Un staff se pondrá en contacto contigo.\n> **No abras otro ticket** sobre el mismo asunto.", inline=False)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_ip():
    e = discord.Embed(title="🌐  NightMc Network — Cómo conectarte", color=C_BLUE)
    e.description = f"> ¡Bienvenido a **NightMc Network**!\n{DIV}"
    e.add_field(name="☕  Java Edition", value="> **IP:** `NightMc.me`\n> **Versiones:** 1.16 — 1.21", inline=True)
    e.add_field(name="🟩  Bedrock",      value="> ⏳  **Próximamente...**",                              inline=True)
    e.add_field(name=DIV, value="", inline=False)
    e.add_field(name="⚔️  ClashBox",     value="> ✅  Disponible",   inline=True)
    e.add_field(name="🗡️  FullPvP",      value="> ⏳  Próximamente", inline=True)
    e.add_field(name=DIV, value="", inline=False)
    e.add_field(name="🔗  Redes", value=(
        "> 💬  [Discord](https://discord.gg/2r2byXBgsv)\n"
        "> 🔴  [YouTube](https://www.youtube.com/@NightMCNetwork-me)"
    ), inline=False)
    e.set_image(url=BANNER_IP)
    e.set_footer(text="© NightMc Network  ✦  nightmc.me")
    return e

def embed_help(guild):
    e = discord.Embed(title="📋  Comandos  ·  NightMc Bot", color=C_BLUE)
    e.set_author(name="NightMc Network", icon_url=_ico(guild))
    e.description = f"> Todos los comandos funcionan con `/` **y** con `!`.\n{DIV}"
    e.add_field(name="🎫  Tickets",    value="> `/claim` `/close` `/transcript`",                              inline=True)
    e.add_field(name="👥  Usuarios",   value="> `/add @usuario` `/remove @usuario`",                          inline=True)
    e.add_field(name=DIV, value="", inline=False)
    e.add_field(name="⚙️  Canal",      value="> `/rename <nombre>` `/slowmode [seg]`",                        inline=True)
    e.add_field(name="🔄  Transferir", value="> `/transfer` `/specifictag_staff` `/specifictag_role`",        inline=True)
    e.add_field(name=DIV, value="", inline=False)
    e.add_field(name="🛠️  Admin",      value="> `!setup` — Panel de tickets\n> `!sync` — Registrar comandos", inline=False)
    e.set_footer(text=FOOTER_TXT, icon_url=_ico(guild))
    return e

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🤖  BOT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class NightBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self._ticket_msg_ids:   dict[int, int] = {}
        self._claimed_channels: dict[int, int] = {}

    async def setup_hook(self):
        self.add_view(TicketLauncher())
        self.add_view(TicketControl())
        print("✦  NightMc Bot v2.1 — listo.")

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="NightMc Network 🌙"))
        print(f"✦  Online  ·  {self.user}  ({self.user.id})")

bot = NightBot()
tickets_abiertos: dict[int, int]              = {}
cooldowns:        dict[int, datetime.datetime] = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔧  UTILIDADES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def es_staff(m): return any(r.name in TODOS_STAFF for r in m.roles)

def en_cooldown(uid):
    return uid in cooldowns and \
        (datetime.datetime.now() - cooldowns[uid]).total_seconds() < COOLDOWN_SEG

def leer_topic(canal, clave):
    if not canal.topic: return ""
    for p in canal.topic.split("|"):
        p = p.strip()
        if p.startswith(f"{clave}:"): return p[len(clave)+1:].strip()
    return ""

def owner_id_de(canal):
    try:    return int(leer_topic(canal, "ownerid"))
    except: return 0

async def get_o_crear_cat(guild, nombre):
    cat = discord.utils.get(guild.categories, name=nombre)
    if not cat:
        try:
            cat = await guild.create_category(nombre, overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
            })
        except discord.Forbidden: return None
    return cat

async def get_o_crear_logs(guild):
    canal = discord.utils.get(guild.text_channels, name=LOGS_CANAL)
    if canal: return canal
    try:
        cat   = discord.utils.get(guild.categories, name="📋 LOGS") or await guild.create_category("📋 LOGS")
        rol_s = discord.utils.get(guild.roles, name=ROL_TEAM)
        perms = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if rol_s: perms[rol_s] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        return await guild.create_text_channel(LOGS_CANAL, category=cat, overwrites=perms)
    except: return None

async def enviar_log(guild, embed, file=None):
    c = await get_o_crear_logs(guild)
    if c:
        try:
            await c.send(embed=embed, file=file) if file else await c.send(embed=embed)
        except: pass

async def hacer_transcript(canal):
    lines = [f"═══ TRANSCRIPT  #{canal.name}  ═══\n\n"]
    async for m in canal.history(limit=500, oldest_first=True):
        ts   = m.created_at.strftime("%d/%m/%Y %H:%M")
        body = m.content or ""
        for emb in m.embeds:
            if emb.title: body += f" [embed: {emb.title}]"
        lines.append(f"[{ts}]  {m.author.display_name}: {body}\n")
    return io.BytesIO("".join(lines).encode("utf-8"))

async def renombrar(canal, nuevo):
    nuevo = nuevo[:50].lower().replace(" ", "-")
    if canal.name == nuevo: return
    try:
        await canal.edit(name=nuevo)
    except discord.HTTPException as e:
        if e.status == 429:
            await asyncio.sleep(float(getattr(e, "retry_after", 600)) + 2)
            try: await canal.edit(name=nuevo)
            except: pass

async def base_nombre(canal):
    b = canal.name
    if b.endswith("-pendiente"): b = b[:-10]
    partes = b.split("-")
    if len(partes) >= 3 and len(partes[-1]) <= 15: b = "-".join(partes[:-1])
    return b

async def cerrar(canal, guild, por, owner_id):
    for uid, cid in list(tickets_abiertos.items()):
        if cid == canal.id: del tickets_abiertos[uid]; break
    bot._ticket_msg_ids.pop(canal.id, None)
    bot._claimed_channels.pop(canal.id, None)
    owner  = guild.get_member(owner_id)
    nombre = f"transcript-{canal.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    le = discord.Embed(title="📤  Ticket Cerrado", color=C_RED, timestamp=datetime.datetime.now())
    le.add_field(name="Canal",       value=f"#{canal.name}", inline=True)
    le.add_field(name="Cerrado por", value=por.mention,      inline=True)
    if owner: le.add_field(name="Dueño", value=owner.mention, inline=True)
    le.set_footer(text=FOOTER_TXT)
    arch = await hacer_transcript(canal)
    await enviar_log(guild, le, file=discord.File(arch, filename=nombre))
    await asyncio.sleep(5)
    try:    await canal.delete()
    except discord.NotFound: pass

def _tiene_claim(msg):
    for row in msg.components:
        for child in row.children:
            if getattr(child, "custom_id", None) == "claim_t": return True
    return False

async def resetear_claim(canal, nombre_canal, owner_id):
    bot._claimed_channels.pop(canal.id, None)
    view = TicketControl(nombre_canal=nombre_canal, owner_id=owner_id)
    mid  = bot._ticket_msg_ids.get(canal.id)
    if mid:
        try: m = await canal.fetch_message(mid); await m.edit(view=view); return
        except: pass
    try:
        async for m in canal.history(limit=50, oldest_first=True):
            if m.author.id == canal.guild.me.id and _tiene_claim(m):
                await m.edit(view=view); bot._ticket_msg_ids[canal.id] = m.id; return
    except: pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🎫  CREAR TICKET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def crear_ticket(inter, tipo, campos, nombre_canal):
    guild, user = inter.guild, inter.user
    await inter.response.defer(ephemeral=True)
    if en_cooldown(user.id): return await inter.followup.send(ERR_COOLDOWN, ephemeral=True)
    if user.id in tickets_abiertos:
        if guild.get_channel(tickets_abiertos[user.id]): return await inter.followup.send(ERR_DUPLICADO, ephemeral=True)
        del tickets_abiertos[user.id]
    cat = await get_o_crear_cat(guild, CATEGORIAS_TICKET.get(tipo, CAT_SOPORTE))
    if not cat: return await inter.followup.send(ERR_NO_CAT, ephemeral=True)
    nombre_rol_esp, usar_team = ROLES_TICKET.get(tipo, (None, True))
    rol_esp  = discord.utils.get(guild.roles, name=nombre_rol_esp) if nombre_rol_esp else None
    rol_team = discord.utils.get(guild.roles, name=ROL_TEAM)
    perms = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        user:               discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
    }
    if rol_esp:             perms[rol_esp]  = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if usar_team and rol_team: perms[rol_team] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    try:
        canal = await guild.create_text_channel(
            name=f"{nombre_canal}-pendiente", category=cat,
            overwrites=perms, topic=f"tipo:{tipo} | ownerid:{user.id}")
    except discord.Forbidden:
        return await inter.followup.send("❌  Sin permisos para crear canales.", ephemeral=True)
    tickets_abiertos[user.id] = canal.id
    cooldowns[user.id]        = datetime.datetime.now()
    rol_tag = (rol_team.mention if usar_team and rol_team else rol_esp.mention if rol_esp else f"@{ROL_TEAM}")
    view = TicketControl(nombre_canal=nombre_canal, owner_id=user.id)
    msg  = await canal.send(content=f"{user.mention}  {rol_tag}", embed=build_ticket_embed(tipo, guild, user, rol_tag, campos), view=view)
    bot._ticket_msg_ids[canal.id] = msg.id
    await inter.followup.send(f"✅  Tu ticket fue creado en {canal.mention}", ephemeral=True)
    le = discord.Embed(title="📥  Ticket Abierto", color=C_GREEN, timestamp=datetime.datetime.now())
    le.add_field(name="Usuario",   value=user.mention,  inline=True)
    le.add_field(name="Canal",     value=canal.mention, inline=True)
    le.add_field(name="Categoría", value=CATEGORIAS_TICKET.get(tipo, CAT_SOPORTE), inline=True)
    le.set_footer(text=FOOTER_TXT)
    await enviar_log(guild, le)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📝  MODALES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class GeneralModal(ui.Modal, title="NightMc  ·  Soporte General"):
    nick     = ui.TextInput(label="Tu nick en Minecraft",  placeholder="Exactamente como aparece en el juego")
    consulta = ui.TextInput(label="¿Cuál es tu consulta?", placeholder="Explica con detalle", style=discord.TextStyle.paragraph)
    async def on_submit(self, i): await crear_ticket(i, "soporte", {"Nick": self.nick.value, "Duda": self.consulta.value}, "soporte")

class ReporteModal(ui.Modal, title="NightMc  ·  Reportar Usuario"):
    nick    = ui.TextInput(label="Tu nick",                  placeholder="Exactamente como aparece en el juego")
    acusado = ui.TextInput(label="Nick del usuario a reportar", placeholder="Nombre exacto del jugador")
    pruebas = ui.TextInput(label="Pruebas",                  placeholder="Link a imgur, YouTube...", style=discord.TextStyle.paragraph)
    async def on_submit(self, i): await crear_ticket(i, "reporte", {"Nick": self.nick.value, "Usuario reportado": self.acusado.value, "Pruebas": self.pruebas.value}, "reporte")

class ApelacionModal(ui.Modal, title="NightMc  ·  Apelar Sanción"):
    nick  = ui.TextInput(label="Cuenta sancionada",           placeholder="Nick de la cuenta baneada/muteada")
    staff = ui.TextInput(label="Staff que te sancionó",       placeholder="¿Qué staff aplicó la sanción?")
    razon = ui.TextInput(label="Razón de la sanción",         placeholder="¿Cuál fue el motivo?", style=discord.TextStyle.paragraph)
    unban = ui.TextInput(label="¿Por qué debería retirarse?", placeholder="Explica tu caso con honestidad", style=discord.TextStyle.paragraph)
    async def on_submit(self, i): await crear_ticket(i, "apelacion", {"Nick sancionado": self.nick.value, "Staff que sancionó": self.staff.value, "Razón de la sanción": self.razon.value, "¿Por qué retirar la sanción?": self.unban.value}, "apelacion")

class PagosTiendaModal(ui.Modal, title="NightMc  ·  Soporte Pagos Tienda"):
    nick    = ui.TextInput(label="Nick con el que compraste", placeholder="Exactamente como aparece en el juego")
    id_pago = ui.TextInput(label="ID de transacción (Tebex)", placeholder="Revisa tu correo electrónico")
    error   = ui.TextInput(label="Descripción del problema",  placeholder="¿Qué ocurrió con tu compra?", style=discord.TextStyle.paragraph)
    async def on_submit(self, i): await crear_ticket(i, "pagos_tienda", {"Nick de compra": self.nick.value, "ID de compra": self.id_pago.value, "Problema": self.error.value}, "pagos-tienda")

class JuegoModal(ui.Modal, title="NightMc  ·  Soporte de Juego"):
    nick  = ui.TextInput(label="Tu nick",              placeholder="Exactamente como aparece en el juego")
    bug   = ui.TextInput(label="Bug o error",          placeholder="Describe el problema con detalle", style=discord.TextStyle.paragraph)
    lugar = ui.TextInput(label="¿Dónde ocurrió?",      placeholder="Mundo, coordenadas, modalidad...", style=discord.TextStyle.paragraph, required=False)
    async def on_submit(self, i): await crear_ticket(i, "juego", {"Nick": self.nick.value, "Bug": self.bug.value, "Ubicacion": self.lugar.value or "No especificada"}, "juego")

class PostulacionModal(ui.Modal, title="NightMc  ·  Postulación Staff"):
    nick = ui.TextInput(label="Tu nick",              placeholder="Exactamente como aparece en el juego")
    duda = ui.TextInput(label="¿Cuál es tu consulta?", placeholder="¿Qué quieres saber sobre el proceso?", style=discord.TextStyle.paragraph)
    async def on_submit(self, i): await crear_ticket(i, "postulacion", {"Nick": self.nick.value, "Duda": self.duda.value}, "postulacion")

class AlianzaModal(ui.Modal, title="NightMc  ·  Propuesta de Alianza"):
    servidor  = ui.TextInput(label="Nombre del servidor",     placeholder="¿Cómo se llama tu servidor?")
    miembros  = ui.TextInput(label="Miembros aproximados",    placeholder="Ej: 1.500 miembros")
    propuesta = ui.TextInput(label="Propuesta",               placeholder="¿Qué tipo de alianza propones?", style=discord.TextStyle.paragraph)
    async def on_submit(self, i): await crear_ticket(i, "alianza", {"Servidor": self.servidor.value, "Miembros": self.miembros.value, "Propuesta": self.propuesta.value}, "alianza")

class EventoModal(ui.Modal, title="NightMc  ·  Soporte de Eventos"):
    nick   = ui.TextInput(label="Tu nick",            placeholder="Exactamente como aparece en el juego")
    evento = ui.TextInput(label="Nombre del evento",  placeholder="¿En qué evento participaste?")
    premio = ui.TextInput(label="Premio esperado",    placeholder="¿Qué premio te corresponde?")
    desc   = ui.TextInput(label="Descripción",        placeholder="Explica el problema con detalle", style=discord.TextStyle.paragraph)
    async def on_submit(self, i): await crear_ticket(i, "evento", {"Nick": self.nick.value, "Evento": self.evento.value, "Premio": self.premio.value, "Descripcion": self.desc.value}, "evento")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🎡  PANEL PRINCIPAL — Dropdown
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODALES_MAP = {
    "soporte": GeneralModal, "reporte": ReporteModal, "apelacion": ApelacionModal,
    "pagos_tienda": PagosTiendaModal, "juego": JuegoModal, "postulacion": PostulacionModal,
    "alianza": AlianzaModal, "evento": EventoModal,
}

class TicketLauncher(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.select(
        custom_id="main_sel",
        placeholder="✦  Selecciona una categoría para abrir tu ticket...",
        options=[
            discord.SelectOption(label="Soporte General",     value="soporte",      emoji="🛠️", description="Dudas y ayuda general"),
            discord.SelectOption(label="Reportes",            value="reporte",      emoji="🚫", description="Reportar jugadores o hacks"),
            discord.SelectOption(label="Apelaciones",         value="apelacion",    emoji="⚖️", description="Apelar bans, mutes o sanciones"),
            discord.SelectOption(label="Pagos Tienda",        value="pagos_tienda", emoji="💰", description="Problemas con compras o rangos"),
            discord.SelectOption(label="Soporte de Juego",    value="juego",        emoji="🎮", description="Bugs in-game y glitches"),
            discord.SelectOption(label="Postulaciones Staff", value="postulacion",  emoji="📋", description="Aplicar para ser staff"),
            discord.SelectOption(label="Alianzas",            value="alianza",      emoji="🤝", description="Propuestas de colaboración"),
            discord.SelectOption(label="Eventos",             value="evento",       emoji="🎉", description="Premios de eventos no recibidos"),
        ]
    )
    async def select_callback(self, inter, select):
        await inter.response.send_modal(MODALES_MAP[select.values[0]]())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🎮  BOTONES DE CONTROL DEL TICKET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TicketControl(ui.View):
    def __init__(self, nombre_canal="ticket", owner_id=0):
        super().__init__(timeout=None)
        self.nombre_canal = nombre_canal
        self.owner_id     = owner_id

    def _owner(self, canal): return self.owner_id or owner_id_de(canal)

    @ui.button(label="Reclamar",   style=discord.ButtonStyle.success, emoji="🔑", custom_id="claim_t")
    async def claim(self, inter, btn):
        if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
        cid = inter.channel.id
        oid = self._owner(inter.channel)
        if inter.user.id == oid:                           return await inter.response.send_message(ERR_PROPIO,       ephemeral=True)
        claimed = bot._claimed_channels.get(cid)
        if claimed and claimed != inter.user.id:           return await inter.response.send_message(ERR_YA_RECLAMADO, ephemeral=True)
        if claimed == inter.user.id:                       return await inter.response.send_message(ERR_YA_TUYO,      ephemeral=True)
        bot._claimed_channels[cid] = inter.user.id
        btn.label = f"Reclamado  ·  {inter.user.display_name}"; btn.emoji = None; btn.disabled = True
        await inter.response.edit_message(view=self)
        base = await base_nombre(inter.channel)
        asyncio.create_task(renombrar(inter.channel, f"{base}-{inter.user.name[:12].lower()}"))
        await inter.channel.send(embed=embed_claimed(inter.user, inter.guild))

    @ui.button(label="Transferir", style=discord.ButtonStyle.primary, emoji="🔄", custom_id="transfer_t")
    async def transfer_btn(self, inter, btn):
        if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
        await inter.response.send_message(embed=embed_transfer_menu(inter.guild), view=TransferView(owner_id=self._owner(inter.channel)), ephemeral=True)

    @ui.button(label="Cerrar",     style=discord.ButtonStyle.danger,  emoji="🗑️", custom_id="close_t")
    async def close_btn(self, inter, btn):
        if not es_staff(inter.user): return await inter.response.send_message("❌  Solo el staff puede cerrar este ticket.", ephemeral=True)
        await inter.response.send_message(embed=embed_close(inter.guild))
        await cerrar(inter.channel, inter.guild, inter.user, self._owner(inter.channel))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔄  MENÚ DE TRANSFERENCIA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TransferView(ui.View):
    def __init__(self, owner_id=0):
        super().__init__(timeout=180)
        self.owner_id = owner_id

    @ui.select(placeholder="✦  Selecciona el tipo de gestión...", options=[
        discord.SelectOption(label="Ganadores de Eventos",   value="ganadores-eventos", emoji="🎖️", description="👑 Head staff"),
        discord.SelectOption(label="Unregister",             value="unregister",         emoji="🔐", description="👑 Head staff"),
        discord.SelectOption(label="Reembolso",              value="reembolso",          emoji="💸", description="👑 Head staff"),
        discord.SelectOption(label="Staff Report",           value="staff-report",       emoji="🚨", description="👑 Head staff"),
        discord.SelectOption(label="Error de Configuración", value="error-config",       emoji="⚠️", description="👑 Head staff"),
        discord.SelectOption(label="Revives",                value="revives",            emoji="💊", description="🔰 Hight staff"),
        discord.SelectOption(label="Cambio de Nick",         value="cambio-nick",        emoji="✏️", description="🔰 Hight staff"),
    ])
    async def select_callback(self, inter, select):
        destino = select.values[0]
        sub = TRANSFER_SUBS.get(destino)
        if not sub: return await inter.response.send_message("❌  Subcategoría no encontrada.", ephemeral=True)
        nombre_rol, cat_nombre, label = sub
        rol_nuevo = discord.utils.get(inter.guild.roles, name=nombre_rol)
        canal, guild = inter.channel, inter.guild
        oid = self.owner_id or owner_id_de(canal)
        cat_t = await get_o_crear_cat(guild, cat_nombre)
        if cat_t and canal.category != cat_t:
            try: await canal.edit(category=cat_t)
            except: pass
        asyncio.create_task(renombrar(canal, destino + "-pendiente"))
        for target in list(canal.overwrites):
            if isinstance(target, discord.Role) and target.name in TODOS_STAFF:
                try: await canal.set_permissions(target, overwrite=None)
                except: pass
        if rol_nuevo:
            try: await canal.set_permissions(rol_nuevo, read_messages=True, send_messages=True)
            except: pass
        if oid:
            owner = guild.get_member(oid)
            if owner:
                try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
                except: pass
        await resetear_claim(canal, destino, oid)
        mention = rol_nuevo.mention if rol_nuevo else f"@{nombre_rol}"
        await inter.response.send_message(embed=embed_transfer_done(label, guild))
        await canal.send(f"{mention}  ✦  Se requiere atención — **{label}**.")
        le = discord.Embed(title="🔄  Ticket Transferido", color=C_YELLOW, timestamp=datetime.datetime.now())
        le.add_field(name="Canal",   value=canal.mention,      inline=True)
        le.add_field(name="Destino", value=label,               inline=True)
        le.add_field(name="Staff",   value=inter.user.mention,  inline=True)
        le.set_footer(text=FOOTER_TXT)
        await enviar_log(guild, le)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ⚡  SLASH COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name="transfer",   description="Transfiere este ticket a otro equipo")
async def slash_transfer(inter):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.send_message(embed=embed_transfer_menu(inter.guild), view=TransferView(owner_id=owner_id_de(inter.channel)), ephemeral=True)

@bot.tree.command(name="close",      description="Cierra este ticket")
async def slash_close(inter):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.defer()
    await inter.followup.send(embed=embed_close(inter.guild))
    await cerrar(inter.channel, inter.guild, inter.user, owner_id_de(inter.channel))

@bot.tree.command(name="claim",      description="Reclama este ticket")
async def slash_claim(inter):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.defer()
    oid = owner_id_de(inter.channel)
    if inter.user.id == oid: return await inter.followup.send(ERR_PROPIO, ephemeral=True)
    base = await base_nombre(inter.channel)
    asyncio.create_task(renombrar(inter.channel, f"{base}-{inter.user.name[:12].lower()}"))
    await inter.followup.send(embed=embed_claimed(inter.user, inter.guild))

@bot.tree.command(name="transcript", description="Genera el transcript de este ticket")
async def slash_transcript(inter):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.defer(ephemeral=True)
    arch   = await hacer_transcript(inter.channel)
    nombre = f"transcript-{inter.channel.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    await inter.followup.send("📄  Transcript generado:", file=discord.File(arch, filename=nombre), ephemeral=True)
    arch2 = await hacer_transcript(inter.channel)
    le = discord.Embed(title="📄  Transcript", color=C_YELLOW, timestamp=datetime.datetime.now())
    le.add_field(name="Canal", value=inter.channel.mention, inline=True)
    le.add_field(name="Staff", value=inter.user.mention,    inline=True)
    le.set_footer(text=FOOTER_TXT)
    lc = await get_o_crear_logs(inter.guild)
    if lc:
        try: await lc.send(embed=le, file=discord.File(arch2, filename=nombre))
        except: pass

@bot.tree.command(name="add",    description="Añade un usuario al ticket")
@discord.app_commands.describe(usuario="Usuario a añadir")
async def slash_add(inter, usuario: discord.Member):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.defer()
    try:
        await inter.channel.set_permissions(usuario, read_messages=True, send_messages=True)
        await inter.followup.send(f"✅  {usuario.mention} fue añadido al ticket.")
    except discord.Forbidden: await inter.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="remove", description="Elimina un usuario del ticket")
@discord.app_commands.describe(usuario="Usuario a eliminar")
async def slash_remove(inter, usuario: discord.Member):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.defer()
    try:
        await inter.channel.set_permissions(usuario, overwrite=None)
        await inter.followup.send(f"🚫  {usuario.mention} fue eliminado del ticket.")
    except discord.Forbidden: await inter.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="rename", description="Renombra el canal del ticket")
@discord.app_commands.describe(nombre="Nuevo nombre del canal")
async def slash_rename(inter, nombre: str):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.defer(ephemeral=True)
    try:
        await inter.channel.edit(name=nombre.lower().replace(" ", "-")[:50])
        await inter.followup.send("✏️  Canal renombrado.", ephemeral=True)
    except Exception as e: await inter.followup.send(f"❌  {e}", ephemeral=True)

@bot.tree.command(name="slowmode", description="Activa el modo lento (0 para desactivar)")
@discord.app_commands.describe(segundos="Segundos de espera entre mensajes")
async def slash_slowmode(inter, segundos: int = 0):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.defer()
    seg = max(0, min(segundos, 21600))
    try:
        await inter.channel.edit(slowmode_delay=seg)
        await inter.followup.send(f"🐢  Slowmode: **{seg}s**." if seg else "✅  Slowmode desactivado.")
    except discord.Forbidden: await inter.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="specifictag_staff", description="Asigna el ticket a un miembro del staff")
@discord.app_commands.describe(staff="Miembro del staff al que asignar")
async def slash_tag_staff(inter, staff: discord.Member):
    if not es_staff(inter.user):  return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    if not es_staff(staff):       return await inter.response.send_message("❌  El usuario no es staff.", ephemeral=True)
    if staff.id == inter.user.id: return await inter.response.send_message("❌  No puedes asignarte el ticket a ti mismo.", ephemeral=True)
    await inter.response.defer()
    canal, guild = inter.channel, inter.guild
    oid = owner_id_de(canal)
    for target in list(canal.overwrites):
        if isinstance(target, discord.Role) and target.name in TODOS_STAFF:
            try: await canal.set_permissions(target, overwrite=None)
            except: pass
    for rn in ROLES_SUPERIORES:
        r = discord.utils.get(guild.roles, name=rn)
        if r:
            try: await canal.set_permissions(r, read_messages=True, send_messages=True)
            except: pass
    try: await canal.set_permissions(staff, read_messages=True, send_messages=True)
    except: pass
    if oid:
        owner = guild.get_member(oid)
        if owner:
            try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
            except: pass
    cat_t = await get_o_crear_cat(guild, CAT_TRANSFER)
    if cat_t and canal.category != cat_t:
        try: await canal.edit(category=cat_t)
        except: pass
    nd = f"staff-{staff.name[:12].lower()}"
    await resetear_claim(canal, nd, oid)
    asyncio.create_task(renombrar(canal, f"{nd}-pendiente"))
    e = discord.Embed(title="👤  Ticket Asignado", color=C_BLUE)
    e.description = (f"> Asignado a {staff.mention}.\n"
                     f"> Solo **{staff.display_name}** y roles superiores pueden verlo.")
    e.set_image(url=BANNER_URL); _footer(e, guild)
    await inter.followup.send(embed=e)
    await canal.send(f"{staff.mention}  ✦  Se te ha asignado este ticket.")
    le = discord.Embed(title="👤  Ticket → Staff", color=C_BLUE, timestamp=datetime.datetime.now())
    le.add_field(name="Canal", value=canal.mention, inline=True)
    le.add_field(name="A",     value=staff.mention, inline=True)
    le.add_field(name="Por",   value=inter.user.mention, inline=True)
    le.set_footer(text=FOOTER_TXT); await enviar_log(guild, le)

@bot.tree.command(name="specifictag_role", description="Asigna el ticket a un rol específico")
@discord.app_commands.describe(rol="Rol al que asignar el ticket")
async def slash_tag_rol(inter, rol: discord.Role):
    if not es_staff(inter.user): return await inter.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await inter.response.defer()
    canal, guild = inter.channel, inter.guild
    oid = owner_id_de(canal)
    for target in list(canal.overwrites):
        if isinstance(target, discord.Role) and target.name in TODOS_STAFF:
            try: await canal.set_permissions(target, overwrite=None)
            except: pass
    for rn in ROLES_SUPERIORES:
        r = discord.utils.get(guild.roles, name=rn)
        if r:
            try: await canal.set_permissions(r, read_messages=True, send_messages=True)
            except: pass
    try: await canal.set_permissions(rol, read_messages=True, send_messages=True)
    except: pass
    if oid:
        owner = guild.get_member(oid)
        if owner:
            try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
            except: pass
    cat_t = await get_o_crear_cat(guild, CAT_TRANSFER)
    if cat_t and canal.category != cat_t:
        try: await canal.edit(category=cat_t)
        except: pass
    nd = rol.name[:20].lower().replace(" ", "-")
    await resetear_claim(canal, nd, oid)
    asyncio.create_task(renombrar(canal, f"{nd}-pendiente"))
    e = discord.Embed(title="🎭  Ticket Asignado a Rol", color=C_BLUE)
    e.description = f"> Asignado al rol {rol.mention}."
    e.set_image(url=BANNER_URL); _footer(e, guild)
    await inter.followup.send(embed=e)
    await canal.send(f"{rol.mention}  ✦  Se requiere atención en este ticket.")
    le = discord.Embed(title="🎭  Ticket → Rol", color=C_BLUE, timestamp=datetime.datetime.now())
    le.add_field(name="Canal", value=canal.mention, inline=True)
    le.add_field(name="Rol",   value=rol.mention,   inline=True)
    le.add_field(name="Por",   value=inter.user.mention, inline=True)
    le.set_footer(text=FOOTER_TXT); await enviar_log(guild, le)

@bot.tree.command(name="ip",   description="Muestra cómo conectarte al servidor")
async def slash_ip(inter):   await inter.response.send_message(embed=embed_ip())

@bot.tree.command(name="help", description="Muestra todos los comandos disponibles")
async def slash_help(inter):  await inter.response.send_message(embed=embed_help(inter.guild), ephemeral=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🛠️  COMANDOS DE PREFIJO  (!)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await ctx.send(embed=embed_setup(ctx.guild), view=TicketLauncher())
    try: await ctx.message.delete()
    except: pass

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    msg = await ctx.send("⏳  Sincronizando comandos...")
    try:
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await msg.edit(content=f"✅  **{len(synced)} comandos** registrados en **{ctx.guild.name}**.\n💡  Si no aparecen, recarga Discord con **Ctrl+R**.")
    except Exception as e: await msg.edit(content=f"❌  Error: {e}")

@bot.command(name="claim")
async def prefix_claim(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    if ctx.author.id == owner_id_de(ctx.channel): return await ctx.send(ERR_PROPIO)
    base = await base_nombre(ctx.channel)
    asyncio.create_task(renombrar(ctx.channel, f"{base}-{ctx.author.name[:12].lower()}"))
    await ctx.send(embed=embed_claimed(ctx.author, ctx.guild))

@bot.command(name="close")
async def prefix_close(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    await ctx.send(embed=embed_close(ctx.guild))
    await cerrar(ctx.channel, ctx.guild, ctx.author, owner_id_de(ctx.channel))

@bot.command(name="transcript")
async def prefix_transcript(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    m = await ctx.send("⏳  Generando...")
    arch   = await hacer_transcript(ctx.channel)
    nombre = f"transcript-{ctx.channel.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    await m.delete()
    await ctx.send("📄  Transcript:", file=discord.File(arch, filename=nombre))

@bot.command(name="add")
async def prefix_add(ctx, usuario: discord.Member = None):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    if not usuario: return await ctx.send("❌  Uso: `!add @usuario`")
    try:
        await ctx.channel.set_permissions(usuario, read_messages=True, send_messages=True)
        await ctx.send(f"✅  {usuario.mention} fue añadido.")
    except discord.Forbidden: await ctx.send("❌  Sin permisos.")

@bot.command(name="remove")
async def prefix_remove(ctx, usuario: discord.Member = None):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    if not usuario: return await ctx.send("❌  Uso: `!remove @usuario`")
    try:
        await ctx.channel.set_permissions(usuario, overwrite=None)
        await ctx.send(f"🚫  {usuario.mention} eliminado.")
    except discord.Forbidden: await ctx.send("❌  Sin permisos.")

@bot.command(name="ip")
async def prefix_ip(ctx): await ctx.send(embed=embed_ip())

@bot.command(name="help", aliases=["ayuda", "h"])
async def prefix_help(ctx): await ctx.send(embed=embed_help(ctx.guild))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    if isinstance(error, commands.MissingPermissions): return await ctx.send("❌  Sin permisos.")
    raise error

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🚀  ARRANQUE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if not TOKEN:
    print("\n❌  ERROR: No se encontró DISCORD_TOKEN")
    print("   Railway → Variables → añade DISCORD_TOKEN\n")
    exit(1)

bot.run(TOKEN)
