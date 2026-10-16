# Guía paso a paso para probar CommunityLab

Esta guía permite repetir la prueba funcional desde el dashboard sin necesidad
de usar Swagger ni comandos de API. Para conocer cada pantalla y operación,
consultar también el [manual de usuario](../MANUAL_USUARIO.md).

## 1. Qué archivos se cargan

Sólo se deben seleccionar archivos cuyo nombre comienza con `entrada`. Los
archivos `salida_*` y `manifest*` son referencias para comparar el resultado;
**no se cargan en la aplicación**.

| Orden | Archivo que se carga | Objetivo |
|---:|---|---|
| 1 | `docs/sets_pruebas/set_04_prueba_inicial/entrada_interacciones_25.json` | Recorrido funcional principal con 25 casos variados. |
| 2 | `docs/sets_pruebas/set_04_prueba_inicial/entrada_interacciones_25.csv` | Comprobar lectura CSV, fechas y nombres de campos compatibles. |
| 3 | `docs/sets_pruebas/set_01_empleabilidad_formacion/entrada_60.json` | Probar empleabilidad y formación tecnológica. |
| 4 | `docs/sets_pruebas/set_02_producto_saas/entrada_60.json` | Probar producto SaaS y comunidad técnica. |
| 5 | `docs/sets_pruebas/set_03_sostenibilidad_impacto/entrada_60.json` | Probar sostenibilidad e impacto social. |

Archivos de apoyo que no se cargan:

- `salida_procesada_ejemplo.json` y `salida_esperada_60.json`: ejemplos para
  revisar la forma y el comportamiento esperado. Las cantidades y puntuaciones
  pueden variar cuando se usa Gemini.
- `manifest_ejemplo.json` y `manifest.json`: metadatos, checksums y trazabilidad
  esperada para almacenamiento/publicación.
- Los archivos PNG de `docs/sets_pruebas/evidencia_compatibilidad`: evidencia de
  una ejecución ya realizada.

## 2. Preparar el entorno local

Requisitos: Git, Docker Desktop y los puertos 8000 y 8501 libres.

```powershell
git clone https://github.com/No-Country-simulation/G10-ONE-equipo-14.git
Set-Location G10-ONE-equipo-14
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

El estado esperado es `Up` en `db`, `api`, `worker` y `dashboard`; `db` y `api`
deben aparecer saludables. Abrir:

- Dashboard: http://localhost:8501
- Estado de la API: http://localhost:8000/api/v1/health

La configuración predeterminada usa `ANALYSIS_PROVIDER=mock`, que es rápida y
reproducible. Para probar Gemini, colocar `ANALYSIS_PROVIDER=gemini` y una
`GEMINI_API_KEY` válida únicamente en `.env`, y reconstruir los servicios. No
subir `.env` ni mostrar la clave en capturas.

## 3. Prueba principal: set 04 en JSON

1. Abrir el dashboard.
2. Dejar estos valores o anotar los que se utilicen:
   - **Organización:** `one`.
   - **Comunidad:** `g10-equipo-14`.
   - **Período de referencia:** el valor propuesto por la pantalla.
3. En **Seleccionar archivo**, elegir
   `docs/sets_pruebas/set_04_prueba_inicial/entrada_interacciones_25.json`.
4. Presionar **Procesar archivo** una sola vez y esperar el resultado. Con
   Gemini puede demorar alrededor de uno o dos minutos.
5. Guardar el **Run ID** que muestra la pantalla.
6. Verificar el resumen:
   - 25 interacciones recibidas;
   - 25 aceptadas en una base limpia;
   - ningún error de validación;
   - análisis, oportunidades, alertas y activos visibles en sus pestañas.
7. Revisar que el caso sensible no produzca un activo público y que las alertas
   negativas aparezcan en **Alertas internas**.
8. Abrir **LinkedIn y FAQ** y confirmar que los activos pertenecen al Run ID
   actual. La cola no debe mezclar resultados históricos.

Las cifras exactas de oportunidades, activos, sentimiento y confianza pueden
cambiar con un modelo real. En la ejecución documentada con Gemini se obtuvieron
25 análisis, 25 oportunidades, 15 activos y 4 alertas.

## 4. Recuperar una ejecución

1. Recargar el navegador.
2. Pegar el Run ID guardado en **Consultar ejecución por Run ID**.
3. Presionar **Buscar ejecución**.
4. Confirmar que reaparecen el resumen y las pestañas del mismo procesamiento.

Esto demuestra que el resultado quedó persistido en PostgreSQL y no dependía de
la sesión del navegador.

## 5. Prueba CSV y deduplicación

El JSON y el CSV del set 04 representan el mismo lote. Para separar la prueba
del formato CSV de la prueba de duplicados, se recomienda este orden:

1. Cambiar temporalmente **Comunidad** a `g10-equipo-14-csv`.
2. Cargar `entrada_interacciones_25.csv` y procesarlo.
3. Verificar 25 registros recibidos, lectura correcta de caracteres y fechas, y
   ausencia de errores.
4. Sin cambiar la comunidad, cargar exactamente el mismo CSV por segunda vez.
5. Confirmar que la segunda carga reporta duplicados y no crea interacciones
   nuevas equivalentes.

Si se carga el CSV inmediatamente después del JSON usando la misma comunidad,
es normal que los registros equivalentes se detecten como duplicados. Eso prueba
deduplicación, pero no ofrece una primera ejecución CSV limpia.

## 6. Probar los tres sets de 60 registros

Procesar uno por uno los sets 01, 02 y 03 siguiendo la tabla inicial. Para que
cada resultado sea fácil de identificar, usar comunidades distintas:

| Set | Comunidad sugerida |
|---|---|
| 01 | `prueba-empleabilidad` |
| 02 | `prueba-saas` |
| 03 | `prueba-sostenibilidad` |

En cada ejecución comprobar:

- 60 registros recibidos y analizados;
- los mensajes neutros no generan activos públicos;
- los casos sensibles quedan bloqueados;
- los activos mantienen `source_interaction_ids` y evidencia;
- los resultados corresponden al tema del set cargado.

## 7. Probar la curaduría

Esta parte requiere `MUTATIONS_ENABLED=true`; es el valor local predeterminado.

1. En **LinkedIn y FAQ**, elegir un activo `PENDING_REVIEW`.
2. Editar su contenido y guardar. Confirmar que aumenta la versión.
3. Aprobar un activo pendiente.
4. Rechazar otro. La interfaz registra al revisor `dashboard`; la versión actual
   no solicita un motivo adicional.
5. Verificar que un activo aprobado ya no pueda editarse.
6. La pantalla retira de la cola los activos aprobados o rechazados. La
   publicación de un activo aprobado se valida actualmente mediante la API
   documentada en `http://localhost:8000/docs`; debe devolver un recibo/manifest
   y una repetición debe recuperar el mismo resultado sin duplicarlo.

## 8. Evidencia mínima que se debe guardar

Para una nueva entrega, capturar sin secretos:

1. servicios disponibles;
2. nombre del archivo y resumen de la ejecución;
3. Run ID recuperado;
4. análisis y oportunidades;
5. alertas internas;
6. cola de activos filtrada por la ejecución;
7. ejemplo de aprobación o rechazo, si forma parte del alcance.

Guardar las imágenes numeradas en una nueva carpeta dentro de
`docs/evidence/` o `docs/sets_pruebas/`, agregar un `README.md` con fecha,
entorno, archivo utilizado y resultado, y evitar datos personales o claves.

## 9. Criterio de aprobación

La prueba se considera aprobada cuando la API y PostgreSQL están disponibles,
la carga termina sin errores inesperados, se puede recuperar el Run ID, las
reglas de privacidad y deduplicación funcionan, y cada activo conserva su
trazabilidad. Si se usa Gemini, una variación semántica en el texto no constituye
por sí sola un fallo.

Ante una falla, registrar el archivo, comunidad, Run ID, hora aproximada y el
mensaje mostrado; luego revisar `docker compose logs --tail 200 api worker
dashboard`.
