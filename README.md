# Jsonnet translator

This project is a docker container intended to run inside a kubernetes cluster to collect and translates jsonnet resources.
It looks for config maps with jsonnet code specified by labels in all namespaces. Jsonnet is afterwards evaluated and 
appropriate k8s objects are generated. Grafana dashboards and prometheus rules generated from jsonnet are supported.

### Installation

Prerequisites
 - [Helm3](https://helm.sh/)
 
dNation Jsonnet Translator Chart is hosted in the [dNation helm repository](https://dnationcloud.github.io/helm-hub/).

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

Examples can be run even without installation to cluster (but there has to be accessible cluster config).
In order to run examples outside cluster uncomment [this line](translator/main.py#L544).
Install [jsonnet bundler](https://github.com/jsonnet-bundler/jsonnet-bundler) and run:
  ```
  mkdir jsonnet_libs
  cd jsonnet_libs
  jb init
  cd ..
  python3 sidecar/main.py --libsonnet https://github.com/grafana/grafonnet-lib/grafonnet@ff69572caf78c3163980d0d723c85a722eab73d9 \
  https://github.com/bitnami-labs/kube-libsonnet@2c48e8e3fb40e38461ba27b05a290877c1e39cec \
  https://github.com/thelastpickle/grafonnet-polystat-panel@275a48de57afdac0d72219d82863d8ab8bd0e682
  ```

At this moment, you should have running python script (steps above) or installed chart with helm or created own [deployment](exampes/example-deployment.yaml).
In order tu run these examples you have to have downloaded [examples folder](examples).

 - plaintext jsonnet dashboards
    - `kubectl apply -f examples/jsonnet-cm.yaml`
    - config map `grafana-dashboards-generated` with label `grafana_dashboard: 1` and json dashboard should be generated
    
 - jsonnet + libsonnet + usage of build arguments 
    - `kubectl apply -f examples/jsonnet-ext-cm.yaml`
    - config map `grafana-dashboards-generated` with label `grafana_dashboard: 1` and json dashboard should be generated
    
 - archive jsonnet (compressed file structure/folder)
    - `kubectl apply -f examples/tar-jsonnet-cm.yaml`
    - config map `grafana-dashboards-generated` with label `grafana_dashboard: 1` and json dashboards of [dnation monitoring](https://github.com/dNationCloud/kubernetes-monitoring-stack) should be generated
    
    NOTE: config map with archive data, has to have annotation `jsonnet_filename: path/to/file` which defines 
    which file after archive extraction should be build
    
  - plaintext jsonnet prometheus rule
    - `kubectl apply -f examples/jsonnet-rule-cm.yaml`
    - prometheusrule object `prometheus-rules-generated` with label `prometheus_rule: 1` and prometheus rule should be generated
    

### Configuration

Global setup can be done by arguments of program (in case of helm installation args are set in [values.yaml](chart/values.yaml)). 
Possible arguments and their defaults can be found [here](default_config.yaml). Descriptions are in [arg_parser.py](translator/arg_parser.py).
    
Other configuration can be done by annotations of jsonnet config maps. See [example](examples/jsonnet-ext-cm.yaml#L8). \
Supported jsonnet build keyword arguments can be found [here](https://jsonnet.org/ref/bindings.html) (except callbacks).
