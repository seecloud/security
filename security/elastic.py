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
import json
import logging

import elasticsearch
from elasticsearch import helpers

from security import base

INDEX = "ms_security_"
ELASTIC_DATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss Z"
PY_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S +00"


def elastic_to_issue(dict_):
    for attr in ("discovered_at", "confirmed_at", "resolved_at"):
        value = dict_.get(attr)
        if value:
            dict_[attr] = datetime.datetime.strptime(value, PY_DATETIME_FORMAT)
    return dict_


def issue_to_elastic(issue):
    dict_ = {
        "description": issue.description,
        "subject": issue.subject,
        "region": issue.region,
        "discovered_at": issue.discovered_at.strftime(PY_DATETIME_FORMAT),
        "confirmed_at": issue.confirmed_at.strftime(PY_DATETIME_FORMAT),
    }
    if issue.resolved_at:
        dict_["resolved_at"] = issue.resolved_at.strftime(PY_DATETIME_FORMAT)
    return dict_


class StorageException(Exception):
    pass


class Backend(object):
    """Represent elasticsearch backend.

    usage:
        b = elastic.Backend(urls=["url1", "url2"])
        issues = b.get_issues("Region1", "IssueType1,IssueType2")
        b.begin()
        b.store_issue(Issue(...))
        b.commit("region1")
    """

    def __init__(self, urls, **kwargs):
        self.index = INDEX
        self.es = elasticsearch.Elasticsearch(urls)
        self.body = []

    def get_issues(self, region, types=None, discovered_days=None):
        query = {
            "query": {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": "resolved_at",
                        },
                    },
                },
            }
        }
        if discovered_days:
            query["query"]["bool"]["must"] = {
                "range": {
                    "discovered_at": {"gte": "now-%dd/h" % discovered_days}
                }
            }
        issues = []
        try:
            for i in helpers.scan(self.es, index=self.index + region,
                                  doc_type=types, query=query, scroll="1m"):
                kwargs = i["_source"]
                kwargs = elastic_to_issue(kwargs)
                kwargs["region"] = region
                kwargs["type_"] = i["_type"]
                logging.debug("Loaded issue %s" % kwargs)
                issues.append(base.Issue(**kwargs))
            return issues
        except elasticsearch.NotFoundError:
            return []

    def begin(self):
        if self.body:
            logging.warning("Unsaved data %s", self.body)
        self.body = ""

    def commit(self, region):
        if not region:
            raise StorageException("Missing region")
        try:
            self.es.indices.create(index=self.index + region, body={
                "mappings": {
                    "_default_": {
                        "properties": {
                            "region": {
                                "type": "text",
                            },
                            "description": {
                                "type": "text",
                            },
                            "discovered_at": {
                                "type": "date",
                                "format": ELASTIC_DATETIME_FORMAT,
                            },
                            "confirmed_at": {
                                "type": "date",
                                "format": ELASTIC_DATETIME_FORMAT,
                            },
                            "resolved_at": {
                                "type": "date",
                                "format": ELASTIC_DATETIME_FORMAT,
                            },
                        }
                    }
                }
            })
        except elasticsearch.RequestError as ex:
            if ex.error != "index_already_exists_exception":
                raise
        retval = self.es.bulk(self.body, self.index + region)
        self.body = ""
        try:
            for item in retval["items"]:
                if not (200 <= item["index"]["status"] <= 201):
                    raise KeyError
        except KeyError:
            raise StorageException(
                "Failed to create some items: %s" % retval)

        return retval

    def store(self, issue):
        self.body += json.dumps({"index": {
            "_type": issue.type,
            "_id": issue.id,
        }}) + "\n"
        self.body += json.dumps(issue_to_elastic(issue)) + "\n"
