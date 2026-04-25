# El Tintero — Sistema de Gestión

> Sistema de gestión integral para el **Taller Literario El Tintero** y el emprendimiento de copywriting **Norte Copywriting Solutions**. Desarrollado en Python con CustomTkinter, base de datos local SQLite, sin dependencias en la nube.

---

## Índice

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura de archivos](#estructura-de-archivos)
- [Primer uso](#primer-uso)
- [Módulos del sistema](#módulos-del-sistema)
  - [El Tintero — Taller Literario](#el-tintero--taller-literario)
  - [Norte Copywriting Solutions](#norte-copywriting-solutions)
  - [Configuración](#configuración)
- [Base de datos](#base-de-datos)
- [Tipografía y diseño](#tipografía-y-diseño)
- [Preguntas frecuentes](#preguntas-frecuentes)

---

## Requisitos

| Componente | Versión mínima |
|---|---|
| Python | 3.10 o superior |
| customtkinter | 5.2.0 o superior |
| Pillow | 9.0 o superior |

---

## Instalación

**1. Clonar o descargar el proyecto**

Asegurate de que la carpeta tenga esta estructura antes de continuar (ver [Estructura de archivos](#estructura-de-archivos)).

**2. Instalar dependencias**

```bash
pip install customtkinter pillow
```

**3. Instalar las fuentes** *(opcional pero recomendado)*

El sistema usa **Cormorant Garamond** para títulos y **Nunito** para la interfaz general. Ambas están disponibles gratuitamente en [Google Fonts](https://fonts.google.com). Descargalas e instalálas en el sistema operativo haciendo doble clic sobre los archivos `.ttf`. Si no están instaladas, el programa funciona igual usando fuentes del sistema como alternativa.

**4. Ejecutar**

```bash
python tintero_app.py
```

---

## Estructura de archivos

```
📁 tu_carpeta/
│
├── tintero_app.py              # Aplicación principal
├── tintero.db                  # Base de datos SQLite (se crea automáticamente)
├── tintero_config.json         # Configuración del sistema (se crea en el primer uso)
│
└── 📁 assets/
    ├── Logo_El_Tintero.png                                    # Logo El Tintero
    └── NorteCopywritingSolutions.png                          # Logo Norte Copywriting
```

> La carpeta `assets/` debe estar en el mismo directorio que `tintero_app.py`. Si los logos no se encuentran, el programa funciona normalmente sin mostrarlos.

---

## Primer uso

La primera vez que se ejecuta el programa, como no existe `tintero_config.json`, aparece una **pantalla de configuración inicial** para crear la contraseña de acceso. Esta contraseña se guarda localmente en `tintero_config.json`.

A partir de la segunda ejecución, el sistema muestra directamente la pantalla de login.

> Para **resetear la contraseña manualmente**, borrá el archivo `tintero_config.json` y el sistema volverá al estado de primer uso.

---

## Módulos del sistema

### El Tintero — Taller Literario

#### Alumnos Taller

Gestión completa de los participantes del taller literario.

- Alta, edición y baja de alumnos
- Campos: nombre, email, teléfono, notas, estado activo/inactivo
- Visualización de saldo de cuenta corriente en la lista
- Indicadores visuales de nivel de habilidad

**Nivel de habilidad** — cada alumno tiene 4 habilidades que se marcan como *Pendiente* o *Logrado*, basadas en la metodología del taller:

| Habilidad | Descripción |
|---|---|
| Hábito de escritura | Escritura diaria y constancia |
| Redacción congruente | Claridad y cohesión textual |
| Construcción de trama | Estructura narrativa y dramaturgia |
| Corrección / Publicación | Proceso de revisión y presentación final |

**Test de los 6 Enfoques** — cuestionario de 10 preguntas inspirado en *Taller de corte y corrección* de Marcelo Di Marco. Determina el perfil de escritura del alumno en 6 dimensiones:

| Enfoque | Descripción |
|---|---|
| Narrativa | Inclinación hacia la ficción y el cuento |
| Estética / Poesía | Sensibilidad hacia la imagen y la musicalidad |
| Ensayo / Opinión | Vocación argumentativa e intelectual |
| Erudición / Divulgación | Interés por transmitir conocimiento |
| Persuasión / Retórica | Orientación a convencer y comunicar estratégicamente |
| Reflexión | Tendencia al pensamiento introspectivo |

El enfoque dominante queda visible en la tarjeta del alumno dentro de la lista.

---

#### Alumnos Edición

Gestión de los participantes de los talleres o cursos de **edición literaria**. Son tratados como clientes del servicio, con su propia cuenta corriente independiente de los alumnos del taller.

---

#### Cuentas Taller / Cuentas Edición

Sistema de cuenta corriente por alumno.

- Registro de ingresos y egresos con fecha y concepto
- Cálculo automático de saldo en tiempo real
- El saldo se actualiza inmediatamente al registrar cada movimiento
- Saldo positivo en verde, saldo negativo en rojo

> **Lógica del saldo:** el sistema no presupone un monto mensual fijo. El saldo refleja la diferencia entre todos los ingresos y egresos registrados. Para indicar que un alumno adeuda, registrá un **egreso** con el concepto y monto correspondiente. Cuando pague, registrá un **ingreso** por el mismo importe.

---

#### Cuentos

Seguimiento de las producciones escritas de cada alumno.

- Registro por alumno con título, género y estado
- Estados del flujo de trabajo:
  - `Borrador` — en proceso de escritura
  - `En revisión` — entregado para corrección
  - `Finalizado` — aprobado por el taller
  - `Publicado` — difundido o enviado a concursos
- Campo de devolución/feedback del coordinador
- Filtro por alumno para ver la obra de una sola persona

---

#### Agenda

Cronograma de actividades del taller.

- Tipos de eventos: `Evento`, `Curso`, `Charla`, `Taller`
- Campos: título, fecha, hora, lugar, descripción
- Los eventos pasados se muestran atenuados para distinguirlos de los próximos
- Formato de fecha: `YYYY-MM-DD` (por ejemplo: `2025-04-15`)

---

### Norte Copywriting Solutions

#### Clientes

Directorio de clientes del servicio de copywriting.

- Alta, edición de clientes con empresa, email, teléfono y notas
- Estado activo/inactivo por cliente

---

#### Tareas

Gestión de proyectos y encargos.

- Asignación opcional a un cliente
- Fecha límite con indicador visual de vencimiento (rojo si está vencida)
- Estados del flujo de trabajo:
  - `Pendiente` — sin comenzar
  - `En progreso` — en ejecución
  - `Completada` — entregada
  - `Cancelada` — descartada
- Marcado rápido de estado con un clic desde la lista

---

### Configuración

Pestaña `⚙ Config` accesible desde la app principal.

**Cambiar contraseña**
Requiere ingresar la contraseña actual para confirmar la identidad antes de establecer una nueva. Cambios efectivos de inmediato sin necesidad de reiniciar.

**Cerrar sesión**
Vuelve a la pantalla de login sin cerrar la aplicación. Útil en entornos compartidos.

---

## Base de datos

El sistema usa **SQLite** de forma local. El archivo `tintero.db` se crea automáticamente en el mismo directorio que `tintero_app.py` la primera vez que se ejecuta.

### Tablas

| Tabla | Descripción |
|---|---|
| `students` | Alumnos del taller y de edición |
| `accounts` | Movimientos de cuenta corriente |
| `stories` | Producciones literarias de los alumnos |
| `events` | Agenda de actividades |
| `copy_clients` | Clientes de Norte Copywriting |
| `copy_tasks` | Tareas y proyectos de copywriting |

### Backup

Para hacer una copia de seguridad, basta con copiar el archivo `tintero.db` a otro directorio o medio de almacenamiento. Es un archivo estándar SQLite que puede abrirse con cualquier cliente compatible, como [DB Browser for SQLite](https://sqlitebrowser.org/).

---

## Tipografía y diseño

### Paleta de colores

| Variable | Hex | Uso |
|---|---|---|
| `C_NAVY` | `#1C223A` | Fondo principal |
| `C_NAVY2` | `#242b47` | Fondo secundario / paneles |
| `C_CARD` | `#2d3657` | Cards y contenedores |
| `C_CARD2` | `#1e2840` | Cards interiores / inputs |
| `C_GOLD` | `#EDA745` | Acento dorado principal |
| `C_CREAM` | `#F0EADC` | Texto principal (beige claro) |
| `C_MUTED` | `#8892b0` | Texto secundario / subtítulos |

### Fuentes

| Variable | Familia | Uso |
|---|---|---|
| `FONT_DISPLAY` | Cormorant Garamond | Títulos y headings |
| `FONT_BODY` | Nunito | Interfaz general |
| `FONT_MONO` | Consolas | Datos numéricos |

---

## Preguntas frecuentes

**¿Dónde se guarda la contraseña?**
En el archivo `tintero_config.json`, en texto plano dentro del mismo directorio del programa. No se envía a ningún servidor. Es una contraseña de acceso local, no un sistema de seguridad criptográfico.

**¿Qué pasa si borro `tintero.db`?**
Se perderán todos los datos. El programa creará una base de datos vacía en el próximo inicio. Siempre hacé backup antes de cualquier operación.

**¿Qué pasa si borro `tintero_config.json`?**
El sistema volverá al estado de primer uso y pedirá crear una nueva contraseña. Los datos en `tintero.db` no se ven afectados.

**¿Puedo cambiar la contraseña sin entrar al programa?**
Sí: abrí `tintero_config.json` con cualquier editor de texto y modificá el valor del campo `"password"` directamente.

**¿El programa necesita conexión a internet?**
No. Funciona completamente de forma offline.

**¿Puedo usar el programa en más de una computadora?**
Sí, pero no de forma simultánea. Copiá la carpeta completa (incluyendo `tintero.db` y `tintero_config.json`) a la otra máquina. Si necesitás sincronización entre equipos, podés guardar la carpeta en Google Drive o Dropbox y acceder desde distintas computadoras (nunca abrir el programa desde dos equipos al mismo tiempo).

---

*El Tintero — Sistema desarrollado a medida · 2025*
