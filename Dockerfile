FROM python:3.8.5
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /usr/src/app
COPY . .
RUN python -m pip --no-cache-dir install --upgrade pip \
    && python -m pip --no-cache-dir install --requirement requirements.txt \
    && rm requirements.txt
CMD [ "pytest" ]
