import pytest

from pytest_kind import KindCluster


@pytest.fixture(scope="session")
def kind():
    cluster = KindCluster("matko")
    cluster.create()
    yield cluster
    cluster.delete()


@pytest.fixture(scope="session")
def kubeconfig(kind):
    return kind.kubeconfig_path
