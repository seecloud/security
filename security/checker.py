# Copyright 2016: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import functools
import importlib
import logging
import time

import schedule

from security import storage  # noqa

SCHEDULE_DELAY = 5


class Checker(object):

    def configure(self, config):
        self.storage = storage.Storage(config["elastic"])
        self.regions = {}
        self.plugins = []
        for region in config["regions"]:
            self.regions[region["name"]] = region
        for plugin_conf in config["plugins"]:
            plugin_module = importlib.import_module(plugin_conf["module"])
            for region_name in plugin_conf["regions"]:
                plugin = plugin_module.Plugin()
                region = self.regions[region_name]
                if region["type"] in plugin.supported_region_types:
                    job = functools.partial(self._discover, plugin,
                                            region)
                    logging.debug("Sceduling job %s %s", plugin, region_name)
                    schedule.every(
                        plugin_conf["checkEveryMinutes"]).seconds.do(job)
                else:
                    logging.warning("Skipping unsupported region type %s by "
                                    "plugin %s", region, plugin_conf["module"])

    def _discover(self, plugin, region):
        logging.info("Discovering region %s by plugin %s", region["name"],
                     plugin)
        issues = plugin.discover(region)
        logging.debug("Issues discovered by plugin %s: %s", plugin, issues)
        self.storage.update_issues(region["name"], issues,
                                   plugin.issue_types)

    def run(self):
        while True:
            logging.debug("Running pending")
            try:
                schedule.run_pending()
            except Exception:
                logging.exception("Error running task")
            time.sleep(SCHEDULE_DELAY)
