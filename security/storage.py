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

import collections
import datetime
import logging

from security import elastic

LOG = logging.getLogger(__name__)


class Storage:

    def __init__(self, config):
        LOG.debug("Loading backend with config %s", config)
        self.backend = elastic.Backend(**config)

    def update_issues(self, region, issues, issue_types):
        """This method should be called by checker.

        :param region:
        :param issues: generator
        :param issue_types: List of issue types supported by plugin
        """
        now = datetime.datetime.utcnow()
        self.backend.begin()
        issues = list(issues)

        #  Create mapping of discovered issues
        discovered_issues = collections.defaultdict(dict)
        for issue in issues:
            discovered_issues[issue.type][issue.id] = issue

        #  Get all issues from backend
        stored_issues = collections.defaultdict(dict)
        for issue in self.backend.get_issues(region, issue_types):
            stored_issues[issue.type][issue.id] = issue
            #  Check if issue had been resolved
            if issue.id not in discovered_issues[issue.type]:
                LOG.info("Resolved issue %s", issue)
                issue.resolved_at = now
                LOG.debug("(discovered %s)", issue.discovered_at)
                self.backend.store(issue)

        #  Update known issues
        for issue in issues:
            LOG.debug("Checking known issue %s", issue)
            LOG.debug("DICT %s", issue.to_dict())
            stored = stored_issues[issue.type].get(issue.id)
            if stored:
                LOG.debug("Updating known issue %s (%s)",
                          issue, issue.discovered_at)
                issue.discovered_at = stored.discovered_at
                issue.confirmed_at = now
            else:
                LOG.info("Storing new issue %s", issue)
                issue.discovered_at = now
                issue.confirmed_at = now
            self.backend.store(issue)
        if self.backend.body:
            self.backend.commit(region)
        else:
            LOG.debug("No issues found at the %s region", region)
