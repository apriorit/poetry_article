# use minikube docker-env to use minikube's docker daemon
eval $(minikube docker-env)

ORDER_MANAGER_NAME=order_manager
ORDER_MANAGER_DOCKER=Microservices/OrderManager/Dockerfile
ORDER_MANAGER_DEPLOY=Deploy/build/order_manager
docker build  -t ${ORDER_MANAGER_NAME} -f ${ORDER_MANAGER_DOCKER} ${ORDER_MANAGER_DEPLOY}

USER_MANAGER_NAME=user_manager
USER_MANAGER_DOCKER=Microservices/UserManager/Dockerfile
USER_MANAGER_DEPLOY=Deploy/build/user_manager
docker build  -t ${USER_MANAGER_NAME} -f ${USER_MANAGER_DOCKER} ${USER_MANAGER_DEPLOY}