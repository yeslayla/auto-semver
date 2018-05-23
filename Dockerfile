FROM centos:7

MAINTAINER RightBrain Networks "ops+docker@rightbrainnetworks.com"

RUN yum update -y && yum install -y epel-release

RUN yum install -y git

RUN yum install -y python-pip
RUN pip install --upgrade pip

RUN useradd -d /semver semver
WORKDIR /semver

ADD ./ /semver

RUN python setup.py sdist 
RUN pip install dist/semver-1.0.4.tar.gz

CMD semver && semver_get_version
