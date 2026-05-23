---
description: "Use when: need MatchPoint global context before a task"
name: "MatchPoint Contexto Global"
argument-hint: "Tarea o pregunta a resolver despues de cargar el contexto"
agent: "agent"
---

CONTEXTO GLOBAL - leer antes de cualquier tarea:

Proyecto: MatchPoint - Sistema de reservas de padel, ranking y penalizaciones.

Arquitectura: Microservicios con Arquitectura Hexagonal por servicio.
- MS-BookingManager (Core): FastAPI + PostgreSQL 16 (asyncpg + SQLAlchemy 2 async)
- MS-Identity (Sincrono REST): FastAPI + MySQL 8 (aiomysql + SQLAlchemy 2 async)
- MS-PenaltyRank (Asincrono): FastAPI + MongoDB 7 (Motor async)
- Broker: RabbitMQ 3.13 (aio-pika)
- Gateway: Nginx (proxy reverso, sin logica de negocio)
- Observabilidad: Prometheus (prometheus-client), Grafana, Jaeger (OpenTelemetry OTLP/gRPC)

Reglas de negocio:
1. Reserva Premium (18:00-22:00): requiere membresia activa validada sincronicamente en MS-Identity ANTES de crear la reserva.
2. Cancelacion tardia (<2h antes): MS-BookingManager publica evento "reservation.cancelled.late" en RabbitMQ -> MS-PenaltyRank lo consume y aplica penalizacion "Baja Confiabilidad" por 1 semana -> publica "user.restricted" -> MS-Identity lo consume y actualiza estado.
3. Reserva Ranked: MS-BookingManager consulta sincronicamente MS-PenaltyRank para obtener niveles de los jugadores. Si la diferencia supera 2.0, rechaza la reserva.

Principios de codigo:
- Python 3.12, tipo-anotado al 100%, sin Any salvo justificacion.
- SOLID aplicado: cada clase tiene una sola responsabilidad, dependencias inyectadas por constructor.
- Inversion de dependencias: el dominio define interfaces (ABC), la infraestructura las implementa.
- Sin ORM en la capa de dominio; entidades son dataclasses o Pydantic BaseModel puros.
- Cada microservicio vive en su propio directorio con su propio Dockerfile y requirements.txt.
- Variables de entorno con pydantic-settings (BaseSettings), nunca hardcodeadas.
- Todos los endpoints documentados con OpenAPI (FastAPI lo genera automaticamente).
- Metricas en /metrics (prometheus-client).
- Trazas con opentelemetry-sdk + opentelemetry-instrumentation-fastapi + exporter OTLP gRPC.

Usa este contexto como fuente de verdad para cualquier decision de diseno o implementacion. Si hay conflicto con la tarea, pide aclaracion.

Tarea solicitada:
{{$input}}
