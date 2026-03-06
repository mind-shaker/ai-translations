import requests
import json

print ("raz")
# First API call with reasoning
response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "arcee-ai/trinity-large-preview:free",
    "messages": [
        {
          "role": "user",
          "content": "а ти б міг знайти й виправити контекстні помилки в даному srt тексті без пояснень? Просто перепиши рядки з уже виправленими словами. Сьогодні я покажу вам, як вчать жіпіті можна перетворити на реальний навчальний інструмент, а не просто на перекладач. І сьогодні я буду говорити не загально, а буду використовувати такі прям конкретні промти і запити, які ви так розможете відтворити."
        }
      ],
    "reasoning": {"enabled": True}
  })
)

print (response)
# Extract the assistant message with reasoning_details
response = response.json()
response = response['choices'][0]['message']
print (response)

# Preserve the assistant message with reasoning_details
messages = [
  {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
  {
    "role": "assistant",
    "content": response.get('content'),
    "reasoning_details": response.get('reasoning_details')  # Pass back unmodified
  },
  {"role": "user", "content": "Are you sure? Think carefully."}
]

# Second API call - model continues reasoning from where it left off
response2 = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  data=json.dumps({
    "model": "arcee-ai/trinity-large-preview:free",
    "messages": messages,  # Includes preserved reasoning_details
    "reasoning": {"enabled": True}
  })
)


print (response2)