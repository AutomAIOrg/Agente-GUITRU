# Política de logging (Clean Architecture)

## Objetivo
Definir qué se loguea, con qué nivel y qué contexto mínimo, para mantener trazabilidad consistente sin acoplar la lógica de negocio a librerías concretas.

## Niveles por entorno
- Desarrollo: `debug` habilitado; `info`, `warn`, `error`, `exception` activos.
- Producción: mínimo `info`; `debug` deshabilitado; `warn` para anomalías recuperables; `error/exception` para fallos.

## Contexto mínimo en cada log
- `trace_id`: generado en el punto de entrada y propagado.
- `use_case`: nombre del caso de uso (ej. `ProcessIncomingMessageUseCase`).
- Identificadores de negocio cuando existan: `message_id`, `reservation_id`, `user_id`.
- `action`: operación puntual (ej. `fetch_oldest_message`, `save_message`).

## Qué loguear por caso de uso (ej. ProcessIncomingMessageUseCase)
- Entrada (`info`): `trace_id`, ids conocidos, payload resumido (sin PII, truncado si es largo).
- Validaciones/decisiones (`info` o `warn` si es recuperable): añade `reason`/`field`.
- Llamadas a infraestructura (`debug` en dev; `info` en prod solo si aporta valor de negocio): `action`, `entity_id`, `rows_affected` si aplica.
- Resultado éxito (`info`): `status=success`, ids relevantes.
- Errores de negocio esperados (`error` o `warn` si se maneja): `error_type`, `details` sin PII.
- Excepciones no controladas (`exception`): incluir `trace_id`; el adapter añadirá stacktrace.

## Sanitización
- No loguear PII en claro; redactar o anonimizar (hash) si es necesario.
- Truncar payloads grandes (ej. mensajes > N caracteres).

## Dónde vive el contrato
- El port interno está en `backend/application/logging/logger_port.py`. Los casos de uso y servicios internos dependen solo de este contrato.
- Las implementaciones concretas (adapters) viven en infraestructura y se inyectan vía dependencias.

## Testing
- Usar fakes/spies del port en tests de casos de uso para verificar llamadas y contexto.
- Tests del adapter para formato, nivel y manejo de excepciones.
