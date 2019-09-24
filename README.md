# Microservices and the Saga Pattern

## The actors

camilla is lovely, graham is a cad and diego is unknown

## The scenarios

1. normal service
* camilla is accepted and an account is created
* graham is declined and has no account
* diego's account is undecided

2. The /checks system api is DOWN
* everyone has an account request in a queue

## The architecture

* a happy javascript client that thumbs up when persons are added
* a register experience api that always accepts and sends 204
* an accounts process api that queues or creates depending on the system api
* a checks system api that knows about graham (and camilla)

```
curl -d "person=camilla" -X POST http://localhost:5002/checks

{
  "results": {
    "person": "camilla",
      "pass": true
  }
}
```
