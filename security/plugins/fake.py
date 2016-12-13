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

import itertools

from security import base


class Plugin(base.Plugin):
    supported_region_types = {"openstack"}
    issue_types = ["testType1", "testType2"]

    def __init__(self):
        self._all_issues = []
        for id_, type_ in enumerate(["testType1"] * 2 + ["testType2"] * 3):
            args = ["id-%d" % id_, type_, "Issue %s" % type_]
            self._all_issues.append(args)

        self._call_cycle = itertools.cycle((
            self._all_issues[:-1],
            self._all_issues[1:],
            self._all_issues,
        ))

    def discover(self, region):
        for issue in self._call_cycle.next():
            args = issue[:]
            args.insert(2, region["name"])
            yield base.Issue(*args)
