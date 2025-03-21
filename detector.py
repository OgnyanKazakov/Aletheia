import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

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
        try:
            # Try to parse the response as JSON
            analysis = json.loads(result["response"])
        except json.JSONDecodeError:
            # If not JSON, return the raw text response
            analysis = {
                "raw_analysis": result["response"],
                "note": "Model did not return JSON. Consider parsing the raw analysis manually."
            }
        
        return analysis, 200
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status": "failed"}, 500

@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    """
    API endpoint to analyze news content for propaganda
    
    Expected JSON payload:
    {
        "text": "News content to analyze",
        "model": "llama3",  # optional
        "ollama_host": "http://localhost:11434"  # optional
    }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Check if text is provided
    if 'text' not in data or not data['text']:
        return jsonify({"error": "No text provided for analysis"}), 400
    
    # Get optional parameters with defaults
    model = data.get('model', 'llama3')
    host = data.get('ollama_host', 'http://localhost:11434')
    
    # Analyze the text
    result, status_code = analyze_propaganda(data['text'], model=model, host=host)
    
    return jsonify(result), status_code

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the propaganda analysis API server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind the server to")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    print(f"Starting propaganda analysis API server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
