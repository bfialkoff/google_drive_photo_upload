url_host = 'https://93792fa47b3d.ngrok.io'
app_name = 'https://uploadphotobot.herokuapp.com/'
telegram_token = '1156639980:AAH59Yi1udq15JrUlxKyUcsOB7l9-a6DjnA'
telegram_set_webhook = 'api.telegram.org/bot{}/setWebHook?url={}'.format(telegram_token, url_host)
telegream_webhook_info = 'api.telegram.org/bot{}/getWebhookInfo'.format(telegram_token)
bot_url = 'https://api.telegram.org/bot{}/'.format(telegram_token)

mongodb_user = 'photo-bot'
mongodb_password = 'FncQJgTiklYIZBeo'
cluster_name = 'photo-app'
mongo_db_name = 'drive_bot'
collection = 'users'
