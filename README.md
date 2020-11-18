# Jsonnet translator

This project is a docker container intended to run inside a kubernetes cluster to collect and translates jsonnet resources.
It looks for config maps with jsonnet code specified by labels in all namespaces. Jsonnet is afterwards evaluated and 
appropriate k8s objects are generated. Grafana dashboards and prometheus rules generated from jsonnet are supported.

### Prerequisities

 

### Examples (outside k8s cluster)

In order to run examples outside cluster uncomment [this line](translator/main/#L544).
Install [jsonnet bundler](https://github.com/jsonnet-bundler/jsonnet-bundler) and run:
  ```
  mkdir jsonnet_libs
  cd jsonnet_libs
  jb init
  cd ..
  ```

 - plaintext jsonnet dashboards
    - run `python3 sidecar/main.py --libsonnet https://github.com/grafana/grafonnet-lib/grafonnet@ff69572caf78c3163980d0d723c85a722eab73d9` 
    - `kubectl apply -f examples/jsonnet-cm.yaml`
    - config map `grafana-dashboards-generated` with label `grafana_dashboard: 1` and json dashboard should be generated
    
 - jsonnet + libsonnet + usage of build arguments
    - run `python3 sidecar/main.py --libsonnet https://github.com/grafana/grafonnet-lib/grafonnet@ff69572caf78c3163980d0d723c85a722eab73d9` 
    - `kubectl apply -f examples/jsonnet-ext-cm.yaml`
    - config map `grafana-dashboards-generated` with label `grafana_dashboard: 1` and json dashboard should be generated
    
 - archive jsonnet (compressed file structure/folder)
    - run 
        ```
        python3 sidecar/main.py --libsonnet https://github.com/grafana/grafonnet-lib/grafonnet@ff69572caf78c3163980d0d723c85a722eab73d9 \
        https://github.com/bitnami-labs/kube-libsonnet@2c48e8e3fb40e38461ba27b05a290877c1e39cec \
        https://github.com/thelastpickle/grafonnet-polystat-panel@275a48de57afdac0d72219d82863d8ab8bd0e682
        ```
    - `kubectl apply -f examples/tar-jsonnet-cm.yaml`
    - config map `grafana-dashboards-generated` with label `grafana_dashboard: 1` and json dashboard should be generated
    
    NOTE: config map with archive data, has to have annotation `jsonnet_filename: path/to/file` which defines 
    which file after archive extraction should be build
    
  - plaintext jsonnet prometheus rule
    - run `python3 sidecar/main.py` 
    - `kubectl apply -f examples/jsonnet-rule-cm.yaml`
    - prometheusrule object `prometheus-rules-generated` with label `prometheus_rule: 1` and prometheus rule should be generated
    
### Usage in grafana pod

Depending on the cluster setup you might have to grant yourself admin rights first: 
`kubectl create clusterrolebinding cluster-admin-binding --clusterrole cluster-admin --user`

Example of deployment can be found [here](exampes/example-deployment.yaml).

### Configuration

Global setup can be done by arguments of program. Possible arguments and their defaults can be found [here](default_config.yaml).
    
Other configuration can be done by annotations of jsonnet config maps. See [example](examples/jsonnet-ext-cm.yaml). \
Supported jsonnet build keyword arguments can be found [here](https://jsonnet.org/ref/bindings.html) (except callbacks).
