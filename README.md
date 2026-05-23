# MatchPoint — Sistema de Reservas de Pádel

Plataforma de microservicios para gestión de reservas, ranking competitivo
y penalizaciones por cancelación tardía.

## Arquitectura
Jugador → Nginx (API Gateway)
├── MS-BookingManager  (Core)      PostgreSQL
├── MS-Identity        (Síncrono)  MySQL
└── MS-PenaltyRank     (Asíncrono) MongoDB
↕
RabbitMQ
↕
Prometheus · Grafana · Jaege

## Reglas de negocio implementadas

| # | Regla | Tipo |
|---|-------|------|
| 1 | Reserva Premium (18-22h) requiere membresía activa | Síncrono |
| 2 | Cancelación < 2h genera penalización "Baja Confiabilidad" | Asíncrono |
| 3 | Reserva Ranked rechazada si diferencia de nivel > 2.0 | Síncrono |

## Requisitos

- Docker & Docker Compose
- Python 3.12 (solo desarrollo local)

## Despliegue

```bash
# 1. Configurar variables
cp .env.example .env

# 2. Levantar todo
docker compose up --build -d

# 3. Verificar estado
docker compose ps
```

## Servicios disponibles

| Servicio | URL | Descripción |
|---------|-----|-------------|
| API Gateway | http://localhost | Punto único de entrada |
| MS-BookingManager | http://localhost/docs | Swagger Core |
| MS-PenaltyRank | http://localhost/penalty/docs | Swagger Ranking |
| RabbitMQ Management | http://localhost:15672 | Usuario: matchpoint |
| Jaeger UI | http://localhost:16686 | Trazas distribuidas |
| Grafana | http://localhost:3000 | Dashboards (admin/admin) |
| Prometheus | http://localhost:9090 | Métricas |

## Health checks

```bash
curl http://localhost/health          # BookingManager
curl http://localhost:8082/health     # Identity
curl http://localhost:8083/health     # PenaltyRank
```

## Smoke test

```bash
pip install httpx
python scripts/smoke_test.py
```

Para habilitar el test de reserva Ranked:

```bash
# Seed de datos de ranking
docker compose exec ms-penalty-rank python scripts/seed_ranks.py

# Correr con los IDs generados
$env:RANK_HIGH_PLAYER_ID="<id-high>"
$env:RANK_LOW_PLAYER_ID="<id-low>"
python scripts/smoke_test.py
```

## Variables de entorno (.env raíz)

```env
# PostgreSQL
POSTGRES_USER=matchpoint
POSTGRES_PASSWORD=matchpoint
POSTGRES_DB=bookingdb
BOOKING_DATABASE_URL=postgresql+asyncpg://matchpoint:matchpoint@postgres:5432/bookingdb

# MySQL
MYSQL_USER=matchpoint
MYSQL_PASSWORD=matchpoint
MYSQL_ROOT_PASSWORD=matchpointroot
MYSQL_DATABASE=identitydb
IDENTITY_DATABASE_URL=mysql+aiomysql://matchpoint:matchpoint@mysql:3306/identitydb

# MongoDB
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB=penaltyrank

# RabbitMQ
RABBITMQ_DEFAULT_USER=matchpoint
RABBITMQ_DEFAULT_PASS=matchpoint
RABBITMQ_URL=amqp://matchpoint:matchpoint@rabbitmq:5672/

# Microservicios
IDENTITY_SERVICE_URL=http://ms-identity:8082
PENALTY_SERVICE_URL=http://ms-penalty-rank:8083

# Observabilidad
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
GF_SECURITY_ADMIN_PASSWORD=admin
```

## Estructura del proyecto

matchpoint/
├── ms_booking_manager/     # Core — FastAPI + PostgreSQL
├── ms_identity/            # Síncrono — FastAPI + MySQL
├── ms_penalty_rank/        # Asíncrono — FastAPI + MongoDB
├── nginx/                  # API Gateway
├── monitoring/             # Prometheus + Grafana
├── scripts/                # smoke_test.py
├── docker-compose.yml
└── .env.example

## Decisiones arquitectónicas destacadas

- **REST síncrono** hacia MS-Identity y MS-PenaltyRank para validaciones críticas previas a la reserva
- **RabbitMQ asíncrono** para eventos de cancelación tardía — no bloquea la respuesta al usuario
- **Persistencia poliglota** — PostgreSQL (transaccional), MySQL (relacional simple), MongoDB (documentos de auditoría)
- **Arquitectura Hexagonal** por microservicio — dominio sin dependencias de frameworks