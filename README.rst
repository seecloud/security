Security Monitoring Service
###########################

Configuration
*************

Config file is a single yaml file. Configuration may be specified via --config option or ``$SECURITY_CHECKER_CONF`` environment variable.

.. code-block::

    regions:
      - type: openstack
        name: region1
        credentials:
          auth_url: http://example.net:5000/
          username: admin
          password: admin
          tenant: admin
          
    elastic:
      - host: example.com
        port: 9200
      
    plugins:
      - module: security.plugins.secgroup
        checkEveryMinutes: 1
        regions: ["region1"]

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
