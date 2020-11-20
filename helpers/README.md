# Helpers

A set of scripts and configuration files which helps to simplify local development.

## Local development using KinD (Kubernetes in Docker)

Prerequisites

* [Kind](https://kind.sigs.k8s.io/)
* [Docker](https://www.docker.com/)
* [Helm3](https://helm.sh/)
* [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

### Build 

Create kind cluster
```bash
kind create cluster --image kindest/node:v1.19.1
```

Translator can run without installation to cluster (but there has to be accessible cluster config).
Install [jsonnet bundler](https://github.com/jsonnet-bundler/jsonnet-bundler) and run:
```
mkdir jsonnet_libs
cd jsonnet_libs
jb init
cd ..

pip3 install .
python3 translator/main.py --dev --libsonnet https://github.com/grafana/grafonnet-lib/grafonnet@ff69572caf78c3163980d0d723c85a722eab73d9
```

Generate example grafana dashboard
```
kubectl apply -f examples/grafana-jsonnet.yaml
# see results
kubectl desribe cm grafana-dashboards-generated
```
If everything was installed correctly, described config map should contain grafana dashboard in JSON.

More examples can be found in [examples](../examples) folder.
