FROM frank_envs

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