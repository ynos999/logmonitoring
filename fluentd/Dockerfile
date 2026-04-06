FROM fluent/fluentd:v1.16-debian-1

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ruby-dev && \
    gem install fluent-plugin-kafka --no-document && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
USER fluent
