import requests
import json
import argparse

def analyze_propaganda(text, model="llama3", host="http://localhost:11434"):
    """
    Send text to an Ollama model to analyze if it contains propaganda.
    
    Args:
        text (str): The news text to analyze
        model (str): The Ollama model to use
        host (str): The Ollama API host address
    
    Returns:
        dict: The analysis result
    """
    # Construct the system prompt with context about propaganda analysis
    system_prompt = """
    You are an expert in propaganda analysis with deep knowledge of rhetorical techniques, 
    logical fallacies, and media manipulation strategies. Your task is to analyze the 
    provided news content and determine if it contains propaganda elements.
    
    For your analysis, consider these propaganda techniques:
    1. Name-calling or labeling
    2. Glittering generalities (virtue words)
    3. Transfer (associating with something respected/reviled)
    4. Testimonial (endorsement from respected/reviled source)
    5. Plain folks appeal (speaker as "one of the people")
    6. Card stacking (selective facts/omissions)
    7. Bandwagon (everyone's doing it)
    8. Fear-mongering
    9. False dilemmas/black-and-white thinking
    10. Loaded language/emotional appeals
    
    Provide a structured analysis with:
    - Propaganda assessment (yes/no/partial)
    - Confidence level (0-100%)
    - Identified techniques, if any
    - Supporting evidence (specific phrases/claims)
    - Overall assessment
    """
    
    # Construct the request payload
    payload = {
        "model": model,
        "prompt": text,
        "system": system_prompt,
        "stream": False,
        "format": "json"  # Request response in JSON format
    }
    
    # Send request to Ollama API
    try:
        response = requests.post(f"{host}/api/generate", json=payload)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Extract the model's analysis from the response
        # Note: The format depends on the model's output structure
        try:
            # Try to parse the response as JSON
            analysis = json.loads(result["response"])
        except json.JSONDecodeError:
            # If not JSON, return the raw text response
            analysis = {
                "raw_analysis": result["response"],
                "note": "Model did not return JSON. Consider parsing the raw analysis manually."
            }
        
        return analysis
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status": "failed"}

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Analyze news for propaganda using Ollama")
    parser.add_argument("--text", type=str, help="News text to analyze")
    parser.add_argument("--file", type=str, help="Path to file containing news text")
    parser.add_argument("--model", type=str, default="llama3", help="Ollama model to use")
    parser.add_argument("--host", type=str, default="http://localhost:11434", help="Ollama API host address")
    
    args = parser.parse_args()
    
    # Get the text to analyze
    if args.text:
        text = args.text
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            return
    else:
        # Interactive mode
        print("Enter the news text to analyze (type 'EOF' on a new line when finished):")
        lines = []
        while True:
            line = input()
            if line == "EOF":
                break
            lines.append(line)
        text = "\n".join(lines)
    
    if not text:
        print("Error: No text provided for analysis")
        return
    
    # Analyze the text
    print(f"Analyzing with {args.model}...")
    result = analyze_propaganda(text, model=args.model, host=args.host)
    
    # Print the results
    print("\n===== PROPAGANDA ANALYSIS RESULTS =====\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
