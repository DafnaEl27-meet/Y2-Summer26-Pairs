import os
import re
from tkinter import Tk, filedialog  # Added for visual folder picker
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

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

def get_user_save_directory():
    """Opens a native visual folder picker dialog window."""
    print("Select a destination folder in the pop-up window...")
    root = Tk()
    root.withdraw()  # Hide the main tiny tkinter window
    root.attributes('-topmost', True)  # Bring folder picker window to the front
    
    selected_dir = filedialog.askdirectory(title="Choose Where to Save the File")
    root.destroy()  # Clean up tkinter instance
    
    if not selected_dir:
        print("⚠️ Save location not selected. Saving to current workspace instead.")
        return "."  # Fallback to current folder if user closes window
    return selected_dir

def create_markdown_document(chat_history):
    """Processes live chat history, strips tags, and exports a clean .md file to a chosen path."""
    md_content = []
    md_content.append("# Financial Advisory Session Transcript\n")
    md_content.append("**Assistant Agent:** Dave (*Investing & Savings Expert*)\n")
    md_content.append("---\n") 
    
    for message in chat_history:
        role = message['role'].capitalize()
        content = message['content']
        
        clean_content = re.sub(r'\[CREATE_MARKDOWN\]|\[CREATE_DASHBOARD\]', '', content).strip()
        if "```html" in clean_content:
            clean_content = clean_content.split("```html")[0].strip()
            
        if not clean_content:
            continue
            
        if role == 'User':
            md_content.append(f"### 👤 You\n> {clean_content}\n")
        else:
            md_content.append(f"### {clean_content.split(':')[0] if ':' in clean_content else '🤖 AI'}\n> {clean_content}\n")
            
    # Get user folder selection and build full path
    target_dir = get_user_save_directory()
    filename = "Financial_Chat_Summary.md"
    full_save_path = os.path.join(target_dir, filename)

    with open(full_save_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
    return full_save_path

def create_html_dashboard(raw_reply):
    """Extracts the HTML code block from Claude's response and writes it to a chosen path."""
    code_block_match = re.search(r'```html\s*(.*?)\s*```', raw_reply, re.DOTALL)
    if code_block_match:
        html_content = code_block_match.group(1)
    else:
        html_content = re.sub(r'\[CREATE_DASHBOARD\]', '', raw_reply).strip()

    # Get user folder selection and build full path
    target_dir = get_user_save_directory()
    filename = "savings_dashboard.html"
    full_save_path = os.path.join(target_dir, filename)

    with open(full_save_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return full_save_path


# CHANGED: Accepts history parameter from main.py
def run_chat(history):
    print('\nDave: Hello! I am Dave. Ask me anything about investing or savings.')
    print("Type 'return' to switch back to the main menu.\n")

    while True:
        user_input = input('Dave >> ').strip()
        
        if not user_input:
            continue

        if user_input.lower() in ['exit', 'return']:
            print("Returning to main menu...\n")
            break

        history.append({'role': 'user', 'content': user_input})
        
        try: 
            response = client.messages.create(
                model='claude-3-5-sonnet-20241022', # Standard active model identifier 
                max_tokens=4000, 
                temperature=0.3,  
                system=system_message,
                messages=history
            )
        except Exception as e:
            print(f"Something went wrong with the API call: {e}")
            break

        reply = f"Dave: {response.content[0].text}"
        
        # --- AGENT AUTOMATED DOCUMENT CREATION ---
        if "[CREATE_MARKDOWN]" in reply:
            print(f'\nDave: Creating your Markdown document now...')
            try:
                saved_file = create_markdown_document(history)
                print(f"✅ Success: Document saved at:\n👉 {saved_file}\n")
            except Exception as file_err:
                print(f"⚠️ Failed to generate Markdown file: {file_err}")
                
        # --- AGENT AUTOMATED INTERACTIVE DASHBOARD GENERATION ---
        elif "[CREATE_DASHBOARD]" in reply:
            print(f'\nDave: Building your live interactive savings dashboard app now...')
            try:
                text_intro = reply.split("[CREATE_DASHBOARD]")[0].strip()
                print(f"\n{text_intro}")
                saved_dashboard = create_html_dashboard(reply)
                print(f"\n🚀 Success: Dashboard application written to:\n👉 {saved_dashboard}\n")
            except Exception as html_err:
                print(f"⚠️ Failed to generate HTML Dashboard file: {html_err}")
        else:
            print(f'\n{reply}\n')

        history.append({'role': 'assistant', 'content': reply})

if __name__ == "__main__":
    conversation_history = []
    run_chat(conversation_history)