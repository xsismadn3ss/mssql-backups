# MSSQL Backups

Herramienta para automatizar la restauración de backups (.bak) en SQL Server.

Este proyecto proporciona utilidades para listar backups, construir la consulta de RESTORE y ejecutar `sqlcmd` para restaurar bases de datos. Está pensado para usarse desde la terminal y usa interacción para pedir la configuración de la base de datos y/o del contenedor.

## Instalación
- Instala uv en tu entorno local usando
```
winget install --id=astral-sh.uv -e
```
- Instala mssql-backups como herramienta con uv
```
uv tool install mssql-backups
```

## Ejecutar herramienta
```
uv tool run mssql-backups
```


## Requisitos

- Python 3.12
- `sqlcmd` (herramienta de cliente de SQL Server / mssql-tools) disponible en la máquina donde se ejecuta el script o en el contenedor de SQL Server.
- Si usas backups ubicados dentro de contenedores Docker, necesitas acceso al daemon de Docker y el paquete `docker` de Python.

## Preparar entorno virtual (usando uv)

Este proyecto utiliza `uv` para crear el entorno virtual y gestionar dependencias. Se recomienda Python 3.12.

Instala uv en tu entorno local usando
```
winget install --id=astral-sh.uv -e
```

Desde el directorio raíz del proyecto (`restore_all`):

```
uv venv .venv
```

`uv` imprimirá en la terminal la instrucción que debes ejecutar para activar el entorno virtual según la consola que estés usando (cmd, PowerShell, bash, etc.). Sigue esa indicación para activar `.venv`.

Si no usas `uv`, puedes crear el venv con:

```
python3.12 -m venv .venv
# luego activa según tu shell, ejemplo en bash:
source .venv/bin/activate
```

## Instalar dependencias (usando uv)

Para sincronizar e instalar las dependencias del proyecto con `uv`, usa:

```
uv sync
```

## Ejecución en modo desarrollo

Una vez activado el entorno virtual, ejecuta la aplicación desde el directorio raíz del proyecto:


```
uv run main.py
```

El flujo típico es:

1. El script pedirá la configuración interactiva (usuario, host, puerto, password y/o datos de contenedor o ruta de backups).
2. Listará los backups disponibles.
3. Para cada backup, ejecutará `RESTORE FILELISTONLY` para detectar nombres lógicos y luego construirá y ejecutará la consulta `RESTORE DATABASE ... WITH MOVE ...` mediante `sqlcmd`.
4. Mostrará el resultado de cada restauración en la consola.


## Recomendaciones y consideraciones

- Asegúrate de que SQL Server (o el contenedor donde corre) tenga acceso al archivo `.bak` en la ruta que indicas. Si SQL Server corre en un contenedor, la ruta debe ser la ruta dentro del contenedor o un volumen montado.
- `sqlcmd` debe estar disponible en el PATH del entorno donde se ejecuta la aplicación. En Linux, instala `mssql-tools` para obtener `sqlcmd`.
- Si la restauración falla por nombres lógicos (error 3234), el script ejecuta `RESTORE FILELISTONLY` para obtener los `LogicalName` correctos. Si eso falla, revisa manualmente el contenido del `.bak` usando `sqlcmd`.
- Evita exponer contraseñas en variables de entorno o procesos visibles. Usa mecanismos seguros (archivos con permisos restringidos, vaults, autenticación integrada) cuando sea posible.
