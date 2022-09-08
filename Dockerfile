FROM python:3.9-slim

# additional repositories for fonts
RUN sed -i'.bak' 's/$/ contrib/' /etc/apt/sources.list

# install linux packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget git poppler-utils ttf-mscorefonts-installer && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

# install TeX packages
COPY texlive-profile.txt /tmp
RUN wget http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz; \
    mkdir /install-tl-unx; \
    tar -xvf install-tl-unx.tar.gz -C /install-tl-unx --strip-components=1; \
    echo "selected_scheme scheme-basic" >> /install-tl-unx/texlive.profile; \
    /install-tl-unx/install-tl -profile /tmp/texlive-profile.txt; \
    rm -r /install-tl-unx; \
    rm install-tl-unx.tar.gz
ENV PATH=/usr/local/texlive/bin/x86_64-linux:$PATH
RUN tlmgr install preview varwidth standalone xkeyval

ENV PYTHONUNBUFFERED 1

# install Python packages
RUN python -m pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# clone the repo
RUN git clone https://github.com/Snaptraks/physbot.git
WORKDIR /physbot

COPY start.sh ./
# give permission to execute start script
RUN chmod +x start.sh

# copy config files
COPY config.py ./
COPY lexique_physique_filtre.txt ./

# start the Bot
CMD ["./start.sh"]
# CMD ["python", "PhysBot.py"]
