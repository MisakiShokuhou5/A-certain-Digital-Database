import os
import subprocess
import shutil
import sys
import urllib.request
import winreg
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def git_instalado():
    return shutil.which("git") is not None

def adicionar_git_ao_path(git_path):
    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        )
        path_value, _ = winreg.QueryValueEx(reg_key, "Path")
        if git_path not in path_value:
            novo_path = f"{path_value};{git_path}"
            winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, novo_path)
            print("🔧 Git adicionado ao PATH. Você precisará reiniciar o terminal.")
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"❌ Erro ao modificar o PATH: {e}")
        sys.exit(1)

def instalar_git():
    print("⬇️ Baixando Git para Windows...")
    url = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
    instalador = os.path.join(os.getenv("TEMP"), "git_installer.exe")
    urllib.request.urlretrieve(url, instalador)
    print("📥 Instalador baixado com sucesso.")

    print("🔧 Instalando Git de forma silenciosa...")
    try:
        subprocess.run([instalador, "/VERYSILENT", "/NORESTART", "/SUPPRESSMSGBOXES"], check=True)
        print("✅ Git instalado com sucesso.")
    except subprocess.CalledProcessError as e:
        print("❌ Falha na instalação do Git:", e)
        sys.exit(1)

    # Caminho padrão onde o Git se instala
    git_bin_path = r"C:\Program Files\Git\cmd"
    if os.path.exists(git_bin_path):
        adicionar_git_ao_path(git_bin_path)
    else:
        print("⚠️ Git instalado, mas o caminho não foi encontrado para adicionar ao PATH.")

def executar_comando(comando):
    try:
        subprocess.run(comando, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {' '.join(comando)}")
        print(e)
        sys.exit(1)

def configurar_git_global():
    print("⚙️ Configurando nome e email do Git...")
    nome = input("Digite seu nome: ").strip()
    email = input("Digite seu email: ").strip()
    if nome and email:
        executar_comando(["git", "config", "--global", "user.name", nome])
        executar_comando(["git", "config", "--global", "user.email", email])
    else:
        print("⚠️ Nome ou email inválido. Abortando.")
        sys.exit(1)

def main():
    print("=== Atualizador de Projeto GitHub COMPLETO ===")

    if not is_admin():
        print("❌ Este script precisa ser executado como administrador.")
        print("➡️ Clique com o botão direito e escolha 'Executar como administrador'.")
        sys.exit(1)

    if not git_instalado():
        instalar_git()
        if not git_instalado():
            print("❌ Git não foi detectado mesmo após a instalação.")
            sys.exit(1)

    projeto_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(projeto_path)
    print(f"📁 Projeto: {projeto_path}")

    # Configuração do Git se não estiver feita
    resultado = subprocess.run(["git", "config", "--global", "user.name"], capture_output=True, text=True)
    if resultado.returncode != 0 or not resultado.stdout.strip():
        configurar_git_global()

    # Inicializar repositório se não existir
    if not os.path.exists(os.path.join(projeto_path, ".git")):
        print("🔧 Inicializando repositório Git...")
        executar_comando(["git", "init"])
        executar_comando(["git", "remote", "add", "origin", "https://github.com/MisakiShokuhou5/A-certain-Digital-Database.git"])

    executar_comando(["git", "add", "."])

    mensagem = input("📝 Digite a mensagem do commit: ").strip()
    if not mensagem:
        print("⚠️ Mensagem de commit vazia. Abortando.")
        return

    executar_comando(["git", "commit", "-m", mensagem])
    executar_comando(["git", "branch", "-M", "main"])
    executar_comando(["git", "push", "-u", "origin", "main"])

    print("✅ Projeto atualizado com sucesso no GitHub!")

if __name__ == "__main__":
    main()