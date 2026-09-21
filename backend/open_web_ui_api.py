from fastapi import HTTPException
import requests
import os
from dotenv import load_dotenv
import time
import asyncio

load_dotenv()

open_web_ui_api_url = os.getenv('OPEN_WEB_UI_API_URL')
try:
    with open('/shared/openwebui_api_key', 'r') as file:
        open_web_ui_api_key = file.read().strip()
except FileNotFoundError:
    open_web_ui_api_key = os.getenv('OPEN_WEB_UI_API_KEY')

#######################
#   helper functions  #
#######################

def make_open_web_ui_request(method, url, headers=None, timeout=60, **kwargs):
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            timeout=timeout,
            **kwargs
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the AI service."
        )

    if response.status_code != 200:
        print("OPEN WEB UI STATUS:", response.status_code)
        print("OPEN WEB UI RESPONSE:", response.text)
        raise HTTPException(
            status_code=502,
            detail="The AI service is currently unavailable."
        )

    try:
        response_data = response.json()
    except ValueError:
        print("STATUS:", response.status_code)
        print("CONTENT TYPE:", response.headers.get("content-type"))
        print("RESPONSE:", response.text)
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an invalid response."
        )

    return response_data

#######################
#       models        #
#######################

def get_available_models():
    url = f'{open_web_ui_api_url}/api/v1/models'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json'
    }
    
    response_data = make_open_web_ui_request(
        "GET",
        url,
        headers,
        timeout=30
    )
        
    if "data" not in response_data:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )

    return response_data["data"]

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
        
    response_data = make_open_web_ui_request(
        "POST",
        url,
        headers,
        json=data,
        timeout=30
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
    
    response_data = make_open_web_ui_request(
        "POST",
        url,
        headers,
        files=files,
        timeout=60
    )
    
    if "id" not in response_data:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )
        
    return response_data['id']

async def wait_for_file_processing(file_id, timeout=300, poll_interval=2):
    url = f'{open_web_ui_api_url}/api/v1/files/{file_id}/process/status'
    headers = {'Authorization': f'Bearer {open_web_ui_api_key}'}
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        response_data = make_open_web_ui_request(
            "GET",
            url,
            headers
        )
        status = response_data.get('status')
        
        if status == 'completed':
            return response_data['status']
        elif status == 'failed':
            print("FILE PROCESSING ERROR:", response_data.get("error"))
            raise HTTPException(
                status_code=502,
                detail="The AI service failed to process the document."
            )
        
        await asyncio.sleep(poll_interval)
    
    raise HTTPException(
        status_code=504,
        detail="The AI service took too long to process the document."
    )

def get_file_content_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/files/{id}/content'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': '*/*'
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
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
        
    return response

def delete_file_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/files/{id}'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response_data = make_open_web_ui_request(
        "DELETE",
        url,
        headers,
        timeout=30
    )
    
    if "message" not in response_data:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )
        
    return response_data

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
    response_data = make_open_web_ui_request(
        "POST",
        url,
        headers,
        json=data,
        timeout=60
    )
    
    if "id" not in response_data:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )
        
    return response_data['id']

def update_knowledge_by_id(id, name, description):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{id}/update'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    data = {
        "name": name,
        "description": description
    }
    response_data = make_open_web_ui_request(
        "POST",
        url,
        headers,
        json=data,
        timeout=30
    )
    
    if "id" not in response_data:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )
        
    return response_data

def add_file_to_knowledge(knowledge_id, file_id):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{knowledge_id}/file/add'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response_data = make_open_web_ui_request(
        "POST",
        url,
        headers,
        json=data,
        timeout=60
    )
    
    if "id" not in response_data:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )
        
    return response_data

def remove_file_from_knowledge(knowledge_id, file_id):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{knowledge_id}/file/remove'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "file_id": file_id
    }
    response_data = make_open_web_ui_request(
        "POST",
        url,
        headers,
        json=data,
        timeout=60
    )
    
    if "id" not in response_data:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response."
        )
        
    return response_data

def delete_knowledge_by_id(id):
    url = f'{open_web_ui_api_url}/api/v1/knowledge/{id}/delete'
    headers = {
        'Authorization': f'Bearer {open_web_ui_api_key}',
        'accept': 'application/json'
    }
    response_data = make_open_web_ui_request(
        "DELETE",
        url,
        headers,
        timeout=30
    )
        
    return response_data

#######################
#       health        #
#######################

def healthy():
    url = f'{open_web_ui_api_url}/health'
    response_data = make_open_web_ui_request(
        "GET",
        url,
        timeout=30
    )
        
    return response_data

def ready():
    url = f'{open_web_ui_api_url}/ready'
    response_data = make_open_web_ui_request(
        "GET",
        url,
        timeout=30
    )
        
    return response_data

def db_healthy():
    url = f'{open_web_ui_api_url}/health/db'
    response_data = make_open_web_ui_request(
        "GET",
        url,
        timeout=30
    )
        
    return response_data

