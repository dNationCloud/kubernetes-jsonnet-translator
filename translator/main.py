# Copyright 2020 The dNation Jsonnet Translator Authors. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import _jsonnet
import json
import utils
import logger
import time

from multiprocessing import Process
from arg_parser import get_parser
from subprocess import Popen, PIPE, TimeoutExpired
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from urllib3.exceptions import ProtocolError
from urllib3.exceptions import MaxRetryError


log = logger.get_logger(__name__)


def parse_json_with_files(input_filepath):
    """Parses json file with created files (dashboards/rules).

    Args:
        input_filepath (str): Path to json file with files.

    Returns:
        list of (str, str): List of tuples (filename, data), where filename is
            <filename>.json and data is file in json format.

    """
    try:
        with open(input_filepath, "r") as in_f:
            big_json = json.loads(in_f.read())
            return big_json.items()
    except OSError as e:
        log.error(f"Error when reading {input_filepath}, error: {e}")


def get_config_maps(label_selector):
    """Retrieves config maps from all namespaces labeled by label_selector.

    Args:
        label_selector (str): Label with value from config map
            (example: "grafana_dashboard_jsonnet=1").

    Returns:
        client.models.v1_config_map_list.V1ConfigMapList:
            Kubernetes client class that contains config maps.
    """
    v1 = client.CoreV1Api()
    config_maps = v1.list_config_map_for_all_namespaces(label_selector=label_selector)
    return config_maps


def get_jsonnet_keywords_args(annotations):
    """Tries keyword args to jsonnet build provided by user.

    Args:
        annotations (dict of str: str):  Annotations from jsonnet configmap.

    Returns:
        dict: valid keyword arguments with eval values.
    """
    supported_args = [
        "max_stack",
        "gc_min_objects",
        "gc_growth_trigger",
        "ext_vars",
        "ext_codes",
        "tla_vars",
        "tla_codes",
        "max_trace",
    ]
    valid_args = {}
    for key, value in annotations.items():
        if key not in supported_args:
            continue
        try:
            _jsonnet.evaluate_snippet("dummy", "{}", **{key: eval(value)})
            valid_args[key] = eval(value)
        except TypeError as e:
            log.error(f"Build argument from annotations {key} is invalid, error: {e}")
        except Exception as e:
            log.error(
                f"Evaluation of build argument {key} from annotations failed,"
                f" error: {e}"
            )

    return valid_args


def get_labels(
    user_labels, user_annotations, old_label_selector, new_selector_annotation
):
    """Replaces label selectors.

    Deletes old label selector from labels and adds new one,
    defined in annotations by new_selector_annotation.

    Args:
        user_labels (dict):  Labels of kubernetes object.
        user_annotations (dict): Annotations of kubernetes object.
        old_label_selector (str): Label to be removed.
            (in format '<label>=<key>')
        new_selector_annotation (str): Key in annotations, where new
            label selector is stored.

    Returns:
        dict: updated labels.
    """
    try:
        key, _ = old_label_selector.split("=")
    except ValueError:
        log.error(f"Label selector is invalid: {old_label_selector}")
    else:
        user_labels.pop(key, None)

    try:
        new_label_selector = user_annotations[new_selector_annotation]
        key, value = new_label_selector.split("=")
    except KeyError:
        log.error(f"Annotations not containing field {new_selector_annotation}")
    except ValueError:
        log.error(f"Label for kubernetes object is invalid: {new_selector_annotation}")
    else:
        user_labels[key] = value

    return user_labels


def create_rules_object(args_, jsons, user_labels, user_annotations):
    """Creates prometheusrule object.

    Creates or replaces prometheusrule object from json rules with provided metadata.

    Args:
        args_ (argparse.Namespace): Args from ArgumentParser.
        jsons (array of (str, dict)): Generated rules in format
            (filename, dict from json).
        user_labels (dict):  Labels of kubernetes object.
        user_annotations (dict): Annotations of kubernetes object.

    Returns:
        None
    """
    coa = client.CustomObjectsApi()

    name = args_.prometheus_rules_object_name
    namespace = args_.namespace
    group = "monitoring.coreos.com"
    version = "v1"
    plural = "prometheusrules"

    labels = {}
    if len(jsons) > 0:
        labels = get_labels(
            user_labels,
            user_annotations,
            args_.jsonnet_rules_selector,
            args_.prometheus_label,
        )

    groups = []
    for filename, json_data in jsons:
        groups.extend(json_data["groups"])

    metadata = {
        "name": name,
        "namespace": namespace,
        "labels": labels,
    }

    prom_rules_object = {
        "apiVersion": f"{group}/{version}",
        "kind": "PrometheusRule",
        "metadata": metadata,
        "spec": {"groups": groups},
    }

    log.info(f"Regenerating rules resource {name}")

    name_selector = f"metadata.name={name}"
    rules_objects = coa.list_namespaced_custom_object(
        group, version, namespace, plural, field_selector=name_selector
    )
    rules_objects = rules_objects["items"]

    if len(rules_objects) > 0:
        try:
            resource_version = rules_objects[0]["metadata"]["resourceVersion"]
            prom_rules_object["metadata"]["resourceVersion"] = resource_version
            coa.replace_namespaced_custom_object(
                group, version, namespace, plural, name, prom_rules_object
            )
        except ApiException as e:
            log.error(f"Error when replacing prometheus rule {name}, error {e}")
    else:
        try:
            coa.create_namespaced_custom_object(
                group, version, namespace, plural, prom_rules_object
            )
        except ApiException as e:
            log.error(f"Error when creating prometheus rule {name}, error {e}")


def create_dashboard_cm(args_, jsons, user_labels, user_annotations):
    """Creates config map.

    Creates or replaces config map from json dashboards with provided metadata.

    Args:
        args_ (argparse.Namespace): Args from ArgumentParser.
        jsons (array of (str, dict)): Generated dashboards in format
            (filename, dict from json).
        user_labels (dict):  Labels of kubernetes object.
        user_annotations (dict): Annotations of kubernetes object.

    Returns:
        None
    """
    v1 = client.CoreV1Api()

    name = args_.grafana_dashboards_cm_name
    namespace = args_.namespace

    labels = {}
    if len(jsons) > 0:
        labels = get_labels(
            user_labels,
            user_annotations,
            args_.jsonnet_dashboards_selector,
            args_.grafana_label,
        )

    data = {}
    for filename, json_data in jsons:
        data[filename] = json.dumps(json_data)

    metadata = client.V1ObjectMeta(name=name, namespace=namespace, labels=labels)
    body = client.V1ConfigMap(data=data, metadata=metadata)

    log.info(f"Regenerating dashboards resource {name}")

    name_selector = f"metadata.name={name}"
    cms = v1.list_namespaced_config_map(namespace, field_selector=name_selector)
    if len(cms.items) > 0:
        try:
            v1.replace_namespaced_config_map(name, namespace, body)
        except ApiException as e:
            log.error(f"Error when replacing config map {name}, error {e}")
    else:
        try:
            v1.create_namespaced_config_map(namespace, body)
        except ApiException as e:
            log.error(f"Error when creating config map {name}, error {e}")


def process_cm_data(data, ext_libs=[], user_args={}):
    """Processes data field from jsonnet config map.

    Iterates through jsonnet files in configMap (.libsonnet files first)
    and generates json data.


    Args:
        data (dict): Data from config map labeled as jsonnet code.
        ext_libs (:obj:`list of str`, optional): List of paths to
            external jsonnet libs.
        user_args (:obj:`dict`, optional): Keyword arguments to jsonnet build function.

    Returns:
        list of (str, dict): Generated json data.
    """
    libsonnet_folder = "./libsonnets"
    jsons = []

    # sort by extension: .libsonnet fields first, .jsonnet second
    for dataKey in sorted(data.keys(), key=lambda x: x.split(".")[1], reverse=True):

        _, extension = os.path.splitext(dataKey)
        if extension == ".libsonnet":
            utils.save_text_to_file(libsonnet_folder, dataKey, data[dataKey])
            continue

        try:
            jsonnet_code = data[dataKey]
            json_ = _jsonnet.evaluate_snippet(
                dataKey, jsonnet_code, jpathdir=ext_libs, **user_args
            )
        except RuntimeError as e:
            log.error(f"{dataKey} is not a valid jsonnet, raised error: {e}")
        else:
            json_filename = utils.replace_extension(dataKey, "json")
            jsons.append((json_filename, json.loads(json_)))

    if os.path.exists(libsonnet_folder):
        utils.remove_folder(libsonnet_folder)

    return jsons


def process_cm_binary_data(data, main_jsonnet, ext_libs=[], user_args={}):
    """Process binary_data field from jsonnet configMap.

    Extracts folder, evaluates main_jsonnet file from folder
    and parses it to separate json objects.
    main_jsonnet should generate all jsons in one json file.

    Args:
        data (dict): Binary data from configMap labeled as jsonnet code.
            It should be base64 encoded jsonnet folder (archive).
        main_jsonnet (str): Path in extracted folder to jsonnet file
            that will be evaluated.
        ext_libs (:obj:`list of str`, optional): List of paths to
            external jsonnet libs.
        user_args (:obj:`dict`, optional): Keyword arguments to jsonnet build function.

    Returns:
        list of (str, dict): Generated json data.
    """
    tmp_folder_name = "jsonnet_archive"
    tmp_file_name = "generated_from_archive.json"

    jsons = []
    for dataKey in data.keys():
        filename, extension = os.path.splitext(dataKey)

        if extension not in [
            ".gz",
            ".tar",
            ".zip",
            ".bz2",
            ".7z",
            ".tgz",
            ".rar",
            ".xz",
        ]:
            log.error(f"Unsupported compress format: {dataKey}")
            return

        archive_data = data[dataKey]
        utils.extract_archive_data(archive_data, dataKey, tmp_folder_name)

        jsonnet_filepath = os.path.join(tmp_folder_name, main_jsonnet)
        try:
            json_ = _jsonnet.evaluate_file(
                jsonnet_filepath, jpathdir=ext_libs, **user_args
            )
        except RuntimeError as e:
            log.error(f"{main_jsonnet} is not a valid jsonnet, raised error: {e}")
        else:
            utils.save_text_to_file("./", tmp_file_name, json_)
            dashboards = parse_json_with_files(tmp_file_name)
            jsons.extend(dashboards)

            utils.remove_file("./", tmp_file_name)
            utils.remove_folder(tmp_folder_name)

    return jsons


def regenerate_jsonnets_resources(args_, label_selector):
    """Process jsonnet configMap depending on content.

    Args:
        args_ (argparse.Namespace): Args from ArgumentParser.
        label_selector (str): Label selector of jsonnet resources,
            that should be regenerated. (in format '<label>=<key>')

    Returns:
        None
    """
    external_libraries_paths = [
        "./jsonnet_libs/vendor",
        "./libsonnets",
    ]

    jsons = []
    labels = {}
    annotations = {}

    config_maps = get_config_maps(label_selector)
    for config_map in config_maps.items:

        jsonnet_keywords_args = get_jsonnet_keywords_args(
            config_map.metadata.annotations
        )
        labels.update(config_map.metadata.labels or {})
        annotations.update(config_map.metadata.annotations or {})

        if config_map.data is not None:
            jsons.extend(
                process_cm_data(
                    config_map.data,
                    external_libraries_paths,
                    jsonnet_keywords_args,
                )
            )

        if config_map.binary_data is not None:
            try:
                main_jsonnet = config_map.metadata.annotations["jsonnet_filename"]
            except KeyError:
                log.error(
                    f"ConfigMap {config_map.metadata.name} contains jsonnet archive, "
                    f"but no annotation for main jsonnet file"
                )
            else:
                jsons.extend(
                    process_cm_binary_data(
                        config_map.binary_data,
                        main_jsonnet,
                        external_libraries_paths,
                        jsonnet_keywords_args,
                    )
                )

    if label_selector == args_.jsonnet_rules_selector:
        create_rules_object(args_, jsons, labels, annotations)
    else:
        create_dashboard_cm(args_, jsons, labels, annotations)


def watch_changes(args_, label_selector):
    """Watches jsonnet resources and regenerates on change.

    Args:
        args_ (argparse.Namespace): Args from ArgumentParser.
        label_selector (str): Label selector of jsonnet resources,
            that should be regenerated. (in format '<label>=<key>')

    Return:
        None
    """
    v1 = client.CoreV1Api()
    w = watch.Watch()

    config_maps = get_config_maps(label_selector)
    resource_version = config_maps.metadata.resource_version

    for event in w.stream(
        v1.list_config_map_for_all_namespaces,
        label_selector=label_selector,
        resource_version=resource_version,
    ):
        log.info(f"Event: {event['type']} {event['object'].metadata.name}")
        regenerate_jsonnets_resources(args_, label_selector)


def watch_loop(args_, label_selector):
    """Starts watch loop and processes exceptions.

    Args:
        args_ (argparse.Namespace): Args from ArgumentParser.
        label_selector (str): label selector of k8s resource to watch.
            (in format '<label>=<key>')

    Return:
        None
    """
    initial_run = True
    while True:
        try:
            if initial_run:
                regenerate_jsonnets_resources(args_, label_selector)
                initial_run = False

            # sleep to slow down loop in case of exceptions
            time.sleep(5)
            watch_changes(args_, label_selector)

        except ApiException as e:
            if e.status != 500:
                log.error(f"ApiException when calling kubernetes: {e}")
            else:
                raise

        except ProtocolError as e:
            log.error(f"ProtocolError when calling kubernetes: {e}")

        except MaxRetryError as e:
            log.error(f"MaxRetryError when calling kubernetes: {e}")

        except Exception as e:
            log.error(f"Received unknown exception: {e}\n")


def install_dependencies(libsonnets):
    """Installs libsonnet dependencies.

    Install libsonnets from URLs with jsonnet-bundler.
    (https://github.com/jsonnet-bundler/jsonnet-bundler)
    If lib is installing longer than 15s, process is killed.
    (Because if wrong git URL is given, process waits for credentials.)

    Args:
        libsonnets (list of str): List with URLs to jsonnet libraries.

    Return:
        None
    """
    libs_path = os.environ.get("LIBSONNET_PATH")

    for lib in libsonnets:
        try:
            process = Popen(
                f"jb install --quiet {lib}",
                shell=True,
                cwd=libs_path,
                stdout=PIPE,
                stderr=PIPE,
            )
            outs, errs = process.communicate(timeout=15)
            if errs != b"":
                log.error(f"Failed to install libsonnet {lib}, error: {errs}")
            else:
                log.info(f"Libsonnet library {lib} installed")
        except TimeoutExpired as e:
            process.kill()
            log.error(f"Failed to install libsonnet {lib}, error: {e}")
        except OSError as e:
            log.error(f"Failed to install libsonnet {lib}, error: {e}")


def watch_for_changes(args_):
    """Starts watch processes.

    Starts processes to watch and regenerate jsonnet
    resources - dashboards and rules. In case one process fails,
    the other is terminated.

    Args:
        args_ (argparse.Namespace): Args from ArgumentParser.

    Return:
        None
    """
    dashboard_proc = Process(
        target=watch_loop, args=(args_, args_.jsonnet_dashboards_selector)
    )
    dashboard_proc.daemon = True
    dashboard_proc.start()

    rule_proc = Process(target=watch_loop, args=(args_, args_.jsonnet_rules_selector))
    rule_proc.daemon = True
    rule_proc.start()

    while True:
        if not dashboard_proc.is_alive():
            log.error("Process for dashboards died. Stopping and exiting")
            if rule_proc.is_alive():
                rule_proc.terminate()
            else:
                log.error("Process for rules also died...")
            raise Exception("Loop died")

        if not rule_proc.is_alive():
            log.error("Process for rules died. Stopping and exiting")
            if dashboard_proc.is_alive():
                dashboard_proc.terminate()
            else:
                log.error("Process for dashboards also died...")
            raise Exception("Loop died")

        time.sleep(5)


def main(args_):
    """Installs dependencies, loads kube config and starts watch loop.

    Args:
        args_ (argparse.Namespace): args from ArgumentParser

    Return:
        None
    """
    if args_.dev:
        os.environ['LIBSONNET_PATH'] = './jsonnet_libs'
    install_dependencies(args.libsonnet)

    try:
        config.load_kube_config()
    except config.config_exception.ConfigException:
        config.load_incluster_config()

    watch_for_changes(args_)


if __name__ == "__main__":
    args = get_parser().parse_args()
    main(args)
