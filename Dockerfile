FROM python:3.10-slim

ENV RUN_USER phile
ENV RUN_GROUP phile
ENV APP_HOME /home/phile

# Set up a special phile user and group
RUN addgroup --system ${RUN_GROUP} \
    && adduser --disabled-password --gecos "" --home $APP_HOME --ingroup ${RUN_GROUP} ${RUN_USER}

WORKDIR $APP_HOME

COPY app app
COPY philetag.py boot.sh ./
RUN chmod +x boot.sh

RUN chown -Rc ${RUN_USER}:${RUN_GROUP} $APP_HOME
USER ${RUN_USER}
ENV PATH="/home/phile/.local/bin:${PATH}"

RUN python -m venv venv

RUN pip install --upgrade pip && \
    pip install gunicorn mutagen flask flask-bootstrap flask-wtf python-dotenv

ENV FLASK_APP=philetag

CMD ["./boot.sh"]

# Test only
# CMD ["/bin/sh","-c","sleep 600"]
