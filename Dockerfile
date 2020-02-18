FROM python:3.8-slim-buster

ADD sm-api/ sm-api/
ADD sm-node/ sm-node/
ADD sm-mgmt/ sm-mgmt/

ADD wrapper.sh

ENTRYPOINT ["wrapper.sh"]
CMD ["api"]
