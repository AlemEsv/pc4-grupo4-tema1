# Proyecto 1: "Plataforma de despliegue continuo local (Mini-GitOps)"

> Grupo 4:
>
> 1. Cinver Alem Espinoza Valera
>
> 2. Benjamin Joel Seminario Serna
>
---

Repositorio de despliegue para la aplicación: [app-manifest](https://github.com/AlemEsv/app-manifests)

## Índice

- [Requisitos](#requisitos)
- [Herramientas usadas](#herramientas)
- [Instalación General](#instalación-general)
- [Instalación con Makefile](#instalación-usando-el-makefile)
- [Hooks personalizados](#git-hooks)

## Pre-requisitos

- Instalar [**Chocolatey**](https://chocolatey.org/) Package manager.
- Instalar [**Docker-desktop**](https://docs.docker.com/desktop/setup/install/windows-install/)
## Requisitos

Siguiendo la documentación de minikube en: [minikube_docs](https://minikube.sigs.k8s.io/docs/).
Este proyecto está ejecutandose en equipos con sistemas operativos Windows, con el avance de los sprints veremos opciones para correrlo en linux.

Desde una terminal, correr los siguientes comandos para tener tanto el proyecto para el monitorieo como minikube instalados en nuestro equipo:

```bash
choco install minikube #instala versión más actual de minikube
git clone https://github.com/AlemEsv/app-manifests.git
```

Para verificar la instalación de minikube:

```bash
minikube version
# inicialmente el cluster estará apagado.
minikube status
```

## Videos grupales

- [**Video Sprint 1**](https://drive.google.com/file/d/1-30PtTELNW6knPTHX6XkzuL55M5NAowj/view?usp=sharing)

- [**Video Sprint 2**](https://drive.google.com/file/d/1qTVA4tNJcs28HX3VMUCkSAreZabxeLB3/view?usp=sharing)

- [**Video Sprint 3**](https://drive.google.com/drive/folders/17LHca0hkqFgUesVOaw6JTp_Z-2xtlv5w)

## Herramientas

### 1. flake8

* **flake8**: Verifica código en Python por incorrecta sintáxis y malas prácticas.

```bash
flake8 -r scripts/
```

### 2. Pytest

Framework de pruebas para python, usado para asegurar buenas pruebas en los scripts `validate_manifest.py`, `git_monitor.py`, pruebas de integración y pruenas E2E.

## Instalación General

Asegurarse de tener Docker-desktop ejecutando en segundo plano para poder inicializar el cluster.

```bash
minikube start --driver=docker
docker build -t python-flask:latest .
```

Aplicamos los manifestos definidos en el repositorio:

```bash
kubectl apply -f ./manifests/deployment.yaml
kubectl apply -f ./manifests/service.yaml
```

Verificamos que los pods estén corriendo y el servicio haya sido desplegado con exito:

```bash
# mostrará 4 pods creados
kubectl get pods
# mostrará un servicio del tipo NodePort
kubectl get svc
```

Por ultimo ejecutamos el comando para conocer el url con la que se desplegará la aplicación:

```bash
minikube service python-flask-service --url
```

Para poder dar de baja el servicio orquestado por minikube, colocaremos el siguiente comando:

```bash
kubectl delete all --all
minikube stop
```

## Instalación usando el Makefile

Para inicializar nuestro cluster de minikube dentro de docker-desktop

```bash
make start
```

Luego desplegamos la aplicación:

```bash
make build
make deploy

# verifica el estado de los pods y el servicio
make status
# muestra los logs al desplegar la aplicación
make logs
```

y para poder dar de baja el servicio

```bash
make clean
```

## Git Hooks

### Pre-commit

Decidimos versionar los hooks de Git para mejorar su trazabilidad y facilitar su distribución entre el equipo (mediante git pull).

Con este enfoque, los hooks no se almacenan en la ubicación predeterminada hooks (que no permite versionado), sino en el directorio git-hooks. Para que todos los colaboradores puedan utilizar estos hooks versionados, es necesario configurar Git para que reconozca esta nueva ubicación personalizada, lo cual se logra ejecutando el siguiente comando:

```bash
git config core.hooksPath git-hooks
```

#### **Funcionalidades**

- Verificación el nombrado de ramas
  - Valida que el nombre de la rama siga las convenciones del proyecto (`feature/*`, `fix/*`, `docs/*`)
  - **Ejemplo válido**: `feature/readme-update`, `fix/flask-app`
  - **Ejemplo inválido**: `main`, `rama2/f`, `ramita/feat_1`

- Validación de manifiestos
  - **Archivos verificados**: Todos los `.yaml` en la carpeta `manifests/`
  - Si hay errores de sintaxis YAML, el commit se rechaza

- Linting de código Python
  - **Reglas aplicadas**:
    - `E9`: Errores de sintaxis
    - `F63`: Comparaciones inválidas
    - `F7`: Errores de sintaxis en f-strings
    - `F82`: Variables no definidas
  - **Archivos verificados**: Solo archivos `.py` modificados en el commit
