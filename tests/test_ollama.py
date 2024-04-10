import pytest
import ollama

def test_ollama_list():
    try:
        models_list = ollama.list()
        print(models_list)
        assert len(models_list['models']) > 0, "The models list is empty, Ollama might not be active."
        assert len(models_list['models']) ==3 , "The models list is not complete."
    except Exception as e:
        pytest.fail(f"An error occurred while fetching models: {str(e)}")
        
        
def test_ollama_chat_streaming():
    messages = [{'role': 'user', 'content': 'Why is the sky blue?'}]
    try:
        stream = ollama.chat(model='llama2:13b', messages=messages, stream=True)
        assert hasattr(stream, '__iter__'), "The response should be an iterable (generator)."
        first_response = next(stream, None)
        assert first_response is not None, "The streaming response did not yield any output."
        assert 'message' in first_response and 'content' in first_response['message'], "The response format is incorrect."

    except StopIteration:
        pytest.fail("The streaming response generator did not yield any data.")
    except Exception as e:
        pytest.fail(f"An error occurred during the streaming chat: {str(e)}")
