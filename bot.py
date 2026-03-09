"""
╔══════════════════════════════════════════════════════════════╗
   NightMc Network — Bot de Tickets v2.0
   Host recomendado: Railway (gratis)
   Para reiniciar: Railway → Deployments → Redeploy
   Token: Railway → Variables → DISCORD_TOKEN
╚══════════════════════════════════════════════════════════════╝
"""

import discord
from discord import ui
from discord.ext import commands
import asyncio, datetime, io, os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ╔══════════════════════════════════════════════════════════════╗
#   ⚙️  CONFIGURACIÓN — Solo edita esta sección
# ╚══════════════════════════════════════════════════════════════╝

# ── Roles de staff (de menor a mayor) ─────────────────────────
ROL_LOW    = "Low staff"
ROL_MED    = "Medium Staff"
ROL_HIGH   = "Hight staff"
ROL_HEAD   = "Head staff"
ROL_TEAM   = "Staff team"

TODOS_ROLES_STAFF = [ROL_LOW, ROL_MED, ROL_HIGH, ROL_HEAD, ROL_TEAM]
ROLES_SUPERIORES  = [ROL_HIGH, ROL_HEAD]

# ── Estética ───────────────────────────────────────────────────
BANNER_URL = "https://i.imgur.com/uhYEbZj.png"
FOOTER     = "NightMc.me"
LOGS_CANAL = "ticket-logs"

# ── Categorías de Discord ──────────────────────────────────────
CAT_SOPORTE     = "🛠️ SOPORTE"
CAT_REPORTE     = "🚫 REPORTES"
CAT_APELACION   = "⚖️ APELACIONES"
CAT_PAGOS       = "💰 Pagos Tienda"
CAT_JUEGO       = "🎮 Soporte de Juego"
CAT_POSTULACION = "📋 Postulaciones Staff"
CAT_ALIANZA     = "🤝 Alianzas"
CAT_EVENTO      = "🎉 Eventos"
CAT_TRANSFER    = "🔄 TRANSFERIDOS"

# ── Colores por categoría ──────────────────────────────────────
COLORES = {
    "soporte":      0x5865f2,
    "reporte":      0xed4245,
    "apelacion":    0xfee75c,
    "pagos_tienda": 0x57f287,
    "juego":        0x00b0f4,
    "postulacion":  0xeb459e,
    "alianza":      0xf47b67,
    "evento":       0xa259ff,
}

# ── Qué rol atiende cada tipo y si va Staff team también ───────
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

TRANSFER_SUBS = {
    "ganadores-eventos": (ROL_HEAD, CAT_TRANSFER, "🎖️  Ganadores de Eventos"),
    "unregister":        (ROL_HEAD, CAT_TRANSFER, "🔐  Unregister"),
    "reembolso":         (ROL_HEAD, CAT_TRANSFER, "💸  Reembolso"),
    "staff-report":      (ROL_HEAD, CAT_TRANSFER, "🚨  Staff Report"),
    "error-config":      (ROL_HEAD, CAT_TRANSFER, "⚠️  Error de Config"),
    "revives":           (ROL_HIGH, CAT_TRANSFER, "💊  Revives"),
    "cambio-nick":       (ROL_HIGH, CAT_TRANSFER, "✏️  Cambio de Nick"),
}

# ── Info de cada tipo de ticket ────────────────────────────────
TICKET_INFO = {
    "soporte": {
        "emoji": "🛠️", "titulo": "Soporte General",
        "descripcion": "Tu ticket pronto será atendido. Gracias por tu paciencia.",
        "campos": [("🎮  Nick en Minecraft", "Nick"), ("❓  Duda o consulta", "Duda")],
    },
    "reporte": {
        "emoji": "🚫", "titulo": "Reporte de Usuario",
        "descripcion": "Tu reporte será revisado. Asegúrate de incluir pruebas válidas.",
        "campos": [("🎮  Tu nick", "Nick"), ("🎯  Usuario reportado", "Usuario reportado"), ("🔗  Pruebas", "Pruebas")],
    },
    "apelacion": {
        "emoji": "⚖️", "titulo": "Apelación de Sanción",
        "descripcion": "Tu apelación será evaluada con atención. Sé paciente.",
        "campos": [
            ("🎮  Cuenta sancionada", "Nick sancionado"),
            ("🛡️  Staff que sancionó", "Staff que sancionó"),
            ("📋  Razón de la sanción", "Razón de la sanción"),
            ("💬  ¿Por qué retirar la sanción?", "¿Por qué retirar la sanción?"),
        ],
    },
    "pagos_tienda": {
        "emoji": "💰", "titulo": "Soporte Pagos Tienda",
        "descripcion": "Tu solicitud de compra será atendida. Adjunta toda la información.",
        "campos": [("🎮  Nick de compra", "Nick de compra"), ("🧾  ID de compra", "ID de compra"), ("⚠️  Problema", "Problema")],
    },
    "juego": {
        "emoji": "🎮", "titulo": "Soporte de Juego",
        "descripcion": "Tu reporte de bug será revisado. Incluye el máximo de detalles.",
        "campos": [("🎮  Nick", "Nick"), ("🐛  Bug o error", "Bug"), ("📍  ¿Dónde ocurrió?", "Ubicacion")],
    },
    "postulacion": {
        "emoji": "📋", "titulo": "Postulación Staff",
        "descripcion": "Tu postulación será evaluada. El proceso puede tomar varios días.",
        "campos": [("🎮  Nick", "Nick"), ("💬  Duda", "Duda")],
    },
    "alianza": {
        "emoji": "🤝", "titulo": "Propuesta de Alianza",
        "descripcion": "Tu propuesta será revisada con atención.",
        "campos": [("🏷️  Servidor", "Servidor"), ("👥  Miembros aprox.", "Miembros"), ("💡  Propuesta", "Propuesta")],
    },
    "evento": {
        "emoji": "🎉", "titulo": "Soporte de Eventos",
        "descripcion": "Tu solicitud de evento será atendida. Verificaremos tu participación.",
        "campos": [("🎮  Nick", "Nick"), ("🎪  Evento", "Evento"), ("🏆  Premio esperado", "Premio"), ("📋  Descripción", "Descripcion")],
    },
}

# Mensajes de error reutilizables
ERR_NO_STAFF     = "❌  Solo el staff puede realizar esta acción."
ERR_YA_RECLAMADO = "⚠️  Este ticket ya está siendo atendido por otro miembro del staff."
ERR_YA_TUYO      = "ℹ️  Ya tienes este ticket reclamado."
ERR_PROPIO       = "❌  No puedes reclamar tu propio ticket."
ERR_NO_CAT       = "❌  No se pudo crear la categoría. Revisa los permisos del bot."
ERR_DUPLICADO    = "❌  Ya tienes un ticket abierto. Ciérralo antes de abrir otro."
ERR_COOLDOWN     = "⏳  Espera un momento antes de abrir otro ticket."
COOLDOWN_SEG     = 60

# ╔══════════════════════════════════════════════════════════════╗
#   🎨  EMBEDS
# ╚══════════════════════════════════════════════════════════════╝

def _footer(e, guild):
    e.set_footer(text=FOOTER, icon_url=guild.icon.url if guild.icon else None)
    return e

def build_ticket_embed(tipo, guild, user, rol_tag, campos):
    info  = TICKET_INFO[tipo]
    e = discord.Embed(color=COLORES.get(tipo, 0x2b2d31))
    e.set_author(name=f"NightMc Network  ✦  {info['titulo']}", icon_url=guild.icon.url if guild.icon else None)
    e.title = f"{info['emoji']}  {info['titulo']} — NightMC Network"
    e.description = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Buenas {user.mention} — {info['descripcion']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    e.add_field(name="👤  Staff responsable", value=f"> {rol_tag}", inline=False)
    for label, key in info["campos"]:
        e.add_field(name=label, value=f"```{campos.get(key, '—')}```", inline=len(label) < 22)
    e.add_field(
        name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        value="> ⚠️  Respeta las normas en todo momento.\n> ⏳  El staff te atenderá lo antes posible.\n> 🙏  Gracias por contactar con el **Staff Team de NightMC**.",
        inline=False
    )
    e.set_thumbnail(url=user.display_avatar.url)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_setup(guild):
    e = discord.Embed(color=0x2b2d31)
    e.set_author(name="NightMc Network  ✦  Sistema de Soporte", icon_url=guild.icon.url if guild.icon else None)
    e.title = "🎫  ¿Necesitas ayuda?"
    e.description = (
        "\nBienvenido al **Centro de Soporte** de NightMc Network.\n"
        "Estamos aquí para ayudarte con cualquier problema o duda.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "┃  🛠️  **Soporte General** — Dudas, ayuda general\n"
        "┃  🚫  **Reportes** — Jugadores, bugs, hacks\n"
        "┃  ⚖️  **Apelaciones** — Bans, mutes, sanciones\n"
        "┃  💰  **Pagos Tienda** — Compras, rangos, problemas\n"
        "┃  🎮  **Soporte de Juego** — Bugs in-game, glitches\n"
        "┃  📋  **Postulaciones Staff** — Aplicar para ser staff\n"
        "┃  🤝  **Alianzas** — Propuestas de colaboración\n"
        "┃  🎉  **Eventos** — Premios no recibidos, participación\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    e.add_field(name="📋  Normas del ticket", value=(
        "> 🔹 Sé respetuoso con el staff en todo momento\n"
        "> 🔹 Proporciona información clara y verídica\n"
        "> 🔹 No abuses del sistema de tickets\n"
        "> 🔹 Un ticket por asunto"
    ), inline=False)
    e.add_field(name="⏱️  Tiempo de respuesta", value="> Nuestro equipo te atenderá **lo antes posible**.", inline=False)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

def embed_claimed(user, guild):
    e = discord.Embed(description=f"🔑  **{user.mention}** tomó el control de este ticket.", color=0x57f287)
    e.set_footer(text="NightMc Network  ✦  Soporte activo")
    return e

def embed_close(guild):
    e = discord.Embed(
        title="🔒  Cerrando Ticket",
        description="Este ticket será eliminado en **5 segundos**.\n\n*Gracias por contactar al soporte de NightMc.*\n✦  Hasta pronto.",
        color=0xed4245
    )
    return _footer(e, guild)

def embed_transfer_menu(guild):
    e = discord.Embed(color=0xfee75c)
    e.set_author(name="NightMc Network  ✦  Escalación Interna", icon_url=guild.icon.url if guild.icon else None)
    e.title = "🔄  Transferir Expediente"
    e.description = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Selecciona el tipo de gestión que necesitas.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👑  **{ROL_HEAD}** — Gestiones críticas\n"
        f"🔰  **{ROL_HIGH}** — Gestiones avanzadas"
    )
    e.set_footer(text="NightMc Network  ✦  Solo staff puede usar esta función")
    return e

def embed_transfer_msg(label, guild):
    e = discord.Embed(color=0x5865f2)
    e.set_author(name="NightMc Network  ✦  Transferencia de Ticket", icon_url=guild.icon.url if guild.icon else None)
    e.title = "🔄  Ticket Redirigido"
    e.description = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nTu ticket ha sido escalado a\n**{label}**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    e.add_field(name="⏳  Estado",       value="> El equipo especializado revisará tu caso.", inline=False)
    e.add_field(name="💬  ¿Qué sigue?",  value="> Un miembro del staff se pondrá en contacto.\n> Por favor, **no abras otro ticket** sobre el mismo tema.", inline=False)
    e.set_image(url=BANNER_URL)
    return _footer(e, guild)

# ╔══════════════════════════════════════════════════════════════╗
#   🤖  BOT
# ╚══════════════════════════════════════════════════════════════╝

class NightBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self._ticket_msg_ids:   dict[int, int]              = {}
        self._claimed_channels: dict[int, int]              = {}
        self._last_rename:      dict[int, float]            = {}

    async def setup_hook(self):
        self.add_view(TicketLauncher())
        self.add_view(TicketControl())
        print("✦  NightMc Bot v2.0 listo.")

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="NightMc Network 🌙"))
        print(f"✦  Online  ·  {self.user}  ·  {self.user.id}")

bot = NightBot()
tickets_abiertos: dict[int, int]               = {}
cooldowns:        dict[int, datetime.datetime]  = {}

# ╔══════════════════════════════════════════════════════════════╗
#   🔧  UTILIDADES
# ╚══════════════════════════════════════════════════════════════╝

def es_staff(m: discord.Member) -> bool:
    return any(r.name in TODOS_ROLES_STAFF for r in m.roles)

def en_cooldown(uid: int) -> bool:
    return uid in cooldowns and (datetime.datetime.now() - cooldowns[uid]).total_seconds() < COOLDOWN_SEG

def leer_topic(canal: discord.TextChannel, clave: str) -> str:
    if not canal.topic: return ""
    for parte in canal.topic.split("|"):
        parte = parte.strip()
        if parte.startswith(f"{clave}:"):
            return parte[len(clave)+1:].strip()
    return ""

def _get_owner_id_from_topic(canal) -> int:
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
        cat    = discord.utils.get(guild.categories, name="📋 LOGS") or await guild.create_category("📋 LOGS")
        rol_st = discord.utils.get(guild.roles, name=ROL_TEAM)
        perms  = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if rol_st: perms[rol_st] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        return await guild.create_text_channel(LOGS_CANAL, category=cat, overwrites=perms)
    except: return None

async def enviar_log(guild, embed, file=None):
    c = await get_o_crear_logs(guild)
    if c:
        try:
            await c.send(embed=embed, file=file) if file else await c.send(embed=embed)
        except: pass

async def hacer_transcript(canal: discord.TextChannel) -> io.BytesIO:
    lineas = [f"=== TRANSCRIPT #{canal.name} ===\n\n"]
    async for msg in canal.history(limit=500, oldest_first=True):
        ts   = msg.created_at.strftime("%d/%m/%Y %H:%M")
        cont = msg.content or ""
        for emb in msg.embeds:
            if emb.title: cont += f" [EMBED: {emb.title}]"
        lineas.append(f"[{ts}] {msg.author.display_name}: {cont}\n")
    return io.BytesIO("".join(lineas).encode("utf-8"))

async def rename_robusto(canal: discord.TextChannel, nuevo: str):
    import time
    nuevo = nuevo[:50].lower().replace(" ", "-")
    if canal.name == nuevo: return True
    try:
        await canal.edit(name=nuevo)
        bot._last_rename[canal.id] = time.monotonic()
        return True
    except discord.HTTPException as e:
        if e.status == 429:
            await asyncio.sleep(float(getattr(e, "retry_after", 600)) + 2)
            try:
                await canal.edit(name=nuevo)
                return True
            except: return False
        return False
    except: return False

async def calcular_base_nombre(canal: discord.TextChannel) -> str:
    base   = canal.name
    if base.endswith("-pendiente"): base = base[:-10]
    partes = base.split("-")
    if len(partes) >= 3 and 2 <= len(partes[-1]) <= 15:
        base = "-".join(partes[:-1])
    return base

async def cerrar_ticket(canal, guild, cerrado_por, owner_id):
    for uid, cid in list(tickets_abiertos.items()):
        if cid == canal.id:
            del tickets_abiertos[uid]
            break
    bot._ticket_msg_ids.pop(canal.id, None)
    bot._claimed_channels.pop(canal.id, None)
    owner    = guild.get_member(owner_id)
    nombre_t = f"transcript-{canal.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    log_e    = discord.Embed(title="📤  Ticket Cerrado", color=0xed4245, timestamp=datetime.datetime.now())
    log_e.add_field(name="Canal",       value=f"#{canal.name}",    inline=True)
    log_e.add_field(name="Cerrado por", value=cerrado_por.mention, inline=True)
    if owner: log_e.add_field(name="Dueño", value=owner.mention, inline=True)
    log_e.set_footer(text=FOOTER)
    arch = await hacer_transcript(canal)
    await enviar_log(guild, log_e, file=discord.File(arch, filename=nombre_t))
    await asyncio.sleep(5)
    try:    await canal.delete()
    except discord.NotFound: pass

def _tiene_claim_button(msg: discord.Message) -> bool:
    for row in msg.components:
        for child in row.children:
            if getattr(child, "custom_id", None) == "claim_t": return True
    return False

async def resetear_claim_en_canal(canal, nombre_canal, owner_id):
    bot._claimed_channels.pop(canal.id, None)
    nuevo_view = TicketControl(nombre_canal=nombre_canal, owner_id=owner_id)
    mid = bot._ticket_msg_ids.get(canal.id)
    if mid:
        try:
            msg = await canal.fetch_message(mid)
            await msg.edit(view=nuevo_view)
            return
        except: pass
    try:
        async for m in canal.history(limit=50, oldest_first=True):
            if m.author.id == canal.guild.me.id and _tiene_claim_button(m):
                await m.edit(view=nuevo_view)
                bot._ticket_msg_ids[canal.id] = m.id
                return
    except: pass

# ╔══════════════════════════════════════════════════════════════╗
#   🎫  CREAR TICKET
# ╚══════════════════════════════════════════════════════════════╝

async def crear_ticket(interaction: discord.Interaction, tipo: str, campos: dict, nombre_canal: str):
    guild, user = interaction.guild, interaction.user
    await interaction.response.defer(ephemeral=True)
    if en_cooldown(user.id):
        return await interaction.followup.send(ERR_COOLDOWN, ephemeral=True)
    if user.id in tickets_abiertos:
        existe = guild.get_channel(tickets_abiertos[user.id])
        if existe: return await interaction.followup.send(ERR_DUPLICADO, ephemeral=True)
        del tickets_abiertos[user.id]

    cat = await get_o_crear_cat(guild, CATEGORIAS_TICKET.get(tipo, CAT_SOPORTE))
    if not cat: return await interaction.followup.send(ERR_NO_CAT, ephemeral=True)

    nombre_rol_esp, usar_st = ROLES_TICKET.get(tipo, (None, True))
    rol_esp = discord.utils.get(guild.roles, name=nombre_rol_esp) if nombre_rol_esp else None
    rol_st  = discord.utils.get(guild.roles, name=ROL_TEAM)

    perms = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        user:               discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
    }
    if rol_esp:            perms[rol_esp] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if usar_st and rol_st: perms[rol_st]  = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    try:
        canal = await guild.create_text_channel(
            name=f"{nombre_canal}-pendiente", category=cat,
            overwrites=perms, topic=f"tipo:{tipo} | ownerid:{user.id}")
    except discord.Forbidden:
        return await interaction.followup.send("❌  Sin permisos para crear canales.", ephemeral=True)

    tickets_abiertos[user.id] = canal.id
    cooldowns[user.id]        = datetime.datetime.now()
    rol_tag = (rol_st.mention if usar_st and rol_st else rol_esp.mention if rol_esp else f"@{ROL_TEAM}")

    view = TicketControl(nombre_canal=nombre_canal, owner_id=user.id)
    msg  = await canal.send(
        content=f"{user.mention}  {rol_tag}",
        embed=build_ticket_embed(tipo, guild, user, rol_tag, campos),
        view=view)
    bot._ticket_msg_ids[canal.id] = msg.id
    await interaction.followup.send(f"✅  Tu ticket fue abierto en {canal.mention}", ephemeral=True)

    log_e = discord.Embed(title="📥  Ticket Abierto", color=0x57f287, timestamp=datetime.datetime.now())
    log_e.add_field(name="Usuario",   value=user.mention,                             inline=True)
    log_e.add_field(name="Canal",     value=canal.mention,                            inline=True)
    log_e.add_field(name="Categoría", value=CATEGORIAS_TICKET.get(tipo, CAT_SOPORTE), inline=True)
    log_e.set_footer(text=FOOTER)
    await enviar_log(guild, log_e)

# ╔══════════════════════════════════════════════════════════════╗
#   🎮  BOTONES DEL TICKET (Claim / Transferir / Cerrar)
# ╚══════════════════════════════════════════════════════════════╝

class TicketControl(ui.View):
    def __init__(self, nombre_canal: str = "ticket", owner_id: int = 0):
        super().__init__(timeout=None)
        self.nombre_canal = nombre_canal
        self.owner_id     = owner_id

    def _owner(self, canal):
        if self.owner_id: return self.owner_id
        try:    return int(leer_topic(canal, "ownerid"))
        except: return 0

    @ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="🔑", custom_id="claim_t")
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        if not es_staff(interaction.user):
            return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
        cid      = interaction.channel.id
        owner_id = self._owner(interaction.channel)
        if interaction.user.id == owner_id:
            return await interaction.response.send_message(ERR_PROPIO, ephemeral=True)
        claimed = bot._claimed_channels.get(cid)
        if claimed and claimed != interaction.user.id:
            return await interaction.response.send_message(ERR_YA_RECLAMADO, ephemeral=True)
        if claimed == interaction.user.id:
            return await interaction.response.send_message(ERR_YA_TUYO, ephemeral=True)
        bot._claimed_channels[cid] = interaction.user.id
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
            return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
        owner_id = self._owner(interaction.channel)
        await interaction.response.send_message(
            embed=embed_transfer_menu(interaction.guild),
            view=TransferView(owner_id=owner_id), ephemeral=True)

    @ui.button(label="Cerrar", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="close_t")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        if not es_staff(interaction.user):
            return await interaction.response.send_message("❌  Solo el personal autorizado puede cerrar este ticket.", ephemeral=True)
        owner_id = self._owner(interaction.channel)
        await interaction.response.send_message(embed=embed_close(interaction.guild))
        await cerrar_ticket(interaction.channel, interaction.guild, interaction.user, owner_id)

# ╔══════════════════════════════════════════════════════════════╗
#   🔄  MENÚ DE TRANSFERENCIA
# ╚══════════════════════════════════════════════════════════════╝

class TransferView(ui.View):
    def __init__(self, owner_id: int = 0):
        super().__init__(timeout=180)
        self.owner_id = owner_id

    @ui.select(placeholder="✦  Selecciona el tipo de gestión...", options=[
        discord.SelectOption(label="Ganadores de Eventos",   value="ganadores-eventos", emoji="🎖️", description=f"Head staff"),
        discord.SelectOption(label="Unregister",             value="unregister",         emoji="🔐", description=f"Head staff"),
        discord.SelectOption(label="Reembolso",              value="reembolso",          emoji="💸", description=f"Head staff"),
        discord.SelectOption(label="Staff Report",           value="staff-report",       emoji="🚨", description=f"Head staff"),
        discord.SelectOption(label="Error de Configuración", value="error-config",       emoji="⚠️", description=f"Head staff"),
        discord.SelectOption(label="Revives",                value="revives",            emoji="💊", description=f"Hight staff"),
        discord.SelectOption(label="Cambio de Nick",         value="cambio-nick",        emoji="✏️", description=f"Hight staff"),
    ])
    async def select_callback(self, interaction: discord.Interaction, select: ui.Select):
        destino = select.values[0]
        sub     = TRANSFER_SUBS.get(destino)
        if not sub:
            return await interaction.response.send_message("❌  Subcategoría no encontrada.", ephemeral=True)
        nombre_rol, cat_nombre, label = sub
        rol_nuevo = discord.utils.get(interaction.guild.roles, name=nombre_rol)
        canal     = interaction.channel
        guild     = interaction.guild
        owner_id  = self.owner_id or _get_owner_id_from_topic(canal)

        cat_t = await get_o_crear_cat(guild, cat_nombre)
        if cat_t and canal.category != cat_t:
            try: await canal.edit(category=cat_t)
            except: pass

        asyncio.create_task(rename_robusto(canal, destino + "-pendiente"))

        for target in list(canal.overwrites):
            if isinstance(target, discord.Role) and target.name in TODOS_ROLES_STAFF:
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

        log_e = discord.Embed(title="🔄  Ticket Transferido", color=0xfee75c, timestamp=datetime.datetime.now())
        log_e.add_field(name="Canal",   value=canal.mention,            inline=True)
        log_e.add_field(name="Destino", value=label,                    inline=True)
        log_e.add_field(name="Rol",     value=nombre_rol,               inline=True)
        log_e.add_field(name="Staff",   value=interaction.user.mention, inline=True)
        log_e.set_footer(text=FOOTER)
        await enviar_log(guild, log_e)

# ╔══════════════════════════════════════════════════════════════╗
#   📝  MODALES
# ╚══════════════════════════════════════════════════════════════╝

class GeneralModal(ui.Modal, title="NightMc  ·  Soporte General"):
    nick     = ui.TextInput(label="Nick", placeholder="Tu nick en Minecraft")
    consulta = ui.TextInput(label="Duda", placeholder="¿Cuál es tu duda?", style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "soporte", {"Nick": self.nick.value, "Duda": self.consulta.value}, "soporte")

class ReporteModal(ui.Modal, title="NightMc  ·  Reportar Usuario"):
    nick    = ui.TextInput(label="Nick",                 placeholder="Tu nick en Minecraft")
    acusado = ui.TextInput(label="Usuario que reportas", placeholder="Nick del usuario a reportar")
    pruebas = ui.TextInput(label="Pruebas",              placeholder="Link de imgur, YouTube, etc.", style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "reporte", {"Nick": self.nick.value, "Usuario reportado": self.acusado.value, "Pruebas": self.pruebas.value}, "reporte")

class ApelacionModal(ui.Modal, title="NightMc  ·  Apelar Sanción"):
    nick  = ui.TextInput(label="Nick sancionado",             placeholder="Cuenta sancionada")
    staff = ui.TextInput(label="Staff que te sancionó",       placeholder="¿Quién te sancionó?")
    razon = ui.TextInput(label="Razón de la sanción",         placeholder="¿Por qué te sancionaron?", style=discord.TextStyle.paragraph)
    unban = ui.TextInput(label="¿Por qué debería retirarse?", placeholder="Explica tu caso", style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "apelacion", {
            "Nick sancionado": self.nick.value, "Staff que sancionó": self.staff.value,
            "Razón de la sanción": self.razon.value, "¿Por qué retirar la sanción?": self.unban.value
        }, "apelacion")

class PagosTiendaModal(ui.Modal, title="NightMc  ·  Soporte Pagos Tienda"):
    nick    = ui.TextInput(label="Nick",         placeholder="Nick con el que compraste")
    id_pago = ui.TextInput(label="ID de compra", placeholder="ID de tu transacción en Tebex")
    error   = ui.TextInput(label="Problema",     placeholder="¿Qué sucedió con tu compra?", style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "pagos_tienda", {"Nick de compra": self.nick.value, "ID de compra": self.id_pago.value, "Problema": self.error.value}, "pagos-tienda")

class JuegoModal(ui.Modal, title="NightMc  ·  Soporte de Juego"):
    nick  = ui.TextInput(label="Nick",            placeholder="Tu nick en Minecraft")
    bug   = ui.TextInput(label="Bug o error",     placeholder="¿Qué bug encontraste?", style=discord.TextStyle.paragraph)
    lugar = ui.TextInput(label="¿Dónde ocurrió?", placeholder="Mundo, coordenadas...", style=discord.TextStyle.paragraph, required=False)
    async def on_submit(self, i):
        await crear_ticket(i, "juego", {"Nick": self.nick.value, "Bug": self.bug.value, "Ubicacion": self.lugar.value or "—"}, "juego")

class PostulacionModal(ui.Modal, title="NightMc  ·  Postulación Staff"):
    nick = ui.TextInput(label="Nick", placeholder="Tu nick en Minecraft")
    duda = ui.TextInput(label="Duda", placeholder="¿Qué clase de duda tienes?", style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "postulacion", {"Nick": self.nick.value, "Duda": self.duda.value}, "postulacion")

class AlianzaModal(ui.Modal, title="NightMc  ·  Propuesta de Alianza"):
    servidor  = ui.TextInput(label="Nombre del servidor",       placeholder="¿Cómo se llama tu servidor?")
    miembros  = ui.TextInput(label="Miembros aproximados",      placeholder="Ej: 500 miembros")
    propuesta = ui.TextInput(label="Propuesta de colaboración", placeholder="¿Qué tipo de alianza propones?", style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "alianza", {"Servidor": self.servidor.value, "Miembros": self.miembros.value, "Propuesta": self.propuesta.value}, "alianza")

class EventoModal(ui.Modal, title="NightMc  ·  Soporte de Eventos"):
    nick   = ui.TextInput(label="Nick",              placeholder="Tu nick en Minecraft")
    evento = ui.TextInput(label="Nombre del evento", placeholder="¿En qué evento participaste?")
    premio = ui.TextInput(label="Premio esperado",   placeholder="¿Qué premio te corresponde?")
    desc   = ui.TextInput(label="Descripción",       placeholder="Explica el problema con detalle", style=discord.TextStyle.paragraph)
    async def on_submit(self, i):
        await crear_ticket(i, "evento", {"Nick": self.nick.value, "Evento": self.evento.value, "Premio": self.premio.value, "Descripcion": self.desc.value}, "evento")

# ╔══════════════════════════════════════════════════════════════╗
#   🎡  PANEL PRINCIPAL — 8 botones visuales
# ╚══════════════════════════════════════════════════════════════╝

class TicketLauncher(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Soporte",    style=discord.ButtonStyle.secondary, emoji="🛠️", custom_id="btn_soporte",     row=0)
    async def btn_soporte(self, i, b):     await i.response.send_modal(GeneralModal())

    @ui.button(label="Reportar",   style=discord.ButtonStyle.danger,    emoji="🚫", custom_id="btn_reporte",     row=0)
    async def btn_reporte(self, i, b):     await i.response.send_modal(ReporteModal())

    @ui.button(label="Apelar",     style=discord.ButtonStyle.primary,   emoji="⚖️", custom_id="btn_apelacion",   row=0)
    async def btn_apelacion(self, i, b):   await i.response.send_modal(ApelacionModal())

    @ui.button(label="Pagos",      style=discord.ButtonStyle.success,   emoji="💰", custom_id="btn_pagos",       row=1)
    async def btn_pagos(self, i, b):       await i.response.send_modal(PagosTiendaModal())

    @ui.button(label="Juego",      style=discord.ButtonStyle.primary,   emoji="🎮", custom_id="btn_juego",       row=1)
    async def btn_juego(self, i, b):       await i.response.send_modal(JuegoModal())

    @ui.button(label="Staff",      style=discord.ButtonStyle.secondary, emoji="📋", custom_id="btn_postulacion", row=1)
    async def btn_postulacion(self, i, b): await i.response.send_modal(PostulacionModal())

    @ui.button(label="Alianza",    style=discord.ButtonStyle.secondary, emoji="🤝", custom_id="btn_alianza",     row=2)
    async def btn_alianza(self, i, b):     await i.response.send_modal(AlianzaModal())

    @ui.button(label="Eventos",    style=discord.ButtonStyle.secondary, emoji="🎉", custom_id="btn_evento",      row=2)
    async def btn_evento(self, i, b):      await i.response.send_modal(EventoModal())

# ╔══════════════════════════════════════════════════════════════╗
#   ⚡  SLASH COMMANDS
# ╚══════════════════════════════════════════════════════════════╝

@bot.tree.command(name="transfer", description="Deriva este ticket a otro equipo de staff")
async def transfer_slash(interaction: discord.Interaction):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    owner_id = _get_owner_id_from_topic(interaction.channel)
    await interaction.response.send_message(embed=embed_transfer_menu(interaction.guild), view=TransferView(owner_id=owner_id), ephemeral=True)

@bot.tree.command(name="close", description="Cierra este ticket")
async def close_slash(interaction: discord.Interaction):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    owner_id = _get_owner_id_from_topic(interaction.channel)
    await interaction.followup.send(embed=embed_close(interaction.guild))
    await cerrar_ticket(interaction.channel, interaction.guild, interaction.user, owner_id)

@bot.tree.command(name="claim", description="Reclama este ticket")
async def claim_slash(interaction: discord.Interaction):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    owner_id = _get_owner_id_from_topic(interaction.channel)
    if interaction.user.id == owner_id: return await interaction.followup.send(ERR_PROPIO, ephemeral=True)
    base = await calcular_base_nombre(interaction.channel)
    asyncio.create_task(rename_robusto(interaction.channel, f"{base}-{interaction.user.name[:12].lower()}"))
    await interaction.followup.send(embed=embed_claimed(interaction.user, interaction.guild))

@bot.tree.command(name="transcript", description="Genera el transcript de este ticket")
async def transcript_slash(interaction: discord.Interaction):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    arch   = await hacer_transcript(interaction.channel)
    nombre = f"transcript-{interaction.channel.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    await interaction.followup.send("📄  Transcript generado:", file=discord.File(arch, filename=nombre), ephemeral=True)
    arch2 = await hacer_transcript(interaction.channel)
    log_e = discord.Embed(title="📄  Transcript Generado", color=0xfee75c, timestamp=datetime.datetime.now())
    log_e.add_field(name="Canal", value=interaction.channel.mention, inline=True)
    log_e.add_field(name="Staff", value=interaction.user.mention,    inline=True)
    log_e.set_footer(text=FOOTER)
    lc = await get_o_crear_logs(interaction.guild)
    if lc:
        try: await lc.send(embed=log_e, file=discord.File(arch2, filename=nombre))
        except: pass

@bot.tree.command(name="add", description="Añade a un usuario al ticket")
@discord.app_commands.describe(usuario="Usuario a añadir")
async def add_slash(interaction: discord.Interaction, usuario: discord.Member):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    try:
        await interaction.channel.set_permissions(usuario, read_messages=True, send_messages=True)
        await interaction.followup.send(f"✅  {usuario.mention} fue añadido al ticket.")
    except discord.Forbidden:
        await interaction.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="remove", description="Elimina a un usuario del ticket")
@discord.app_commands.describe(usuario="Usuario a eliminar")
async def remove_slash(interaction: discord.Interaction, usuario: discord.Member):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    try:
        await interaction.channel.set_permissions(usuario, overwrite=None)
        await interaction.followup.send(f"🚫  {usuario.mention} fue eliminado del ticket.")
    except discord.Forbidden:
        await interaction.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="rename", description="Renombra el canal del ticket")
@discord.app_commands.describe(nombre="Nuevo nombre (sin espacios)")
async def rename_slash(interaction: discord.Interaction, nombre: str):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.channel.edit(name=nombre.lower().replace(" ", "-")[:50])
        await interaction.followup.send("✏️  Canal renombrado.", ephemeral=True)
    except (discord.Forbidden, discord.HTTPException) as e:
        await interaction.followup.send(f"❌  {e}", ephemeral=True)

@bot.tree.command(name="slowmode", description="Activa o desactiva el modo lento")
@discord.app_commands.describe(segundos="Segundos (0 para desactivar)")
async def slowmode_slash(interaction: discord.Interaction, segundos: int = 0):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    segundos = max(0, min(segundos, 21600))
    try:
        await interaction.channel.edit(slowmode_delay=segundos)
        await interaction.followup.send(f"🐢  Slowmode: **{segundos}s**." if segundos else "✅  Slowmode desactivado.")
    except discord.Forbidden:
        await interaction.followup.send("❌  Sin permisos.", ephemeral=True)

@bot.tree.command(name="specifictag_staff", description="Transfiere este ticket a un staff específico")
@discord.app_commands.describe(staff="Miembro del staff al que transferir")
async def specifictag_staff(interaction: discord.Interaction, staff: discord.Member):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    if not es_staff(staff):            return await interaction.response.send_message("❌  El usuario no es staff.", ephemeral=True)
    if staff.id == interaction.user.id: return await interaction.response.send_message("❌  No puedes transferirte el ticket a ti mismo.", ephemeral=True)
    await interaction.response.defer()
    canal, guild = interaction.channel, interaction.guild
    owner_id = _get_owner_id_from_topic(canal)
    for target in list(canal.overwrites):
        if isinstance(target, discord.Role) and target.name in TODOS_ROLES_STAFF:
            try: await canal.set_permissions(target, overwrite=None)
            except: pass
    for nombre_rol in ROLES_SUPERIORES:
        r = discord.utils.get(guild.roles, name=nombre_rol)
        if r:
            try: await canal.set_permissions(r, read_messages=True, send_messages=True)
            except: pass
    try: await canal.set_permissions(staff, read_messages=True, send_messages=True)
    except: pass
    if owner_id:
        owner = guild.get_member(owner_id)
        if owner:
            try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
            except: pass
    cat_t = await get_o_crear_cat(guild, CAT_TRANSFER)
    if cat_t and canal.category != cat_t:
        try: await canal.edit(category=cat_t)
        except: pass
    nombre_destino = f"staff-{staff.name[:12].lower()}"
    await resetear_claim_en_canal(canal, nombre_destino, owner_id)
    asyncio.create_task(rename_robusto(canal, f"{nombre_destino}-pendiente"))
    e = discord.Embed(title="👤  Ticket Transferido a Staff", color=0x5865f2)
    e.description = f"Este ticket fue asignado a {staff.mention}.\nSolo **{staff.display_name}** y **{ROL_HIGH}+** pueden verlo."
    e.set_image(url=BANNER_URL)
    _footer(e, guild)
    await interaction.followup.send(embed=e)
    await canal.send(f"{staff.mention}  ✦  Se te ha asignado este ticket.")
    log_e = discord.Embed(title="👤  Ticket → Staff Específico", color=0x5865f2, timestamp=datetime.datetime.now())
    log_e.add_field(name="Canal",    value=canal.mention,            inline=True)
    log_e.add_field(name="Asignado", value=staff.mention,            inline=True)
    log_e.add_field(name="Por",      value=interaction.user.mention, inline=True)
    log_e.set_footer(text=FOOTER)
    await enviar_log(guild, log_e)

@bot.tree.command(name="specifictag_role", description="Transfiere este ticket a un rol específico")
@discord.app_commands.describe(rol="Rol al que transferir el ticket")
async def specifictag_role(interaction: discord.Interaction, rol: discord.Role):
    if not es_staff(interaction.user): return await interaction.response.send_message(ERR_NO_STAFF, ephemeral=True)
    await interaction.response.defer()
    canal, guild = interaction.channel, interaction.guild
    owner_id = _get_owner_id_from_topic(canal)
    for target in list(canal.overwrites):
        if isinstance(target, discord.Role) and target.name in TODOS_ROLES_STAFF:
            try: await canal.set_permissions(target, overwrite=None)
            except: pass
    for nombre_rol in ROLES_SUPERIORES:
        r = discord.utils.get(guild.roles, name=nombre_rol)
        if r:
            try: await canal.set_permissions(r, read_messages=True, send_messages=True)
            except: pass
    try: await canal.set_permissions(rol, read_messages=True, send_messages=True)
    except: pass
    if owner_id:
        owner = guild.get_member(owner_id)
        if owner:
            try: await canal.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)
            except: pass
    cat_t = await get_o_crear_cat(guild, CAT_TRANSFER)
    if cat_t and canal.category != cat_t:
        try: await canal.edit(category=cat_t)
        except: pass
    nombre_destino = rol.name[:20].lower().replace(" ", "-")
    await resetear_claim_en_canal(canal, nombre_destino, owner_id)
    asyncio.create_task(rename_robusto(canal, f"{nombre_destino}-pendiente"))
    e = discord.Embed(title="🎭  Ticket Transferido a Rol", color=0x5865f2)
    e.description = f"Este ticket fue asignado al rol {rol.mention}."
    e.set_image(url=BANNER_URL)
    _footer(e, guild)
    await interaction.followup.send(embed=e)
    await canal.send(f"{rol.mention}  ✦  Se requiere atención en este ticket.")
    log_e = discord.Embed(title="🎭  Ticket → Rol Específico", color=0x5865f2, timestamp=datetime.datetime.now())
    log_e.add_field(name="Canal", value=canal.mention,            inline=True)
    log_e.add_field(name="Rol",   value=rol.mention,              inline=True)
    log_e.add_field(name="Por",   value=interaction.user.mention, inline=True)
    log_e.set_footer(text=FOOTER)
    await enviar_log(guild, log_e)

@bot.tree.command(name="ip", description="Muestra las IPs del servidor")
async def ip_slash(interaction: discord.Interaction):
    e = discord.Embed(title="👑  NightMc Network — Conexión", color=0x5865f2)
    e.description = "¡Bienvenido a **NightMc Network**!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    e.add_field(name="☕  Java Edition", value="> **IP:** `NightMc.me`\n> **Versiones:** 1.16+", inline=True)
    e.add_field(name="🟩  Bedrock",      value="> ⏳ **Próximamente...**",                       inline=True)
    e.add_field(name="🎮  Modalidades",  value="> ⚔️  **ClashBox** — Disponible\n> 🗡️  **FullPvP** — Próximamente", inline=False)
    e.set_image(url="https://i.imgur.com/WxEp4MV.png")
    e.set_footer(text="© Powered by NightMC")
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="help", description="Muestra todos los comandos disponibles")
async def help_slash(interaction: discord.Interaction):
    e = discord.Embed(title="📋  Comandos — NightMc Tickets", color=0x5865f2)
    e.set_author(name="NightMc Network", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    e.description = "Todos los comandos funcionan con `/` **y** con `!`.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    e.add_field(name="🎫  Tickets",    value="`/claim` `/close` `/transcript`",                         inline=False)
    e.add_field(name="👥  Usuarios",   value="`/add @usuario` `/remove @usuario`",                      inline=False)
    e.add_field(name="⚙️  Canal",      value="`/rename <nombre>` `/slowmode [seg]`",                    inline=False)
    e.add_field(name="🔄  Transferir", value="`/transfer` `/specifictag_staff` `/specifictag_role`",    inline=False)
    e.add_field(name="🛠️  Admin",      value="`!setup` — Publica el panel\n`!sync` — Registra slash commands", inline=False)
    e.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=e, ephemeral=True)

# ╔══════════════════════════════════════════════════════════════╗
#   🛠️  COMANDOS DE PREFIJO (!)
# ╚══════════════════════════════════════════════════════════════╝

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
    except Exception as e:
        await msg.edit(content=f"❌  Error: {e}")

@bot.command(name="claim")
async def claim_prefix(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    if ctx.author.id == _get_owner_id_from_topic(ctx.channel): return await ctx.send(ERR_PROPIO)
    base = await calcular_base_nombre(ctx.channel)
    asyncio.create_task(rename_robusto(ctx.channel, f"{base}-{ctx.author.name[:12].lower()}"))
    await ctx.send(embed=embed_claimed(ctx.author, ctx.guild))

@bot.command(name="close")
async def close_prefix(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    owner_id = _get_owner_id_from_topic(ctx.channel)
    await ctx.send(embed=embed_close(ctx.guild))
    await cerrar_ticket(ctx.channel, ctx.guild, ctx.author, owner_id)

@bot.command(name="transcript")
async def transcript_prefix(ctx):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    msg  = await ctx.send("⏳  Generando...")
    arch = await hacer_transcript(ctx.channel)
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
    except discord.Forbidden: await ctx.send("❌  Sin permisos.")

@bot.command(name="remove")
async def remove_prefix(ctx, usuario: discord.Member = None):
    if not es_staff(ctx.author): return await ctx.send(ERR_NO_STAFF)
    if not usuario: return await ctx.send("❌  Uso: `!remove @usuario`")
    try:
        await ctx.channel.set_permissions(usuario, overwrite=None)
        await ctx.send(f"🚫  {usuario.mention} eliminado.")
    except discord.Forbidden: await ctx.send("❌  Sin permisos.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    if isinstance(error, commands.MissingPermissions): return await ctx.send("❌  Sin permisos.")
    raise error

# ╔══════════════════════════════════════════════════════════════╗
#   🚀  ARRANQUE
# ╚══════════════════════════════════════════════════════════════╝

if not TOKEN:
    print("❌  ERROR: No se encontró DISCORD_TOKEN en el archivo .env")
    print("   Crea un archivo .env con: DISCORD_TOKEN=tu_token_aqui")
    exit(1)

bot.run(TOKEN)
