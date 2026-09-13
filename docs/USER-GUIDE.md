# User Guide — Internal AI Chat Platform

## 1. Purpose

The Internal AI Chat Platform provides employees with a web-based interface for interacting with an AI assistant.

The platform uses Open WebUI as the chat interface and Ollama to run the configured AI model.

## 2. Accessing the Platform

Open the Open WebUI address provided by the system administrator.

The address is environment-specific.

Example:

```text
http://<AZURE_PUBLIC_IP>:3000
```

Replace `<AZURE_PUBLIC_IP>` with the public IP address assigned to the Azure virtual machine.

## 3. Creating an Account

1. Open the Open WebUI address.
2. Create an account if registration is enabled.
3. Sign in.
4. Select the available AI model.
5. Start a conversation.

## 4. Selecting the AI Model

The current configured model is:

```text
llama3.2:3b
```

Select this model from the model selection menu before starting a conversation.

## 5. Using the AI Assistant

The assistant can be used for tasks such as:

* Summarizing information
* Drafting emails
* Explaining technical concepts
* Generating ideas
* Creating outlines
* Reviewing text
* Rewriting content
* Answering general questions

## 6. Writing Effective Prompts

For better results, provide clear instructions and relevant context.

A good prompt should include:

1. The task
2. Relevant information
3. Desired output format
4. Any important restrictions

Example:

```text
Summarize the following information into five bullet points and identify the three most important actions.
```

## 7. Reviewing AI Responses

AI-generated responses should be reviewed before being used for important business decisions.

The AI may produce incorrect, incomplete, or outdated information.

Users are responsible for verifying important information.

## 8. Security Guidelines

Users must not:

* Share passwords with the AI assistant
* Share SSH private keys
* Share authentication tokens
* Share confidential credentials
* Attempt to access another user's account
* Attempt to bypass security controls

Users should follow their organization's information-security policies when entering information into the platform.

## 9. Ending a Session

Users should sign out when finished, particularly when using a shared or public computer.