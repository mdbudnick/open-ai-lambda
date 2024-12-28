import json
import os
import time
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
ASSISTANT_ID = os.environ.get("ASSISTANT_ID")

class ChatRequest(BaseModel):
    thread_id: str = None
    content: str

def wait_on_run(run, thread):
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def lambda_handler(event, context):
    try:
        request = ChatRequest(**event)

        thread = None
        if request.thread_id:
            print("Retrieving thread")
            thread = client.beta.threads.retrieve(request.thread_id)
            if not thread:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"detail": "Thread does not exist"})
                }
        else:
            print("Creating thread")
            thread = client.beta.threads.create()

        print(thread)
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=request.content
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
        )
        wait_on_run(run, thread)

        messages = client.beta.threads.messages.list(
            thread_id=thread.id, order="asc", after=message.id
        )
        response = {
            "response": messages.data[0].content[0].text.value,
            "thread_id": thread.id
        }
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"detail": str(e)})
        }
