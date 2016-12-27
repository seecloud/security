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

import logging

from security import base

from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client

LOG = logging.getLogger(__name__)

UNSAFE_RULES = [
    {
        "protocol": ("0", "tcp", "udp"),
        "remote_ip_prefix": (None, "0.0.0.0/0"),
        "port_range_min": None,
        "port_range_max": None,
    },
]


def match_rule(pattern, rule):
    for field, value in pattern.items():
        if isinstance(value, tuple):
            if rule[field] not in value:
                return False
        else:
            if rule[field] != value:
                return False
    return True


class Plugin(base.Plugin):
    supported_region_types = {"openstack"}
    issue_types = ("SecurityGroupTooOpen", )

    def discover(self, region):
        issues = []
        auth = identity.Password(**region["credentials"])
        sess_kwargs = {"auth": auth}
        cacert = region.get("cacert")
        if cacert:
            sess_kwargs["verify"] = cacert
        sess = session.Session(**sess_kwargs)
        neutron = client.Client(session=sess)
        for sg in neutron.list_security_groups()["security_groups"]:
            LOG.debug("Checking security group %s", sg["name"])
            for rule in sg["security_group_rules"]:
                fmt = ("Rule %(direction)s [%(ethertype)s/%(protocol)s] "
                       "%(remote_ip_prefix)s "
                       "%(port_range_min)s:%(port_range_max)s")
                LOG.debug(fmt, rule)
                for pattern in UNSAFE_RULES:
                    if match_rule(pattern, rule):
                        LOG.info("Unsafe rule found")
                        issue = base.Issue(rule["id"], "SecurityGroupTooOpen",
                                           region["name"],
                                           "Security group too open",
                                           tenant_id=rule["tenant_id"])
                        issues.append(issue)
        return issues
