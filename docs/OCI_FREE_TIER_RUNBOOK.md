# OCI Free Tier: arquitectura y runbook

## Arquitectura

- Una VM ARM `VM.Standard.A1.Flex` con 1 OCPU y 6 GB de RAM.
- Boot volume de 50 GB, VCN y public subnet.
- Solo 22 desde la IP administrativa y 80/443 públicos.
- Caddy termina HTTPS; API, dashboard y PostgreSQL permanecen en la red Docker.
- Object Storage usa principal de instancia y un bucket privado.

Antes de aplicar Terraform, confirmar en la consola que la forma, almacenamiento y bucket sean **Always Free eligible**. Terraform no crea recursos adicionales ni activa servicios pagos.

## Aprovisionamiento

1. Instalar Terraform y configurar autenticación del provider OCI.
2. Copiar `terraform.tfvars.example` como `terraform.tfvars` fuera de Git.
3. Ejecutar `terraform init`, `terraform plan` y revisar que solo aparezcan los recursos documentados.
4. Ejecutar `terraform apply` y apuntar el DNS del dominio al `public_ip`.
5. Clonar el repositorio en `/opt/communitylab` como usuario `opc`.
6. Copiar `deploy/.env.production.example` a `deploy/.env.production`, completar valores y ejecutar `chmod 600`.
7. Ejecutar `docker compose -f deploy/compose.prod.yml up -d --build`.

## IAM para Object Storage

Crear un dynamic group que incluya la instancia y una policy limitada al bucket de CommunityLab. No usar claves API dentro del contenedor.

## Respaldo y recuperación

Programar `deploy/backup.sh` diariamente mediante cron. Copiar backups cifrados fuera de la VM. Para restaurar: descomprimir y canalizar a `psql` en el contenedor DB antes de levantar API/dashboard.

## Validación

Ejecutar `deploy/smoke-test.sh https://DOMINIO`. Verificar health, documentación HTTPS, carga de dataset, aprobación y manifest. Revisar `docker compose ps` y logs sin secretos.

## Rollback

Conservar la imagen/commit anterior, ejecutar `git checkout <commit>` y reconstruir. Las migraciones destructivas requieren backup y un downgrade probado previamente.
