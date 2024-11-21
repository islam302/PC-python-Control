from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pyautogui
import subprocess
import time
from PIL import ImageGrab
import base64
from io import BytesIO
from dotenv import load_dotenv
import os
from openai import OpenAI

# تحميل ملف البيئة
load_dotenv()



def analyze_command(command):

    try:
        # Initialize OpenAI client
        client = OpenAI()

        # Ensure the API key is loaded from environment variables
        client.api_key = os.getenv("OPENAI_API_KEY")

        # Send the command to the o1-preview model
        response = client.chat.completions.create(
            model="gpt-4o",  # Use o1-preview model as per the documentation
            messages=[
                {
                    "role": "user",
                    "content": (
                            "Translate the following user command into Python automation code "
                            "using PyAutoGUI and subprocess. Respond ONLY with executable Python code, "
                            "no explanations or additional text:\n\n"
                            + command
                   ),
                }
            ]
        )

        # Extract and return the code from the response
        message_content = response.choices[0].message.content
        return message_content

    except Exception as e:
        return f"Error analyzing command: {str(e)}"

def clean_code(code):
    """
    تنظيف الكود المستلم من OpenAI وإضافة المكتبات الناقصة إذا لزم الأمر.
    """
    code = code.replace("```python", "").replace("```", "").strip()

    # تحقق من وجود استيراد مكتبة math
    if "cos" in code or "sin" in code or "radians" in code:
        if "import math" not in code:
            code = "import math\n" + code

    return code

def execute_code_from_openai(code):
    """
    تنفيذ الكود المستلم من OpenAI بعد تنظيفه.
    """
    try:
        cleaned_code = clean_code(code)  # تنظيف الكود
        print("Executing cleaned code from OpenAI:")
        print(cleaned_code)
        exec(cleaned_code)
    except Exception as e:
        print("Error executing code:", e)
        return f"Execution error: {e}"

@csrf_exempt
def handle_command(request):
    """
    استقبال الأوامر من المستخدم عبر HTTP POST وتنفيذها.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_command = data.get("command")
            print('User command: '+ user_command)
            # تحليل الأمر باستخدام OpenAI
            code = analyze_command(user_command)
            if "Error" not in code:
                analysis = execute_code_from_openai(code)
                print(analysis)
                return JsonResponse({"status": "success", "message": "Command executed successfully."})
            else:
                return JsonResponse({"status": "error", "message": code})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."})

