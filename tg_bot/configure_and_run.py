from pyngrok import ngrok

# Открываем тунель
flask_tunnel = ngrok.connect(5000, bind_tls=True)

# Получаем dns
def get_tunnel_url():
    return flask_tunnel.public_url

print(get_tunnel_url())