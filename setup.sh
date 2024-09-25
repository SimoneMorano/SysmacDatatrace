mkdir -p ~/.streamlit/
echo "[general]
email = \"simone.morano@omron.com\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml