<a href="https://dNation.cloud/"><img src="https://cdn.ifne.eu/public/icons/dnation.png" width="250" alt="dNationCloud"></a>

# dNation Kubernetes Jsonnet Translator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Artifact HUB](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/dnationcloud)](https://artifacthub.io/packages/search?repo=dnationcloud)
[![version](https://img.shields.io/badge/dynamic/yaml?color=blue&label=Version&prefix=v&query=%24.appVersion&url=https%3A%2F%2Fraw.githubusercontent.com%2FdNationCloud%2Fkubernetes-jsonnet-translator%2Fmain%2Fchart%2FChart.yaml)](https://artifacthub.io/packages/search?repo=dnationcloud)

dNation Translator is a simple container for translating jsonnet content stored in k8s configmaps to **grafana dashboards** or **prometheus rules**.

This project is intended to run inside a k8s cluster to collect and translates jsonnet resources. 
It looks for k8s configmaps with jsonnet code specified by labels in defined namespaces. 
Jsonnet configmap is afterwards evaluated and appropriate k8s objects are generated. Currently grafana dashboards and prometheus rules are supported.

### Installation

Prerequisites
 - [Helm3](https://helm.sh/)
 
dNation Kubernetes Jsonnet Translator Chart is hosted in the [dNation helm repository](https://artifacthub.io/packages/search?repo=dnationcloud).

```bash
# Add dNation helm repository
helm repo add dnationcloud https://dnationcloud.github.io/helm-hub/
helm repo update

# Install dNation Jsonnet Translator
helm install dnation-kubernetes-jsonnet-translator dnationcloud/dnation-kubernetes-jsonnet-translator
```

Examples how to test if everything is working correctly can be found in [examples](./examples) folder.

### Configuration

Global setup can be done by arguments of program (in case of helm installation args are set in [values.yaml](chart/values.yaml)). 
Possible arguments and their defaults can be found [here](default_config.yaml). Descriptions are in [arg_parser.py](translator/arg_parser.py).
    
Other configuration can be done by annotations of jsonnet config maps. See [example](examples/grafana-jsonnet-ext.yaml#L11). \
Supported jsonnet build keyword arguments can be found [here](https://jsonnet.org/ref/bindings.html) (except callbacks).
