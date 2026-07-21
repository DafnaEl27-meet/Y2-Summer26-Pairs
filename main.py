import sys

# Import the original agents
from app1 import run_chat as run_chat_app1
from app2 import run_chat as run_chat_app2

def main():
    # This single list holds the entire conversation for both AIs to read
    shared_history = []

    print("Hello user. In this program, you can chat with two ai models.")
    print("The first is an ai assistant that can calculate and answer your questions about finance.")
    print("The second is an ai model that can help you find good investment and savings options.")
    print("✨ Both models now share the exact same conversational memory track!")

    while True:
        print("\nWhich agent do you want to use?")
        print("Agent 1 — Finance Calculator Assistant (Jon Snow)")
        print("Agent 2 — Investment and Savings Strategy Expert (Dave)")
        print("stop — Exit Program")

        choice = input("Please select one of the ai models to chat with (1, 2, or stop): ").strip()

        if choice == '1':
            # Run Agent 1 and give it access to the shared memory track
            run_chat_app1(shared_history) 
        elif choice == '2':
            # Run Agent 2 and give it access to the shared memory track
            run_chat_app2(shared_history) 
        elif choice == 'stop':
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice! Please type 1, 2, or stop to proceed.")

if __name__ == "__main__":
    main()
