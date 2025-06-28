import requests
import json

def format_prompt(text):
    """
    Formats the prompt for the LLM to extract a fixed set of key-value pairs from the insurance report text.
    Always returns all required keys, with empty string if missing.
    """
    required_fields = [
        # Original and recent warning fields
        "DATE_INSPECTED", "DATE_RECEIVED", "INSURED_H_CITY", "INSURED_H_STATE", "INSURED_H_ZIP", "MORTGAGEE", "MORTGAGE_CO", "TOL_CODE",
        "DATE_LOSS", "INSURED_NAME", "INSURED_H_STREET", "CARRIER_NAME", "POLICY_NO", "SERVICE_PROVIDER", "SERVICE_PROVIDER_ADDRESS", "SERVICE_PROVIDER_PHONE",
    
        # Add any other fields you want to always extract
    ]
    fields_str = ", ".join(required_fields)
    return (
        "You are an expert insurance claims assistant. "
        "Extract all relevant key-value pairs from the following insurance report text. "
        "Return ONLY a valid JSON object, with no extra text or explanation. "
        "If you cannot find any key-value pairs, return an empty JSON object: {}.\n\n"
        f"Report Text:\n{text}\n\nKey-Value Pairs (JSON):"
    )


def extract_key_value_pairs(text, api_key, model="openai/gpt-3.5-turbo"):
    """
    Sends the extracted text to the LLM and returns structured key-value pairs as a dict.
    Handles API errors and invalid responses. Returns (key_value_pairs, raw_response).
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = format_prompt(text)
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.2
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        response.raise_for_status()
        result = response.json()
        # Extract the LLM's reply
        reply = result["choices"][0]["message"]["content"]
        # Try to parse the reply as JSON
        try:
            key_value_pairs = json.loads(reply)
        except json.JSONDecodeError:
            # Try to extract JSON from the reply if extra text is present
            import re
            match = re.search(r'\{.*\}', reply, re.DOTALL)
            if match:
                try:
                    key_value_pairs = json.loads(match.group(0))
                except Exception as e:
                    print(f"Error parsing extracted JSON: {e}")
                    key_value_pairs = {}
            else:
                print("LLM response is not valid JSON.")
                key_value_pairs = {}
        return key_value_pairs, reply
    except Exception as e:
        print(f"Error communicating with LLM API: {e}")
        return {}, f"API Error: {e}"
