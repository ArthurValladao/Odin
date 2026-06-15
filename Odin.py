import sounddevice as sd
import numpy as np
import pyttsx3
import subprocess
import webbrowser
import requests
import speech_recognition as sr
import io
import wave
import os
import sys
import random
import ctypes
import time
import json

# ══════════════════════════════════════════════════════════════════
#  CONFIGURAÇÃO DO SPOTIFY  (preencha com suas credenciais)
#  1. Acesse: https://developer.spotify.com/dashboard
#  2. Crie um app → copie Client ID e Client Secret
#  3. Em "Redirect URIs" adicione: http://localhost:8888/callback
# ══════════════════════════════════════════════════════════════════
SPOTIFY_CLIENT_ID     = "a838b4c173634e89be377723dc4facad"
SPOTIFY_CLIENT_SECRET = "a5a8f7749f6248d1a1e2d785d0f376fb"
SPOTIFY_REDIRECT_URI  = "http://127.0.0.1:8888/callback"
# ──────────────────────────────────────────────────────────────────

# ─── Cores ───────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
PURPLE = "\033[95m"
BLUE   = "\033[94m"
DIM    = "\033[2m"

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    limpar()
    print(f"{BLUE}{BOLD}")
    print("  ██████╗ ██████╗ ██╗███╗   ██╗")
    print("██╔═══██╗██╔══██╗██║████╗  ██║")
    print("██║   ██║██║  ██║██║██╔██╗ ██║")
    print("██║   ██║██║  ██║██║██║╚██╗██║")
    print("╚██████╔╝██████╔╝██║██║ ╚████║")
    print(" ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝")
    print(f"{RESET}{DIM} · Protocolo de voz ativo{RESET}")
    print(f"{CYAN}{'─' * 47}{RESET}\n")

def log(tipo, mensagem):
    icones = {
        "escutando": f"{DIM}  ◈  {mensagem}{RESET}",
        "ativado":   f"\n{BLUE}{BOLD}  ◉  {mensagem}{RESET}",
        "usuario":   f"{CYAN}  ▸  Sr. Arthur: {BOLD}{mensagem}{RESET}",
        "agente":    f"{YELLOW}  ◆  Odin: {BOLD}{mensagem}{RESET}",
        "erro":      f"{RED}  ✖  {mensagem}{RESET}",
        "acao":      f"{GREEN}  ✔  {mensagem}{RESET}",
        "spotify":   f"{GREEN}  ♪  {mensagem}{RESET}",
    }
    print(icones.get(tipo, f"  {mensagem}"))

# ─── Voz ─────────────────────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty("rate", 170)  # Ritmo pausado e elegante

vozes = engine.getProperty("voices")
for v in vozes:
    if "brazil" in v.id.lower() or "portuguese" in v.id.lower() or "pt" in v.id.lower():
        engine.setProperty("voice", v.id)
        break

def falar(texto):
    log("agente", texto)
    engine.say(texto)
    engine.runAndWait()

# ─── Banco de falas estilo J.A.R.V.I.S ───────────────────────────
FALAS = {
    "ativado": [
        "Ao seu dispor, Sr. Arthur.",
        "Prontamente, Sr. Arthur. Qual é a sua ordem?",
        "Sistemas operacionais. O que necessita, Sr. Arthur?",
        "Odin online. Aguardando instruções.",
        "Protocolo de resposta ativado. Como posso auxiliá-lo?",
        "Presença confirmada, Sr. Arthur. Pode prosseguir.",
    ],
    "nao_ouvi": [
        "Peço desculpas, Sr. Arthur. Não consegui captar o sinal de áudio.",
        "Interferência detectada. Poderia repetir, Sr. Arthur?",
        "Sinal insuficiente. Por favor, reafirme o comando.",
        "Não registrei entrada de voz, Sr. Arthur. Aguardo sua instrução.",
    ],
    "nao_entendi": [
        "Esse comando não consta em meus protocolos, Sr. Arthur.",
        "Solicitação não reconhecida. Poderia reformular?",
        "Parâmetros inválidos. Não fui capaz de processar, Sr. Arthur.",
        "Hmm. Esse não é um comando que conheço ainda, Sr. Arthur.",
    ],
    "site_abrindo": [
        "Acessando o endereço solicitado, Sr. Arthur.",
        "Protocolo de navegação iniciado.",
        "Redirecionando o browser, Sr. Arthur.",
        "Conexão estabelecida. Abrindo agora.",
    ],
    "app_abrindo": [
        "Inicializando o aplicativo, Sr. Arthur.",
        "Processo de execução iniciado.",
        "Sistema carregando, Sr. Arthur. Um momento.",
        "Aplicativo sendo lançado conforme solicitado.",
    ],
    "instalando": [
        "Protocolo de instalação iniciado, Sr. Arthur. Isso pode levar alguns instantes.",
        "Iniciando download e instalação. Aguarde, Sr. Arthur.",
        "Solicitação de instalação processada. Monitorando o progresso.",
    ],
    "volume_aumentando": [
        "Amplificando os sistemas de áudio, Sr. Arthur.",
        "Volume elevado conforme solicitado.",
        "Aumentando a saída de áudio.",
    ],
    "volume_diminuindo": [
        "Reduzindo os sistemas de áudio, Sr. Arthur.",
        "Volume atenuado conforme solicitado.",
        "Nível sonoro reduzido.",
    ],
    "volume_mutando": [
        "Silenciando todos os canais de áudio, Sr. Arthur.",
        "Protocolo de silêncio ativado.",
        "Áudio suprimido.",
    ],
    "minimizando": [
        "Limpando a área de trabalho, Sr. Arthur.",
        "Todas as janelas foram minimizadas.",
        "Interface zerada. Área de trabalho livre, Sr. Arthur.",
    ],
    "desligando": [
        "Encerrando todos os sistemas. Até a próxima, Sr. Arthur.",
        "Protocolo de desligamento iniciado. Foi um prazer servi-lo.",
    ],
    "reiniciando": [
        "Reinicialização em andamento, Sr. Arthur. Estarei de volta em breve.",
        "Executando reinicialização do sistema conforme solicitado.",
    ],
    "bloqueando": [
        "Terminal bloqueado, Sr. Arthur. Segurança garantida.",
        "Protocolo de segurança ativado. Estação bloqueada.",
    ],
    "captura": [
        "Captura de tela realizada e salva na área de trabalho, Sr. Arthur.",
        "Screenshot registrado com sucesso.",
        "Imagem da tela capturada, Sr. Arthur.",
    ],
    "tarefa_encerrada": [
        "Processo encerrado com êxito, Sr. Arthur.",
        "Aplicativo finalizado conforme solicitado.",
        "Tarefa eliminada dos sistemas.",
    ],
    "despedida": [
        "Até logo, Sr. Arthur. Os sistemas permanecerão em standby.",
        "Encerrando protocolos. Foi uma honra servi-lo.",
        "Odin em modo de espera. Até a próxima, Sr. Arthur.",
    ],
    # Spotify
    "spotify_play": [
        "Reprodução iniciada, Sr. Arthur.",
        "Música em andamento.",
        "Ativando a trilha sonora, Sr. Arthur.",
    ],
    "spotify_pause": [
        "Reprodução pausada, Sr. Arthur.",
        "Música suspensa.",
        "Pausando o áudio conforme solicitado.",
    ],
    "spotify_proxima": [
        "Avançando para a próxima faixa, Sr. Arthur.",
        "Próxima música selecionada.",
        "Pulando para a faixa seguinte.",
    ],
    "spotify_anterior": [
        "Retornando à faixa anterior, Sr. Arthur.",
        "Música anterior selecionada.",
    ],
    "spotify_buscando": [
        "Localizando a faixa nos servidores do Spotify, Sr. Arthur.",
        "Processando sua solicitação musical.",
        "Buscando e preparando a reprodução, Sr. Arthur.",
    ],
    "spotify_erro": [
        "Não consegui acessar o Spotify, Sr. Arthur. Verifique a conexão.",
        "Falha na comunicação com o Spotify, Sr. Arthur.",
    ],
}

def falar_aleatorio(contexto):
    opcoes = FALAS.get(contexto, ["Feito, Sr. Arthur."])
    falar(random.choice(opcoes))

# ─── Reconhecimento de voz ────────────────────────────────────────
recognizer = sr.Recognizer()

def gravar(duracao=5):
    fs = 16000
    audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(audio.tobytes())
    buf.seek(0)
    return sr.AudioData(buf.read(), fs, 2)

def transcrever(audio_data):
    try:
        return recognizer.recognize_google(audio_data, language="pt-BR").lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        log("erro", "Sem conexão com o Google Speech")
        return ""

def aguardar_palavra_chave():
    log("escutando", "Aguardando palavra-chave 'Odin'...")
    while True:
        audio = gravar(duracao=4)
        texto = transcrever(audio)
        if "odin" in texto:
            return True

def ouvir_comando():
    log("escutando", "Canal de voz aberto. Aguardando instrução...")
    audio = gravar(duracao=10)
    texto = transcrever(audio)
    if texto:
        log("usuario", texto)
    return texto

# ══════════════════════════════════════════════════════════════════
#  SPOTIFY CONTROLLER
# ══════════════════════════════════════════════════════════════════
_spotify_token = None
_spotify_token_expira = 0

def _spotify_get_token():
    """Obtém token de acesso via Client Credentials (controle básico)."""
    global _spotify_token, _spotify_token_expira
    if _spotify_token and time.time() < _spotify_token_expira:
        return _spotify_token
    try:
        import base64
        creds = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {creds}"},
            data={"grant_type": "client_credentials"},
            timeout=8
        )
        data = r.json()
        _spotify_token = data.get("access_token")
        _spotify_token_expira = time.time() + data.get("expires_in", 3600) - 60
        return _spotify_token
    except Exception as e:
        log("erro", f"Falha no token Spotify: {e}")
        return None

# Cache do token de usuário (OAuth) - necessário para controle de playback
_spotify_user_token = None

def _spotify_user_token_load():
    """Carrega token de usuário do arquivo .spotify_token.json"""
    global _spotify_user_token
    caminho = os.path.join(os.path.dirname(__file__), ".spotify_token.json")
    if os.path.exists(caminho):
        with open(caminho) as f:
            data = json.load(f)
            _spotify_user_token = data.get("access_token")
    return _spotify_user_token

def spotify_autorizar():
    """
    Faz o fluxo OAuth do Spotify para obter permissão de controle de playback.
    Deve ser chamado uma vez na primeira execução.
    """
    import urllib.parse
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler

    scopes = "user-modify-playback-state user-read-playback-state streaming"
    params = urllib.parse.urlencode({
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scopes,
    })
    auth_url = f"https://accounts.spotify.com/authorize?{params}"
    webbrowser.open(auth_url)
    log("acao", "Aguardando autorização do Spotify no navegador...")

    codigo = [None]

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            codigo[0] = qs.get("code", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Odin autorizado! Pode fechar esta janela.</h2>")
        def log_message(self, *a): pass

    server = HTTPServer(("127.0.0.1", 8888), Handler)
    server.handle_request()
    server.server_close()

    if not codigo[0]:
        log("erro", "Não recebi o código de autorização do Spotify.")
        return False

    # Troca código por token
    import base64
    creds = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {creds}"},
        data={
            "grant_type": "authorization_code",
            "code": codigo[0],
            "redirect_uri": SPOTIFY_REDIRECT_URI,
        },
        timeout=10
    )
    data = r.json()
    caminho = os.path.join(os.path.dirname(__file__), ".spotify_token.json")
    with open(caminho, "w") as f:
        json.dump(data, f)
    global _spotify_user_token
    _spotify_user_token = data.get("access_token")
    log("acao", "Spotify autorizado com sucesso!")
    return True

def _spotify_refresh_token():
    """Renova o token de usuário usando o refresh_token."""
    global _spotify_user_token
    caminho = os.path.join(os.path.dirname(__file__), ".spotify_token.json")
    if not os.path.exists(caminho):
        return None
    with open(caminho) as f:
        data = json.load(f)
    refresh = data.get("refresh_token")
    if not refresh:
        return None
    import base64
    creds = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {creds}"},
        data={"grant_type": "refresh_token", "refresh_token": refresh},
        timeout=10
    )
    novo = r.json()
    if "access_token" in novo:
        data["access_token"] = novo["access_token"]
        with open(caminho, "w") as f:
            json.dump(data, f)
        _spotify_user_token = novo["access_token"]
    return _spotify_user_token

def _spotify_headers():
    token = _spotify_user_token or _spotify_user_token_load()
    if not token:
        return None
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def _spotify_api(method, endpoint, body=None, retry=True):
    """Wrapper para chamadas à API do Spotify com auto-refresh de token."""
    h = _spotify_headers()
    if not h:
        log("erro", "Token Spotify não encontrado. Execute spotify_autorizar() primeiro.")
        return None
    url = f"https://api.spotify.com/v1{endpoint}"
    try:
        r = getattr(requests, method)(url, headers=h, json=body, timeout=8)
        if r.status_code == 401 and retry:
            log("acao", "Token expirado. Renovando...")
            _spotify_refresh_token()
            return _spotify_api(method, endpoint, body, retry=False)
        return r
    except Exception as e:
        log("erro", f"Erro na API do Spotify: {e}")
        return None

def spotify_play_pause():
    r = _spotify_api("get", "/me/player")
    if r and r.status_code == 200 and r.json().get("is_playing"):
        _spotify_api("put", "/me/player/pause")
        falar_aleatorio("spotify_pause")
    else:
        _spotify_api("put", "/me/player/play")
        falar_aleatorio("spotify_play")

def spotify_proxima():
    _spotify_api("post", "/me/player/next")
    falar_aleatorio("spotify_proxima")

def spotify_anterior():
    _spotify_api("post", "/me/player/previous")
    falar_aleatorio("spotify_anterior")

def spotify_buscar_e_tocar(query):
    """Busca uma música/artista e toca no Spotify."""
    falar_aleatorio("spotify_buscando")
    token = _spotify_get_token()
    if not token:
        falar_aleatorio("spotify_erro")
        return
    r = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": query, "type": "track", "limit": 1},
        timeout=8
    )
    items = r.json().get("tracks", {}).get("items", [])
    if not items:
        falar(f"Não encontrei nenhuma música com esse nome, Sr. Arthur.")
        return
    faixa = items[0]
    uri = faixa["uri"]
    nome = faixa["name"]
    artista = faixa["artists"][0]["name"]

    # Toca a música no dispositivo ativo
    _spotify_api("put", "/me/player/play", body={"uris": [uri]})
    falar(f"Tocando {nome} de {artista}, Sr. Arthur.")
    log("spotify", f"{nome} — {artista}")

def spotify_volume(nivel):
    """Define o volume do Spotify (0-100)."""
    _spotify_api("put", f"/me/player/volume?volume_percent={nivel}")
    falar(f"Volume do Spotify ajustado para {nivel} por cento, Sr. Arthur.")

def spotify_o_que_esta_tocando():
    r = _spotify_api("get", "/me/player/currently-playing")
    if r and r.status_code == 200:
        data = r.json()
        if data and data.get("item"):
            nome = data["item"]["name"]
            artista = data["item"]["artists"][0]["name"]
            falar(f"Tocando agora: {nome}, de {artista}, Sr. Arthur.")
            log("spotify", f"▶ {nome} — {artista}")
        else:
            falar("Nenhuma música tocando no momento, Sr. Arthur.")
    else:
        falar_aleatorio("spotify_erro")

def spotify_shuffle(ativar=True):
    state = "true" if ativar else "false"
    _spotify_api("put", f"/me/player/shuffle?state={state}")
    if ativar:
        falar("Modo aleatório ativado, Sr. Arthur.")
    else:
        falar("Modo aleatório desativado, Sr. Arthur.")

# ─── Controle do Sistema ──────────────────────────────────────────
def controlar_volume(acao):
    VK_UP   = 0xAF
    VK_DOWN = 0xAE
    VK_MUTE = 0xAD
    EXT = 0x0001
    if acao == "aumentar":
        for _ in range(5):
            ctypes.windll.user32.keybd_event(VK_UP, 0, EXT, 0)
        falar_aleatorio("volume_aumentando")
    elif acao == "diminuir":
        for _ in range(5):
            ctypes.windll.user32.keybd_event(VK_DOWN, 0, EXT, 0)
        falar_aleatorio("volume_diminuindo")
    elif acao == "mudo":
        ctypes.windll.user32.keybd_event(VK_MUTE, 0, EXT, 0)
        falar_aleatorio("volume_mutando")

def minimizar_tudo():
    subprocess.Popen("explorer.exe shell:::{3080F90D-D7AD-11D9-BD98-0000947B0257}", shell=True)
    falar_aleatorio("minimizando")

def tirar_screenshot():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    nome = f"screenshot_{int(time.time())}.png"
    caminho = os.path.join(desktop, nome).replace("\\", "\\\\")
    cmd = (
        'powershell -Command "'
        'Add-Type -AssemblyName System.Windows.Forms,System.Drawing;'
        '$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;'
        '$b=New-Object System.Drawing.Bitmap($s.Width,$s.Height);'
        '$g=[System.Drawing.Graphics]::FromImage($b);'
        '$g.CopyFromScreen(0,0,0,0,$b.Size);'
        f'$b.Save(\'"{caminho}"\');"'
    )
    subprocess.Popen(cmd, shell=True)
    log("acao", f"Screenshot: {nome}")
    falar_aleatorio("captura")

def desligar_pc():
    falar_aleatorio("desligando")
    time.sleep(2)
    subprocess.Popen("shutdown /s /t 5", shell=True)

def reiniciar_pc():
    falar_aleatorio("reiniciando")
    time.sleep(2)
    subprocess.Popen("shutdown /r /t 5", shell=True)

def bloquear_pc():
    ctypes.windll.user32.LockWorkStation()
    falar_aleatorio("bloqueando")

def fechar_app(nome):
    nome = nome.strip()
    if not nome.endswith(".exe"):
        nome_exe = nome + ".exe"
    else:
        nome_exe = nome
    subprocess.Popen(f"taskkill /f /im {nome_exe}", shell=True)
    log("acao", f"Encerrando {nome}")
    falar_aleatorio("tarefa_encerrada")

# ─── Instalação via winget ────────────────────────────────────────
INSTALADORES = {
    "chrome":             "Google.Chrome",
    "google chrome":      "Google.Chrome",
    "firefox":            "Mozilla.Firefox",
    "vlc":                "VideoLAN.VLC",
    "7zip":               "7zip.7zip",
    "winrar":             "RARLab.WinRAR",
    "discord":            "Discord.Discord",
    "steam":              "Valve.Steam",
    "spotify":            "Spotify.Spotify",
    "zoom":               "Zoom.Zoom",
    "vs code":            "Microsoft.VisualStudioCode",
    "vscode":             "Microsoft.VisualStudioCode",
    "visual studio code": "Microsoft.VisualStudioCode",
    "notepad++":          "Notepad++.Notepad++",
    "obs":                "OBSProject.OBSStudio",
    "obs studio":         "OBSProject.OBSStudio",
    "teams":              "Microsoft.Teams",
    "telegram":           "Telegram.TelegramDesktop",
    "whatsapp":           "WhatsApp.WhatsApp",
    "brave":              "Brave.Brave",
    "git":                "Git.Git",
    "python":             "Python.Python.3",
    "node":               "OpenJS.NodeJS",
    "java":               "Oracle.JavaRuntimeEnvironment",
    "malwarebytes":       "Malwarebytes.Malwarebytes",
    "anydesk":            "AnyDeskSoftwareGmbH.AnyDesk",
    "7-zip":              "7zip.7zip",
}

def instalar_app(nome):
    nome = nome.lower().strip()
    pacote = INSTALADORES.get(nome)
    if not pacote:
        falar(f"Não localizo um pacote de instalação para {nome} em meus registros, Sr. Arthur.")
        return
    falar_aleatorio("instalando")
    log("acao", f"Instalando {nome} via winget → {pacote}")
    subprocess.Popen(
        f'start cmd /k "winget install --id={pacote} -e --accept-source-agreements --accept-package-agreements"',
        shell=True
    )

# ─── Mapa de sites ────────────────────────────────────────────────
SITES = {
    "youtube":       "https://www.youtube.com",
    "you tube":      "https://www.youtube.com",
    "blaze":         "https://blaze.bet.br/pt/",
    "bet":           "https://blaze.bet.br/pt/",
    "google":        "https://www.google.com",
    "gmail":         "https://mail.google.com",
    "google drive":  "https://drive.google.com",
    "google docs":   "https://docs.google.com",
    "google maps":   "https://maps.google.com",
    "maps":          "https://maps.google.com",
    "whatsapp":      "https://web.whatsapp.com",
    "instagram":     "https://www.instagram.com",
    "facebook":      "https://www.facebook.com",
    "twitter":       "https://www.twitter.com",
    "x":             "https://www.x.com",
    "tiktok":        "https://www.tiktok.com",
    "netflix":       "https://www.netflix.com",
    "spotify":       "https://open.spotify.com",
    "twitch":        "https://www.twitch.tv",
    "reddit":        "https://www.reddit.com",
    "github":        "https://www.github.com",
    "linkedin":      "https://www.linkedin.com",
    "amazon":        "https://www.amazon.com.br",
    "mercado livre": "https://www.mercadolivre.com.br",
    "nubank":        "https://app.nubank.com.br",
    "chatgpt":       "https://chat.openai.com",
    "claude":        "https://claude.ai",
    "outlook":       "https://outlook.live.com",
    "hotmail":       "https://outlook.live.com",
}

# ─── Mapa de aplicativos ──────────────────────────────────────────
APPS = {
    "chrome":               r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome":        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "brave":                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "firefox":              r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":                 r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "notepad":              "Bloco de notas.exe",
    "bloco de notas":       "Bloco de notas.exe",
    "calculadora":          "calc.exe",
    "explorador":           "explorer.exe",
    "arquivos":             "explorer.exe",
    "paint":                "mspaint.exe",
    "gerenciador de tarefas": "taskmgr.exe",
    "task manager":         "taskmgr.exe",
    "painel de controle":   "control.exe",
    "configurações":        "ms-settings:",
    "cmd":                  "cmd.exe",
    "prompt de comando":    "cmd.exe",
    "powershell":           "powershell.exe",
    "word":                 r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":                r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":           r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "teams":                r"C:\Users\%USERNAME%\AppData\Local\Microsoft\Teams\current\Teams.exe",
    "vlc":                  r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "riot":                 r"C:\Riot Games\Riot Client\RiotClient.exe",
    "steam":                r"C:\Program Files (x86)\Steam\Steam.exe",
    "discord":              r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe",
    "vs code":              r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vscode":               r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "zoom":                 r"C:\Users\%USERNAME%\AppData\Roaming\Zoom\bin\Zoom.exe",
    "winrar":               r"C:\Program Files\WinRAR\WinRAR.exe",
    "spotify":              r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
    "telegram":             r"C:\Users\%USERNAME%\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "obs":                  r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    "whatsapp":             r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe",
}

# ─── Detecção de comandos Spotify ─────────────────────────────────
def detectar_spotify(comando):
    """Verifica se o comando é uma ação do Spotify e executa."""

    # Tocar música específica
    gatilhos_tocar = ["toca ", "tocar ", "coloca ", "play ", "bota "]
    for g in gatilhos_tocar:
        if g in comando:
            query = comando.split(g, 1)[-1].strip()
            # Remove preposições comuns
            for rem in ["no spotify", "a música", "a musica", "o álbum", "o artista"]:
                query = query.replace(rem, "").strip()
            if query:
                spotify_buscar_e_tocar(query)
                return True

    # O que está tocando
    if any(x in comando for x in ["o que está tocando", "que música é essa", "qual música", "qual musica", "o que toca"]):
        spotify_o_que_esta_tocando()
        return True

    # Play/Pause
    if any(x in comando for x in ["pausa", "pausar", "pause", "para a música", "para musica"]):
        spotify_play_pause()
        return True
    if any(x in comando for x in ["continua", "continuar", "resume", "despausar", "volta música"]):
        spotify_play_pause()
        return True

    # Próxima / Anterior
    if any(x in comando for x in ["próxima", "proxima", "pula", "pular", "next", "avança música"]):
        spotify_proxima()
        return True
    if any(x in comando for x in ["anterior", "voltar música", "música anterior", "musica anterior"]):
        spotify_anterior()
        return True

    # Shuffle
    if any(x in comando for x in ["modo aleatório", "shuffle", "aleatório", "embaralha"]):
        spotify_shuffle(True)
        return True
    if any(x in comando for x in ["desativa aleatório", "desativa shuffle", "sem aleatório"]):
        spotify_shuffle(False)
        return True

    # Volume Spotify
    import re
    m = re.search(r"volume (?:do spotify|da música).*?(\d+)", comando)
    if m:
        spotify_volume(int(m.group(1)))
        return True

    return False

# ─── Detecção direta de sistema ───────────────────────────────────
KEYWORDS_SISTEMA = {
    ("aumenta", "volume"):        ("volume", "aumentar"),
    ("sobe", "volume"):           ("volume", "aumentar"),
    ("diminui", "volume"):        ("volume", "diminuir"),
    ("abaixa", "volume"):         ("volume", "diminuir"),
    ("muda", "volume"):           ("volume", "mudo"),
    ("silêncio",):                ("volume", "mudo"),
    ("muta",):                    ("volume", "mudo"),
    ("minimiza",):                ("sistema", "minimizar"),
    ("minimizar",):               ("sistema", "minimizar"),
    ("área de trabalho",):        ("sistema", "minimizar"),
    ("print",):                   ("sistema", "screenshot"),
    ("screenshot",):              ("sistema", "screenshot"),
    ("captura de tela",):         ("sistema", "screenshot"),
    ("desliga", "computador"):    ("sistema", "desligar"),
    ("desligar", "pc"):           ("sistema", "desligar"),
    ("reinicia",):                ("sistema", "reiniciar"),
    ("reiniciar",):               ("sistema", "reiniciar"),
    ("bloqueia", "tela"):         ("sistema", "bloquear"),
    ("bloquear", "tela"):         ("sistema", "bloquear"),
}

def detectar_sistema(comando):
    for palavras, (tipo, acao) in KEYWORDS_SISTEMA.items():
        if all(p in comando for p in palavras):
            return tipo, acao
    return None, None

def detectar_instalacao(comando):
    for g in ["instala ", "instalar ", "baixa ", "baixar ", "download de "]:
        if g in comando:
            parte = comando.split(g, 1)[-1].strip()
            for nome in INSTALADORES:
                if nome in parte:
                    return nome
            return parte
    return None

def detectar_fechar(comando):
    for g in ["fecha ", "fechar ", "encerra ", "encerrar ", "mata ", "fecha o ", "fechar o "]:
        if g in comando:
            nome = comando.split(g, 1)[-1].strip()
            for rem in ["o ", "a ", "os "]:
                nome = nome.replace(rem, "").strip()
            return nome
    return None

# ─── LLM (Ollama fallback) ────────────────────────────────────────
def perguntar_ollama(comando):
    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": f"""Você é um assistente de IA que controla o computador Windows.
O usuário disse: "{comando}"
Responda APENAS com uma das opções abaixo, sem nenhuma explicação:

- ABRIR_APP: nome_do_app
- ABRIR_SITE: url_completa_com_https
- INSTALAR: nome_do_app
- FECHAR_APP: nome_do_processo
- VOLUME: aumentar | diminuir | mudo
- SISTEMA: minimizar | screenshot | desligar | reiniciar | bloquear
- SPOTIFY: play_pause | proxima | anterior | o_que_toca
- RESPONDER: resposta curta e direta

Exemplos:
- "abre o youtube" -> ABRIR_SITE: https://www.youtube.com
- "abre o chrome" -> ABRIR_APP: chrome
- "instala o discord" -> INSTALAR: discord
- "fecha o chrome" -> FECHAR_APP: chrome
- "aumenta o volume" -> VOLUME: aumentar
- "minimiza tudo" -> SISTEMA: minimizar
- "tira um print" -> SISTEMA: screenshot
- "próxima música" -> SPOTIFY: proxima
- "que música é essa" -> SPOTIFY: o_que_toca
""",
            "stream": False
        }, timeout=15)
        return r.json()["response"].strip()
    except Exception:
        return ""

# ─── Executar resposta do Ollama ──────────────────────────────────
def executar(acao):
    if "ABRIR_APP:" in acao:
        nome = acao.split("ABRIR_APP:")[-1].strip().lower()
        abrir_app(nome)
    elif "ABRIR_SITE:" in acao:
        url = acao.split("ABRIR_SITE:")[-1].strip()
        if not url.startswith("http"):
            url = "https://" + url
        abrir_site(url)
    elif "INSTALAR:" in acao:
        instalar_app(acao.split("INSTALAR:")[-1].strip().lower())
    elif "FECHAR_APP:" in acao:
        fechar_app(acao.split("FECHAR_APP:")[-1].strip().lower())
    elif "VOLUME:" in acao:
        controlar_volume(acao.split("VOLUME:")[-1].strip().lower())
    elif "SISTEMA:" in acao:
        sub = acao.split("SISTEMA:")[-1].strip().lower()
        executar_sistema(sub)
    elif "SPOTIFY:" in acao:
        sub = acao.split("SPOTIFY:")[-1].strip().lower()
        if sub == "play_pause":  spotify_play_pause()
        elif sub == "proxima":   spotify_proxima()
        elif sub == "anterior":  spotify_anterior()
        elif sub == "o_que_toca":spotify_o_que_esta_tocando()
    elif "RESPONDER:" in acao:
        falar(acao.split("RESPONDER:")[-1].strip())
    else:
        falar_aleatorio("nao_entendi")

def executar_sistema(acao):
    if acao == "minimizar":    minimizar_tudo()
    elif acao == "screenshot": tirar_screenshot()
    elif acao == "desligar":   desligar_pc()
    elif acao == "reiniciar":  reiniciar_pc()
    elif acao == "bloquear":   bloquear_pc()

def abrir_site(url, nome="o endereço"):
    webbrowser.open(url)
    log("acao", f"Abrindo {url}")
    falar(f"{random.choice(FALAS['site_abrindo'])}")

def abrir_app(nome):
    nome_l = nome.lower().strip()
    if nome_l in SITES:
        abrir_site(SITES[nome_l], nome_l)
        return
    caminho = APPS.get(nome_l)
    if not caminho:
        subprocess.Popen(nome_l, shell=True)
        falar(f"Tentando inicializar {nome_l}, Sr. Arthur. Se não responder, verifique se está instalado.")
        return
    caminho = os.path.expandvars(caminho)
    if caminho.endswith(":"):
        subprocess.Popen(f"start {caminho}", shell=True)
    else:
        subprocess.Popen(caminho, shell=True)
    log("acao", f"Iniciando {nome_l}")
    falar_aleatorio("app_abrindo")

# ─── Detecção local unificada ─────────────────────────────────────
def detectar_direto(comando):
    # 1. Spotify
    if detectar_spotify(comando):
        return True
    # 2. Fechar app
    nome_fechar = detectar_fechar(comando)
    if nome_fechar:
        fechar_app(nome_fechar)
        return True
    # 3. Instalar
    nome_instalar = detectar_instalacao(comando)
    if nome_instalar:
        instalar_app(nome_instalar)
        return True
    # 4. Sistema
    tipo, acao = detectar_sistema(comando)
    if tipo == "volume":
        controlar_volume(acao)
        return True
    if tipo == "sistema":
        executar_sistema(acao)
        return True
    # 5. Sites conhecidos
    for nome, url in SITES.items():
        if nome in comando:
            abrir_site(url, nome)
            return True
    return False

# ══════════════════════════════════════════════════════════════════
#  INICIALIZAÇÃO
# ══════════════════════════════════════════════════════════════════
banner()

# Verifica credenciais do Spotify
if SPOTIFY_CLIENT_ID == "SEU_CLIENT_ID_AQUI":
    print(f"{YELLOW}  ⚠  Spotify não configurado. Edite SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET.{RESET}")
    print(f"{DIM}     Acesse: https://developer.spotify.com/dashboard{RESET}\n")
else:
    # Carrega token salvo ou pede autorização
    if not _spotify_user_token_load():
        print(f"{CYAN}  ♪  Primeira execução: autorização do Spotify necessária...{RESET}")
        time.sleep(1)
        spotify_autorizar()
    else:
        log("acao", "Token Spotify carregado com sucesso.")

falar("Sistemas operacionais, Sr. Arthur. Odin em pleno funcionamento. Aguardando sua palavra-chave.")

# ─── Loop principal ───────────────────────────────────────────────
while True:
    try:
        aguardar_palavra_chave()
        log("ativado", "Palavra-chave detectada.")
        falar_aleatorio("ativado")

        comando = ouvir_comando()

        if not comando.strip():
            falar_aleatorio("nao_ouvi")
            continue

        if any(p in comando for p in ["sair", "encerrar", "tchau", "desativar", "desativa", "até logo"]):
            falar_aleatorio("despedida")
            break

        if not detectar_direto(comando):
            acao = perguntar_ollama(comando)
            if acao:
                executar(acao)
            else:
                falar_aleatorio("nao_entendi")

        print(f"{DIM}  {'─' * 45}{RESET}")

    except KeyboardInterrupt:
        print(f"\n{DIM}  Encerrando protocolos...{RESET}\n")
        falar("Encerrando. Até logo, Sr. Arthur.")
        break