# Setup

## 1. Python 3

Solo hace falta Python 3.10+ (aquí 3.12.3). **No se instala ninguna librería**: el script usa la stdlib (`json`, `zipfile`, `urllib`, `datetime`).

```bash
python3 --version
```

**Por qué sin librerías:** menos cosas que instalar = menos cosas que romper. `requests` sería más cómodo que `urllib`, pero para ~450 peticiones GET no compensa una dependencia.

## 2. El export de Playmax

En Playmax: Perfil → Ajustes → Exportar datos. Descarga un ZIP tipo `playmax-userdata-DD-MM-YYYY-HH-MM-SS.zip`. No hace falta descomprimirlo: el script lo lee directamente.

## 3. Client ID de Trakt (obligatorio)

Showly identifica todo por **Trakt ID** y Playmax no lo trae. Para traducirlo hay que preguntar a la API de Trakt, que exige una clave.

1. Entra en https://trakt.tv y crea cuenta (gratis) si no tienes.
2. Ve a **https://app.trakt.tv/settings/apps/api/new** (formulario *Create an app*).
   > ⚠️ Muchas guías dicen `trakt.tv/oauth/applications` → *New Application*. Esa página ya no muestra el botón: Trakt movió los ajustes de API a `app.trakt.tv` (ver 05_ERRORES, E9).
3. Rellena:
   | Campo | Valor |
   |---|---|
   | App name | `playmax-to-showly` (cualquiera) |
   | Description | vacío |
   | App type | **Development** (tú y hasta 16 personas; sin pedir aprobación a Trakt) |
   | Redirect URIs | `http://localhost` (obligatorio, pero el script no lo usa: no hay login) |
   | Allowed origins | vacío |
4. Crea la app. En su página copia el **Client ID**. El *Client Secret* NO hace falta: no lo compartas.
5. Pásalo al script como variable de entorno, nunca escrito en el código. `read -s` la pide sin mostrarla en pantalla ni dejarla en el historial:

```bash
read -s -p "Trakt Client ID: " TRAKT_CLIENT_ID && export TRAKT_CLIENT_ID && echo
```

**Por qué variable de entorno:** si la clave va en el código, acaba en git o en un pantallazo. En el entorno solo vive en tu terminal.

## 4. Showly en el móvil

Necesitas una versión de Showly con **Ajustes → Backup → Importar** (scheme v2, código de 2026). Showly lee el archivo con el selector de archivos de Android, así que basta con copiarlo a `Descargas/` del móvil.

## 5. ADB (opcional)

Solo para copiar el archivo al móvil desde el PC (`adb push`). También vale pasarlo por cable/Drive/Telegram.

```bash
adb devices
```
