FROM golang:1.13 as builder
WORKDIR /app
COPY invoke.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -v -o server

FROM ghcr.io/dbt-labs/dbt-bigquery:1.2.latest
USER root
WORKDIR /dbt
COPY --from=builder /app/server ./
COPY script.sh ./
COPY . ./

ENTRYPOINT "./server"