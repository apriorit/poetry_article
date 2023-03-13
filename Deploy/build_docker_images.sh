# use minikube docker-env to use minikube's docker daemon
eval $(minikube docker-env)

ORDER_MANAGER_NAME=order_manager
ORDER_MANAGER_DOCKER=Microservices/OrderManager/Dockerfile
docker build  -t ${ORDER_MANAGER_NAME} -f ${ORDER_MANAGER_DOCKER} ./

USER_MANAGER_NAME=user_manager
USER_MANAGER_DOCKER=Microservices/UserManager/Dockerfile
docker build  -t ${USER_MANAGER_NAME} -f ${USER_MANAGER_DOCKER} ./
