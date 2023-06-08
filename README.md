# 1c-log-exporter

Инструмент для предобработки и выгрузки логов 1С

Пока поддерживается только Grafana Loki.

## Использование

```shell script
python3 main.py --help

Tool to parse and export 1C technological log into Grafana Loki

optional arguments:
  -h, --help            show this help message and exit
  -i <file>, --input_file <file>
                        Log file
```

## Установка монитора

```shell script
git clone "https://github.com/ivasilyev/1c-log-exporter.git"

export TOOL_NAME=1c-log-exporter
export TOOL_DIR="$(pwd)/${TOOL_NAME}/"
export TOOL_SCRIPT="${TOOL_DIR}${TOOL_NAME}.sh"
cd "${TOOL_DIR}" || exit 1

cat <<EOF | tee "${TOOL_SCRIPT}"
#!/usr/bin/env bash
# nano "${TOOL_SCRIPT}"
cd "${TOOL_DIR}"
LOGGING_LEVEL=5 \
python3 monitor.py \
    --input_dirs <пути до директорий> \
    --delay 3600
EOF

(crontab -l 2>/dev/null; echo "@reboot /usr/bin/bash \"${TOOL_SCRIPT}\" &") | crontab -
crontab -l
```

### Конфигурация

```shell script
cp secret.template.json secret.json
nano secret.json
```

### Пробный запуск

```shell script
LOGGING_LEVEL=0 \
python3 monitor.py \
    --input_dirs "${C1_LOG_DIR}" \
    --delay 900
```
