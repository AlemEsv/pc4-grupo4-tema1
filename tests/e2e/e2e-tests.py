import subprocess
import requests
import time
import sys

def run_cmd(cmd, timeout=30):
    """Ejecutar comando y retornar resultado"""
    try:
        result = subprocess.run(cmd, shell=True, text=True, 
                              capture_output=True, timeout=timeout)
        return result.returncode == 0, result.stdout.strip(), result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"

def get_service_url():
    """Obtener URL del túnel de minikube"""
    # URL del túnel de minikube que aparece en una terminal separada
    # Cambia esta URL por la que aparece en tu terminal de minikube service
    tunnel_url = "http://127.0.0.1:63990"  # Reemplaza con tu URL actual
    return tunnel_url

def test_http_response():
    """Verificar respuesta HTTP de la aplicación"""
    print("Verificando respuesta HTTP...")
    
    service_url = get_service_url()
    if not service_url:
        print("No se pudo obtener URL del service")
        return False
    
    try:
        response = requests.get(service_url, timeout=15)
        if response.status_code == 200:
            print(f"Respuesta HTTP: OK.  desde {service_url}")
            return True
        else:
            print(f"error HTTP: código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error en petición HTTP: {e}")
        return False

def test_application_content():
    """Verificar contenido de la aplicación"""
    print("Verificando contenido de la aplicación...")
    
    service_url = get_service_url()
    if not service_url:
        print("No se pudo obtener URL del service")
        return False
    
    try:
        response = requests.get(service_url, timeout=15)
        if response.status_code != 200:
            print(f"Error HTTP: {response.status_code}")
            return False
        
        # Verificar contenido esperado
        content = response.text.lower()
        expected_keywords = ["html", "body", "title"]
        
        found_keywords = [kw for kw in expected_keywords if kw in content]
        
        if found_keywords:
            print(f"Contenido válido encontrado: {found_keywords}")
            return True
        else:
            # Si no encuentra keywords, verificar que al menos responde algo válido
            if len(response.text) > 10:
                print(f"Aplicación responde con contenido válido")
                return True
            else:
                print(f"Contenido inesperado: {response.text[:50]}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"Error verificando contenido: {e}")
        return False

def test_application_availability():
    """Verificar disponibilidad con reintentos"""
    print("Verificando disponibilidad con reintentos...")
    
    service_url = get_service_url()
    if not service_url:
        print("No se pudo obtener URL del service")
        return False
    
    max_retries = 8
    for attempt in range(max_retries):
        try:
            response = requests.get(service_url, timeout=10)
            if response.status_code == 200:
                print(f"Aplicación disponible (intento {attempt + 1})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_retries - 1:
            print(f"Intento {attempt + 1}/{max_retries} falló, reintentando...")
            time.sleep(10)
    
    print(f"Aplicación no disponible después de {max_retries} intentos")
    return False

def main():
    """Ejecutar todas las pruebas E2E"""
    print("Iniciando pruebas E2E...")
    
    tests = [
        ("HTTP Response", test_http_response),
        ("Contenido Aplicación", test_application_content),
        ("Disponibilidad", test_application_availability)
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"Error en {test_name}: {e}")
            failed_tests.append(test_name)
        
        # Pausa entre pruebas E2E
        time.sleep(3)
    
    if failed_tests:
        print(f"\n Las Pruebas E2E fallaron:")
        for test in failed_tests:
            print(f"  - {test}")
        sys.exit(1)
    else:
        print(f"\nTodas las pruebas E2E pasaron")
        sys.exit(0)

if __name__ == "__main__":
    main()