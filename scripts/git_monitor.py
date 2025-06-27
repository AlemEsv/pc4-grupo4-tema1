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

#hash del commit local  
def get_local_commit():
    out, err = run_cmd("git rev-parse HEAD", cwd=REPO_DIR)
    return out

#hash del último commit remoto 
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

        if current_remote != local_commit:
            print(f"\nNuevo commit detectado:")
            print(f"Remoto: {current_remote}")
            print(f"Local:  {local_commit}")

            print("\nEjecutando git pull...")
            out, err = run_cmd("git pull", cwd=REPO_DIR)
            print(out or err)

            print("\n Aplicando manifiestos de Kubernetes...")
            manifests_dir = os.path.join(REPO_DIR, "manifests")

            deploy_out, deploy_err = run_cmd("kubectl apply -f deployment.yaml", cwd=manifests_dir)
            print(deploy_out or deploy_err)

            service_out, service_err = run_cmd("kubectl apply -f service.yaml", cwd=manifests_dir)
            print(service_out or service_err)

            print("Se aplicaron los manifiestos correctamente.")
        else:
            print("Sin nuevos commits.")

if __name__ == "__main__":
    monitor_repo()
