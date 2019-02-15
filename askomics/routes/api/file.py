"""Api routes
"""
from flask import jsonify, session, request
from askomics import app, login_required
from askomics.libaskomics.FilesHandler import FilesHandler

@app.route('/api/files', methods=['GET', 'POST'])
@login_required
def get_files():

    files_id = None
    if request.method == 'POST':
        data = request.get_json()
        files_id = data['filesId']

    try:
        files_handler = FilesHandler(app, session)
        files = files_handler.get_files_infos(files_id=files_id)
    except Exception as e:
        return jsonify({
            'error': True,
            'errorMessage': e
        })

    return jsonify({
        'files': files,
        'error': False,
        'errorMessage': ''
    })

@app.route('/api/files/upload', methods=['POST'])
@login_required
def upload():

    inputs = request.files

    try:
        files = FilesHandler(app, session)
        uploaded_files = files.persist_files(inputs)
    except Exception as e:
        return jsonify({
            'error': True,
            'errorMessage': e
        })

    return jsonify({
        'uploadedFiles': uploaded_files,
        'error': False,
        'errorMessage': ''
    })

@app.route('/api/files/preview', methods=['POST'])
@login_required
def get_preview():

    data = request.get_json()

    try:
        files_handler = FilesHandler(app, session)
        files_handler.handle_files(data['filesId'])

        results = []
        for file in files_handler.files:
            file.set_preview()
            res = file.get_preview()
            results.append(res)
    except Exception as e:
        return jsonify({
            'error': True,
            'errorMessage': e
        })

    return jsonify({
        'previewFiles': results
        'error': False,
        'errorMessage': ''
    })

@app.route('/api/files/delete', methods=['POST'])
@login_required
def delete_files():

    data = request.get_json()

    try:
        files = Files(app, session)
        remaining_files = files.delete_files(data['filesIdToDelete'])
    except Exception as e:
        return jsonify({
            'error': True,
            'errorMessage': e
        })

    return jsonify({
        'files': remaining_files
        'error': False,
        'errorMessage': ''
    })

@app.route('/api/files/integrate', methods=['POST'])
@login_required
def integrate():

    data = request.get_json()
