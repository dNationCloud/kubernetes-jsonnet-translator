from translator.main import get_config_maps


def test_kubernetes_version(kubeconfig):
    print('test1')
    print(kubeconfig)


def test_kubernetes_version1(kubeconfig):
    print('test2')
    print(kubeconfig)


def test_get_config_maps(kube):
    configmap = kube.load_configmap('/home/mato/Dev/ifne/dnation/kubernetes-jsonnet-translator/examples/grafana-jsonnet.yaml')
    configmap.create()
    configmap.wait_until_ready(timeout=50)
    configmap.refresh()
    configmap_is_ready = configmap.is_ready()
    assert configmap_is_ready
    cm = get_config_maps(label_selector="grafana_dashboard_jsonnet=1")
    assert len(cm.items) == 1
    print('test3')
