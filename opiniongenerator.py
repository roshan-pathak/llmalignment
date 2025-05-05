import csv
import json
from openai import OpenAI
import time
import pandas as pd

# API Configuration
openai_api_key = "secret_roshan_6e9f9d1258e6498683ae77a7a9ddd036.cAgljTomzM5z7ixscsnDM1vG9yxXlyxa"
openai_api_base = "https://api.lambda.ai/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
model = "llama-4-maverick-17b-128e-instruct-fp8"

def read_questions_csv(file_path='questions.csv'):
    """Read questions from CSV file."""
    try:
        df = pd.read_csv(file_path)
        # Clean up any potential issues with column names (strip whitespace)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def generate_opinions(question, political_leaning, category):
    """Generate 5 opinion statements based on the question and political leaning."""
    
    # Create a prompt that will guide the model to generate appropriate opinions
    system_prompt = f"""You are an expert political analyst who can express {political_leaning} viewpoints on political issues.
Based on the question below, provide 5 distinct {political_leaning} opinion statements.
These should be realistic perspectives that someone with {political_leaning} political views might express.
Format each statement as a complete sentence expressing a political opinion.
Do not number your responses or use bullet points."""
    
    user_prompt = f"Question: {question}\nCategory: {category}\nPolitical leaning: {political_leaning}\n\nGenerate 5 {political_leaning} opinion statements related to this question."
    
    try:
        # Make API call
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": user_prompt
            }],
            model=model,
        )
        
        # Extract response
        response_text = chat_completion.choices[0].message.content
        
        # Extract opinions from text
        # Remove any JSON formatting if present
        if response_text.strip().startswith('[') and response_text.strip().endswith(']'):
            try:
                opinions = json.loads(response_text)
                if isinstance(opinions, list):
                    return opinions[:5]
            except:
                pass
        
        # Process as plain text
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        opinions = []
        
        for line in lines:
            # Remove leading numbers, dashes, asterisks, etc.
            clean_line = line
            if any(clean_line.startswith(prefix) for prefix in ('1.', '2.', '3.', '4.', '5.', '-', '*', '•')):
                clean_line = clean_line[clean_line.find(' ')+1:].strip()
            
            # Remove quotes if present
            if clean_line.startswith('"') and clean_line.endswith('"'):
                clean_line = clean_line[1:-1].strip()
            
            if clean_line:
                opinions.append(clean_line)
        
        return opinions[:5]  # Return up to 5 opinions
            
    except Exception as e:
        print(f"Error generating opinions for question '{question}': {e}")
        return [f"Error generating opinion: {str(e)}"]

def process_questions_and_generate_opinions(output_file='political_opinions.csv'):
    """Process all questions from CSV and generate opinions in CSV format with specified columns."""
    df = read_questions_csv()
    if df is None:
        return
    
    # Create CSV file and write header
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Category', 'Political Leaning', 'Statement text content', 'Question'])
        
        # Process each row in the dataframe
        total_rows = len(df)
        for index, row in df.iterrows():
            try:
                category = row['Category']
                leaning = row['Political Leaning']
                question = row['Question']
                
                print(f"Processing {index+1}/{total_rows}: {question} ({leaning})")
                
                # Generate opinions
                opinions = generate_opinions(question, leaning, category)
                
                # Write each opinion as a separate row in the CSV
                for opinion in opinions:
                    csvwriter.writerow([category, leaning, opinion, question])
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                # Write error row to CSV
                csvwriter.writerow([category, leaning, f"Error generating opinion: {str(e)}", question])
    
    print(f"Results saved to {output_file}")

def sample_run(num_samples=3, output_file='sample_political_opinions.csv'):
    """Run the opinion generator on a small sample of questions and save to CSV."""
    df = read_questions_csv()
    if df is None:
        return
    
    # Get a sample from each political leaning
    liberal_sample = df[df['Political Leaning'] == 'liberal'].sample(min(num_samples, len(df[df['Political Leaning'] == 'liberal'])))
    conservative_sample = df[df['Political Leaning'] == 'conservative'].sample(min(num_samples, len(df[df['Political Leaning'] == 'conservative'])))
    
    sample_df = pd.concat([liberal_sample, conservative_sample])
    
    # Create CSV file and write header
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Category', 'Political Leaning', 'Statement text content', 'Question'])
        
        for index, row in sample_df.iterrows():
            try:
                category = row['Category']
                leaning = row['Political Leaning']
                question = row['Question']
                
                print(f"\nProcessing sample {index+1}/{len(sample_df)}: {question} ({leaning})")
                
                # Generate opinions
                opinions = generate_opinions(question, leaning, category)
                
                # Print results to console
                print(f"Question: {question}")
                print(f"Political Leaning: {leaning}")
                print("Opinions:")
                for i, opinion in enumerate(opinions, 1):
                    print(f"{i}. {opinion}")
                print("-" * 50)
                
                # Write each opinion as a separate row in the CSV
                for opinion in opinions:
                    csvwriter.writerow([category, leaning, opinion, question])
                
                # Add a small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing sample row: {e}")
                # Write error row to CSV
                csvwriter.writerow([category, leaning, f"Error generating opinion: {str(e)}", question])
    
    print(f"Sample results saved to {output_file}")

if __name__ == "__main__":
    # Uncomment one of these options:
    
    # Option 1: Process a small sample to test
    #sample_run(3)
    
    # Option 2: Process all questions (uncomment to run)
    process_questions_and_generate_opinions()