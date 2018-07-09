2 actors

camilla is lovely
graham is a cad

3 scenarios

1. normal service
* camilla pass checks and creates account
* graham fails check and has no account

2. slow /checks service
* camilla same
* graham is told account created but then fails check and no account

no /checks service
* camilla same
* graham is told account created but account is marked pending check

4 components

* a js client that thumbs up/down when persons are added
* a process api that talks to client
* a checks service that knows about graham (and camilla)
* an accounts service that logs everything

