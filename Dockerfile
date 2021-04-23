FROM python:3.8

WORKDIR /app

# Required for TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

ADD rsibot .

RUN pip install -r requirements.txt

ADD entrypoint.sh .

ENTRYPOINT [ "/app/entrypoint.sh" ]
