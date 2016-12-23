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

import datetime
import os
import time
import unittest

import mock

from security import base
from security import elastic


def store(backend, type_, id_, discovered_at=None, confirmed_at=None,
          region="region1"):
    return backend.store(base.Issue(id_, type_, region,
                                    "Test issue %s" % type_,
                                    discovered_at=discovered_at,
                                    confirmed_at=confirmed_at))


class ElasticTestCase(unittest.TestCase):

    @unittest.skipIf("SC_ELASTIC_URL" not in os.environ,
                     "$SC_ELASTIC_URL is not set")
    def test_create_and_get(self):
        now = datetime.datetime.now()
        days3 = now - datetime.timedelta(days=3)
        days8 = now - datetime.timedelta(days=8)
        b = elastic.Backend(hosts=[os.environ["SC_ELASTIC_URL"]])
        for reg in ("region1", "region2"):
            try:
                b.es.indices.delete(reg)
            except Exception:
                pass
        self.assertEqual([], b.get_issues("region1"))
        b.begin()
        store(b, "Type1", "id1", discovered_at=now, confirmed_at=now)
        store(b, "Type2", "id2", discovered_at=now, confirmed_at=now)
        store(b, "Type2", "id3", discovered_at=days3, confirmed_at=now)
        store(b, "Type2", "id4", discovered_at=days8, confirmed_at=now)
        b.commit("region1")
        time.sleep(1)  # elastic needs some time to update
        # get all
        issues = [i.to_dict() for i in b.get_issues("region1")]
        self.assertEqual(4, len(issues))
        # get day
        issues = [i.to_dict() for i in b.get_issues("region1",
                                                    discovered_days=1)]
        self.assertEqual(2, len(issues))
        # get Type2
        issues = [i.to_dict() for i in b.get_issues("region1", ["Type2"])]
        self.assertEqual(3, len(issues))
        # get Type1 and Type2
        issues = [i.to_dict() for i in b.get_issues("region1",
                                                    ["Type1", "Type2"])]
        self.assertEqual(4, len(issues))

        # test get from multiple regions
        b.begin()
        store(b, "Type1", "id1", discovered_at=now, confirmed_at=now,
              region="region2")
        b.commit("region2")
        time.sleep(1)
        issues = [i.to_dict() for i in b.get_issues()]
        issue = {
            "description": "Test issue Type1",
            "confirmed_at": mock.ANY,
            "region": "region2",
            "discovered_at": mock.ANY,
            "type": "Type1",
            "id": "id1",
        }
        self.assertIn(issue, issues)
        self.assertEqual(5, len(issues))
