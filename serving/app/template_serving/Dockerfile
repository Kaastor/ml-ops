FROM python:3.8-slim-bullseye

COPY ./requirements.txt .

RUN pip install -r ./requirements.txt

CMD mkdir demo_serving

COPY . ./demo_serving

RUN chmod 777 -R /tmp

EXPOSE 8000

# enables logging 'print' to output in Pod's logs
ENV PYTHONUNBUFFERED=1

# needed for proper module discovery by python
ENV PYTHONPATH=/

ENTRYPOINT python -m demo_serving.app.main
