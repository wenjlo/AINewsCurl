FROM python:3.11.9
RUN apt-get update && apt-get -y install cron vim
WORKDIR /app
ADD . /app


#RUN apt-get install -y wget
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
#    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update

RUN apt-get -y install google-chrome-stable

RUN apt install dos2unix
RUN find -type f -print0 | xargs -0 dos2unix
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python3", "api.py"]
#COPY crontab /etc/cron.d/schedule-cron
#COPY entrypoint.sh /entrypoint.sh
#RUN touch /var/log/cron.log
#RUN chmod 0644 /etc/cron.d/schedule-cron \
#    && chmod +x /entrypoint.sh \
#    && crontab /etc/cron.d/schedule-cron
#ENTRYPOINT ["/entrypoint.sh"]
#
##
##CMD cron && tail -f /var/log/cron.log
#CMD ["cron","&&","tail","-f","/var/log/cron.log"]
