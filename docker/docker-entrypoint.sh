if [ ! -f /var/project/app/config.json ]; then
    echo $CONFIG_JSON > /var/project/app/config.json
fi
python main.py