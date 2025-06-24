import os
from flask import send_file, jsonify

@app.route('/download/starter_kit')
def download_starter_kit():
    """下载Starter Kit文件"""
    try:
        file_path = os.path.join(os.getcwd(), 'starter_kit.zip')
        if os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name='ECG_Compression_Starter_Kit.zip',
                mimetype='application/zip'
            )
        else:
            return jsonify({
                'success': False,
                'message': 'Starter Kit文件不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下载失败: {str(e)}'
        }), 500