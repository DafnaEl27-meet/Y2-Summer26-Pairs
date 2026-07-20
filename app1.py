import os
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# System message updated to handle both markdown reports and HTML visual dashboards
system_message = """
You are Dave, a helpful assistant that helps users with investing and savings options.

Your job is to answer all the user's questions about investing and savings.

Rules:
- Always answer the user's questions in a helpful and professional manner.
- Always provide accurate information and never make up answers.
- Don't answer questions that are not related to investing and savings (unless they ask you to export/save the current conversation history).

Document Creation Trigger:
- CRITICAL: IF the user asks you to save the conversation, make a copy of the chat, export, or generate a report as a document, you MUST include this exact tag at the very end of your response text: [CREATE_MARKDOWN]
- Do not output the document content as raw text in the chat. Just confirm that you are generating it and append the tag.

Visual Dashboard Trigger:
- CRITICAL: IF the user asks you to create an interactive dashboard, visual comparison tool, calculator, matrix, or visual savings tracker, you MUST include this exact tag at the very end of your response text: [CREATE_DASHBOARD]
- Underneath that tag, output the FULL, raw, self-contained HTML/CSS/JS code block. The code must use Tailwind CSS via CDN for styling. It must feature dynamic sliders for timelines (1 month to 5 years), compound interest formulas reflecting actual product structures (HYSA vs CD vs T-Bill), and a visual Risk vs Return matrix/grid. 
- Do not explain the code in the chat. Just confirm you are building it, append the tag, and output the code block.

Response format (for normal chat replies):
- Start with a one-sentence summary of what the user said.
- Then give your response.
- End with one follow-up question.
"""

def create_markdown_document(chat_history):
    """Processes live chat history, strips tags, and exports a clean .md file."""
    md_content = []
    md_content.append("# Financial Advisory Session Transcript\n")
    md_content.append("**Assistant Agent:** Dave (*Investing & Savings Expert*)\n")
    md_content.append("---\n") 
    
    for message in chat_history:
        role = message['role'].capitalize()
        content = message['content']
        
        # Scrub operational tags out
        clean_content = re.sub(r'\[CREATE_MARKDOWN\]|\[CREATE_DASHBOARD\]', '', content).strip()
        if "```html" in clean_content:
            clean_content = clean_content.split("```html")[0].strip()
            
        if not clean_content:
            continue
            
        if role == 'User':
            md_content.append(f"### 👤 You\n> {clean_content}\n")
        else:
            md_content.append(f"### 🤖 Dave\n> {clean_content}\n")
            
    filename = "Financial_Chat_Summary.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
    return filename

def create_html_dashboard(raw_reply):
    """Extracts the HTML code block from Claude's response and writes it to a file."""
    # Regex to extract everything inside the ```html ``` code blocks
    code_block_match = re.search(r'```html\s*(.*?)\s*```', raw_reply, re.DOTALL)
    
    if code_block_match:
        html_content = code_block_match.group(1)
    else:
        # Fallback if the model didn't wrap it cleanly in markdown blocks
        html_content = re.sub(r'\[CREATE_DASHBOARD\]', '', raw_reply).strip()

    filename = "savings_dashboard.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filename

def run_chat():
    print('Dave: Hello! I am Dave. Ask me anything about investing or savings. (type "exit" to quit)')
    history = []

    while True:
        user_input = input('>> ')
        
        if user_input.lower() == 'exit':
            print("Dave: Goodbye!")
            break

        history.append({'role': 'user', 'content': user_input})
        
        try: 
            # Updated to leverage Claude 4.5 for complex code generation & reasoning
            response = client.messages.create(
                model='claude-4-5-20250227', 
                max_tokens=4000, # Increased max tokens to accommodate large HTML application outputs
                temperature=0.3,  # Lowered temperature slightly for precise coding tasks
                system=system_message,
                messages=history
            )
        except Exception as e:
            print(f"Something went wrong with the API call: {e}")
            break

        try:
            if hasattr(response, 'content') and isinstance(response.content, list):
                reply = response.content[0].text
            elif hasattr(response.content, 'text'):
                reply = response.content.text
            else:
                reply = str(response.content)
        except Exception as parse_err:
            print(f"Failed parsing message content: {parse_err}")
            break
        
        # --- AGENT AUTOMATED DOCUMENT CREATION ---
        if "[CREATE_MARKDOWN]" in reply:
            print(f'\nDave: Creating your Markdown document now...')
            try:
                saved_file = create_markdown_document(history)
                print(f"✅ Success: Document saved as '{saved_file}' in your VS Code workspace!")
                print(f"💡 Tip: Click the file, then press 'Ctrl+Shift+V' ('Cmd+Shift+V' on Mac) to view formatted layout.\n")
            except Exception as file_err:
                print(f"⚠️ Failed to generate Markdown file: {file_err}")
                
        # --- AGENT AUTOMATED INTERACTIVE DASHBOARD GENERATION ---
        elif "[CREATE_DASHBOARD]" in reply:
            print(f'\nDave: Building your live interactive savings dashboard app now...')
            try:
                # Strip out the chat response preamble to show to the user
                text_intro = reply.split("[CREATE_DASHBOARD]")[0].strip()
                print(f"\nDave: {text_intro}")
                
                saved_dashboard = create_html_dashboard(reply)
                print(f"\n🚀 Success: Dashboard application written to '{saved_dashboard}'!")
                print(f"💡 Tip: Right-click '{saved_dashboard}' in VS Code and select 'Open Timeline', or open it directly in your web browser to play with the calculators and risk matrix.\n")
            except Exception as html_err:
                print(f"⚠️ Failed to generate HTML Dashboard file: {html_err}")
        else:
            print(f'\nDave: {reply}\n')

        # Save assistant reply to memory
        history.append({'role': 'assistant', 'content': reply})

if __name__ == "__main__":
    run_chat()