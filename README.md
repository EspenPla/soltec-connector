# elma-microservice


It can be used to import  all participants to Sesam.

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

