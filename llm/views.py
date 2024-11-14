from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pyautogui
import openai
import time
import subprocess
from .serializers import CommandSerializer



class Main(APIView):

    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def compare_with_openai(self, command):
        prompt = f"Interpret the following command and return an actionable instruction in JSON format: {command}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.0
            )

            message = response.choices[0].message['content'].strip()

            if "none" in message.lower() or not message:
                return "none"
            return message
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)


    def open_program(self, program_name):
        try:
            subprocess.Popen(program_name)
            return True
        except Exception as e:
            print(f"Failed to open program: {e}")
            return False


    def draw_flower(self):
        for _ in range(6):
            pyautogui.moveTo(500, 500)
            pyautogui.mouseDown()
            pyautogui.move(50, 50)
            pyautogui.mouseUp()
            pyautogui.move(50, -50)

    def post(self, request):
        serializer = CommandSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            target = serializer.validated_data['target']

            if action == 'open_program':
                success = self.open_program(target)
                if success:
                    return Response({"message": f"{target} opened successfully!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": f"Failed to open {target}!"}, status=status.HTTP_400_BAD_REQUEST)

            elif action == 'draw_flower':
                self.draw_flower()
                return Response({"message": "Flower drawn successfully!"}, status=status.HTTP_200_OK)

            return Response({"message": "Invalid action!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
