FROM frank-base-envs

## Install additional Python or R packages below (see which ones are already in frank-base-envs)
# RUN Rscript -e 'install.packages(c("PACKAGE_NAME", "ANOTHER"))'
# RUN pip3 install PACKAGE_NAME ANOTHER

RUN mkdir -p /app/logs/uwsgi
COPY ./ /app