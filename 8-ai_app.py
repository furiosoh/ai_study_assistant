import json 
import requests


print("===== AI STUDY ASSISTANT =====")

print("1. Ask a question")
print("2. Summarize text")
print("3. Generate a quiz")
print("4. Exit")

choice = input("Choose an option: ")

if choice == "1":
    query = input("Please ask your question: ")

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:0.6b",
            "prompt": query,
            "stream": False
        }
    )

    data = response.json()

    print(data["response"])

elif choice == "2":
    text = input("Enter the text you want summarized: ")

    word_count = len(text.split())

    while True:
        print("Choose summary length:")
        print("1. Very short")
        print("2. Normal")
        print("3. Detailed")

        summary_choice = input("Choose an option: ")

        if summary_choice == "1":
            minimum = int(word_count * 0.15)
            maximum = int(word_count * 0.25)
            break

        elif summary_choice == "2":
            minimum = int(word_count * 0.35)
            maximum = int(word_count * 0.45)
            break

        elif summary_choice == "3":
            minimum = int(word_count * 0.65)
            maximum = int(word_count * 0.75)
            break

        else:
            print("Invalid choice. Please choose 1, 2, or 3.")

    prompt = f"""
    Summarize the following text.

    Target length: {minimum}-{maximum} words.

    Keep the important information and do not add information
    that is not present in the original text.

    Text:
    {text}
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:0.6b",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    print(data["response"])

elif choice == "3":
    topic = input("Enter the quiz topic: ")

    print("Choose number of questions:")
    print("1. 5 questions")
    print("2. 10 questions")
    print("3. 15 questions")

    question_count = input("Choose an option: ")

    if question_count == "1":
        number = 5
    elif question_count == "2":
        number = 10
    elif question_count == "3":
        number = 15
    else:
        print("Invalid choice.")
        number = 5

    print("Choose question type:")
    print("1. Multiple Choice")
    print("2. Short Answer")
    print("3. True / False")

    question_type = input("Choose an option: ")

    if question_type == "1":
        q_type = "multiple choice"
    elif question_type == "2":
        q_type = "short answer"
    elif question_type == "3":
        q_type = "true or false"
    else:
        print("Invalid choice.")
        q_type = "multiple choice"

    print("Choose difficulty:")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")

    difficulty = input("Choose an option: ")

    if difficulty == "1":
        level = "easy"
    elif difficulty == "2":
        level = "medium"
    elif difficulty == "3":
        level = "hard"
    else:
        print("Invalid choice.")
        level = "medium"

    prompt = f"""
    Create a {level} difficulty quiz about {topic}.

    Create exactly {number} questions.

    Question type: {q_type}

    Follow these rules:

    If the question type is multiple choice:
    - Each question must have exactly four answer options.
    - Only one option may be correct.
    - The four options must be clearly different.
    - Do not use duplicate or nearly identical options.
    - Incorrect options should be plausible but clearly wrong.
    - The correct_answer must exactly match one of the four options.
    - Questions must be clear and unambiguous.

    If the question type is short answer:
    - Each question must have a clear, concise answer.
    - Do not include answer options.

    If the question type is true or false:
    - Each question must have exactly one correct answer.
    - correct_answer must be exactly "True" or "False".
    - Do not include answer options.

    Before returning the quiz, check every question for:
    1. A clear question.
    2. Exactly one correct answer.
    3. Correct formatting for the requested question type.

    Return ONLY valid JSON.
    Do not use Markdown.
    Do not use code fences.
    Do not include explanations outside the JSON.

    For multiple choice, use:
    [
    {{
        "question": "Question here",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "correct_answer": "Correct option"
    }}
    ]

    For short answer, use:
    [
    {{
        "question": "Question here",
        "correct_answer": "Correct answer"
    }}
    ]

    For true or false, use:
    [
    {{
        "question": "Question here",
        "correct_answer": "True"
    }}
    ]
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:0.6b",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    quiz_text = data["response"].strip()

    print("AI RESPONSE:")
    print(quiz_text)

    # Remove markdown fences if Qwen adds them anyway
    if quiz_text.startswith("```json"):
        quiz_text = quiz_text[7:]

    if quiz_text.endswith("```"):
        quiz_text = quiz_text[:-3]

    try:
        quiz = json.loads(quiz_text)
    except json.JSONDecodeError:
        print("The AI returned invalid JSON. Please try again.")
        exit()

    # Normalize different structures into one list
    if isinstance(quiz, list):
        questions = quiz

    elif isinstance(quiz, dict) and "questions" in quiz:
        questions = quiz["questions"]

    else:
        print("The AI returned an unexpected quiz format.")
        exit()

    # Make sure we actually received questions
    if not questions:
        print("The AI did not return any questions.")
        exit()

    for question in questions:
        if "question" not in question or "correct_answer" not in question:
            print("The AI returned an incomplete question. Please try again.")
            exit()

        if q_type == "multiple choice":
            if "options" not in question or len(question["options"]) != 4:
                print("The AI returned an invalid multiple-choice question.")
                exit()

    # Run the quiz
    score = 0

    for i, question in enumerate(questions, start=1):
        print()
        print(f"Question {i}/{len(questions)}")
        print(question["question"])

        if q_type == "multiple choice":
            for j, option in enumerate(question["options"], start=1):
                print(f"{j}. {option}")

            while True:
                answer = input("Your answer (1-4): ")

                if answer in ["1", "2", "3", "4"]:
                    break

                print("Please enter 1, 2, 3, or 4.")

            selected_answer = question["options"][int(answer) - 1]

        elif q_type == "true or false":
            while True:
                answer = input("Your answer (True/False): ").strip().lower()

                if answer in ["true", "false"]:
                    break

                print("Please enter True or False.")

            selected_answer = answer.capitalize()

        else:
            selected_answer = input("Your answer: ").strip()

        if selected_answer.lower() == question["correct_answer"].strip().lower():
            print("Correct!")
            score += 1
        else:
            print("Incorrect.")
            print(f"Correct answer: {question['correct_answer']}")

    percentage = (score / len(questions)) * 100

    print()
    print("===== QUIZ RESULT =====")
    print(f"Score: {score}/{len(questions)}")
    print(f"Percentage: {percentage:.1f}%")

    if percentage >= 80:
        print("Excellent performance! You have a strong understanding of this topic.")
    elif percentage >= 60:
        print("Good performance! You understand the basics, but there is room for improvement.")
    else:
        print("Keep practicing. Reviewing the topic and trying another quiz should help.")

elif choice == "4":
    print("Goodbye!")

else:
    print("Invalid option.")