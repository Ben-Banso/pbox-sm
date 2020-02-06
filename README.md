# Server Manager

This application let a user to share server that he owns.

## Server API

This program provide an API and a web console to manage a list of servers.

One of its function is to add different servers to the list. To add a server, the user needs to provide a domain name or an IP address, as well as a valid credential (could be password or ssh key).

An other one is to share those servers to other users. To do so he must add the public key of the said user.

## Server manager

This program connects to the servers configured by the user and take a set of actions.

First it register the users in the local database. It will allows the differents users to authenticate and run services.

It then install the requirements for the services to run. Usually docker and the node agent.
