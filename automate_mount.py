import os
import re
import sys
import winreg
import shutil
import argparse
from datetime import datetime

def get_steam_path():
    """Tenta obter o caminho do Steam a partir do registro do Windows."""
    # 1. HKEY_CURRENT_USER
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        if os.path.isdir(path):
            return os.path.normpath(path)
    except Exception:
        pass
        
    # 2. HKEY_LOCAL_MACHINE
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam")
        path, _ = winreg.QueryValueEx(key, "InstallPath")
        winreg.CloseKey(key)
        if os.path.isdir(path):
            return os.path.normpath(path)
    except Exception:
        pass

    # 3. Caminho padrão
    default_path = r"C:\Program Files (x86)\Steam"
    if os.path.isdir(default_path):
        return os.path.normpath(default_path)

    return None

def get_library_paths(steam_path):
    """Lê o arquivo libraryfolders.vdf para encontrar todas as bibliotecas da Steam."""
    paths = []
    if steam_path:
        paths.append(steam_path)
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            try:
                with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Encontra caminhos no formato "path" "D:\\SteamLibrary"
                matches = re.findall(r'"path"\s+"([^"]+)"', content)
                for path in matches:
                    clean_path = path.replace("\\\\", "\\")
                    normalized = os.path.normpath(clean_path)
                    if os.path.isdir(normalized) and normalized not in paths:
                        paths.append(normalized)
            except Exception as e:
                print(f"[-] Aviso: Não foi possível ler libraryfolders.vdf: {e}")
    return paths

def find_game_paths(library_paths):
    """Varre as bibliotecas para encontrar Garry's Mod e Black Mesa."""
    gmod_path = None
    bms_path = None
    
    for lib in library_paths:
        gmod_check = os.path.join(lib, "steamapps", "common", "GarrysMod")
        if os.path.isdir(gmod_check):
            gmod_path = os.path.normpath(gmod_check)
            
        bms_check = os.path.join(lib, "steamapps", "common", "Black Mesa")
        if os.path.isdir(bms_check):
            bms_path = os.path.normpath(bms_check)
            
    return gmod_path, bms_path

def get_valid_directory(prompt, default_val=None):
    """Pede ao usuário um diretório válido de forma interativa."""
    if default_val:
        full_prompt = f"{prompt} [{default_val}]: "
    else:
        full_prompt = f"{prompt}: "
        
    while True:
        val = input(full_prompt).strip()
        if not val and default_val:
            return default_val
        val = val.strip('"\'')
        if os.path.isdir(val):
            return os.path.normpath(val)
        print(f"[-] Erro: O diretório '{val}' não existe. Tente novamente.")

def update_mount_cfg_content(content, bms_path_bms):
    """Atualiza o conteúdo de mount.cfg inserindo ou modificando a chave 'bms'."""
    lines = content.splitlines()
    bms_entry_found = False
    inside_mountcfg = False
    bracket_depth = 0
    new_lines = []
    
    # Normaliza o caminho com barras invertidas normais
    bms_path_bms = os.path.normpath(bms_path_bms)
    
    for line in lines:
        stripped = line.strip()
        
        # Detecta início do bloco mountcfg
        if stripped.lower() == '"mountcfg"':
            inside_mountcfg = True
            new_lines.append(line)
            continue
            
        if inside_mountcfg:
            if '{' in stripped:
                bracket_depth += 1
                new_lines.append(line)
                continue
            if '}' in stripped:
                bracket_depth -= 1
                if bracket_depth == 0:
                    # Saindo do bloco mountcfg. Se o "bms" não foi adicionado, insere antes de fechar.
                    if not bms_entry_found:
                        new_lines.append(f'    "bms"    "{bms_path_bms}"')
                        bms_entry_found = True
                    inside_mountcfg = False
                new_lines.append(line)
                continue
                
            # Verifica se é uma linha ativa de "bms"
            match = re.match(r'^(\s*)"bms"\s+"([^"]*)"', line)
            if match and not stripped.startswith('//'):
                indent = match.group(1)
                new_lines.append(f'{indent}"bms"    "{bms_path_bms}"')
                bms_entry_found = True
                continue
                
        new_lines.append(line)
        
    if not bms_entry_found:
        # Caso o bloco "mountcfg" não exista ou esteja corrompido, reconstrói
        return f'"mountcfg"\n{{\n    "bms"    "{bms_path_bms}"\n}}\n'
        
    return "\n".join(new_lines) + "\n"

def handle_stabilization(bms_content_path, action, dry_run=False):
    """Renomeia ou restaura pastas conflitantes no diretório bms do Black Mesa para evitar crashes."""
    particles_path = os.path.join(bms_content_path, "particles")
    particles_backup = os.path.join(bms_content_path, "_particles_backup")
    scripts_path = os.path.join(bms_content_path, "scripts")
    scripts_backup = os.path.join(bms_content_path, "_scripts_backup")

    if action == 'stabilize':
        # Particles
        if os.path.isdir(particles_path):
            print(f"[i] Estabilização: Desativando pasta de partículas conflitantes...")
            if not dry_run:
                try:
                    os.rename(particles_path, particles_backup)
                    print(f"[+] Pasta 'particles' renomeada para '_particles_backup'")
                except Exception as e:
                    print(f"[-] Erro ao renomear pasta 'particles': {e}")
        elif os.path.isdir(particles_backup):
            print(f"[i] Estabilização: Pasta 'particles' já está desativada ('_particles_backup').")

        # Scripts
        if os.path.isdir(scripts_path):
            print(f"[i] Estabilização: Desativando pasta de scripts conflitantes...")
            if not dry_run:
                try:
                    os.rename(scripts_path, scripts_backup)
                    print(f"[+] Pasta 'scripts' renomeada para '_scripts_backup'")
                except Exception as e:
                    print(f"[-] Erro ao renomear pasta 'scripts': {e}")
        elif os.path.isdir(scripts_backup):
            print(f"[i] Estabilização: Pasta 'scripts' já está desativada ('_scripts_backup').")

    elif action == 'restore':
        # Particles
        if os.path.isdir(particles_backup):
            print(f"[i] Restauração: Ativando pasta de partículas do Black Mesa...")
            if not dry_run:
                try:
                    os.rename(particles_backup, particles_path)
                    print(f"[+] Pasta '_particles_backup' restaurada para 'particles'")
                except Exception as e:
                    print(f"[-] Erro ao restaurar pasta 'particles': {e}")
        elif os.path.isdir(particles_path):
            print(f"[i] Restauração: Pasta 'particles' já está no estado original.")

        # Scripts
        if os.path.isdir(scripts_backup):
            print(f"[i] Restauração: Ativando pasta de scripts do Black Mesa...")
            if not dry_run:
                try:
                    os.rename(scripts_backup, scripts_path)
                    print(f"[+] Pasta '_scripts_backup' restaurada para 'scripts'")
                except Exception as e:
                    print(f"[-] Erro ao restaurar pasta 'scripts': {e}")
        elif os.path.isdir(scripts_path):
            print(f"[i] Restauração: Pasta 'scripts' já está no estado original.")

def main():
    parser = argparse.ArgumentParser(description="Automatiza a montagem de assets do Black Mesa no Garry's Mod.")
    parser.add_argument("--gmod-path", help="Caminho raiz do Garry's Mod (onde fica a pasta garrysmod)")
    parser.add_argument("--bms-path", help="Caminho raiz do Black Mesa (onde fica a pasta bms)")
    parser.add_argument("--non-interactive", action="store_true", help="Não faz perguntas interativas. Falha se caminhos não forem achados.")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simula as mudanças sem modificar arquivos.")
    parser.add_argument("--stabilize", action="store_true", help="Renomeia pastas conflitantes (particles e scripts) no Black Mesa para evitar crashes.")
    parser.add_argument("--restore", action="store_true", help="Restaura as pastas conflitantes do Black Mesa para o estado original.")
    
    args = parser.parse_args()
    
    print("==========================================================")
    print("  Garry's Mod - Auto-Mounter para Black Mesa")
    print("==========================================================")
    
    # 1. Descobrir caminhos do Steam e jogos
    steam_path = get_steam_path()
    libs = get_library_paths(steam_path)
    auto_gmod, auto_bms = find_game_paths(libs)
    
    # Determinar caminho final do Garry's Mod
    gmod_path = args.gmod_path
    if not gmod_path:
        if auto_gmod:
            if args.non_interactive:
                gmod_path = auto_gmod
            else:
                gmod_path = get_valid_directory("[+] Garry's Mod encontrado automaticamente. Confirme ou digite outro caminho", auto_gmod)
        else:
            if args.non_interactive:
                print("[-] Erro: Garry's Mod não encontrado e a execução está em modo não-interativo.")
                sys.exit(1)
            gmod_path = get_valid_directory("[+] Digite o caminho raiz do Garry's Mod (ex: C:\\Program Files (x86)\\Steam\\steamapps\\common\\GarrysMod)")

    # Determinar caminho final do Black Mesa
    bms_path = args.bms_path
    if not bms_path:
        if auto_bms:
            if args.non_interactive:
                bms_path = auto_bms
            else:
                bms_path = get_valid_directory("[+] Black Mesa encontrado automaticamente. Confirme ou digite outro caminho", auto_bms)
        else:
            if args.non_interactive:
                print("[-] Erro: Black Mesa não encontrado e a execução está em modo não-interativo.")
                sys.exit(1)
            bms_path = get_valid_directory("[+] Digite o caminho raiz do Black Mesa (ex: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Black Mesa)")

    # 2. Validar caminhos de configuração e pasta bms
    mount_cfg_path = os.path.normpath(os.path.join(gmod_path, "garrysmod", "cfg", "mount.cfg"))
    bms_content_path = os.path.normpath(os.path.join(bms_path, "bms"))
    
    print(f"\n[i] Garry's Mod: {gmod_path}")
    print(f"[i] Black Mesa: {bms_path}")
    print(f"[i] Arquivo destino: {mount_cfg_path}")
    print(f"[i] Pasta de assets a montar: {bms_content_path}")
    
    if not os.path.isdir(bms_content_path):
        print(f"[-] Erro: A pasta de assets '{bms_content_path}' não existe. Verifique se o Black Mesa está instalado corretamente.")
        sys.exit(1)

    # Se a flag --restore for definida, faz a restauração das pastas e encerra ou prossegue
    if args.restore:
        print("\n--- Restauração de pastas conflitantes do Black Mesa ---")
        handle_stabilization(bms_content_path, 'restore', args.dry_run)
        print("\n[+] Restauração concluída!")
        if args.dry_run:
            sys.exit(0)
        
    if not os.path.exists(mount_cfg_path):
        if args.non_interactive or args.dry_run:
            print(f"[-] Erro: O arquivo '{mount_cfg_path}' não foi encontrado.")
            sys.exit(1)
        # Tenta criar a pasta cfg e o arquivo se não existirem
        print(f"[!] Aviso: {mount_cfg_path} não existe. Deseja criá-lo?")
        confirm = input("Confirmar criação? (s/n): ").strip().lower()
        if confirm != 's':
            print("[-] Cancelado pelo usuário.")
            sys.exit(1)
        os.makedirs(os.path.dirname(mount_cfg_path), exist_ok=True)
        with open(mount_cfg_path, "w", encoding="utf-8") as f:
            f.write('"mountcfg"\n{\n}\n')

    # 3. Ler mount.cfg
    try:
        with open(mount_cfg_path, "r", encoding="utf-8", errors="ignore") as f:
            old_content = f.read()
    except Exception as e:
        print(f"[-] Erro ao ler mount.cfg: {e}")
        sys.exit(1)
        
    # 4. Modificar o conteúdo
    new_content = update_mount_cfg_content(old_content, bms_content_path)
    
    print("\n--- Mudanças planejadas no mount.cfg ---")
    # Mostrar um diff básico das linhas modificadas/inseridas
    print("[+] Linha configurada:")
    print(f'    "bms"    "{bms_content_path}"')
    print("----------------------------------------")
    
    if args.dry_run:
        print("\n[i] Modo Simulação (--dry-run). Nenhuma alteração foi gravada.")
        sys.exit(0)
        
    if not args.non_interactive:
        confirm = input("\nDeseja aplicar essas alterações? (s/n): ").strip().lower()
        if confirm != 's':
            print("[-] Cancelado pelo usuário.")
            sys.exit(0)
            
    # 5. Criar backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{mount_cfg_path}.{timestamp}.bak"
    try:
        shutil.copy2(mount_cfg_path, backup_path)
        print(f"[+] Backup criado com sucesso: {backup_path}")
    except Exception as e:
        print(f"[-] Erro ao criar backup: {e}. Abortando alteração por segurança.")
        sys.exit(1)
        
    # 6. Gravar novo conteúdo
    try:
        with open(mount_cfg_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("[+] Arquivo mount.cfg atualizado com sucesso!")
        
        # Otimização de Estabilização
        print("\n==========================================================")
        print("  Estabilização e Prevenção de Crashes (Isolamento)")
        print("==========================================================")
        
        do_stabilize = False
        if not args.restore:
            if args.stabilize:
                do_stabilize = True
            elif not args.non_interactive:
                print("\n[?] Deseja desativar temporariamente as pastas de partículas e scripts conflitantes do Black Mesa?")
                print("    (Altamente recomendado para evitar Crashes to Desktop (CTD) no GMod)")
                confirm = input("Confirmar otimização? (s/n): ").strip().lower()
                if confirm == 's':
                    do_stabilize = True
        
        if do_stabilize:
            handle_stabilization(bms_content_path, 'stabilize', args.dry_run)
            
        print("\nPronto! Lembre-se de rodar o Garry's Mod na branch x86-64.")
        print("Parâmetros de inicialização sugeridos para maior estabilidade:")
        print("  -systemalloc -heapsize 4194304 -mat_queue_mode 2 -gmod_mcore")
    except Exception as e:
        print(f"[-] Erro ao gravar alterações no mount.cfg: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
