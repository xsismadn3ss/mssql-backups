# MSSQL Backups

[![PyPI Version](https://img.shields.io/pypi/v/mssql-backups)](https://pypi.org/project/mssql-backups/)
[![Package Site](https://img.shields.io/badge/package-PyPI-blue)](https://pypi.org/project/mssql-backups/)
[![DeepWiki](https://img.shields.io/badge/DeepWiki-Indexed-00AEEF)](https://deepwiki.com/xsismadn3ss/mssql-backups)

Herramienta de consola para administrar configuraciones, crear backups, restaurar bases de datos de SQL Server y limpiar logs para liberar espacio.

La aplicación guarda la configuración en SQLite, ejecuta `sqlcmd` para hablar con SQL Server y puede trabajar con rutas locales o con backups dentro de contenedores Docker.

## Requisitos

- `uv`
- `sqlcmd` disponible en el sistema

## Instalación de la herramienta

1. Instala `uv`:

```bash
winget install --id=astral-sh.uv -e
```

2. Instala la herramienta:

```bash
uv tool install mssql-backups
```

3. Verifica que esté disponible:

```bash
uv tool run mssql-backups --help
```

## Configurar `sqlcmd`

La herramienta necesita `sqlcmd` para ejecutar consultas y realizar backups/restauraciones.

### Windows

Instálalo con:

```bash
winget install sqlcmd
```

### Linux

En Linux debes instalar los paquetes oficiales de Microsoft para `sqlcmd`.

Recomendación general:

1. Agrega el repositorio oficial de Microsoft para tu distribución.
2. Instala `mssql-tools18` junto con `unixODBC`.
3. Añade el binario al `PATH` de tu shell.

Ejemplo común en Bash:

```bash
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
source ~/.bashrc
```

Si usas Ubuntu o Debian, sigue la guía oficial de Microsoft para tu versión e instala también `unixodbc-dev`.

## Comandos principales

Los comandos principales de la herramienta son:

| Comando | Descripción |
| --- | --- |
| `config` | Administrar configuraciones guardadas en cache |
| `restore` | Restaurar bases de datos usando backups guardados |
| `cache` | Crear o limpiar la caché local |
| `db` | Probar conexiones, listar bases de datos y reducir logs |
| `bak` | Crear backups de las bases de datos configuradas |

Para obtener ayuda de cualquier comando o subcomando, usa `--help`.
Muchos comandos también son interactivos: si omites un parámetro, la herramienta te lo pedirá en pantalla.

```bash
mssql-backups --help
mssql-backups config --help
mssql-backups restore --help
mssql-backups cache --help
mssql-backups db --help
mssql-backups bak --help
```

## Cómo configurar la aplicación

La configuración se guarda en SQLite dentro de `~/.mssql-bakups/config.db`. Esto permite persistir las configuraciones entre sesiones para evitar tener que configurar todo de nuevo.

### 1. Crear una conexión

Usa `config conn add` para guardar la conexión a SQL Server.

```bash
mssql-backups config conn add
```

Ese comando te pedirá de forma interactiva:

- nombre de la conexión
- host
- puerto
- usuario
- contraseña

También puedes consultar o eliminar conexiones con:

```bash
mssql-backups config conn ls
mssql-backups config conn rm
```

### 2. Crear una configuración de backup

Usa `config bak add` para guardar la ruta de backups y la ruta de datos.

```bash
mssql-backups config bak add
```

Ese comando te pedirá:

- nombre de la configuración
- descripción
- `backup_dir`
- `data_dir`
- si usa contenedor Docker
- nombre del contenedor, si corresponde

Si el backup está dentro de un contenedor, las rutas deben ser rutas válidas dentro del contenedor.

También puedes listar o eliminar configuraciones con:

```bash
mssql-backups config bak ls
mssql-backups config bak rm
```

### 3. Asociar bases de datos a una configuración

Usa `config db add` para registrar una o varias bases de datos dentro de una configuración de backup.

```bash
mssql-backups config db add
```

Puedes ingresar varias bases separadas por comas.

También puedes listar o eliminar asociaciones con:

```bash
mssql-backups config db ls
mssql-backups config db rm
```

## Flujo de uso recomendado

0. Inicializa la caché con `cache init`.
1. Guarda la conexión con `config conn add`.
2. Guarda la configuración de backup con `config bak add`.
3. Registra las bases de datos con `config db add`.
4. Verifica la conexión con `db test --conn mi-conexion`.
5. Crea backups con `bak start --conn mi-conexion --name mi-backup`.
6. Si necesitas restaurar, usa `restore files --conn mi-conexion --bak mi-backup` y luego `restore begin --conn mi-conexion --bak mi-backup`.

## Comandos útiles

### Backups

```bash
mssql-backups bak start --conn mi-conexion --name mi-backup
```

Este comando crea un backup por cada base de datos configurada y guarda los archivos en una carpeta con fecha dentro de `backup_dir`.

### Restauración

```bash
mssql-backups restore files --conn mi-conexion --bak mi-backup
mssql-backups restore begin --conn mi-conexion --bak mi-backup
```

- `restore files` lista los archivos `.bak` disponibles.
- `restore begin` ejecuta la restauración.

### Base de datos

```bash
mssql-backups db test --conn mi-conexion
mssql-backups db ls --conn mi-conexion
mssql-backups db logs reduce --conn mi-conexion --bak mi-backup --threshold 1GB --target 100MB
```

- `db test` valida la conexión.
- `db ls` lista las bases de datos disponibles.
- `db logs reduce` reduce archivos `.ldf` que superen el umbral configurado.

### Caché

```bash
mssql-backups cache init
mssql-backups cache clean
```

- `cache init` crea la caché local.
- `cache clean` la elimina.

## Notas importantes

- Antes de usar los comandos que dependen de la configuración guardada, inicializa la caché con `mssql-backups cache init`.
- Para trabajar con contenedores, Docker debe estar instalado y en ejecución.
- Asegúrate de que SQL Server pueda leer los archivos `.bak` cuando uses rutas locales.
- Si un comando no te queda claro, usa siempre `--help` en el comando o subcomando correspondiente.
