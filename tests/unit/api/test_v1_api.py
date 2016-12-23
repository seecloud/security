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

from security import app
from tests.unit import test

import ddt
import mock

import json


@ddt.ddt
@mock.patch("security.api.v1.api.get_backend")
class ApiTestCase(test.TestCase):

    def __init__(self, *args, **kwargs):
        super(ApiTestCase, self).__init__(*args, **kwargs)
        self.tc = app.app.test_client

    def _get(self, url):
        with self.tc() as c:
            return json.loads(c.get(url).data.decode("utf8"))

    @ddt.data("day", "week", "month")
    def test_get_issues(self, period, mock_backend):
        issue1, issue2 = mock.Mock(), mock.Mock()
        issue1.to_dict.return_value = "i1"
        issue2.to_dict.return_value = "i2"
        mock_backend.return_value.get_issues.return_value = [issue1, issue2]
        issues = self._get("/api/v1/region/r1/security/issues/" + period)
        expected = {"issues": ["i1", "i2"]}
        self.assertEqual(expected, issues)

    def test_get_regions(self, mock_backend):
        mock_backend.return_value.get_regions.return_value = [1, 2, 3]
        regions = self._get("/api/v1/regions")
        expected = {"regions": [1, 2, 3]}
        self.assertEqual(expected, regions)
