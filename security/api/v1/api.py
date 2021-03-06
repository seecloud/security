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

import flask
from oss_lib import config

from security import elastic

CONF = config.CONF

PERIOD_MAP = {
    "day": 1,
    "week": 7,
    "month": 30,
}
bp = flask.Blueprint("issues", __name__)


def get_backend():
    if not hasattr(flask.g, "elastic"):
        flask.g.elastic = elastic.Backend(**CONF["elastic"])
    return flask.g.elastic


def _get_issues(region, period):
    backend = get_backend()
    days = PERIOD_MAP.get(period)
    if not days:
        flask.abort(404)
    issues = backend.get_issues(region, discovered_days=days)
    return [i.to_dict() for i in issues]


@bp.route("/regions", methods=["GET"])
def get_regions():
    backend = get_backend()
    return flask.jsonify({"regions": list(backend.get_regions())})


@bp.route("/region/<region>/security/issues/<period>", methods=["GET"])
def get_issues(region, period):
    return flask.jsonify({"issues": _get_issues(region, period)})


@bp.route("/security/issues/<period>", methods=["GET"])
def get_issues_all_regions(period):
    return flask.jsonify({"issues": _get_issues(None, period)})
