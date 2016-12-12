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
    issue_types = ["fakeIssueType1", "fakeIssueType2"]

    _all_issues = [
        ["fakeIssueType1", "Type1 issue", {"id": "fake-id-1"}],
        ["fakeIssueType1", "Type1 issue", {"id": "fake-id-2"}],
        ["fakeIssueType2", "Type2 issue", {"id": "fake-id-1"}],
        ["fakeIssueType2", "Type2 issue", {"id": "fake-id-2"}],
        ["fakeIssueType2", "Type2 issue", {"id": "fake-id-3"}],
    ]
    _call_cycle = itertools.cycle((
        _all_issues[:-1],
        _all_issues[1:],
        _all_issues,
    ))

    def discover(self, region):
        issues = self._call_cycle.next()
        for issue in issues:
            issue.append(region)
        return [base.Issue(*args) for args in issues]
