# Manual de usuario de CommunityLab

## 1. Propósito

CommunityLab transforma interacciones de una comunidad en análisis,
oportunidades, alertas internas y borradores de contenido para LinkedIn y FAQ.
Los borradores pasan por revisión humana antes de aprobarse o publicarse.

## 2. Acceso

- Entorno local: http://localhost:8501
- Demostración pública: https://communitylab-dashboard.onrender.com

En Render gratuito, la aplicación puede tardar cerca de un minuto en responder
después de un período sin uso. La demostración pública puede estar configurada
en modo sólo lectura; las operaciones de carga y curaduría se realizan en local
o en un entorno compartido autorizado.

## 3. Pantalla principal

La cabecera informa si la API y PostgreSQL están disponibles. Antes de procesar
un archivo, completar:

- **Organización:** agrupador general de las comunidades.
- **Comunidad:** espacio dentro del cual se aplica la deduplicación.
- **Período de referencia:** etiqueta temporal del lote.
- **Archivo:** JSON o CSV con las interacciones.

Usar nombres de comunidad estables para datos reales. Para pruebas aisladas,
usar nombres diferentes evita que cargas anteriores sean contabilizadas como
duplicados.

## 4. Formato de entrada

La aplicación acepta `.json` y `.csv`. Cada interacción necesita, como mínimo,
autor, canal, tipo, texto y fecha conforme al ejemplo elegido. Los nombres
canónicos son `author`, `channel`, `type` y `text`; también se admiten los alias
documentados en [sets de prueba](sets_pruebas/README.md).

El CSV debe guardarse preferentemente como UTF-8. También se admite
Windows-1252. No cargar archivos de salida ni manifests.

## 5. Procesar un archivo

1. Completar organización, comunidad y período.
2. Seleccionar el archivo JSON o CSV.
3. Presionar **Procesar archivo**.
4. Esperar hasta que aparezca el resumen. No volver a presionar el botón durante
   el procesamiento.
5. Copiar el **Run ID** para consultas y soporte.

El resumen diferencia registros recibidos, aceptados, duplicados y erróneos. Un
duplicado significa que esa interacción ya existe en la misma comunidad; no es
un error del sistema.

## 6. Interpretar los resultados

- **Resumen:** estado, cantidades, sentimiento predominante, temas frecuentes y
  tiempo de procesamiento.
- **Análisis:** clasificación, sentimiento, relevancia, confianza y evidencia de
  cada interacción.
- **Oportunidades:** casos útiles para contenido o atención. Los casos internos
  o sensibles pueden aparecer bloqueados.
- **Alertas internas:** problemas, frustración o sentimiento negativo que deben
  atenderse sin convertirlos automáticamente en contenido público.
- **LinkedIn y FAQ:** borradores trazables, pendientes de revisión humana.

Los resultados generados por IA pueden variar. La evidencia y las interacciones
fuente deben revisarse antes de aprobar un borrador.

## 7. Consultar por Run ID

1. Ubicar **Consultar ejecución por Run ID**.
2. Pegar el identificador completo.
3. Presionar **Buscar ejecución**.

La aplicación recuperará el resultado persistido. Un mensaje de “no encontrado”
indica normalmente que el ID es incorrecto o pertenece a otra base de datos.

## 8. Revisar y curar activos

La cola **LinkedIn y FAQ** muestra los activos de la ejecución seleccionada. El
botón **Actualizar cola** vuelve a consultar la API.

Estados principales:

| Estado | Significado | Acciones permitidas |
|---|---|---|
| `PENDING_REVIEW` | Espera revisión humana. | Editar, aprobar o rechazar. |
| `APPROVED` | Contenido aprobado e inmutable. | Publicar. |
| `REJECTED` | No debe publicarse en su estado actual. | Puede reeditarse mediante la API para crear una nueva versión pendiente. |

Para editar, modificar el texto visible y guardar. Para aprobar, comprobar antes
la redacción, el canal, la evidencia y que no haya datos personales. Para
rechazar, usar el botón correspondiente; la versión actual registra al revisor
`dashboard`, pero no solicita un motivo adicional.

El dashboard actual retira de la cola los activos aprobados o rechazados. La
publicación y la reedición de un rechazado están disponibles en la API, cuyo
explorador se abre en `http://localhost:8000/docs`; todavía no tienen un botón
propio en la pantalla.

## 9. Privacidad y uso responsable

- No cargar secretos, contraseñas ni credenciales.
- Confirmar que existe autorización para usar interacciones reales.
- Los correos y teléfonos se redactan antes del análisis.
- `opt_out=true` impide generar un activo publicable.
- Sin consentimiento de publicación, el autor se anonimiza.
- Ningún borrador de IA debe publicarse sin revisión humana.

## 10. Cerrar la aplicación local

Conservar los datos:

```powershell
docker compose down
```

Volver a iniciar:

```powershell
docker compose up -d
```

No usar `docker compose down -v` salvo que se quiera eliminar deliberadamente
la base local y repetir las pruebas desde cero.

## 11. Problemas frecuentes

### El dashboard no abre

```powershell
docker compose ps -a
docker compose logs --tail 100 dashboard
docker compose up -d
```

### Aparece “API no disponible”

```powershell
docker compose logs --tail 100 db api
```

Esperar a que PostgreSQL esté saludable y las migraciones terminen. Comprobar
también http://localhost:8000/api/v1/health.

### El procesamiento tarda demasiado

Gemini depende de un servicio externo. Esperar sin volver a enviar el archivo y
revisar los logs del worker. Para una prueba determinista, usar el proveedor
`mock`.

### Todos los registros aparecen duplicados

El archivo ya fue procesado para esa comunidad. Cambiar el nombre de comunidad
para una prueba limpia o mantenerlo si se quiere verificar deduplicación.

### No se puede aprobar, rechazar o publicar

El entorno puede estar en modo sólo lectura o requerir una clave. En local,
comprobar `MUTATIONS_ENABLED=true` en `.env` y reconstruir los servicios si se
modificó la configuración.

### Cómo pedir soporte

Informar el Run ID, archivo utilizado, comunidad, hora aproximada y mensaje de
error. Nunca enviar `.env`, claves API ni credenciales.

## 12. Prueba guiada

Para ejecutar una validación completa con los archivos incluidos en el
repositorio, seguir la [guía de prueba funcional](GUIA_PRUEBA_FUNCIONAL.md).
