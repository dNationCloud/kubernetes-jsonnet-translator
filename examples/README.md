# Examples 

Prerequisites

* [Kind](https://kind.sigs.k8s.io/)
* [Docker](https://www.docker.com/)
* [Helm3](https://helm.sh/)
* [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

Download this repo and install kind and translator chart.
```bash
kind create cluster --image kindest/node:v1.19.1
helm install translator ./chart
```

- Example of grafana dashboard
```bash
kubectl apply -f examples/grafana-jsonnet.yaml
# see results
kubectl describe cm grafana-dashboards-generated-example-dashboard
```

- Example of prometheus rule
```bash
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/release-0.42/example/prometheus-operator-crd/monitoring.coreos.com_prometheusrules.yaml
kubectl apply -f examples/prom-rule-jsonnet.yaml
# see results
kubectl describe prometheusrule prometheus-rules-generated
```

More examples can be found in [examples](examples) folder.
