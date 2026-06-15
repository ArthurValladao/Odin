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

# ─── Cores para o terminal ───────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
PURPLE = "\033[95m"
DIM    = "\033[2m"

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    limpar()
    print(f"{PURPLE}{BOLD}")
    print("  ██████╗ ██████╗ ██╗███╗   ██╗")
    print("██╔═══██╗██╔══██╗██║████╗  ██║")
    print("██║   ██║██║  ██║██║████╗  ██║")
    print("██║   ██║██║  ██║██║██╔██╗ ██║")
    print("██║   ██║██║  ██║██║██║╚██╗██║")
    print("╚██████╔╝██████╔╝██║██║ ╚████║")
    print(" ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝")
    print(f"{RESET}{DIM}  Assistente de voz local · diga 'Odin' para ativar{RESET}")
    print(f"{CYAN}{'─' * 45}{RESET}\n")

def log(tipo, mensagem):
    if tipo == "escutando":
        print(f"{DIM}  👂 {mensagem}{RESET}")
    elif tipo == "ativado":
        print(f"\n{GREEN}{BOLD}  ⚡ {mensagem}{RESET}")
    elif tipo == "usuario":
        print(f"{CYAN}  🎙  Você: {BOLD}{mensagem}{RESET}")
    elif tipo == "agente":
        print(f"{YELLOW}  🤖 Odin: {BOLD}{mensagem}{RESET}")
    elif tipo == "erro":
        print(f"{RED}  ✗ {mensagem}{RESET}")
    elif tipo == "acao":
        print(f"{GREEN}  ✓ {mensagem}{RESET}")

# ─── Voz ─────────────────────────────────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty("rate", 170)

def falar(texto):
    log("agente", texto)
    engine.say(texto)
    engine.runAndWait()

# ─── Reconhecimento de voz ───────────────────────────────────────────────────
recognizer = sr.Recognizer()

def gravar(duracao=10):
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
        log("erro", "Sem conexão com o Google")
        return ""

def aguardar_palavra_chave():
    log("escutando", "Aguardando 'Odin'...")
    while True:
        audio = gravar(duracao=4)
        texto = transcrever(audio)
        if "odin" in texto:
            return True

def ouvir_comando():
    log("escutando", "Ouvindo comando...")
    audio = gravar(duracao=10)
    texto = transcrever(audio)
    if texto:
        log("usuario", texto)
    return texto

# ─── LLM ─────────────────────────────────────────────────────────────────────
def perguntar_ollama(comando):
    try:
        resposta = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": f"""Você é um assistente que controla o computador Windows.
O usuário disse: "{comando}"
Responda APENAS com uma dessas opções, sem explicações extras:
- ABRIR_APP: nome_do_app
- ABRIR_SITE: url_completa_com_https
- RESPONDER: sua resposta curta

Exemplos:
- "abre o youtube" -> ABRIR_SITE: https://www.youtube.com
- "abre o google" -> ABRIR_SITE: https://www.google.com
- "abre o chrome" -> ABRIR_APP: chrome
- "que horas são" -> RESPONDER: não tenho acesso ao relógio
""",
            "stream": False
        }, timeout=15)
        return resposta.json()["response"].strip()
    except Exception:
        log("erro", "Não consegui conectar ao Ollama")
        return ""

# ─── Mapa de sites (garante abertura mesmo se o Ollama errar) ────────────────
SITES = {
    "youtube":        "https://www.youtube.com",
    "you tube":       "https://www.youtube.com",
    "google":         "https://www.google.com",
    "gmail":          "https://mail.google.com",
    "google drive":   "https://drive.google.com",
    "google docs":    "https://docs.google.com",
    "google maps":    "https://maps.google.com",
    "maps":           "https://maps.google.com",
    "whatsapp":       "https://web.whatsapp.com",
    "whats app":      "https://web.whatsapp.com",
    "instagram":      "https://www.instagram.com",
    "facebook":       "https://www.facebook.com",
    "twitter":        "https://www.twitter.com",
    "x":              "https://www.x.com",
    "tiktok":         "https://www.tiktok.com",
    "netflix":        "https://www.netflix.com",
    "spotify":        "https://open.spotify.com",
    "twitch":         "https://www.twitch.tv",
    "reddit":         "https://www.reddit.com",
    "github":         "https://www.github.com",
    "linkedin":       "https://www.linkedin.com",
    "amazon":         "https://www.amazon.com.br",
    "mercado livre":  "https://www.mercadolivre.com.br",
    "mercadolivre":   "https://www.mercadolivre.com.br",
    "nubank":         "https://app.nubank.com.br",
    "chatgpt":        "https://chat.openai.com",
    "claude":         "https://claude.ai",
    "bing":           "https://www.bing.com",
    "outlook":        "https://outlook.live.com",
    "hotmail":        "https://outlook.live.com",
}

# ─── Mapa de aplicativos (Windows 10) ────────────────────────────────────────
APPS = {
    # Navegadores
    "chrome":               r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome":        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "navegador":            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":              r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "mozilla":              r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":                 r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "microsoft edge":       r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",

    # Ferramentas do sistema
    "notepad":              "notepad.exe",
    "bloco de notas":       "notepad.exe",
    "calculadora":          "calc.exe",
    "calc":                 "calc.exe",
    "explorador":           "explorer.exe",
    "explorador de arquivos": "explorer.exe",
    "arquivos":             "explorer.exe",
    "paint":                "mspaint.exe",
    "wordpad":              "wordpad.exe",
    "word pad":             "wordpad.exe",
    "gerenciador de tarefas": "taskmgr.exe",
    "task manager":         "taskmgr.exe",
    "painel de controle":   "control.exe",
    "configuracoes":        "ms-settings:",
    "configurações":        "ms-settings:",
    "prompt de comando":    "cmd.exe",
    "cmd":                  "cmd.exe",
    "powershell":           "powershell.exe",
    "recorte":              "snippingtool.exe",
    "ferramenta de captura": "snippingtool.exe",

    # Microsoft Office
    "word":                 r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "microsoft word":       r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":                r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "microsoft excel":      r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":           r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "power point":          r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "microsoft powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "teams":                r"C:\Users\%USERNAME%\AppData\Local\Microsoft\Teams\current\Teams.exe",
    "microsoft teams":      r"C:\Users\%USERNAME%\AppData\Local\Microsoft\Teams\current\Teams.exe",

    # Multimídia
    "vlc":                  r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "media player":         "wmplayer.exe",
    "windows media player": "wmplayer.exe",

    # Outros
    "steam":                r"C:\Program Files (x86)\Steam\Steam.exe",
    "discord":              r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe",
    "vs code":              r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code":   r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vscode":               r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "zoom":                 r"C:\Users\%USERNAME%\AppData\Roaming\Zoom\bin\Zoom.exe",
    "winrar":               r"C:\Program Files\WinRAR\WinRAR.exe",
    "7zip":                 r"C:\Program Files\7-Zip\7zFM.exe",
}

def abrir_site(url):
    webbrowser.open(url)
    log("acao", f"Abrindo {url}")
    falar("Abrindo o site")

def abrir_app(nome):
    nome = nome.lower().strip()

    # Verifica se é um site no mapa de sites
    if nome in SITES:
        abrir_site(SITES[nome])
        return

    caminho = APPS.get(nome)

    if not caminho:
        log("acao", f"Tentando abrir '{nome}' diretamente...")
        subprocess.Popen(nome, shell=True)
        falar(f"Tentando abrir {nome}")
        return

    caminho = os.path.expandvars(caminho)

    if caminho.endswith(":"):
        subprocess.Popen(f'start {caminho}', shell=True)
    else:
        subprocess.Popen(caminho, shell=True)

    log("acao", f"Abrindo {nome}")
    falar(f"Abrindo {nome}")

# ─── Execução de ações ───────────────────────────────────────────────────────
def executar(acao):
    if "ABRIR_APP:" in acao:
        nome = acao.split("ABRIR_APP:")[-1].strip().lower()
        # Verifica se o Ollama mandou um site disfarçado de app
        if nome in SITES:
            abrir_site(SITES[nome])
        else:
            abrir_app(nome)

    elif "ABRIR_SITE:" in acao:
        url = acao.split("ABRIR_SITE:")[-1].strip()
        # Garante que a URL tenha https://
        if not url.startswith("http"):
            url = "https://" + url
        abrir_site(url)

    elif "RESPONDER:" in acao:
        resposta = acao.split("RESPONDER:")[-1].strip()
        falar(resposta)

    else:
        falar("Não entendi o que fazer")

# ─── Detecção direta de sites (sem depender do Ollama) ───────────────────────
def detectar_site_direto(comando):
    """Se o usuário mencionar um site conhecido, abre direto sem passar pelo Ollama."""
    for nome, url in SITES.items():
        if nome in comando:
            abrir_site(url)
            return True
    return False

# ─── Loop principal ───────────────────────────────────────────────────────────
banner()
falar("Odin pronto. Me chame pelo nome para começar.")

while True:
    try:
        aguardar_palavra_chave()
        log("ativado", "Ativado! Pode falar o comando.")
        falar("Oi! O que você quer?")

        comando = ouvir_comando()
        if not comando.strip():
            falar("Não ouvi nada. Me chame de novo quando precisar.")
            continue
        if "sair" in comando or "encerrar" in comando:
            falar("Encerrando. Até logo!")
            break

        # Tenta detectar site direto antes de chamar o Ollama
        if not detectar_site_direto(comando):
            acao = perguntar_ollama(comando)
            if acao:
                executar(acao)

        print(f"{DIM}{'─' * 45}{RESET}")

    except KeyboardInterrupt:
        print(f"\n{DIM}  Encerrando...{RESET}\n")
        break