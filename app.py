from flask import Flask, request, send_file, render_template, redirect, url_for, flash
from spleeter.separator import Separator
import os
import uuid
import zipfile

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # مهم لعرض الرسائل
separator = Separator('spleeter:4stems')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'audio' not in request.files:
            flash('لم يتم اختيار ملف صوتي')
            return redirect(request.url)

        audio = request.files['audio']
        if audio.filename == '':
            flash('الرجاء اختيار ملف صالح')
            return redirect(request.url)

        temp_id = str(uuid.uuid4())
        os.makedirs(f'temp/{temp_id}', exist_ok=True)
        input_path = f'temp/{temp_id}/input.mp3'
        output_dir = f'temp/{temp_id}/output'

        audio.save(input_path)
        separator.separate_to_file(input_path, output_dir)

        # ضغط الناتج
        zip_path = f'temp/{temp_id}/separated.zip'
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(f'{output_dir}/input'):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, f'{output_dir}/input')
                    zipf.write(full_path, arcname)

        return send_file(zip_path, as_attachment=True)

    return render_template('index.html')

# API
@app.route('/api/separate', methods=['POST'])
def api_separate():
    if 'audio' not in request.files:
        return {'error': 'No file uploaded'}, 400

    audio = request.files['audio']
    temp_id = str(uuid.uuid4())
    os.makedirs(f'temp/{temp_id}', exist_ok=True)
    input_path = f'temp/{temp_id}/input.mp3'
    output_dir = f'temp/{temp_id}/output'

    audio.save(input_path)
    separator.separate_to_file(input_path, output_dir)

    zip_path = f'temp/{temp_id}/separated.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(f'{output_dir}/input'):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, f'{output_dir}/input')
                zipf.write(full_path, arcname)

    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)