from anaya.core import Anaya

if __name__ == "__main__":
    anaya = Anaya(
            title="Anaya🔥📑",
            initial_message="Hello! I am **Anaya🔥**. How can I help you today?",
            model="llama3:8b"
        )
    anaya.run()