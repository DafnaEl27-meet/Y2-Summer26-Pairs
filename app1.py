import os
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Check if API key exists
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables.")
    exit()

client = Anthropic(api_key=api_key)

system_message = """You are Jon Snow, a highly professional, analytical, and supportive personal finance and expenses manager.

Your core responsibility is to help users manage their financial decisions, track expenses, and allocate their budget strictly based on their total income.

Core Rules:
- Income Constraint: You must operate strictly within the user's provided income. If their expenses exceed their income, clearly highlight the deficit and provide realistic adjustments.
- Data Integrity: Never invent or use random numbers. Rely exclusively on the exact financial data provided by the user. If key data points (like fixed costs or exact income) are missing, ask for them.
- Tone: Professional, clear, concise, and encouraging. Avoid unnecessary fluff or financial jargon; focus on actionable, practical advice.

Response Format:
1. One-Sentence Summary.
2. Financial Assessment.
3. Exactly one follow-up question.

Rules:
- Always work according to the given income.
- Always spend strictly on the given expenses.
- Never invent numbers.
"""


def create_markdown_document(client, history, system_message):
    """Generate a professional Markdown report of the conversation."""
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

Only include information that actually appeared.
Do not invent facts or numbers.

After the report, include a complete transcript of the conversation.
"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            temperature=0,
            system=system_message,
            messages=history + [
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ]
        )

        summary = response.content[0].text
        md = []

        md.append("# 💰 Jon Snow Financial Report")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## AI Summary")
        md.append("")
        md.append(summary)
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Full Conversation")
        md.append("")

        for message in history:
            role = message["role"]
            content = re.sub(r"\[CREATE_MARKDOWN\]", "", message["content"]).strip()

            if role == "user":
                md.append(f"### 👤 You")
            else:
                md.append(f"### {content.split(':')[0] if ':' in content else '🤖 AI'}")

            md.append("")
            md.append(content)
            md.append("")
            md.append("---")
            md.append("")

        filename = "Financial_Chat_Report.md"
        with open(filename, "w", encoding="utf-8") as file:
            file.write("\n".join(md))

        return filename

    except Exception as e:
        print(f"Error generating report: {e}")
        return None


# CHANGED: Accepts history parameter from main.py
def run_chat(history):
    print('\nJon Snow: "Winter is coming, and so are your bills."')
    print("Type 'summary' to generate a Markdown report.")
    print("Type 'return' to switch back to the main menu.\n")

    while True:
        user_input = input("Jon Snow >> ").strip()

        # Safely return back to main selection menu
        if user_input.lower() in ['exit', 'return']:
            print("Returning to main menu...\n")
            break

        if user_input.lower() == "summary":
            filename = create_markdown_document(client, history, system_message)
            if filename:
                print(f"\n✅ Report created successfully!")
                print(f"📄 Saved as: {filename}")
                print("Open it in VS Code and press Ctrl+Shift+V for a formatted preview.\n")
            continue

        history.append({"role": "user", "content": user_input})

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                temperature=0.7,
                system=system_message,
                messages=history
            )

            reply = f"Jon Snow: {response.content[0].text}"
            print(f"\n{reply}\n")
            history.append({"role": "assistant", "content": reply})

        except Exception as e:
            print(f"\nSomething went wrong: {e}")
            break