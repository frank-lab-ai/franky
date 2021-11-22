FROM tiangolo/uwsgi-nginx-flask:python3.8

# (Based on https://hub.docker.com/r/nuest/mro 4.0.2 and tidyverse version and https://github.com/rocker-org/rocker/blob/master/r-base/latest/Dockerfile)


### Pre-installation configuration and tools

# Set a default user. Available via runtime flag `--user docker`
# Add user to 'staff' group, granting them write privileges to /usr/local/lib/R/site.library
# User should also have & own a home directory (e.g. for linked volumes to work properly).
RUN useradd docker \
	&& mkdir /home/docker \
	&& chown docker:docker /home/docker \
	&& addgroup docker staff
RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen \
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
		# MRO dependencies which do not sort themselves out on their own:
		less \
		libgomp1 \
		libpango-1.0-0 \
		libxt6 \
		libsm6 \
		# Needed for Rcpp:
		make \
		g++ \
	&& rm -rf /var/lib/apt/lists/*



### MRO

# Configuration Variables
ENV MRO_VERSION=4.0.2
ENV R_HOME=/opt/microsoft/ropen/$MRO_VERSION/lib64/R
ENV R_PROFILE=/opt/microsoft/ropen/$MRO_VERSION/lib64/R/etc/Rprofile.site
ENV CRAN_SNAPSHOT_DATE=2021-10-01
ENV CRAN_SNAPSHOT="options(repos=c(CRAN='https:\/\/mran.revolutionanalytics.com\/snapshot\/$CRAN_SNAPSHOT_DATE\/',CRANextra='http:\/\/www.stats.ox.ac.uk\/pub\/RWin'))"

# Installation
WORKDIR /home/docker
# Donwload and install MRO & MKL; see https://mran.microsoft.com/download https://mran.blob.core.windows.net/install/mro/4.0.2/microsoft-r-open-4.0.2.tar.gz
RUN curl -LO -# https://mran.blob.core.windows.net/install/mro/$MRO_VERSION/Ubuntu/microsoft-r-open-$MRO_VERSION.tar.gz \
	&& tar -xzf microsoft-r-open-$MRO_VERSION.tar.gz
RUN tar -xzf microsoft-r-open-$MRO_VERSION.tar.gz
WORKDIR /home/docker/microsoft-r-open
RUN  ./install.sh -a -u
# Clean up downloaded files
WORKDIR /home/docker
RUN rm microsoft-r-open-*.tar.gz \
	&& rm -r microsoft-r-open

# Profile changes and groundwork for installation of packages
RUN sed -i "s/repos\.date <- .*$/repos.date <- '$CRAN_SNAPSHOT_DATE'/" $R_PROFILE
RUN sed -i "s/options(repos=r)$/$CRAN_SNAPSHOT/" $R_PROFILE
# Use libcurl for download, otherwise problems with tar files
RUN echo "options('download.file.method' = 'libcurl')" >> $R_PROFILE
# Add Rcpp first since it may be used in other package installations
RUN Rscript -e "install.packages('Rcpp')"



### R Packages

# "Mute" the R startup since it ends up in the middle of a g++ command
RUN sed -i "s/cat(/cat('') #/" $R_PROFILE

# Extra C++ compiler configuration and alias (required at least for rstan)
RUN mkdir ~/.R \
    && echo "CXX14FLAGS=-O3 -march=native -mtune=native -fPIC\nCXX14=/usr/bin/g++" >> ~/.R/Makevars
# Respectively used in devtools and rstan installations
RUN apt-get -y install libgit2-dev libv8-dev

# Generic useful packages
RUN Rscript -e "install.packages(c('devtools', 'formatR', 'remotes', 'selectr', 'caTools', 'BiocManager'))"

## Arbitrary packages
# metap dependency
RUN Rscript -e "BiocManager::install('multtest')"
RUN Rscript -e "install.packages(c('tidyverse', 'corrr', 'broom', 'moderndive', 'MASS', 'stats', 'lme4', 'mgcv', 'betareg', 'nnet', 'zoo', 'forecast', 'stinepack', 'smooth', 'ggfortify', 'gridExtra', 'rstan', 'rstanarm', 'metap', 'lmtest'))"

# "Unmute" the R startup
RUN sed -i "s/cat('') #/cat(/" $R_PROFILE



### Python Packages
RUN pip3 install mysqlclient requests pymongo==3.10.1 flask_httpauth flask_cors numpy pandas spacy redis neo4j sklearn matplotlib keras tensorflow py2neo GPy-ABCD Graph-State-Machine
RUN python3 -m spacy download en


