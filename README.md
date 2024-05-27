# envoy-rnd

Testing envoy on local


## envoy-setup

- Install minikube
- Install helm <br/>
`brew install helm`
- Setup envoy gateway <br/>
`helm install eg oci://docker.io/envoyproxy/gateway-helm --version v0.0.0-latest -n envoy-gateway-system --create-namespace`
- Wait for envoy gateway to set up<br/>
`kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available`
- Setup example app and routes<br/>
`kubectl apply -f envoy/config.yaml -n default`
- Get name of envoy service<br/>
`export ENVOY_SERVICE=$(kubectl get svc -n envoy-gateway-system --selector=gateway.envoyproxy.io/owning-gateway-namespace=default,gateway.envoyproxy.io/owning-gateway-name=eg -o jsonpath='{.items[0].metadata.name}')`
- Port forward envoy to localhost<br/>
`kubectl -n envoy-gateway-system port-forward service/${ENVOY_SERVICE} 8888:80`
- Example curl you can hit<br/>
```
curl -X POST http://localhost:8888/service1/post \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_access_token_here" \
  -H "Custom-Header: custom_value" \
  -d '{"key1": "value1", "key2": "value2"}'
  ```
- Port forwarding can also be set using lens. Go to Network > Services > <gateway service> and click port forward and forward to 8888