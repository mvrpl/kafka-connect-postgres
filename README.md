# Kafka para PostgreSQL

Este projeto consulta preços de criptomoedas na API da Binance, publica os eventos em um tópico Kafka e usa o Redpanda Connect para gravá-los no PostgreSQL.

## Pré-requisitos

- Python 3.10 ou superior
- Node.js e `dotenvx`
- Redpanda Connect (`redpanda-connect`)
- Acesso a um cluster Kafka com SASL/SSL
- PostgreSQL acessível pela aplicação
- Certificado da autoridade certificadora do Kafka salvo como `ca.pem` na raiz do projeto

O arquivo `ca.pem` é obrigatório. Ele é usado pelo produtor Python e pelo Redpanda Connect para validar o certificado do broker Kafka. Solicite o certificado CA ao administrador do cluster e não o substitua por um certificado aleatório.

## Configuração do `.env`

Crie um arquivo `.env` na raiz do projeto. Não versionar esse arquivo, pois ele contém credenciais.

```dotenv
KAFKA_SEED_BROKERS=broker.example.com:9093
KAFKA_USER=seu_usuario
KAFKA_PASSWORD=sua_senha

DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cripto
```

Variáveis utilizadas:

| Variável | Uso |
| --- | --- |
| `KAFKA_SEED_BROKERS` | Endereço do broker Kafka, incluindo a porta TLS |
| `KAFKA_USER` | Usuário SASL do Kafka |
| `KAFKA_PASSWORD` | Senha SASL do Kafka |
| `DB_USER` | Usuário do PostgreSQL |
| `DB_PASSWORD` | Senha do PostgreSQL |
| `DB_HOST` | Host do PostgreSQL |
| `DB_PORT` | Porta do PostgreSQL |
| `DB_NAME` | Nome do banco de dados |

O tópico Kafka esperado é `cripto_prices`. A tabela PostgreSQL esperada é `cripto_prices`, com as colunas `symbol`, `price` e `price_at`.

### Exemplo de tabela no PostgreSQL

Com `DB_NAME=cripto`, você pode criar a tabela assim:

```sql
CREATE TABLE IF NOT EXISTS public.cripto_prices (
    symbol text NOT NULL,
    price numeric(18,8) NOT NULL,
    price_at timestamptz NOT NULL
);
```

> O Redpanda Connect mapeia os campos do evento Kafka para `symbol`, `price` e `price_at`, em conformidade com a tabela acima.

### Exemplo de evento JSON no tópico Kafka

O produtor publica um payload em formato JSON semelhante a este, vindo da API da Binance:

```json
{
  "symbol": "XRPBRL",
  "priceChange": "0.012345",
  "priceChangePercent": "0.987",
  "weightedAvgPrice": "1.685432",
  "prevClosePrice": "1.670000",
  "lastPrice": "1.682500",
  "lastQty": "12.000000",
  "bidPrice": "1.682100",
  "askPrice": "1.682600",
  "openPrice": "1.670000",
  "highPrice": "1.690000",
  "lowPrice": "1.660000",
  "volume": "123456.789000",
  "quoteVolume": "208000.000000",
  "openTime": 1720000000000,
  "closeTime": 1720003600000,
  "firstId": 123456,
  "lastId": 123789,
  "count": 334
}
```

O pipeline do Redpanda Connect converte esse evento para um INSERT na tabela `cripto_prices`, produzindo algo como:

```json
{
  "symbol": "XRPBRL",
  "price": "1.670000",
  "price_at": "2024-07-05T12:00:00.000Z"
}
```

## Instalação

As instruções e os pacotes abaixo seguem estes repositórios:

- [windows-apps](https://github.com/mvrpl/windows-apps)
- [unix-apps](https://github.com/mvrpl/unix-apps)
- [Redpanda Connect](https://github.com/redpanda-data/connect)

Instale as dependências Python:

```powershell
python -m pip install -r requirements.txt
```

### Windows

Com o [Scoop](https://scoop.sh/) instalado, execute:

```powershell
scoop install redpanda-connect
scoop install dotenvx
```

### macOS/Linux

Com o [Homebrew](https://brew.sh/) instalado, execute:

```bash
brew install dotenvx
brew install redpanda-data/tap/redpanda
```

Confirme que os comandos estão disponíveis:

```bash
dotenvx --version
redpanda-connect --version
```

## Execução

Abra dois terminais na raiz do projeto. No primeiro, inicie o produtor Python usando o `.env` com o `dotenvx`:

```powershell
dotenvx run -- python kafka_crypto.py
```

No segundo, inicie o pipeline do Redpanda Connect usando o mesmo `.env`:

```powershell
redpanda-connect run --env-file .env connect.yaml
```

O produtor publica os preços de `XRPBRL`, `SOLBRL` e `BTCBRL` a cada 15 segundos. O pipeline consome o tópico, transforma os campos e insere os registros no PostgreSQL em lotes de até 100 eventos ou a cada 5 segundos.

## Estrutura

- `kafka_crypto.py`: consulta a Binance e publica mensagens no Kafka.
- `connect.yaml`: configura o consumo do Kafka e a gravação no PostgreSQL.
- `ca.pem`: certificado CA usado na conexão TLS com o Kafka.
- `.env`: credenciais e endereços locais, mantido fora do controle de versão.
