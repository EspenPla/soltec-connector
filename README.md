# Solteq-microservice


It can be used to connect Solteq to Sesam.
- Support for getting all addresses and organizations
- Support for creating new addresses
- Support for updating existing addresses

**An example of system config**   
```
{
  "_id": "solteq-system",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "LOG_LEVEL": "INFO",
      "batch_size": 500,
      "env": "<environment>",
      "password": "XXXXX",
      "username": "XXXXXX"
    },
    "image": "espenplatou/solteq:test",
    "port": 5000
  },
  "verify_ssl": true
}
```


**An example of input pipe config to participants**  
   ```
{
  "_id": "solteq-addresses-pipe",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "solteq-system",
    "supports_since": true,    
    "url": "/addresses" ## Add parameter "?since=X" to just get the latest X pages
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }
}
```

