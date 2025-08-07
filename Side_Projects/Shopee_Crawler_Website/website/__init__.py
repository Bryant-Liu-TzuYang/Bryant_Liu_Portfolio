import os
import platform
import sys
import time
import zipfile
import io
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
# import time
# import pyodbc, struct
# from azure import identity
# from typing import Union
# from pydantic import BaseModel
# from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
import pandas as pd
from .src.getlink import main
from flask import (Flask, redirect, render_template, request,
                   send_file, url_for, session, jsonify)
from .db import get_db

from werkzeug.middleware.proxy_fix import ProxyFix

import sentry_sdk
from .notion_service import NotionUpdatesService

if platform == "linux":
    from sentry_sdk.integrations.flask import FlaskIntegration
    from .config import SENTRY_DSN
    
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            # Add data like request headers and IP for users,
            # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
            send_default_pii=True,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for tracing.
            traces_sample_rate=1.0,
            _experiments={
                # Set continuous_profiling_auto_start to True
                # to automatically start the profiler on when
                # possible.
                "continuous_profiling_auto_start": True,
            },
        )


### -------- Logging Setup -------- ###
import logging
from logging.handlers import RotatingFileHandler

import pytz
# 建立 logs 資料夾
os.makedirs('logs', exist_ok=True)

# 設定 UTC+8 時區
taipei_tz = pytz.timezone('Asia/Taipei')

# 自定義 Formatter 類別，使用 GMT+8 時區
class GMT8Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=taipei_tz)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]  # 保留毫秒但只取前3位
        return s

now = datetime.now(taipei_tz)
date_time = now.strftime("%Y%m%d")
log_path = f'logs/app_{date_time}.log'

# 檔案 Handler
file_handler = RotatingFileHandler(
    log_path, maxBytes=10_000_000, backupCount=5, encoding='utf-8'
)
file_handler.setLevel(logging.WARNING)
file_formatter = GMT8Formatter(
    '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
)
file_handler.setFormatter(file_formatter)

# Console Handler（stdout）
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)
console_formatter = GMT8Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s'
)
console_handler.setFormatter(console_formatter)

# 主 logger 註冊 handler
logger = logging.getLogger()
logger.setLevel(logging.WARNING)
logger.addHandler(file_handler)
logger.addHandler(console_handler)




def create_app(test_config=None):
    # Load environment variables from .env file
    load_dotenv()
    
    # Basic settings
    app = Flask(__name__, static_url_path='/static')
    
    # Import config after loading environment variables
    from .config import SECRET_KEY
    
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, 'shoppee.sqlite'),
    )

    # Configure MIME types for static files
    import mimetypes
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')

    # Apply ProxyFix for both direct access and proxied access
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # Ensure static files are served with proper headers
    @app.after_request
    def after_request(response):
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            if request.path.endswith('.js'):
                response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
            elif request.path.endswith('.css'):
                response.headers['Content-Type'] = 'text/css; charset=utf-8'
        return response


    UPLOAD_FOLDER = 'data/uploads'
    OUTPUT_FOLDER = 'data/outputs'


    # ensure the uploads and outputs folders exist
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    except OSError:
        pass
    try:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    except OSError:
        pass
    try:
        os.makedirs('data/ranking', exist_ok=True)
    except OSError:
        pass
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass



    @app.route('/', methods=['GET', 'POST'])
    def main_page():
        # connect to database first
        db = get_db()
        files = db.execute(
                "SELECT filename, status, percentage, progress, timeSpent, stamp, platforms FROM files ORDER BY id DESC"
            ).fetchall()

        if request.method == 'POST':
            # upload file flask
            f = request.files.get('file')

            if (f.filename == ''):
                return redirect(url_for('main_page'))

            # Get selected platforms
            platforms = request.form.get('platforms', 'coupang')  # Default to coupang if not specified
            
            # 設定為 +8 時區
            tz = timezone(timedelta(hours=+8))
            # 取得現在時間、指定時區、轉為 ISO 格式
            time_stamp = str(datetime.now(tz).strftime("%Y-%m-%d_%H-%M-%S"))

            db.execute(
                    "INSERT INTO files (filename, status, percentage, progress, timeSpent, stamp, platforms) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (f.filename, 'processing', 0, "0% (0/detecting)", "calculating", time_stamp, platforms)    
                )
            db.commit()

            # safe uploaded file to the default directory: uploads
            SAVED_FILEPATH = f"{UPLOAD_FOLDER}/{time_stamp}_{f.filename}"
            f.save(SAVED_FILEPATH)
            
            if (os.path.exists(SAVED_FILEPATH) == False):
                db.execute(
                    "UPDATE files SET status = ? WHERE stamp = ?", ("failed [0]: saving file", "0%", time_stamp)
                )
                db.commit()
                mes = f"Error saving the uploaded file"
                app.logger.error(mes)
                print(mes)
                return redirect(url_for('main_page'))

            app.logger.warning(f"filename in main_mage is {f.filename}")
            app.logger.warning(f"time_stamp in main_mage is {time_stamp}")
            app.logger.warning(f"platforms in main_page is {platforms}")

            return redirect(url_for('tempPage_processingFile', filename=f.filename, time_stamp=time_stamp, platforms=platforms))

        return render_template('home_page.html', files=files)



    @app.route('/processingFile/<filename>/<time_stamp>/<platforms>', methods=['GET', 'POST'])
    def tempPage_processingFile(filename, time_stamp, platforms):
        try:
            import threading
            process = threading.Thread(target=processingFile, args=(filename, time_stamp, platforms))
            process.start()
        except Exception as e:
            db = get_db()
            db.execute(
                "UPDATE files SET status = ? WHERE stamp = ?", ("failed [1]: threading", time_stamp)
            )
            db.commit()
            
            mes = f"Error threading the processFile: {e}"
            app.logger.error(mes)
            raise Exception(mes)
        else:
            app.logger.warning("start processingFile")

        return redirect(url_for('main_page'))



    @app.route('/show_data/<stamp>/<filename>', methods=['GET'])
    def showData(filename, stamp):
        # Processed File Path
        data_file_path = os.path.join(OUTPUT_FOLDER, f"links_{stamp}_{filename}")
        
        # Check if file exists
        if not os.path.exists(data_file_path):
            return render_template('show_csv_output.html',
                                data_var="<p>Error: File not found</p>")
        
        # Check if file is empty
        if os.path.getsize(data_file_path) == 0:
            return render_template('show_csv_output.html',
                                data_var="<p>Error: File is empty. The processing may have failed or is still in progress.</p>")
        
        try:
            # read file
            fileType = filename.rsplit('.', 1)[-1].lower()
            if fileType == "xlsx":
                processed_df = pd.read_excel(data_file_path, engine='openpyxl')
            elif fileType == "csv":
                processed_df = pd.read_csv(data_file_path, encoding='utf-8')
            
            # Converting to html Table
            uploaded_df_html = processed_df.to_html()
            return render_template('show_csv_output.html',
                                data_var=uploaded_df_html)
                                
        except pd.errors.EmptyDataError:
            return render_template('show_csv_output.html',
                                data_var="<p>Error: File contains no data. The processing may have failed or is still in progress.</p>")
        except Exception as e:
            app.logger.error(f"Error reading file {data_file_path}: {e}")
            return render_template('show_csv_output.html',
                                data_var=f"<p>Error reading file: {str(e)}</p>")



    @app.route('/download/<stamp>/<filename>', methods=['GET'])
    def download_file(filename, stamp):
        output_filename = f"links_{stamp}_{filename}"
        return send_file(f"data/outputs/{output_filename}",
                        as_attachment=True)



    @app.route('/delete/<stamp>/<filename>', methods=['POST'])
    def delete_file(filename, stamp):
        try:
            db = get_db()
            
            # Delete from database
            result = db.execute(
                "DELETE FROM files WHERE filename = ? AND stamp = ?", 
                (filename, stamp)
            )
            
            if result.rowcount == 0:
                return jsonify({'status': 'error', 'message': 'File not found in database'}), 404
            
            db.commit()
            
            # # Delete files from filesystem
            # uploaded_file_path = f"{UPLOAD_FOLDER}/{stamp}_{filename}"
            # output_file_path = f"data/outputs/links_{stamp}_{filename}"
            
            # # Delete uploaded file if it exists
            # if os.path.exists(uploaded_file_path):
            #     os.remove(uploaded_file_path)
            #     app.logger.info(f"Deleted uploaded file: {uploaded_file_path}")
            
            # # Delete output file if it exists (both .csv and .xlsx versions)
            # for ext in ['.csv', '.xlsx']:
            #     output_path = output_file_path.replace('.csv', ext).replace('.xlsx', ext)
            #     if os.path.exists(output_path):
            #         os.remove(output_path)
            #         app.logger.info(f"Deleted output file: {output_path}")
            
            app.logger.info(f"Successfully deleted file record: {filename} with stamp: {stamp}")
            return jsonify({'status': 'success', 'message': 'File deleted successfully'})
            
        except Exception as e:
            app.logger.error(f"Error deleting file {filename} with stamp {stamp}: {e}")
            return jsonify({'status': 'error', 'message': f'Error deleting file: {str(e)}'}), 500

    

    

    @app.route('/how_to_use', methods=['GET'])
    def how_to_use():
        return render_template('how_to_use.html')
    


    @app.route('/updates', methods=['GET'])
    def updates():
        # Always return template immediately with cached data or loading state
        try:
            from .config import NOTION_INTEGRATION_TOKEN, NOTION_PAGE_ID
            
            notion_service = NotionUpdatesService(
                integration_token=NOTION_INTEGRATION_TOKEN,
                page_id=NOTION_PAGE_ID
            )
            
            # Only try to get cached data, don't wait for fresh API calls
            cache_data = notion_service._load_cache()
            if cache_data and notion_service._is_cache_valid(cache_data):
                updates_data = cache_data['data']
            else:
                # Return with no data, let frontend load asynchronously
                updates_data = None
            
            return render_template('updates.html', updates_data=updates_data)
        except Exception as e:
            app.logger.error(f"Error loading updates: {e}")
            return render_template('updates.html', updates_data=None, error=str(e))

    @app.route('/updates/data', methods=['GET'])
    def get_updates_data():
        """Async endpoint to fetch updates data"""
        try:
            from .config import NOTION_INTEGRATION_TOKEN, NOTION_PAGE_ID
            
            notion_service = NotionUpdatesService(
                integration_token=NOTION_INTEGRATION_TOKEN,
                page_id=NOTION_PAGE_ID
            )
            
            # Get updates data (this will use cache if available)
            updates_data = notion_service.get_updates()
            
            if updates_data:
                return jsonify({'status': 'success', 'data': updates_data})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to load updates'}), 500
        except Exception as e:
            app.logger.error(f"Error loading updates data: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/updates/refresh', methods=['POST'])
    def refresh_updates():
        try:
            from .config import NOTION_INTEGRATION_TOKEN, NOTION_PAGE_ID
            
            notion_service = NotionUpdatesService(
                integration_token=NOTION_INTEGRATION_TOKEN,
                page_id=NOTION_PAGE_ID
            )
            
            updates_data = notion_service.refresh_cache()
            return jsonify({'status': 'success', 'message': 'Updates refreshed successfully'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    

    @app.route('/trending', methods=['GET'])
    def trending():
        """Display the trending Coupang products page"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('trending_coupang.html', current_date=current_date)

    def get_category_mapping():
        """Map display names to file names"""
        return {
            'Phone Only': 'phone_only',
            'Phone Accessories': 'phone_accessories', 
            'Computer Laptop': 'computer_laptop',
            'Computer Accessories': 'computer_accessories',
            'Game': 'game',
            'Home Electronic': 'home_electronic'
        }

    def get_file_name_from_display(display_name):
        """Convert display name to file name"""
        mapping = get_category_mapping()
        return mapping.get(display_name, display_name.lower().replace(' ', '_'))

    def get_display_name_from_file(file_name):
        """Convert file name to display name"""
        mapping = get_category_mapping()
        reverse_mapping = {v: k for k, v in mapping.items()}
        return reverse_mapping.get(file_name, file_name.replace('_', ' ').title())

    @app.route('/trending_data', methods=['GET'])
    def trending_data():
        """API endpoint to get trending data for a specific category and date"""
        try:
            category_display_raw = request.args.get('category')
            app.logger.info(f"Category display raw: {category_display_raw}")
            date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            # Ensure proper URL decoding (Flask usually does this automatically, but let's be explicit)
            category_display = urllib.parse.unquote(category_display_raw)
            
            # Debug logging
            app.logger.info(f"Trending request - Category: '{category_display}', Date: '{date_str}'")
            
            # Convert display name to file name
            category_file = get_file_name_from_display(category_display)
            app.logger.info(f"Mapped to file name: '{category_file}'")
            
            # Convert date format from YYYY-MM-DD to YYYY-MM-DD for filename
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                filename_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid date format'}), 400
            
            # Construct filename
            filename = f"coupang_trending_{category_file}_{filename_date}.csv"
            filepath = os.path.join(os.path.dirname(app.instance_path), 'data', 'ranking', filename)

            app.logger.info(f"Looking for file: {filepath}")
            
            # Check if file exists
            if not os.path.exists(filepath):
                return jsonify({
                    'success': False, 
                    'message': f'No trending data available for {category_display} on {date_str}'
                }), 404
            
            # Read CSV file
            df = pd.read_csv(filepath)
            
            # Get file creation time
            file_stat = os.stat(filepath)
            file_creation_time = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            
            return jsonify({
                'success': True, 
                'data': data,
                'file_created': file_creation_time
            })
            
        except Exception as e:
            app.logger.error(f"Error in trending_data: {str(e)}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500

    @app.route('/download_trending', methods=['GET'])
    def download_trending():
        """Download trending data as CSV"""
        try:
            app.logger.info(f"Download request received - All args: {dict(request.args)}")
            
            category_display_raw = request.args.get('category')
            app.logger.info(f"Category display raw: {category_display_raw}")
            date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
            download_all = request.args.get('all', 'false').lower() == 'true'
            
            app.logger.info(f"Parameters - Category: '{category_display_raw}', Date: '{date_str}', All: {download_all}")
            
            # Ensure proper URL decoding
            category_display = urllib.parse.unquote(category_display_raw) if category_display_raw else None
            app.logger.info(f"Decoded category: '{category_display}'")
            
            # Convert date format
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                filename_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return "Invalid date format", 400
            
            data_folder = os.path.join(os.path.dirname(app.instance_path), 'data', 'ranking')
            
            if download_all:
                # Create a zip file with all categories for the selected date
                zip_buffer = io.BytesIO()
                # Use the file naming convention for all categories
                categories = ['phone_only', 'phone_accessories', 'computer_laptop', 
                             'computer_accessories', 'game', 'home_electronic']
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for cat in categories:
                        filename = f"coupang_trending_{cat}_{filename_date}.csv"
                        filepath = os.path.join(data_folder, filename)
                        
                        if os.path.exists(filepath):
                            zip_file.write(filepath, filename)
                
                zip_buffer.seek(0)
                
                return send_file(
                    io.BytesIO(zip_buffer.read()),
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f'coupang_trending_all_{filename_date}.zip'
                )
            else:
                # Download single category
                if not category_display:
                    app.logger.error("No category provided for single download")
                    return "Category is required for single download", 400
                
                app.logger.info(f"Single download requested - Category: '{category_display}', Date: '{date_str}'")
                
                # Convert display name to file name
                try:
                    category_file = get_file_name_from_display(category_display)
                    app.logger.info(f"Mapped category '{category_display}' to file name: '{category_file}'")
                except Exception as e:
                    app.logger.error(f"Error mapping category name: {str(e)}")
                    return f"Error processing category name: {str(e)}", 500
                
                filename = f"coupang_trending_{category_file}_{filename_date}.csv"
                filepath = os.path.join(data_folder, filename)
                
                app.logger.info(f"Looking for file: {filepath}")
                app.logger.info(f"File exists: {os.path.exists(filepath)}")
                
                if not os.path.exists(filepath):
                    app.logger.error(f"File not found: {filepath}")
                    return f"File not found for {category_display} on {date_str}", 404
                
                app.logger.info(f"Sending file: {filepath}")
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=filename
                )
                
        except Exception as e:
            app.logger.error(f"Error in download_trending: {str(e)}")
            return "Internal server error", 500

    @app.route('/about', methods=['GET'])
    def about():
        return render_template('about.html')
    


    @app.route('/test', methods=['GET'])
    def test():
        1/0  # raises an error
        return "<p>Hello, World!</p>"
    


    @app.route('/test2', methods=['GET'])
    def test2():
        return "test2", 200


    def processingFile(filename, time_stamp, platforms):
        with app.app_context():
            db = get_db()

            # Main logic for processing the file
            try:
                app.logger.debug("try to start main")
                main(filename, time_stamp, platforms)  # Pass platforms to main function
            except Exception as e:
                mes = f"Error arised in processingFile: {e}"
                app.logger.error(mes)
                db.execute(
                    "UPDATE files SET status = ? WHERE stamp = ?", ("failed [2]: processingFile", time_stamp)
                )
                db.commit()
            else:
                app.logger.debug("no error arised")
                db.execute(
                    "UPDATE files SET status = ? WHERE stamp = ?", ("done!", time_stamp)
                )
                db.commit()
            finally:
                app.logger.debug("this is the end of processingFile")



    from .db import init_app
    init_app(app)


    # Warm up the notion cache on startup
    try:
        from .config import NOTION_INTEGRATION_TOKEN, NOTION_PAGE_ID
        
        def warm_notion_cache():
            try:
                notion_service = NotionUpdatesService(
                    integration_token=NOTION_INTEGRATION_TOKEN,
                    page_id=NOTION_PAGE_ID
                )
                notion_service.warm_cache_if_needed()
            except Exception as e:
                app.logger.warning(f"Failed to warm notion cache: {e}")
        
        # Run cache warming in a separate thread
        import threading
        cache_thread = threading.Thread(target=warm_notion_cache, daemon=True)
        cache_thread.start()
        
    except Exception as e:
        app.logger.warning(f"Failed to start cache warming: {e}")

    # if __name__ == '__main__':
    # app.run()

    return app
