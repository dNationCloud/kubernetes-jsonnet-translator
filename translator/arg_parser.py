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

from argparse import ArgumentParser
import yaml


def get_defaults():

    with open("./default_config.yaml", "r") as f:
        defaults = yaml.load(f, Loader=yaml.FullLoader)

    return defaults


def get_parser():

    defaults = get_defaults()

    parser = ArgumentParser(
        description="Jsonnet translator, for creating grafana dashboards "
                    "and prometheus rules from jsonnet."
    )

    parser.add_argument(
        "--namespace",
        type=str,
        default=defaults["namespace"],
        help="Namespace for generated objects, default: 'default'",
    )

    parser.add_argument(
        "--jsonnet_dashboards_selector",
        type=str,
        default=defaults["jsonnet_dashboards_selector"],
        help="Selector of dashboards jsonnet config maps in format: "
             "'<label>=<value>', default: 'grafana_dashboard_jsonnet=1'",
    )

    parser.add_argument(
        "--jsonnet_rules_selector",
        type=str,
        default=defaults["jsonnet_rules_selector"],
        help="Selector of rules jsonnet config maps in format: "
             "'<label>=<value>', default: 'prometheus_rule_jsonnet=1'",
    )

    parser.add_argument(
        "--grafana_dashboards_cm_name",
        type=str,
        default=defaults["grafana_dashboards_cm_name"],
        help="Name of config map with generated dashboards, "
             "default: 'grafana-dashboards-generated'",
    )

    parser.add_argument(
        "--prometheus_rules_object_name",
        type=str,
        default=defaults["prometheus_rules_object_name"],
        help="Name of prometheus rules object with generated rules, "
             "default: 'prometheus-rules-generated'",
    )

    parser.add_argument(
        "--grafana_label",
        type=str,
        default=defaults["grafana_label"],
        help="Field in annotations, which defines label of grafana dashboards "
             "in format: '<label>=<value>', default: 'grafana_label'",
    )

    parser.add_argument(
        "--prometheus_label",
        type=str,
        default=defaults["prometheus_label"],
        help="Field in annotations, which defines label of prometheus rules "
             "in format: '<label>=<value>', default: 'prometheus_label'",
    )

    parser.add_argument(
        "--libsonnet",
        type=str,
        nargs="+",
        default=[],
        help="URLs to libsonnet libs, divided by space",
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Set if running outside docker",
    )

    return parser
