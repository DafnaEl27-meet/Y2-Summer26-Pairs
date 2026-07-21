import os
import re
import sys
from tkinter import Tk, filedialog  # Added for folder selection window
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found.")
    sys.exit(1)

client = Anthropic(api_key=api_key)
MODEL = "claude-3-5-sonnet-20241022"  
MAX_HISTORY = 20

system_message = """You are Jon Snow, a highly professional, analytical, and supportive personal finance and expenses manager. Your core responsibility is to help users manage their financial decisions, track expenses, and allocate their budget strictly based on their total income.

Core Rules:
- Income Constraint: You must operate strictly within the user's provided income.
- Never invent numbers.
- If information is missing, ask for it.

Standalone File Creation Trigger:
- CRITICAL: If the user asks you to create a separate script, tracking spreadsheet format, configuration file, or any specific external file (e.g., script.py, budget.csv, config.json), you MUST include this exact tag at the very end of your text response: [CREATE_FILE]
- Directly below that tag, output a structured header specifying the filepath and code block like this:
FILEPATH: <your_filename_here>
```<language>
<file contents here>
```
- Do not output explanations of the code in the main chat. Just confirm you are generating the file, append the tag, and output the structure.

Response Format (for normal chat replies when not creating files):
1. One-sentence summary.
2. Financial assessment.
3. Exactly one follow-up question."""

def extract_text(response):
    return "".join(block.text for block in response.content if hasattr(block, "text"))

def get_user_save_directory():
    """Opens a native visual folder picker dialog window."""
    print("Select a folder in the pop-up window...")
    root = Tk()
    root.withdraw()  # Hide the main tiny tkinter window
    root.attributes('-topmost', True)  # Bring folder picker to the front
    
    selected_dir = filedialog.askdirectory(title="Choose Where to Save the File")
    root.destroy()  # Clean up tkinter instance
    
    if not selected_dir:
        print("⚠️ Save cancelled. Saving to current workspace folder instead.")
        return "."  # Fallback to current folder if user closes window
    return selected_dir

def auto_generate_file(raw_reply):
    """Parses out the filename, asks user for target directory, and saves it."""
    filepath_match = re.search(r'FILEPATH:\s*([^\s\n\r]+)', raw_reply)
    if not filepath_match:
        raise ValueError("Could not extract a valid filename from the response structure.")
        
    filename = filepath_match.group(1).strip()
    # Strip path details if AI tried to guess a folder structure
    filename = os.path.basename(filename) 
    
    # Extract contents enclosed within standard markdown code blocks
    code_block_match = re.search(r'```[a-zA-Z]*\s*(.*?)\s*```', raw_reply, re.DOTALL)
    if code_block_match:
        file_content = code_block_match.group(1)
    else:
        file_content = raw_reply.split("```")[-1].strip()

    # Get destination from user browse window
    target_dir = get_user_save_directory()
    full_save_path = os.path.join(target_dir, filename)

    with open(full_save_path, "w", encoding="utf-8") as f:
        f.write(file_content)
    return full_save_path

def run_chat(history):
    print("\nJon Snow: Winter is coming, and so are your bills.")
    print("You can ask me to create specialized data files or scripts directly.")
    print("Type 'return' to go back.\n")
    
    while True:
        user_input = input("Jon Snow >> ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ("return", "exit"):
            print("Returning to menu...\n")
            break
            
        history.append({"role": "user", "content": user_input})
        
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4000,  
                temperature=0.3,
                system=system_message,
                messages=history[-MAX_HISTORY:]
            )
            raw_reply = extract_text(response)
            reply = f"Jon Snow: {raw_reply}"
            
            if "[CREATE_FILE]" in reply:
                text_intro = reply.split("[CREATE_FILE]")[0].strip()
                print(f"\n{text_intro}")
                try:
                    saved_path = auto_generate_file(raw_reply)
                    print(f"✅ Success: File written cleanly to:\n👉 {saved_path}\n")
                except Exception as file_err:
                    print(f"⚠️ Failed to write external file: {file_err}")
            else:
                print(f"\n{reply}\n")
                
            history.append({"role": "assistant", "content": reply})
                
        except Exception as e:
            print(f"\nSomething went wrong:\n{e}")
            break

if __name__ == "__main__":
    conversation_history = []
    run_chat(conversation_history)