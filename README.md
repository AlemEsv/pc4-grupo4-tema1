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
- 20GB de espacio en disco.
- Tener un **contenedor** de Docker o un gestor de **máquinas virtuales**.

## Requisitos

Este proyecto está ejecutandose en equipos con sistemas operativos Windows, con el avance de los sprints veremos opciones para correrlo en linux.

Desde una terminal con permisos de administrador, correr los siguientes comandos:

```bash
choco install minikube #instala versión más actual de minikube
minikube start
minikube version #verifica si inició correctamente
```

Las imagenes de docker que necesitamos correr deben estar dentro de minikube, no desde nuestro computador, por lo que se debe ejecutar el siguiente comando:

```bash
minikube -p minikube docker-env | Invoke-Expression
```

Para verificar cada una de las imagenes instaladas:

```bash
docker image ls
```

## Instalación

```bash
docker build -t python-flask:latest .
```

Aplicamos los manifestos definidos en el repositorio:

```bash
kubectl apply -f ./manifests/deployment.yaml
kubectl apply -f ./manifests/service.yaml
```

Por lo que se creará corretamente tanto los servicios como los pods

```bash
# mostrará 4 pods creados
kubectl get pods
# mostrará un servicio del tipo NodePort
kubectl get svc
```

Por ultimo ejecutamos el comando para conocer el url con la que se levanta la aplicación:

```bash
minikube service python-flask-service --url
```


