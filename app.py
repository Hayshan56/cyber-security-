from flask import Flask, render_template, request, jsonify, url_for, redirect
from celery_worker import run_full_scan

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    target = request.form.get('target')
    api_key = request.form.get('api_key')

    if not target:
        return "Error: No target specified.", 400

    task = run_full_scan.delay(target, api_key)
    return redirect(url_for('scan_in_progress', task_id=task.id, target=target))

@app.route('/scan-in-progress/<task_id>/<target>')
def scan_in_progress(task_id, target):
    return render_template('scanning.html', task_id=task_id, target=target)


@app.route('/status/<task_id>')
def scan_status(task_id):
    task = run_full_scan.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'status': 'Scanning...'}
        if task.state == 'SUCCESS':
            response['result_url'] = url_for('scan_results', task_id=task.id)
    else:
        response = {'state': task.state, 'status': str(task.info)}
    return jsonify(response)

@app.route('/results/<task_id>')
def scan_results(task_id):
    task = run_full_scan.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        results = task.get()
        # To get the target, we have to retrieve it from the task arguments
        target = task.request.args[0]
        return render_template('results.html', target=target, results=results)
    else:
        return "Scan is not ready or has failed.", 404

if __name__ == '__main__':
    app.run(debug=True)
