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

import argparse
import os
import sys
import logging
import yaml

from security.checker import Checker


def checker():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str,
                        help=("config file. defaults to $SECURITY_CHECKER_CONF"
                              " environment variable"))
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    filename = args.config
    if not filename:
        filename = os.environ.get("SECURITY_CHECKER_CONF")
        if not filename:
            sys.stderr.write("Error: no config file provided\n")
            parser.print_usage()
    _checker = Checker()
    logging.debug("Loading config")
    config = yaml.safe_load(open(filename))
    _checker.configure(config)
    logging.info("Entering loop")
    _checker.run()
