import os
import re
import sys
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: ANTHROPIC_API_KEY not found.")
    sys.exit(1)

client = Anthropic(api_key=api_key)

MODEL = "claude-sonnet-4-20250514"   # Change to a model available to your account

MAX_HISTORY = 20

system_message = """
You are Jon Snow, a highly professional, analytical, and supportive personal finance and expenses manager.

Your core responsibility is to help users manage their financial decisions, track expenses, and allocate their budget strictly based on their total income.

Core Rules:
- Income Constraint: You must operate strictly within the user's provided income.
- Never invent numbers.
- If information is missing, ask for it.

Response Format:
1. One-sentence summary.
2. Financial assessment.
3. Exactly one follow-up question.
"""


def extract_text(response):
    return "".join(
        block.text
        for block in response.content
        if hasattr(block, "text")
    )


def create_markdown_document(client, history, system_message):

    if not history:
        print("There is no conversation to summarize.")
        return None

    summary_prompt = """
Create a professional financial report summarizing our conversation.

Include:
- Overall financial situation
- Income mentioned
- Expenses mentioned
- Budget recommendations
- Savings advice
- Financial concerns
- Action items
- Remaining questions

Only include information actually mentioned.
Never invent numbers.

After the report include the full transcript.
"""

    try:

        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            temperature=0,
            system=system_message,
            messages=history[-MAX_HISTORY:] + [
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ]
        )

        summary = extract_text(response)

        md = [
            "# 💰 Jon Snow Financial Report",
            "",
            "---",
            "",
            "## AI Summary",
            "",
            summary,
            "",
            "---",
            "",
            "## Full Conversation",
            ""
        ]

        for message in history:

            content = re.sub(
                r"\[CREATE_MARKDOWN\]",
                "",
                message["content"]
            ).strip()

            if message["role"] == "user":
                md.append("### 👤 You")
            else:
                md.append("### 🤖 Jon Snow")

            md.append("")
            md.append(content)
            md.append("")
            md.append("---")
            md.append("")

        filename = "Financial_Chat_Report.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

        return filename

    except Exception as e:
        print(f"Error generating report: {e}")
        return None


def run_chat(history):

    print('\nJon Snow: "Winter is coming, and so are your bills."')
    print("Type 'summary' to generate a report.")
    print("Type 'return' to go back.\n")

    while True:

        user_input = input("Jon Snow >> ").strip()

        if user_input.lower() in ("return", "exit"):
            print("Returning to menu...\n")
            break

        if user_input.lower() == "summary":

            filename = create_markdown_document(
                client,
                history,
                system_message
            )

            if filename:
                print(f"\nReport saved as {filename}\n")

            continue

        history.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        try:

            response = client.messages.create(
                model=MODEL,
                max_tokens=300,
                temperature=0.7,
                system=system_message,
                messages=history[-MAX_HISTORY:]
            )

            reply = extract_text(response)

            print(f"\nJon Snow: {reply}\n")

            history.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )

        except Exception as e:
            print(f"\nSomething went wrong:\n{e}")
            break