# Poetry in microservices

2. Create python virtual envioroment

```
virtualenv -p python3 venv
source venv/bin/activate
```

3. Install requirements

7. Build project wheels

```
./venv/bin/python ./Deploy/build_project_wheels.py
```

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