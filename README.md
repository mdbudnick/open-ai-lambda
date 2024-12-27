# Lambda Handler for serving OpenAI chat message


## Testing

curl -X POST "https://abcdefg.execute-api.us-east-1.amazonaws.com/prod/chat/" \
     -H "Content-Type: application/json" \
     -d '{"thread_id": "thread_GbgHN7tE3COCTzA0FOFlQHrm", "content": "What is the capital of France?"}'
