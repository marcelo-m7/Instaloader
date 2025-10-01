#!/usr/bin/env python3
"""
baixar_instagram.py
Baixa todas as imagens (melhor resolução disponível) de um perfil público do Instagram.

Uso:
    python baixar_instagram.py <username>

Dependência:
    pip install instaloader
"""

import sys
import os
import time
from typing import Optional

try:
    import instaloader
except ImportError:
    print("Instaloader não encontrado. Rode: pip install instaloader")
    sys.exit(1)


def download_profile_images(username: str,
                            dest_dir: Optional[str] = None,
                            login_user: Optional[str] = None,
                            login_pass: Optional[str] = None,
                            wait_between: float = 5.0):
    """
    Baixa imagens de um perfil público do Instagram usando instaloader.

    - username: nome do perfil (ex: 'marcelo.santos.77')
    - dest_dir: pasta base para salvar (por padrão ./<username>/)
    - login_user, login_pass: opcional, credenciais para autenticar (reduz bloqueios / acessa privados permitidos)
    - wait_between: pausa em segundos entre downloads para reduzir chance de rate-limit
    """
    L = instaloader.Instaloader(
        dirname_pattern=dest_dir or "{target}",  # pasta onde salvar (substitui {target} pelo username)
        download_videos=False,                   # não baixar vídeos (apenas imagens)
        download_video_thumbnails=False,
        save_metadata=True,                      # salva metadata JSON e descrição
        post_metadata_txt_pattern=None,          # evita criar .txt com legenda (opcional)
        compress_json=False,
        max_connection_attempts=3
    )

    # Opcional: efetuar login (melhora limites e acesso a perfis privados que você tenha permissão)
    if login_user and login_pass:
        try:
            L.login(login_user, login_pass)
            print(f"[+] Logado como {login_user}")
        except Exception as e:
            print("[!] Falha no login:", e)
            print("[!] Continuando sem login — poderá falhar em perfis privados ou sofrer rate-limits.")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"[ERROR] Perfil '{username}' não existe.")
        return
    except Exception as e:
        print("[ERROR] Não foi possível obter informações do perfil:", e)
        return

    print(f"[+] Iniciando download de posts do perfil: {profile.username}")
    print(f"    total de posts estimado: {profile.mediacount}")
    print(f"    perfil público: {not profile.is_private}")

    target = profile.username
    # cria pasta se não existir (instaloader já faz, mas garantimos)
    os.makedirs(target, exist_ok=True)

    count = 0
    try:
        for post in profile.get_posts():
            # ignora vídeos (post.is_video) e baixa somente imagens (inclui carrossel com imagens)
            if post.is_video:
                print(f" - pulando vídeo: {post.shortcode}")
                continue

            # instaloader detecta e baixa cada item do post (para carrossel baixa várias imagens)
            try:
                L.download_post(post, target=target)
                count += 1
                print(f" - baixado post {post.shortcode} (#{count})")
            except Exception as e:
                print(f" [!] erro ao baixar post {post.shortcode}: {e}")

            time.sleep(wait_between)
    except KeyboardInterrupt:
        print("\n[!] Interrompido pelo usuário.")
    except Exception as e:
        print("[!] Erro durante iteração de posts:", e)

    print(f"[+] Finalizado. Posts processados (tentativas de download de posts com imagens): {count}")
    print(f"[+] Arquivos salvos em: ./{target}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python baixar_instagram.py <username> [login_user login_pass]")
        sys.exit(1)

    usr = sys.argv[1]
    login_u = sys.argv[2] if len(sys.argv) >= 4 else None
    login_p = sys.argv[3] if len(sys.argv) >= 4 else None

    download_profile_images(usr, login_user=login_u, login_pass=login_p)
