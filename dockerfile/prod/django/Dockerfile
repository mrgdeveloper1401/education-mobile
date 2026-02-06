FROM education_mobile:2.0.0

WORKDIR /home/app

COPY .. .

RUN chmod +x ./scripts/*

EXPOSE 8000

ENTRYPOINT ["/home/app/scripts/start.sh"]
