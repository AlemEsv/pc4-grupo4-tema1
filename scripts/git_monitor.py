import os
import time
import subprocess

REPO_DIR = "../../app-manifests"
BRANCH = "main"
CHECK_INTERVAL = 10  # verifica cada 10 segundos

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, shell=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.strip(), result.stderr.strip()

#hash del commit actual 
def get_local_commit():
    out, err = run_cmd("git rev-parse HEAD", cwd=REPO_DIR)
    return out

#hash del último commit 
def get_remote_commit():
    cmd = f"git ls-remote origin refs/heads/{BRANCH}"
    out, err = run_cmd(cmd, cwd=REPO_DIR)
    return out.split('\t')[0] if out else None

#mostrar si hay nuevos commit
def monitor_repo():
    if not os.path.isdir(REPO_DIR):
        print(f"Error: No se encontró el directorio '{REPO_DIR}'")
        return

    print(f"Monitoreando cambios en la rama '{BRANCH}' del repositorio en: {REPO_DIR}")
    
    last_remote_commit = get_remote_commit()
    print("Commit remoto inicial:", last_remote_commit)

    while True:
        time.sleep(CHECK_INTERVAL)

        current_remote = get_remote_commit()
        local_commit = get_local_commit()

        # Compara los commits
        if current_remote != local_commit:
            print(f"\nNuevo commit disponible: {current_remote}")
            print(f"Commit local actual: {local_commit}")
        else:
            print("Sin nuevos commits en la rama principal")

if __name__ == "__main__":
    monitor_repo()
