# Poetry in microservices

1. Build docker images:

```
/bin/bash ./Deploy/build_docker_images.sh
```

2. Install kubernetes and minikube

3. Enable minikube ingress

```
minikube addons enable ingress
```

4. Install helm

```
helm install microservices-app ./Deploy/helm
```

Other helm commands:

```
helm uninstall microservices-app
helm list
```