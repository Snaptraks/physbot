FROM python:3.8-slim

# install linux packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget git poppler-utils && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

# install TeX packages
COPY texlive-profile.txt /tmp
RUN wget http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz && \
    tar -xzf install-tl-unx.tar.gz && \
    install-tl-20*/install-tl --profile=/tmp/texlive-profile.txt && \
    rm -rf install-tl-*
ENV PATH=/usr/local/texlive/bin/x86_64-linux:$PATH
RUN tlmgr install preview varwidth amsmath

WORKDIR .

ENV PYTHONUNBUFFERED 1

# install Python packages
RUN python -m pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# clone the repo
RUN git clone https://github.com/Snaptraks/physbot.git
WORKDIR physbot

# give permission to execute start script
RUN chmod +x start.docker.sh

# copy config files
COPY config.py ./
COPY lexique_physique_filtre.txt ./

# start the Bot
CMD ["./start.docker.sh"]
