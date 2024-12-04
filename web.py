from flask import Flask, request, jsonify, render_template, Response
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys
import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

# 验证必要的环境变量
required_env_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'RECEIVER_EMAIL', 'DOCKER_REGISTRY_URL']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise Exception(f"Missing required environment variables: {', '.join(missing_vars)}")

app = Flask(__name__)

# 从环境变量中读取邮件配置
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT'))
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
try:
    receiver_email = json.loads(os.getenv('RECEIVER_EMAIL'))
    if not isinstance(receiver_email, list):
        raise ValueError("RECEIVER_EMAIL must be a JSON array")
except json.JSONDecodeError:
    raise Exception("RECEIVER_EMAIL must be a valid JSON array")


def send_email(subject, content):
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f6f8fa;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
                margin-bottom: 20px;
            }}
            .header img {{
                width: 60px;
                height: auto;
            }}
            .content {{
                line-height: 1.6;
                color: #333;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                text-align: center;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/97_Docker_logo_logos-1024.png" alt="Docker Logo">
                <h2 style="color: #0db7ed;">{subject}</h2>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>This is an automated message from Yoobit Docker Mirror System</p>
                <p>&copy; {datetime.datetime.now().year} Yoobit. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MIMEText(html_content, 'html', 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = sender_email
    message['To'] = ', '.join(receiver_email)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()  # 如果需要TLS加密，请启用这行
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
    finally:
        server.quit()

def docker_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output_lines = []
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            line = output.strip()
            print(line)
            output_lines.append(line)
            sys.stdout.flush()

    rc = process.poll()
    if rc != 0:
        raise Exception(f"Command failed with return code {rc}")
    return output_lines

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_and_push', methods=['POST'])
def update_and_push():
    try:
        data = request.json
        image_with_tag = data.get('image_with_tag', '')
        
        # 解析镜像名称和标签
        if ':' in image_with_tag:
            image_name, tag = image_with_tag.rsplit(':', 1)
        else:
            image_name = image_with_tag
            tag = 'latest'

        if not image_name:
            return jsonify({'error': 'Image name is required.'}), 400

        if '/' not in image_name:
            image_name = f"library/{image_name}"
        
        original_image = f"{image_name}:{tag}"
        registry_url = os.getenv('DOCKER_REGISTRY_URL')
        new_image = f"{registry_url}/{image_name}:{tag}"

        def generate_output():
            try:
                # 执行docker pull命令
                yield 'data: ' + json.dumps({'type': 'info', 'message': f"Pulling image: {original_image}"}) + '\n\n'
                pull_output = docker_command(f"docker pull {original_image}")
                for line in pull_output:
                    yield 'data: ' + json.dumps({'type': 'info', 'message': line}) + '\n\n'

                # 修改tag
                yield 'data: ' + json.dumps({'type': 'info', 'message': f"Tagging image as: {new_image}"}) + '\n\n'
                docker_command(f"docker tag {original_image} {new_image}")

                # 推送到新的仓库
                yield 'data: ' + json.dumps({'type': 'info', 'message': f"Pushing image to: {new_image}"}) + '\n\n'
                push_output = docker_command(f"docker push {new_image}")
                for line in push_output:
                    yield 'data: ' + json.dumps({'type': 'info', 'message': line}) + '\n\n'

                # 删除本地镜像
                yield 'data: ' + json.dumps({'type': 'info', 'message': "Removing local images..."}) + '\n\n'
                docker_command(f"docker rmi {new_image}")
                docker_command(f"docker rmi {original_image}")

                yield 'data: ' + json.dumps({'type': 'success', 'message': "Image successfully updated and pushed."}) + '\n\n'
                
                # 发送邮件通知
                send_email("Docker Image Update Success", 
                        f"The image {original_image} has been successfully updated and pushed to {registry_url}.")
                
            except Exception as e:
                error_message = str(e)
                yield 'data: ' + json.dumps({'type': 'error', 'message': f"Error: {error_message}"}) + '\n\n'
                raise e

        return Response(generate_output(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)