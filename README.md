# Proyecto 1: "Plataforma de despliegue continuo local (Mini-GitOps)"

> Grupo 4:
>
> 1. Cinver Alem Espinoza Valera
>
> 2. Benjamin Joel Seminario Serna
>
---

Siguiendo la documentación de minikube en: [minikube_docs](https://minikube.sigs.k8s.io/docs/)

## Pre-requisitos

- Instalar [**Chocolatey**](https://chocolatey.org/) Package manager.
- Instalar [**Docker-desktop**]([https://chocolatey.org/](https://docs.docker.com/desktop/setup/install/windows-install/))
## Requisitos

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
```
y para poder dar de baja el servicio
```bash
make clean
```
