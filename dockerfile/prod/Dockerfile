FROM education_mobile:1.0.0

WORKDIR /home/app

COPY . .

RUN chmod +x ./scripts/*

EXPOSE 8000

ENTRYPOINT ["./scripts/start.sh"]
