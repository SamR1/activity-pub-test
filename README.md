# activity-pub-test

Minimal [ActivityPub](https://www.w3.org/TR/activitypub/) server to learn about this protocol.  
Python version of '[How to implement a basic ActivityPub server](https://blog.joinmastodon.org/2018/06/how-to-implement-a-basic-activitypub-server/)' by Eugen Rochko.   

## How-To

* Install Python dependencies
```shell script
$ make install
```

* Create **Makefile.custom.config** file and update user name you want to use and your server domain:  
```shell script
$ cp Makefile.custom.config.example Makefile.custom.config
$ nano Makefile.custom.config
```

* Start the server:  
```shell script
$ make serve
```

* To submit a reply to a toot, for instance to answer the toot in Eugen article:
```shell script
$ curl -d '{ "message" : "Hi!" , "host": "mastodon.social", "toot": "@Gargron/100254678717223630"}' -H "Content-Type: application/json" -X POST https://<domain>/note
```
where `domain` is your ActivityPub server domain.