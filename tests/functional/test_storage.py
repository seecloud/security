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

import os
import time
import unittest

import mock

from security.plugins import fake
from security import storage


class ElasticTestCase(unittest.TestCase):

    def assertNewIssue(self, issue):
        msg = "Issue %s is not new (%s, %s)" % (issue, issue.discovered_at,
                                                issue.confirmed_at)
        self.assertEqual(issue.discovered_at, issue.confirmed_at, msg)
        self.assertIsNone(issue.resolved_at, "Issue %s is not new" % issue)

    def assertConfirmedIssue(self, issue):
        args = (issue, issue.discovered_at, issue.confirmed_at)
        self.assertTrue(issue.discovered_at < issue.confirmed_at,
                        "Issue %s is not confirmed (%s>=%s)" % args)
        self.assertIsNone(issue.resolved_at)

    @unittest.skipIf("SC_ELASTIC_URL" not in os.environ,
                     "$SC_ELASTIC_URL is not set")
    @mock.patch("security.storage.LOG")
    def test_update_issues(self, mock_logging):
        config = {
            "type": "elastic",
            "hosts": [os.environ["SC_ELASTIC_URL"]],
        }

        s = storage.Storage(config)
        plugin = fake.Plugin()
        region = {"name": "region1"}

        try:
            s.backend.es.indices.delete("ms_security_region1")
        except Exception:
            pass

        def run():
            s.update_issues(region["name"], plugin.discover(region),
                            plugin.issue_types)
            time.sleep(4)  # need some time for elastic to update data

            mapping = {}
            for issue in s.backend.get_issues(region["name"],
                                              plugin.issue_types):
                mapping[issue.type + issue.id] = issue
            for key, val in mapping.items():
                print(key, val)
            print("---")
            return mapping

        i = run()
        self.assertEqual(4, len(i))
        for key, issue in i.items():
            self.assertNewIssue(issue)

        i = run()
        self.assertEqual(4, len(i))
        self.assertConfirmedIssue(i["testType1id-1"])
        self.assertConfirmedIssue(i["testType2id-2"])
        self.assertConfirmedIssue(i["testType2id-3"])
        self.assertNewIssue(i["testType2id-4"])

        i = run()
        self.assertEqual(5, len(i))
        self.assertNewIssue(i["testType1id-0"])  # Rediscovered
        self.assertConfirmedIssue(i["testType1id-1"])
        self.assertConfirmedIssue(i["testType2id-2"])
        self.assertConfirmedIssue(i["testType2id-3"])
        self.assertConfirmedIssue(i["testType2id-4"])

        i = run()
        self.assertEqual(4, len(i))
        self.assertConfirmedIssue(i["testType1id-0"])
        self.assertConfirmedIssue(i["testType1id-1"])
        self.assertConfirmedIssue(i["testType2id-2"])
        self.assertConfirmedIssue(i["testType2id-3"])

        print(mock_logging.mock_calls)
        s.backend.es.indices.delete("ms_security_region1")
