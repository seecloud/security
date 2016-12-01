# Security Monitoring Service

## HTTP API

### Requests

#### List Issues For Region

    GET /issues/<region>/

Return list of *Issue* objects

Example:

	GET /issues/Region1/

```javascript
    [
    	{
            "issueType": "SecurityGroupTooOpen",
            "description": "Security group too open",
            "regionId": "Region1",
            "discoveredAt": "2016-02-28T16:41:41.090Z",
            "confirmedAt": "2016-03-28T16:41:41.090Z",
            "subject": {
              "id": "d8b0be7c-2ad7-4083-8d5a-a7a9a56fdd14",
              "type": "securityGroup",
              "tenantId": "demo",
              "userId": "demo"
        }
    ]
```

## Configuration

Config file is a single yaml file. Configuration may be specified via --config option or `$SECURITY_CHECKER_CONF` environment variable.

```yaml
regions:
  - type: openstack
    name: region1
    credentials:
      auth_url: http://example.net:5000/
      username: admin
      password: admin
      tenant: admin

storage:
  url: http://elastic:9200/

plugins:
  - module: security.plugins.secgroup
    checkEveryMinutes: 1
    regions: ["region1"]
```

## Plugin API

Plugin should define class `Plugin` in own module. This class should be subclass of `security.base.Plugin`.

This class must define method `discover(region)`. This method should return list of `security.base.Issue` instances.

Also attribute `supported_region_types` should be defined by plugin class.

Example:

```python
from security import base


class Plugin(base.Plugin):
    supported_region_types = {"dummy"}

    def discover(self, region):
        return [
            base.Issue("dummyIssue", "Sample issue", {"id": "fake-id-1"}),
            base.Issue("dummyIssue", "Sample issue", {"id": "fake-id-2"}),
        ]
```
