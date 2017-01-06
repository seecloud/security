Security Monitoring Service
###########################

Checker configuration
*********************

Config file is a single yaml file. Configuration may be specified via
the ``--config-file`` option or the ``$SECURITY_CHECKER_CONF`` environment
variable.

.. code-block::

    regions:
      - type: openstack
        name: region1
        cacert: /etc/cacert.pem
        insecure: false
        credentials:
          auth_url: http://example.net:5000/
          username: admin
          password: admin
          tenant_name: admin

    elastic:
      hosts:
        - host: e1.example.com
          port: 9200
        - host: e2.example.com
          port: 9200
      use_ssl: true
      verify_certs: false

    plugins:
      - module: security.plugins.secgroup
        checkEveryMinutes: 1
        regions: ["region1"]

Regions with the ``openstack`` type can be configured without checking Keystone
certificate with the ``insecure: false`` value, it also means that ``cacert``
is optional and can be omitted.

By default, the Neutron endpoint with the ``public`` interface is used for
security analyses. The type of endpoint can be changed by the ``interface``
parameter with three available values ``public``, ``private`` and ``admin``:

.. code-block::

    regions:
      - type: openstack
        name: region1
        insecure: false
        interface: admin
        credentials:
          auth_url: http://example.net:5000/
          username: admin
          password: admin
          tenant_name: admin

By some reasons, it is valuable not to use ServiceCatalog to determine
the Neutron endpoint but specify it with some certain value. For this case
the ``endpoint_override`` should be used:

.. code-block::

    regions:
      - type: openstack
        name: region1
        insecure: false
        endpoint_override: http://example.net:9696/
        credentials:
          auth_url: http://example.net:5000/
          username: admin
          password: admin
          tenant_name: admin

SSL configuration for CCP
*************************

In case your region requires ssl, CCP config should have additional fields

.. code-block::

    configs:
      elasticsearch:
        hosts:
          - host: e1.example.com
            port: 9200
          - host: e2.example.com
            port: 9200
          - host: e3.example.com
            port: 9200
      security:
        checker:
          regions:
            - type: openstack
              name: region1
              credentials:
                auth_url: http://example.net:5000/
                username: admin
                password: admin
                tenant_name: admin
              use_ssl: true
          plugins:
            - name: secgroup
              checkEveryMinutes: 1
              regions: ["region1"]    

      files:
        region1-key.pem: /opt/key.pem

Service configuration example
*****************************

.. code-block::

    elastic:
      hosts:
        - host: e1.example.com
          port: 9200
        - host: e2.example.com
          port: 9200
      use_ssl: true
      verify_certs: false

Running service
***************

With flask server
=================

.. code-block::

    security-api --config-file /etc/config.yaml

Use ``security-api --help`` for more information.

With gunicorn
=============

.. code-block::

    export SECURITY_CONF=/etc/config.yaml
    gunicorn security.wsgi:application

See `flask documentation <http://flask.pocoo.org/docs/0.11/deploying/wsgi-standalone/>`_ for more information.

Running checker
***************

.. code-block::

    security-checker --config-file /etc/config.yaml

Use ``security-checker --help`` for more information.

Plugin API
**********

Plugin should define class ``Plugin`` in own module. This class should be subclass of ``security.base.Plugin``.

This class must define method ``discover(region)``. This method should return list of ``security.base.Issue`` instances.

Also attribute ``supported_region_types`` should be defined by plugin class.

Example:

.. code-block:: python

    from security import base


    class Plugin(base.Plugin):
        supported_region_types = {"dummy"}

        def discover(self, region):
            return [
                base.Issue("id-1", "Type1", "region1", "Sample issue"),
                base.Issue("id-2", "Type1", "region1", "Sample issue"),
            ]

HTTP API
********

Types
=====

Requests
========

List Issues For Region
----------------------

.. code-block::

    GET /api/v1/region/{region}/issues/{period}

Return list of ``Issue`` objects

Example:

.. code-block::

    GET /api/v1/region/west/issues/day

    [
        {
            "id": "d8b0be7c-2ad7-4083-8d5a-a7a9a56fdd14",
            "type": "SecurityGroupTooOpen",
            "description": "Security group too open",
            "region_id": "Region1",
            "discovered_at": "2016-02-28T16:41:41.090Z",
            "confirmed_at": "2016-03-28T16:41:41.090Z",
        }
    ]
