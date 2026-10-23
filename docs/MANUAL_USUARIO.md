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

Mientras la API despierta, el dashboard muestra **Conectando con el servicio** y
reintenta cada 15 segundos. Al recuperar la conexión, actualiza el estado y
habilita las acciones automáticamente, sin necesidad de recargar la página.
Si pasan dos minutos sin conectar, muestra un aviso y el botón **Reintentar
conexión**; continúa comprobando una vez por minuto mientras la sesión esté
activa. Los campos y resultados de la sesión se conservan durante la reconexión.

## 3. Pantalla principal

La barra lateral concentra el estado de la API y PostgreSQL en indicadores de
solo lectura. También incluye una ayuda de inicio, enlaces a este manual, la
guía de prueba, los archivos de ejemplo, Swagger y el repositorio. Esos datos no
son campos de entrada y no admiten escritura.

La cabecera presenta el propósito de CommunityLab. Antes de procesar un archivo,
completar únicamente los campos funcionales:

- **Organización:** identifica a quién pertenecen los datos y permite separarlos
  de los de otras organizaciones. Por ejemplo, `one`.
- **Comunidad:** identifica el grupo que se analiza. También delimita la
  detección de duplicados: una interacción repetida se compara dentro de la misma
  comunidad. Por ejemplo, `g10-equipo-14`.
- **Período de referencia:** indica a qué semana o ciclo corresponde la carga y
  facilita su seguimiento en el tiempo. Por ejemplo, `2026-W42` representa la
  semana 42 de 2026.
- **Archivo:** JSON o CSV con las interacciones.

Los tres primeros valores no se deducen del archivo de interacciones. El usuario
debe completarlos para aportar contexto, separar correctamente los datos y
conservar la trazabilidad de cada ejecución. La misma explicación está disponible
en la ayuda lateral del dashboard.

Usar nombres de comunidad estables para datos reales. Si se vuelve a cargar el
mismo archivo en esa comunidad, se crea una ejecucion nueva y se vuelve a enviar
el contenido a la IA; las interacciones ya guardadas no se insertan otra vez.
Para pruebas aisladas que necesiten datos independientes, usar otra comunidad.

Los resúmenes, métricas, Run ID, análisis, oportunidades y evidencias son
elementos de visualización. Las alertas pendientes pueden marcarse como
resueltas mediante su botón. En la cola de curaduría, únicamente
el título y el contenido del borrador pendiente son editables porque el botón
**Guardar** persiste esos cambios.

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

Si el mismo nombre de archivo ya fue procesado para la Organización y Comunidad
seleccionadas, el dashboard pregunta qué hacer:

- **Recuperar ejecución existente:** muestra el resultado anterior sin volver a
  procesar ni modificar registros.
- **Procesar nuevamente y actualizar resultados:** crea un Run nuevo, conserva
  una sola copia de cada interacción ya almacenada y vuelve a generar sus
  análisis, oportunidades y borradores.

La detección automática aplica a cargas realizadas desde esta versión, porque
las ejecuciones anteriores no conservaban el nombre original del archivo.

El resumen diferencia registros recibidos, aceptados, duplicados, reprocesados y
erróneos. Un duplicado significa que la interacción ya existe en la comunidad;
reprocesada indica que volvió a enviarse a la IA en esta ejecución. No es un
error del sistema.

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

La pestaña **Alertas internas** muestra primero las **Alertas del análisis
actual**, correspondientes a la ejecución recién procesada o recuperada. Debajo,
el desplegable **Historial de alertas**, cerrado por defecto, reúne las alertas de
las demás ejecuciones, sin repetir las del análisis actual. Muestra 10 alertas
por página, de más recientes a más antiguas, con botones **Anterior** y
**Siguiente** y un indicador de página y registros. Los botones **Todas**,
**Pendientes** y **Resueltas** filtran el historial e indican cuántas alertas hay
en cada grupo. La paginación se aplica al filtro seleccionado. Al cambiar de
filtro, de ejecución o actualizar las alertas, vuelve a la primera página.
Resolver una alerta actualiza los contadores y la retira del filtro de pendientes.
Si no hay una ejecución
abierta, el desplegable permite consultar todo el historial registrado. Este
historial abarca todas las ejecuciones, sin aplicar los filtros del selector de
recuperación.

Cada alerta indica su estado con un badge: **Pendiente** (`OPEN`) en ámbar o
**Resuelta** (`RESOLVED`) en verde. La prioridad aparece en otro badge, junto al
estado. El comentario original es el contenido principal de la tarjeta y muestra
hasta tres líneas. El pie incluye la fecha de detección en hora de Santiago y el
archivo de origen, cuando esos datos están disponibles. **Ver detalles** despliega
el comentario completo, el motivo, la referencia y el Run ID. El botón verde
**Resolver** permanece a la derecha y permite resolver una alerta pendiente, tanto del análisis
actual como del historial. El cambio se guarda en la base de datos y actualiza
el badge y los contadores. **Actualizar alertas** consulta nuevamente los estados
persistidos. Si la consulta falla, las alertas del análisis siguen visibles con
una advertencia de que corresponden al resultado guardado.

La API expone `POST /api/v1/alerts/{alert_id}/resolve`, con la misma protección
de acceso que las demás operaciones de escritura. Repetir la operación mantiene
la alerta resuelta. Todavía no hay campo de observaciones ni operación para
reabrir alertas.

## 7. Recuperar una ejecución

1. Ubicar **Recuperar una ejecución**.
2. Filtrar opcionalmente por **Organización** y **Comunidad**.
3. Elegir una opción de la lista. Cada etiqueta muestra el nombre del archivo,
   la fecha y, al final, el Run ID completo; por ejemplo,
   `reacciones_LinkedIn_21102026-21102026-36c28c96-0997-438c-bcb8-ef4babcfe677`.
4. Presionar **Abrir ejecución seleccionada**.

Las ejecuciones antiguas que no guardaron el nombre del archivo se identifican
con Comunidad, fecha y Run ID. Si una ejecución no aparece, desplegar **Ingresar
un Run ID manualmente**, pegar el UUID y presionar **Buscar Run ID manual**.

La aplicación recuperará el resultado persistido. Un mensaje de “no encontrado”
indica normalmente que el ID es incorrecto o pertenece a otra base de datos.

## 8. Revisar y curar activos

Las pestanas **LinkedIn** y **FAQ** separan las propuestas de la ejecucion seleccionada. Las FAQ se generan con IA cuando las preguntas recurrentes de un tema alcanzan el umbral configurado. Cada propuesta conserva evidencia y puede editarse manualmente antes de aprobarse. El boton **Actualizar cola** vuelve a consultar la API.

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
- Los borradores de LinkedIn omiten el nombre del autor y se centran en el aprendizaje compartido.
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

Las interacciones ya existen en esa comunidad. La carga debe crear un Run nuevo
y volver a enviarlas a Gemini. Cambiar la comunidad sólo si se necesita otro
conjunto independiente de interacciones.

### No se puede aprobar, rechazar o publicar

El entorno puede estar en modo sólo lectura o requerir una clave. En local,
comprobar `MUTATIONS_ENABLED=true` en `.env` y reconstruir los servicios si se
modificó la configuración.

### Cómo pedir soporte

Informar el Run ID, archivo utilizado, comunidad, hora aproximada y mensaje de
error. Nunca enviar `.env`, claves API ni credenciales.

## 12. Prueba guiada

Para ejecutar una validación completa con los archivos incluidos en el
repositorio, seguir la
[guía de prueba funcional](sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md).
