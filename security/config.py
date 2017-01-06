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

API_DEFAULT_CONF_PATH = "/etc/oss/security/api.yaml"
CHECKER_DEFAULT_CONF_PATH = "/etc/oss/security/checker.yaml"

DEFAULT = {
    "regions": [],
    "elastic": {
        "hosts": [],
    },
    "plugins": [],
}

SCHEMA = {
    "regions": {
        "type": "array",
        "items": {
            "type": "object",
            "uniqueItems": True,
            "properties": {
                "type": {
                    "type": "string",
                    "minLength": 1,
                },
                "name": {
                    "type": "string",
                    "minLength": 1,
                },
                "credentials": {
                    "type": "object",
                    "properties": {
                        "auth_url": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "username": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "password": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "tenant_name": {
                            "type": "string",
                            "minLength": 1,
                        },
                    },
                    "required": ["auth_url", "username", "password",
                                 "tenant_name"],
                    "additionalProperties": False,
                },
                "cacert": {"type": "string"},
                "insecure": {"type": "boolean"},
                "interface": {
                    "type": "string",
                    "oneOf": [
                        {"enum": ["public", "internal", "admin"]},
                        {"enum": ["publicURL", "internalURL", "adminURL"]},
                    ],
                },
                "endpoint_override": {"format": "uri"},
            },
            "required": ["type", "name", "credentials"],
            "additionalProperties": False,
        },
    },
    "plugins": {
        "type": "array",
        "uniqueItems": True,
        "items": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "minLength": 1,
                },
                "checkEveryMinutes": {"type": "integer"},
                "regions": {
                    "type": "array",
                    "uniqueItems": True,
                    "minLenth": 1,
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
            },
            "required": ["module", "checkEveryMinutes", "regions"],
            "additionalProperties": False,
        },
    },
    "elastic": {
        "type": "object",
        "properties": {
            "hosts": {
                "type": "array",
                "uniqueItems": True,
                "items": {
                    "type": "object",
                    "properties": {
                        "host": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "port": {"type": "integer"},
                    },
                    "required": ["host"],
                    "additionalProperties": False,
                },
            },
            "http_auth": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 2,
            },
            "port": {"type": "integer"},
            "use_ssl": {"type": "boolean"},
            "ca_certs": {
                "type": "string",
                "minLength": 1,
            },
            "client_cert": {
                "type": "string",
                "minLength": 1,
            },
            "client_key": {
                "type": "string",
                "minLength": 1,
            },
        },
        "required": ["hosts"],
        "additionalProperties": False,
    },
}
