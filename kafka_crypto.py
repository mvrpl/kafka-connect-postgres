import requests
import time
import json
import os
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=os.environ['KAFKA_SEED_BROKERS'],
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username=os.environ['KAFKA_USER'],
    sasl_plain_password=os.environ['KAFKA_PASSWORD'],
    ssl_cafile="ca.pem",
)

try:
    while True:
        preco_agora = requests.get(
            "https://data-api.binance.vision/api/v3/ticker", params={"symbol": "XRPBRL"}
        )
        producer.send("cripto_prices", json.dumps(preco_agora.json()).encode())
        preco_agora = requests.get(
            "https://data-api.binance.vision/api/v3/ticker", params={"symbol": "SOLBRL"}
        )
        producer.send("cripto_prices", json.dumps(preco_agora.json()).encode())
        preco_agora = requests.get(
            "https://data-api.binance.vision/api/v3/ticker", params={"symbol": "BTCBRL"}
        )
        producer.send("cripto_prices", json.dumps(preco_agora.json()).encode())
        time.sleep(15)
finally:
    producer.close()