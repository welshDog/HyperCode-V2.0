FROM golang:1.21-alpine AS build
WORKDIR /app
COPY go.mod .
RUN go mod download
COPY . .
RUN go build -o /roundtrip-worker

FROM alpine:3.19
COPY --from=build /roundtrip-worker /usr/local/bin/roundtrip-worker
EXPOSE 9100
ENTRYPOINT ["/usr/local/bin/roundtrip-worker"]

