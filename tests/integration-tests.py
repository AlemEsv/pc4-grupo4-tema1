import subprocess
import sys


def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, shell=True, text=True,
                                capture_output=True, timeout=timeout)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"


def test_pod_running_and_ready():
    print("Verificando estado de los pods...")

    success, stdout, stderr = run_cmd(
        "kubectl get pods -l app=python-flask -o jsonpath=\"{.items[*].status.phase}\""
    )
    if not success or 'Running' not in stdout:
        print(f"No hay pods en estado Running: {stderr or stdout}")
        return False

    success, stdout, stderr = run_cmd(
        "kubectl get pods -l app=python-flask -o jsonpath=\"{.items[*].status.conditions[?(@.type=='Ready')].status}\""
    )
    if not success or 'True' not in stdout:
        print(f"Los pods no están en estado Ready: {stderr or stdout}")
        return False

    print("Pods corriendo y listos")
    return True


def test_deployment_ready():
    print("Verificando deployment...")

    success, stdout, stderr = run_cmd(
        "kubectl get deployment python-flask-deployment -o jsonpath=\"{.spec.replicas},{.status.readyReplicas}\""
    )
    if not success:
        print(f"Error al obtener el deployment: {stderr}")
        return False

    if not stdout:
        print("Deployment no encontrado")
        return False

    try:
        desired, ready = stdout.split(",")
        desired = int(desired)
        ready = int(ready) if ready else 0

        if desired == ready and ready > 0:
            print(f"Deployment listo: {ready}/{desired} réplicas")
            return True
        else:
            print(f"Deployment incompleto: {ready}/{desired} réplicas")
            return False
    except Exception as e:
        print(f"Error al interpretar datos del deployment: {e}")
        return False


def test_service_configured():
    print("Verificando service...")

    success, stdout, stderr = run_cmd(
        "kubectl get service python-flask-service -o jsonpath=\"{.spec.type},{.spec.ports[0].nodePort}\""
    )
    if not success:
        print(f"Error al obtener el service: {stderr}")
        return False

    if not stdout:
        print("Service no encontrado")
        return False

    service_info = stdout.split(',')
    service_type = service_info[0].strip("'\" ")

    if service_type != 'NodePort':
        print(f"Tipo de service incorrecto: {service_type}")
        return False

    print("Service correctamente configurado como NodePort")
    return True


def main():
    print("Ejecutando pruebas de integración...")

    tests = [
        ("Pod Running/Ready", test_pod_running_and_ready),
        ("Deployment Ready", test_deployment_ready),
        ("Service Configurado", test_service_configured)
    ]

    failed = []

    for name, test_func in tests:
        print(f"\n- {name}")
        try:
            if not test_func():
                failed.append(name)
        except Exception as e:
            print(f"Error en {name}: {e}")
            failed.append(name)

    if failed:
        print("\nAlgunas pruebas fallaron:")
        for f in failed:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\nTodas las pruebas pasaron")
        sys.exit(0)


if __name__ == "__main__":
    main()
