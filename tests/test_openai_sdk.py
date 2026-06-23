import socket
import threading

import uvicorn
from openai import OpenAI

from app.main import app


def find_free_port() -> int:
      with socket.socket() as sock:
          sock.bind(("127.0.0.1", 0))
          return sock.getsockname()[1]


def test_openai_sdk_can_call_chat_completions() -> None:
      port = find_free_port()
      server = uvicorn.Server(
          uvicorn.Config(
              app,
              host="127.0.0.1",
              port=port,
              log_level="warning",
          )
      )

      thread = threading.Thread(target=server.run, daemon=True)
      thread.start()

      client = OpenAI(
          base_url=f"http://127.0.0.1:{port}/v1",
          api_key="unused-test-key",
      )

      response = client.chat.completions.create(
          model="gateway-mock",
          messages=[
              {
                  "role": "user",
                  "content": "Hello SDK",
              }
          ],
      )

      server.should_exit = True
      thread.join(timeout=5)

      assert response.choices[0].message.content == "Echo: Hello SDK"