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

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S +00"


class Issue(object):
    __slots__ = ("type", "description", "region", "id", "tenant_id",
                 "user_id", "data", "discovered_at", "confirmed_at",
                 "resolved_at")

    def __init__(self, _id, _type, region, description,
                 tenant_id=None, user_id=None, data=None,
                 discovered_at=None,
                 confirmed_at=None,
                 resolved_at=None):
        self.id = _id
        self.type = _type
        self.description = description
        self.region = region
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.data = data

        self.discovered_at = discovered_at
        self.confirmed_at = confirmed_at
        self.resolved_at = resolved_at

    def to_dict(self):
        dict_ = {}
        for field in self.__slots__:
            value = getattr(self, field)
            if value is not None:
                if hasattr(value, "strftime"):
                    dict_[field] = value.strftime(DATETIME_FORMAT)
                else:
                    dict_[field] = value
        return dict_

    def __unicode__(self):
        return "<Issue %s region:%s id:%s)>" % (self.type, self.region,
                                                self.id)

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
