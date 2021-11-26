# FROM tiangolo/uwsgi-nginx-flask:python3.8

# RUN apt-get update
# # RUN apt-get install -y python3-pip python3-dev
# RUN pip3 install mysqlclient requests pymongo==3.10.1 flask_httpauth flask_cors numpy pandas spacy redis neo4j GPy sklearn matplotlib keras tensorflow py2neo networkx plotly pyld bs4 GPy_ABCD Graph_State_Machine
# RUN python3 -m spacy download en

# ## Install additional Python or R packages below (see which ones are already in frank-base-envs)
# # RUN Rscript -e 'install.packages(c("PACKAGE_NAME", "ANOTHER"))'
# # RUN pip3 install PACKAGE_NAME ANOTHER

FROM frank_envs

RUN mkdir -p /app/logs/uwsgi
COPY ./ /app

RUN mkdir /SMART
COPY ../../../../SMART /SMART
RUN pip3 install -e '/SMART'