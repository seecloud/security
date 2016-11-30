# Seecloud Security Service

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
