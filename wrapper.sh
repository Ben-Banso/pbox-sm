#!/bin/bash

app=$1


case $app in
	api)
		cd sm-api
		python3 server.py;;
	node)
		cd sm-node
		python3 daemon.py;;
	mgmt)
		cd sm-mgmt
		python3 daemon.py;;
	*)
		echo "Unknow app";;
esac
