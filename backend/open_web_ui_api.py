from fastapi import HTTPException
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

open_web_ui_api_key = os.getenv('OPEN_WEB_UI_API_KEY')
open_web_ui_api_url = os.getenv('OPEN_WEB_UI_API_URL')

#######################
#       models        #
#######################

def get_available_models():
    url = f'{open_web_ui_api_url}/api/v1/models'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

#######################
#        chat         #
#######################
    
def chat_with_model(messages, files = None, model = 'gemini-3.1-flash-lite'):
    url = f'{open_web_ui_api_url}/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
      "model": model,
      "messages": messages
    }
    
    if files != None:
        data['files'] = files
        
    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the AI service."
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="The AI service is currently unavailable."
        )

    try:
        response_data = response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an invalid response."
        )

    if "choices" not in response_data or len(response_data["choices"]) == 0:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )

    message = response_data["choices"][0].get("message")

    if message is None or "content" not in message:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )

    return response_data["choices"][0]["message"]["content"]

#######################
#      documents      #
#######################

def upload_file(file):
    url = f'{open_web_ui_api_url}/api/v1/files/'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Accept': 'application/json'
    }
    files = {
        "file": (
            file.filename,
            file.file,
            file.content_type
        )
    }
    response = requests.post(url, headers=headers, files=files)
    return response.json()

def wait_for_file_processing(file_id, timeout=300, poll_interval=2):
    url = f'{open_web_ui_api_url}/api/v1/files/{file_id}/process/status'
    headers = {'Authorization': f'Bearer {open_web_ui_api_key}'}
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(url, headers=headers)
        result = response.json()
        status = result.get('status')
        
        if status == 'completed':
            return result
        elif status == 'failed':
            raise Exception(f"File processing failed: {result.get('error')}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"File processing did not complete within {timeout} seconds")

def get_files():
    url = f'{open_web_ui_api_url}/api/v1/files/'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_file_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/files/{id}'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_file_content_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/files/{id}'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def delete_file_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/files/{id}'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response = requests.delete(url, headers=headers)
    return response.json()

#######################
#      knowledge      #
#######################

def create_knowledge(name, description):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/create'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    data = {
        "name": name,
        "description": description,
        "access_grants": [
            {
            "additionalProp1": {}
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def update_knowledge_by_id(id, name, description):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{id}/update'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    data = {
        "name": name,
        "description": description,
        "access_grants": [
            {
            "additionalProp1": {}
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def get_knowledge_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{id}'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_knowledge_files_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{id}/files'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def add_file_to_knowledge(knowledge_id, file_id):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{knowledge_id}/file/add'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def remove_file_from_knowledge(knowledge_id, file_id):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{knowledge_id}/file/remove'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json'
    }
    data = {{
        "file_id": file_id,
        "directory_id": "string" # what is this?
    }}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def delete_knowledge_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{id}/delete'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response = requests.delete(url, headers=headers)
    return response.json()

#######################
#       health        #
#######################

def healthy():
    url = f'{open_web_ui_api_url}/health'
    response = requests.get(url)
    return response.json()

def ready():
    url = f'{open_web_ui_api_url}/ready'
    response = requests.get(url)
    return response.json()
def db_healthy():
    url = f'{open_web_ui_api_url}/health/db'
    response = requests.get(url)
    return response.json()

