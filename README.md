<a href="https://dNation.cloud/"><img src="https://cdn.ifne.eu/public/icons/dnation.png" width="250" alt="dNationCloud"></a>

# dnation Jsonnet Translator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Artifact HUB](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/dnationcloud)](https://artifacthub.io/packages/search?repo=dnationcloud)


dNation Translator is a simple container for translating jsonnet content stored in k8s configmaps to **grafana dashboards** or **prometheus rules**.

This project is intended to run inside a k8s cluster to collect and translates jsonnet resources. 
It looks for k8s configmaps with jsonnet code specified by labels in defined namespaces. 
Jsonnet configmap is afterwards evaluated and appropriate k8s objects are generated. Currently grafana dashboards and prometheus rules are supported.

### Installation

Prerequisites
 - [Helm3](https://helm.sh/)
 
dNation Jsonnet Translator Chart is hosted in the [dNation helm repository](https://artifacthub.io/packages/search?repo=dnationcloud).

```bash
# Add dNation helm repository
helm repo add dnationcloud https://dnationcloud.github.io/helm-hub/
helm repo update

# Install dNation Jsonnet Translator
helm install dnation-jsonnet-translator dnationcloud/dnation-jsonnet-translator
```

If you don't want to use helm, example of simple deployment, can be found [here](exampes/example-deployment.yaml). \
(Depending on the cluster setup you might have to grant yourself admin rights first: 
`kubectl create clusterrolebinding cluster-admin-binding --clusterrole cluster-admin --user`) 

### Examples 

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
kubectl desribe cm grafana-dashboards-generated
```

- Example of prometheus rule
```bash
kubectl apply -f examples/prom-rule-jsonnet.yaml
# see results
kubectl desribe prometheusrule prometheus-rules-generated
```

More examples can be found in [examples](./examples) folder.

### Configuration

Global setup can be done by arguments of program (in case of helm installation args are set in [values.yaml](chart/values.yaml)). 
Possible arguments and their defaults can be found [here](default_config.yaml). Descriptions are in [arg_parser.py](translator/arg_parser.py).
    
Other configuration can be done by annotations of jsonnet config maps. See [example](examples/grafana-jsonnet-ext-cm.yaml#L8). \
Supported jsonnet build keyword arguments can be found [here](https://jsonnet.org/ref/bindings.html) (except callbacks).
