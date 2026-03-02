import google.generativeai as genai
import json
import os
import time
import argparse

def get_api_key():
    """
    Gets the Gemini API key from an environment variable or a file.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("Found API key in environment variable.")
        return api_key
    
    try:
        with open("GEMINI_API_KEY.txt", "r") as f:
            api_key = f.read().strip()
            if api_key:
                print("Found API key in GEMINI_API_KEY.txt file.")
                return api_key
    except FileNotFoundError:
        pass

    return None

def generate_explanation_for_question(model, question_obj):
    """
    Constructs a prompt and calls the Gemini API to get a deep explanation.
    """
    q_text = question_obj['question_text']
    options = question_obj['options']
    correct_answers_keys = question_obj['correct_answer'].split(',')
    correct_answers_keys = [ans.strip() for ans in correct_answers_keys]
    
    correct_answers_text = [f"{key}: {options[key]}" for key in correct_answers_keys if key in options]

    prompt_parts = [
        "You are an expert Google Cloud trainer. Your task is to provide a deep and educational analysis of a practice exam question.",
        "**Question:**",
        q_text,
        "**Options:**"
    ]
    for key, value in options.items():
        prompt_parts.append(f"- **{key}:** {value}")

    prompt_parts.append(f"**The correct answer is:**\n- {' | '.join(correct_answers_text)}")
    
    prompt_parts.append("**Your Analysis Task:**")
    prompt_parts.append("1.  **Correct Answer Deep Dive:** Start with the heading '### Correct Answer Explanation'. In detail, explain why the correct option(s) is the best choice. Go beyond surface-level keywords. Connect the problem in the question to the specific architectural advantages and core technical concepts of the chosen GCP service(s).")
    prompt_parts.append("2.  **Incorrect Options Analysis:** Follow with the heading '### Incorrect Answers Analysis'. For EACH of the other, incorrect options, provide a specific, concise reason why it is not the best choice for this scenario. Explain its technical limitations or why it's a less suitable architectural pattern compared to the correct answer.")
    prompt_parts.append("Format your response using Markdown for clarity.")

    prompt = "\n".join(prompt_parts)

    # Correct safety settings to prevent API from blocking legitimate technical content.
    safety_settings = {
        'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
    }

    try:
        response = model.generate_content(prompt, safety_settings=safety_settings)
        # It's safer to check the response before trying to access the text.
        if response.candidates and response.candidates[0].finish_reason == 'SAFETY':
             return f"Error: The response was blocked by the safety filter for the following reasons: {response.candidates[0].safety_ratings}"
        return response.text
    except Exception as e:
        print(f"  [ERROR] API call failed for question {question_obj.get('question_id', 'N/A')}: {e}")
        # Return a specific error message to be placed in the JSON
        return f"Error generating explanation: {e}"

def process_file(model, file_path, start_index=0):
    """
    Processes a JSON file, generates explanations, and saves the result.
    """
    print(f"\n--- Processing {file_path} ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not read or parse {file_path}: {e}")
        return

    # Create a backup
    backup_path = file_path + '.bak'
    print(f"Creating a backup at {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    questions_to_process = data[start_index:]

    for i, q in enumerate(questions_to_process):
        actual_index = i + start_index
        q_id = q.get('question_id', f'index_{actual_index}')
        print(f"  ({actual_index + 1}/{len(data)}) Generating explanation for question ID: {q_id}...")
        
        # Use a more descriptive title
        explanation = generate_explanation_for_question(model, q)
        q['ai_explanation'] = "💡 <b>Gemini Deep Dive Explanation:</b>\n" + explanation
        
        # Save progress every 10 questions
        if (i + 1) % 10 == 0:
            print("  Saving progress...")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        
        # A small delay to respect potential API rate limits
        time.sleep(2)

    # Final save
    print("  Final save...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"--- Finished processing {file_path} ---")


def main():
    parser = argparse.ArgumentParser(description="Generate deep AI explanations for GCP practice questions.")
    parser.add_argument('--file', help='Specify a single JSON file to process (e.g., qa_parsed.json). If not provided, both files will be processed.')
    parser.add_argument('--start_index', type=int, default=0, help='The index of the question to start processing from. Useful for resuming a long job.')
    
    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        print("\n[FATAL] Gemini API Key not found.")
        print("Please create a file named GEMINI_API_KEY.txt in this directory and paste your key in it,")
        print("OR set the GEMINI_API_KEY environment variable.")
        print("You can get a free key from Google AI Studio: https://aistudio.google.com/app/apikey")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')

    files_to_process = []
    if args.file:
        if os.path.exists(args.file):
            files_to_process.append(args.file)
        else:
            print(f"Error: Specified file '{args.file}' not found.")
            return
    else:
        files_to_process = ['qa_parsed.json', 'pde_parsed.json']

    for file_path in files_to_process:
        process_file(model, file_path, args.start_index)
        # Reset start index for the next file if it's not specified
        if args.start_index != 0 and not args.file:
            args.start_index = 0
            
    print("\nAll explanations have been upgraded!")

if __name__ == '__main__':
    main()
