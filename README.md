# envoy-rnd

Testing envoy on local

### Tools Installation
- Install [minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fhomebrew)
```bash
brew install minikube
```
- Install helm
```bash
brew install helm
```

## envoy-setup

- Start minikube
```bash
minikube start
```

- Setup envoy gateway <br/>
```bash
helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.0.2 -n envoy-gateway-system --create-namespace
```
- Wait for envoy gateway to set up<br/>
```bash
kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available
```
- Setup example app and routes<br/>
```bash
kubectl apply -f envoy/config.yaml
```
- Get name of envoy service<br/>
```bash
export ENVOY_SERVICE=$(kubectl get svc -n envoy-gateway-system --selector=gateway.envoyproxy.io/owning-gateway-namespace=default,gateway.envoyproxy.io/owning-gateway-name=eg -o jsonpath='{.items[0].metadata.name}')
```
- Port forward envoy to localhost<br/>
```bash
kubectl -n envoy-gateway-system port-forward service/${ENVOY_SERVICE} 8888:80
```
- Example curl you can hit<br/>
```bash
curl -X POST http://localhost:8888/service1/post \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_access_token_here" \
  -H "X-Session-Token: token1" \
  -H "Custom-Header: custom_value" \
  -d '{"key1": "value1", "key2": "value2"}'
 ```
- Port forwarding can also be set using lens. Go to Network > Services > <gateway service> and click port forward and forward to 8888

## envoy-cleanup
- Delete config
```bash
kubectl delete -f envoy/config.yaml --ignore-not-found=true
```
- Delete envoy
```bash
helm uninstall eg -n envoy-gateway-system
```
- Delete minikube
```bash
minikube delete
```

## Docker setup
Server used for testing can be built using below commands. It's a simple python echo server
- Use docker inside minikube daemon, will be only valid for that terminal session
```bash
eval $(minikube docker-env)
```
- Build echo server image
```bash
docker build --platform=linux/amd64 -t python-echo echo_server/.
```
- Build auth server image
```bash
docker build --platform=linux/amd64 -t python-auth auth_server/.
```

## Envoy-Proxy Setup
- Create config map for envoy proxy. Below command will update the configmap if already exists
```bash
  kubectl create configmap envoy-config --from-file=envoy.yaml=envoy_proxy/envoy.yaml --dry-run=client -o yaml | kubectl apply -f -
```
- Setup python app with sidecar envoy proxy
```bash
kubectl apply -f envoy_proxy/config.yaml
```
- Port forward
```bash
kubectl port-forward service/python-envoy-service 8080:80
```
- Hit below curl for testing
```bash
curl -v -X POST http://localhost:8080/service1/post \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_access_token_here" \
  -H "X-Session-Token: my_token" \
  -H "Custom-Header: custom_value" \
  -d '{"key1": "value1", "key2": "value2"}'
```