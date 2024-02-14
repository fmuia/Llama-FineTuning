# aux_functions.py

import re
from collections import Counter
import pandas as pd
import openai

# Function to extract the LaTeX content between \begin{document} and \end{document}
def extract_latex_content(file_path):
    """Extract content from LaTeX source file between \begin{document} and \end{document}."""
    content = []
    copy = False
    with open(file_path, 'r') as file:
        for line in file:
            if '\\begin{document}' in line:
                copy = True
                continue  # Skip this line
            elif '\\end{document}' in line:
                copy = False
                continue  # Skip this line
            if copy:
                content.append(line)
    return ''.join(content)

def replace_latex_commands(latex_content):
    # Replace specific LaTeX commands with direct character replacements
    replacements = {
        r'\\d': 'd',
        r'\\G': 'G',
        r'\\O': 'O',
        r'\\C': 'C',
        r'\\V': 'V',
        r'\\L': 'L',
        r'\\R': 'R',
        r'\\S': 'S',
    }
    
    # Apply direct replacements
    for command, replacement in replacements.items():
        latex_content = re.sub(command, replacement, latex_content)
    
    # Replace commands with content inside curly braces, preserving the content
    brace_commands = [r'\\emph', r'\\footnote']
    for command in brace_commands:
        latex_content = re.sub(command + r'\{(.*?)\}', r'\1', latex_content)
    
    return latex_content

def clean_latex_content(latex_content):
    # Step 1: Preserve specific LaTeX content with placeholders
    placeholders = {}
    preserved_patterns = {
        r'\\begin\{equation\}.*?\\end\{equation\}': 'EQUATION_PLACEHOLDER',
        r'\\begin\{eqnarray\}.*?\\end\{eqnarray\}': 'EQNARRAY_PLACEHOLDER',
        r'\\emph\{.*?\}': 'EMPH_PLACEHOLDER',
        r'\$.*?\$': 'MATH_PLACEHOLDER',
        r'\\cite\{.*?\}': 'CITE_PLACEHOLDER',
        r'\\eqref\{.*?\}': 'EQREF_PLACEHOLDER',
        r'\\be\b.*?\\ee\b': 'BEEE_PLACEHOLDER'
    }
    for pattern, placeholder in preserved_patterns.items():
        def repl(m):
            placeholder_with_index = f'{placeholder}_{len(placeholders)}'
            placeholders[placeholder_with_index] = m.group(0)
            return placeholder_with_index
        latex_content = re.sub(pattern, repl, latex_content, flags=re.DOTALL)

    # Step 2: Remove unwanted LaTeX commands and clean up the content
    latex_content = re.sub(r'\\[a-zA-Z]+\*?(?:\[.*?\])?(?:\{.*?\})?', '', latex_content)
    latex_content = re.sub(r'\n+', ' ', latex_content)
    latex_content = re.sub(r'\s+', ' ', latex_content)  # Normalize spaces

    # Step 3: Normalize \cite commands and remove extra backslashes
    latex_content = latex_content.replace('\\\\cite', '\\cite')

    # Step 4: Remove unnecessary braces and backslashes not part of placeholders or escaped characters
    latex_content = re.sub(r'\\(?![a-zA-Z])', '', latex_content)  # Remove backslashes not part of a command
    latex_content = re.sub(r'(?<!PLACEHOLDER_\d)\{|\}(?!PLACEHOLDER_\d)', '', latex_content)  # Remove braces not part of placeholders

    # Step 5: Restore preserved content from placeholders
    for placeholder, original in placeholders.items():
        latex_content = latex_content.replace(placeholder, original)

    # Step 6: Address sectioning commands after placeholders are restored to avoid conflicts
    sectioning_commands = {
        r'\\section\*?\{(.*?)\}': 'Section - \\1',
        r'\\subsection\*?\{(.*?)\}': 'Subsection - \\1',
        r'\\subsubsection\*?\{(.*?)\}': 'Subsubsection - \\1',
    }
    for pattern, replacement in sectioning_commands.items():
        latex_content = re.sub(pattern, replacement, latex_content)

    return latex_content.strip()

def chunk_text(text, min_chunk_length):
    # This regex splits the text at sentence boundaries while attempting to preserve LaTeX command integrity
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    overlap_sentence = ""

    for i, sentence in enumerate(sentences):
        if not current_chunk:
            # Start new chunk
            current_chunk = sentence
        elif len(current_chunk) + len(sentence) + 1 < min_chunk_length:
            # Add sentence to current chunk if under min length; +1 accounts for a space
            current_chunk += " " + sentence
        else:
            # Current chunk is at or above min length; prepare for next chunk
            chunks.append(current_chunk)
            current_chunk = overlap_sentence + " " + sentence if overlap_sentence else sentence
            overlap_sentence = ""  # Reset overlap

        # Check if this sentence should be overlap for next chunk
        if i < len(sentences) - 1:  # Ensure not processing the last sentence
            overlap_sentence = sentence

    # Finalize last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def generate_prompt(chunk, num_questions, system_prompt_content, user_prompt_content):
    system_prompt = {
        "role": "system",
        "content": system_prompt_content.format(num_questions=num_questions)
    }
    user_prompt = {
        "role": "user",
        "content": user_prompt_content.format(chunk=chunk)
    }
    return system_prompt, user_prompt



def generate_qa_pairs(text_chunk, num_pairs=1):
    """
    Generate question and answer pairs from a text chunk using OpenAI's GPT-3.5 Turbo.

    :param text_chunk: The text chunk to generate Q&A from.
    :param num_pairs: Number of Q&A pairs to generate for each chunk.
    :return: A list of dictionaries containing questions and answers.
    """
    qa_pairs = []
    for _ in range(num_pairs):
        # Create a message list for the conversation. Start with a system message to set the context.
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Please read the following text and generate a question and an answer based on it."},
            {"role": "user", "content": text_chunk}
        ]
        
        # Generate a completion with the chat model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages
        )
        
        # Assuming the last two messages are the question and answer
        if len(response['choices'][0]['message']['content']) >= 2:
            question = response['choices'][0]['message']['content'][-2]['content']
            answer = response['choices'][0]['message']['content'][-1]['content']
            qa_pairs.append({"question": question, "answer": answer})
    
    return qa_pairs