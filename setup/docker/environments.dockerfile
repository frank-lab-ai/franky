FROM tiangolo/uwsgi-nginx-flask:python3.8


### MRO (From https://hub.docker.com/r/nuest/mro 4.0.2 and tidyverse version)

## (Based on https://github.com/rocker-org/rocker/blob/master/r-base/Dockerfile)
## Set a default user. Available via runtime flag `--user docker`
## Add user to 'staff' group, granting them write privileges to /usr/local/lib/R/site.library
## User should also have & own a home directory (e.g. for linked volumes to work properly).
RUN useradd docker \
	&& mkdir /home/docker \
	&& chown docker:docker /home/docker \
	&& addgroup docker staff
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
	&& apt-get update && apt-get install -y locales \
	&& locale-gen en_US.utf8 \
	&& /usr/sbin/update-locale LANG=en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

# Install some useful tools and dependencies for MRO
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		ca-certificates \
		curl \
		build-essential \
		gfortran \
		# needed on Ubuntu 20.04
		libtinfo5 \
		# MRO dependencies that don't sort themselves out on their own:
		less \
		libgomp1 \
		libpango-1.0-0 \
		libxt6 \
		libsm6 \
		# Needed for Rcpp:
		make \
		g++ \
	&& rm -rf /var/lib/apt/lists/*

# Use major and minor vars to re-use them in non-interactive installation script
ENV MRO_VERSION_MAJOR 4
ENV MRO_VERSION_MINOR 0
ENV MRO_VERSION_BUGFIX 2
ENV MRO_VERSION $MRO_VERSION_MAJOR.$MRO_VERSION_MINOR.$MRO_VERSION_BUGFIX
ENV R_HOME=/opt/microsoft/ropen/$MRO_VERSION/lib64/R

WORKDIR /home/docker

## Donwload and install MRO & MKL, see https://mran.microsoft.com/download https://mran.blob.core.windows.net/install/mro/4.0.2/microsoft-r-open-4.0.2.tar.gz
RUN curl -LO -# https://mran.blob.core.windows.net/install/mro/$MRO_VERSION/Ubuntu/microsoft-r-open-$MRO_VERSION.tar.gz \
	&& tar -xzf microsoft-r-open-$MRO_VERSION.tar.gz
RUN tar -xzf microsoft-r-open-$MRO_VERSION.tar.gz
WORKDIR /home/docker/microsoft-r-open
RUN  ./install.sh -a -u
# Clean up downloaded files
WORKDIR /home/docker
RUN rm microsoft-r-open-*.tar.gz \
	&& rm -r microsoft-r-open

# Add Rcpp because it is widely used
RUN Rscript -e 'install.packages("Rcpp")'
# Use libcurl for download, otherwise problems with tar files
RUN echo 'options("download.file.method" = "libcurl")' >> /opt/microsoft/ropen/$MRO_VERSION/lib64/R/etc/Rprofile.site



### Install Specific Packages

# R
RUN Rscript -e 'install.packages(c("tidyverse", "dplyr", "devtools", "formatR", "remotes", "selectr", "caTools", "BiocManager", "rstan", "rstanarm", "ggfortify", "stats", "MASS", "betareg"))'

# Python
RUN pip3 install mysqlclient requests pymongo==3.10.1 flask_httpauth flask_cors numpy pandas spacy redis neo4j sklearn matplotlib keras tensorflow py2neo GPy-ABCD Graph-State-Machine
RUN python3 -m spacy download en


