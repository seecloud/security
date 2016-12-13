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

import abc

import six


class Issue(object):
    __slots__ = ("type", "description", "subject", "discovered_at",
                 "confirmed_at", "resolved_at", "region", "id")

    def __init__(self, type_, description, subject, region, discovered_at=None,
                 confirmed_at=None, resolved_at=None):
        self.type = type_
        self.description = description
        self.subject = subject
        self.region = region

        self.discovered_at = discovered_at
        self.confirmed_at = confirmed_at
        self.resolved_at = resolved_at

        self.id = subject["id"]

    def to_dict(self):
        dict_ = {
            "type": self.type,
            "description": self.description,
            "subject": self.subject,
            "region": self.region,
            "discoveredAt": self.discovered_at.isoformat(),
            "confirmedAt": self.confirmed_at.isoformat(),
        }
        if self.resolved_at:
            dict_["resolvedAt"] = self.resolved_at.isoformat()
        return dict_

    def __unicode__(self):
        return "<Issue %s %s>" % (self.type, self.id)

    __repr__ = __str__ = __unicode__


@six.add_metaclass(abc.ABCMeta)
class Plugin(object):

    @abc.abstractproperty
    def supported_region_types(self):
        pass

    @abc.abstractproperty
    def issue_types(self):
        pass

    @abc.abstractmethod
    def discover(self, region):
        """Discover given region

        :returns: list of Issue instances
        """
        pass
