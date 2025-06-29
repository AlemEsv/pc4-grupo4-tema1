import os
import time
import subprocess

REPO_DIR = "../../app-manifests"
BRANCH = "main"
CHECK_INTERVAL = 30  # verifica cada 10 segundos
LOG_FILE = "monitor_errors.log"
METRICS_FILE = "monitor_metrics.log"

def log_error(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

def log_metrics(msg):
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

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

def get_commit_timestamp(commit_hash):
    """Obtener timestamp del commit"""
    out, err = run_cmd(f"git log --format=%ct -1 {commit_hash}", cwd=REPO_DIR)
    return int(out) if out else None

def run_e2e_tests():
    """Ejecutar pruebas E2E"""
    print("\nEjecutando pruebas E2E...")
    try:
        # Ejecutar el script de pruebas E2E sin capturar output (para ver en tiempo real)
        result = subprocess.run(
            ["python", "../tests/e2e/e2e-tests.py"],
            cwd=os.path.dirname(__file__),
            timeout=180
        )
        
        if result.returncode == 0:
            print("Pruebas E2E completadas exitosamente")
            return True
        else:
            print("Pruebas E2E fallaron")
            log_error(f"Pruebas E2E fallaron con código: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Timeout en pruebas E2E (180s)")
        log_error("Timeout en pruebas E2E")
        return False
    except Exception as e:
        print(f"Error ejecutando pruebas E2E: {e}")
        log_error(f"Error ejecutando pruebas E2E: {e}")
        return False

def wait_for_deployment():
    """Esperar a que el despliegue esté listo"""
    out, err = run_cmd("kubectl wait --for=condition=available deployment/python-flask --timeout=180s")
    if err:
        log_error(f"Error esperando al despliegue: {err}")
        return False
    else:
        return True

#mostrar si hay nuevos commit
def monitor_repo():
    if not os.path.isdir(REPO_DIR):
        print(f"Error: No se encontró el directorio '{REPO_DIR}'")
        log_error(f"No se encontró el directorio '{REPO_DIR}'")
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

            # Iniciar medición de Lead Time
            deployment_start = time.time()
            commit_timestamp = get_commit_timestamp(current_remote)
            lead_time = deployment_start - commit_timestamp if commit_timestamp else 0
            
            log_metrics(f"DEPLOYMENT_START - Commit: {current_remote[:8]} - Lead Time: {lead_time:.2f}s")

            print("\nEjecutando git pull...")
            out, err = run_cmd("git pull", cwd=REPO_DIR)
            if err:
                log_error(f"Error en git pull: {err}")
            print(out or err)

            print("\n Aplicando manifiestos de Kubernetes...")
            manifests_dir = os.path.join(REPO_DIR, "manifests")

            deploy_out, deploy_err = run_cmd("kubectl apply -f deployment.yaml", cwd=manifests_dir)
            if deploy_err:
                log_error(f"Error en kubectl apply deployment.yaml: {deploy_err}")
            print(deploy_out or deploy_err)

            service_out, service_err = run_cmd("kubectl apply -f service.yaml", cwd=manifests_dir)
            if service_err:
                log_error(f"Error en kubectl apply service.yaml: {service_err}")
            print(service_out or service_err)

            print("Se aplicaron los manifiestos correctamente.")

            # Esperar que el deployment esté listo
            if not wait_for_deployment():
                log_metrics(f"DEPLOYMENT_FAILED - Commit: {current_remote[:8]} - Deployment not ready")
                continue

            # Ejecutar pruebas E2E
            if not run_e2e_tests():
                log_metrics(f"E2E_FAILED - Commit: {current_remote[:8]}")
                continue

             # Calcular Cycle Time (tiempo total hasta validación exitosa)
            cycle_time = time.time() - deployment_start
            
            # Registrar métricas exitosas
            log_metrics(f"Despliegue exitoso - Commit: {current_remote[:8]} - Lead Time: {lead_time:.2f}s - Cycle Time: {cycle_time:.2f}s")
            
            # Validar umbrales
            if lead_time > 300:  # 5 minutos
                log_metrics(f"Lead time excesivo: {lead_time:.1f}s > 300s")
            if cycle_time > 600:  # 10 minutos
                log_metrics(f"Cycle time excesivo: {cycle_time:.1f}s > 600s")
            
            print(f"\nDespliegue completo exitoso!")
            print(f"Lead Time: {lead_time:.1f}s | Cycle Time: {cycle_time:.1f}s")
        else:
            print("Sin nuevos commits.")

if __name__ == "__main__":
    try:
        monitor_repo()
    except KeyboardInterrupt:
        print("Monitoreo detenido.")
