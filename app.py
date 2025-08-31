from flask import Flask, request
import requests
import os
import time
import threading
import uuid

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# Global jobs storage
jobs = {}

def start_sending(job_id, access_token, thread_id, mn, messages, time_interval):
    """ Function for sending messages in loop for each token/thread """
    while jobs[job_id]["running"]:
        try:
            for message1 in messages:
                if not jobs[job_id]["running"]:  # Check stop signal
                    break
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    print(f"✅ [{job_id}] Sent: {message}")
                else:
                    print(f"❌ [{job_id}] Failed: {message}")

                time.sleep(time_interval)
        except Exception as e:
            print(f"⚠️ Error [{job_id}]: {e}")
            time.sleep(30)

    print(f"🛑 Job {job_id} stopped!")


@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        access_tokens = request.form.get('accessToken').split(",")  # Multiple tokens
        thread_ids = request.form.get('threadId').split(",")        # Multiple threads
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        job_ids = []  # Store all job IDs

        for token in access_tokens:
            for t_id in thread_ids:
                job_id = str(uuid.uuid4())[:8]  # Short unique ID
                jobs[job_id] = {"running": True}
                th = threading.Thread(target=start_sending, args=(job_id, token.strip(), t_id.strip(), mn, messages, time_interval))
                th.daemon = True
                th.start()
                job_ids.append(job_id)

        return f"<h3>✅ Multi Loader Started!</h3><p>Job IDs: {', '.join(job_ids)}</p><p>Use /stop?job_id=JOBID to stop.</p>"

    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Muddassir Convo loDer</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body style="background: #f44336; color:white;">
        <div class="container mt-5 p-4 rounded" style="background:#fff; color:black; max-width:400px;">
            <h2 class="text-center">🔥 Multi Convo Loader 🔥</h2>
            <form action="/" method="post" enctype="multipart/form-data">
                <div class="mb-3">
                    <label>Enter Tokens (comma separated):</label>
                    <input type="text" class="form-control" name="accessToken" required>
                </div>
                <div class="mb-3">
                    <label>Enter Thread IDs (comma separated):</label>
                    <input type="text" class="form-control" name="threadId" required>
                </div>
                <div class="mb-3">
                    <label>Enter Hater Name:</label>
                    <input type="text" class="form-control" name="kidx" required>
                </div>
                <div class="mb-3">
                    <label>Select Your Notepad File:</label>
                    <input type="file" class="form-control" name="txtFile" accept=".txt" required>
                </div>
                <div class="mb-3">
                    <label>Speed in Seconds:</label>
                    <input type="number" class="form-control" name="time" required>
                </div>
                <button type="submit" class="btn btn-danger w-100">🚀 Start Multi Loader</button>
            </form>
        </div>
    </body>
    </html>
    '''


@app.route('/stop', methods=['GET'])
def stop_job():
    job_id = request.args.get("job_id")
    if job_id in jobs:
        jobs[job_id]["running"] = False
        return f"<h3>🛑 Job {job_id} stopped successfully!</h3>"
    else:
        return "<h3>❌ Invalid Job ID</h3>"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
