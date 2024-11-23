import time
import asyncio
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from operate.models.prompts import (
    get_system_prompt,
    get_user_prompt,
    get_user_first_message_prompt,
)
from operate.models.apis import get_next_action, clean_json, confirm_system_prompt
from operate.config import Config
from operate.utils.operating_system import OperatingSystem
from operate.utils.style import ANSI_GREEN, ANSI_RESET, ANSI_RED, ANSI_BRIGHT_MAGENTA, ANSI_BLUE
from operate.utils.screenshot import capture_screen_with_cursor
from operate.utils.ocr import get_text_element

# Load configuration
config = Config()

# Operating system utility
operating_system = OperatingSystem()


class ExecuteTaskView(APIView):
    """
    API لتنفيذ المهام باستخدام OpenAI GPT.
    """
    def post(self, request, *args, **kwargs):
        try:
            # Extract data from request
            model = request.data.get("model", "gpt-4")
            objective = request.data.get("objective")
            if not objective:
                return Response({"error": "Objective is required"}, status=400)

            # Prepare messages
            system_prompt = get_system_prompt(model, objective)
            messages = [{"role": "system", "content": system_prompt}]
            session_id = None  # Initialize session
            max_attempts = 10  # Limit to prevent infinite loops
            result = []

            for attempt in range(max_attempts):
                # Call API to get the next action
                operations, session_id = asyncio.run(
                    get_next_action(model, messages, objective, session_id)
                )
                result.extend(operations)

                # Execute operations
                success = self.operate(operations, model)
                if success:
                    break

                # Capture current state for feedback
                current_state_feedback = self.capture_current_state()

                # Append feedback to messages for iterative refinement
                messages.append(
                    {"role": "user", "content": f"Current state feedback: {current_state_feedback}"}
                )

            return Response({"result": "Task executed successfully", "operations": result}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def operate(self, operations, model):
        if config.verbose:
            print("[Self Operating Computer][operate]")
        for operation in operations:
            try:
                operate_type = operation.get("operation").lower()
                if operate_type == "press":
                    operating_system.press(operation.get("keys"))
                elif operate_type == "write":
                    operating_system.write(operation.get("content"))
                elif operate_type == "click":
                    operating_system.mouse(
                        {"x": operation.get("x"), "y": operation.get("y")}
                    )
                elif operate_type == "done":
                    print(f"Task completed: {operation.get('summary')}")
                    return True
            except Exception as e:
                print(f"Error executing operation {operation}: {e}")
                return False
        return False

    def capture_current_state(self):
        """
        Capture the current state of the system for feedback.
        """
        screenshot_path = "temp_screenshot.png"
        capture_screen_with_cursor(screenshot_path)
        try:
            from easyocr import Reader
            reader = Reader(["en"])
            results = reader.readtext(screenshot_path)
            state_text = [text for _, text, _ in results]
            return " ".join(state_text)
        except Exception as e:
            return f"Error capturing state: {e}"
