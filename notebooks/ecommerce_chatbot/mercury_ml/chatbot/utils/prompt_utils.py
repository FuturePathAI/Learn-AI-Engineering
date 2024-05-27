import copy
import json
import yaml
import logging
from mercury_ml.chatbot import config

# initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format='%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s',
)

def insert_non_system_message(message_list, message):
    system_message_indices = [index for index, msg in enumerate(message_list) if msg['role'] == 'system']
    
    if len(system_message_indices) == 2:
        # Two system messages present, insert the new message right before the last system message
        insert_index = system_message_indices[1]
    elif system_message_indices:
        # One system message present, insert the new message right after the first system message
        insert_index = system_message_indices[0] + 1
    else:
        # No system messages present, append the new message at the end
        insert_index = len(message_list)
    
    message_list.insert(insert_index, message)
    return message_list

def extract_last_json(text: str) -> dict:
    start_positions = []
    stack = []
    
    for idx, char in enumerate(text):
        if char == '{':
            stack.append('{')
            start_positions.append(idx)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack:
                    last_start = start_positions.pop(0)
                    last_end = idx
                    try:
                        last_json = json.loads(text[last_start:last_end+1])
                        return last_json
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON format"}
    
    return {"error": "No complete JSON object found in text"}

def prune_messages(messages, N):
    if not messages:
        return []

    pruned_messages = []
    remaining_space = N  # Space available in the pruned_messages list
    
    count_user = 0
    count_assistant = 0
    count_system = 0
    
    # Count the types of messages
    for message in messages:
        if message['role'] == 'system':
            count_system += 1
        elif message['role'] == 'user':
            count_user += 1
        elif message['role'] == 'assistant':
            count_assistant += 1

    # Deduct system messages from remaining space
    remaining_space -= count_system
    
    last_role = None  # Keep track of the last role that was added to pruned_messages
    
    # Traverse the messages list from the end towards the start
    for message in reversed(messages):
        if message['role'] == 'system':
            # Always keep system messages
            pruned_messages.insert(0, message)
        elif message['role'] == 'user' and remaining_space > 0 and (last_role is None or last_role != 'user'):
            # Keep user messages if there's space available and the last message was not from the user
            pruned_messages.insert(0, message)
            remaining_space -= 1
            last_role = 'user'
        elif message['role'] == 'assistant' and remaining_space > 0 and (last_role is None or last_role != 'assistant'):
            # Keep assistant messages if there's space available and the last message was not from the assistant
            pruned_messages.insert(0, message)
            remaining_space -= 1
            last_role = 'assistant'

    return pruned_messages

def update_service_router_last_system_prompt(messages, accumulated_info):
    """Update the last system prompt based on the current state of the accumulated information."""
    # Convert the accumulated information to a formatted string    
    accumulated_info_str = json.dumps(accumulated_info, indent=4)
    # Create the updated prompt
    updated_prompt = (
        f"The current accumulated information in json format is:\n"
        f"{accumulated_info_str}"
        f"Updated accumulated information in json format is:\n"
    )
    
    # Count the number of system messages
    system_count = sum(1 for message in messages if message['role'] == 'system')
    if system_count <=1:
        # simply append the new prompt
        new_system_message = {
            "role": "system",
            "content": updated_prompt
        }
        messages.append(new_system_message)        
    else:
        # If there are more than 1 system messages, update the last one
        found_and_updated = False
        for idx in reversed(range(len(messages))):
            if messages[idx]['role'] == 'system':
                messages[idx]['content'] = updated_prompt
                found_and_updated = True
                break  # break after updating
        
        if not found_and_updated:
            logging.warning(f"Could not update the system message!")
            
    return messages

def remove_router_last_system_prompt(messages):
    """Remove the last system prompt from the messages list."""
    if messages and len(messages) >= 2:
        # Find the index of the last system prompt
        last_system_index = None
        for i, message in reversed(list(enumerate(messages))):
            if message['role'] == 'system':
                last_system_index = i
                break
        # Remove the last system prompt if it's not the only one
        if last_system_index is not None and last_system_index != 0:
            messages.pop(last_system_index)
    return messages

def update_router_first_system_prompt(messages, new_router_prompt):
    """Update the router prompt in the messages list with a new router prompt."""
    updated_messages = copy.deepcopy(messages)
    
    # Check if the first message is a system message
    if updated_messages and updated_messages[0]['role'] == 'system':
        # Overwrite the content of the first system message with the new router prompt
        updated_messages[0]['content'] = new_router_prompt
    else:
        # If no system message is found at position 0, insert a new one
        new_system_message = {
            "role": "system",
            "content": new_router_prompt
        }
        updated_messages.insert(0, new_system_message)
    
    return updated_messages

def update_router_with_full_messages_except_last_user(messages, new_router_prompt):
    """Update the router prompt by appending all messages (with roles) except the last user message."""
    updated_messages = copy.deepcopy(messages)
    last_user_index = None

    # Find the index of the last message with the role 'user'
    for i in range(len(updated_messages) - 1, -1, -1):
        if updated_messages[i]['role'] == 'user':
            last_user_index = i
            break

    # Append all messages (with role) except the last user message to the new router prompt
    for i, message in enumerate(updated_messages):
        if message['role'] in ['user', 'assistant'] and i != last_user_index:
            new_router_prompt += "\n{}: {}".format(message['role'].title(), message['content'])

    # If a last user message exists, keep it and prepend the system prompt
    if last_user_index is not None:
        updated_messages = [updated_messages[last_user_index]]
        new_system_message = {
            "role": "system",
            "content": new_router_prompt
        }
        updated_messages.insert(0, new_system_message)

    return updated_messages

def update_router_with_full_messages_except_last_assistant(messages, new_router_prompt):
    """Update the router prompt by appending all messages (with roles) except the last assistant message."""
    updated_messages = copy.deepcopy(messages)
    last_assistant_index = None

    # Find the index of the last message with the role 'assistant'
    for i in range(len(updated_messages) - 1, -1, -1):
        if updated_messages[i]['role'] == 'assistant':
            last_assistant_index = i
            break

    # Append all messages (with role) except the last assistant message to the new router prompt
    for i, message in enumerate(updated_messages):
        if message['role'] in ['user', 'assistant'] and i != last_assistant_index:
            new_router_prompt += "\n{}: {}".format(message['role'].title(), message['content'])

    # If a last assistant message exists, keep it and prepend the system prompt
    if last_assistant_index is not None:
        updated_messages = [updated_messages[last_assistant_index]]
        new_system_message = {
            "role": "system",
            "content": new_router_prompt
        }
        updated_messages.insert(0, new_system_message)

    return updated_messages
    
def get_service_router_base_prompt(service_name: str) -> str:
    """Generate a router base prompt string based on the service name.
    """
    with open(cfg.prompts.PATH_SERVICE_PROMPT, 'r') as f:
        config = yaml.safe_load(f)
        OrderServiceRouterBasePrompt = config['OrderServiceRouterBasePrompt']
        ProductServiceRouterBasePrompt = config['ProductServiceRouterBasePrompt']
        ShippingServiceRouterBasePrompt = config['ShippingServiceRouterBasePrompt']
        ReturnRefundServiceRouterBasePrompt = config['ReturnRefundServiceRouterBasePrompt']
        PricingDiscountServiceRouterBasePrompt = config['PricingDiscountServiceRouterBasePrompt']
    
    if service_name == "order_functions":
        return OrderServiceRouterBasePrompt
    elif service_name == "product_functions":
        return ProductServiceRouterBasePrompt
    elif service_name == "shipping_functions":
        return ShippingServiceRouterBasePrompt
    elif service_name == "return_refund_functions":
        return ReturnRefundServiceRouterBasePrompt
    elif service_name == "pricing_discount_functions":
        return PricingDiscountServiceRouterBasePrompt
    else:
        return "Service not recognized. Please provide a valid service name."
        
# def update_accumulated_info(accumulated_info, key, value):
#     """Update the accumulated information based on the provided key and value."""
#     # Update the relevant field in the accumulated_info dictionary
#     if key in accumulated_info['arguments']:
#         accumulated_info['arguments'][key] = value
#     elif key == 'function_name':
#         accumulated_info['function_name'] = value
#     else:
#         raise ValueError(f"Invalid key: {key}")
#     return accumulated_info

def update_accumulated_info(accumulated_info, key, value):
    """Update the accumulated information based on the provided key and value."""
    # Check if the key is within the 'arguments' sub-dictionary
    if key in accumulated_info['arguments']:
        # Update only the specific key within 'arguments'
        accumulated_info['arguments'][key] = value
    elif key == 'function_name':
        # Update the 'function_name' field if the key matches
        accumulated_info['function_name'] = value
    else:
        # Raise an error if the key is invalid
        raise ValueError(f"Invalid key: {key}")
    return accumulated_info

def update_accumulated_info_from_response(accumulated_info, response_content, all_service_functions):
    """
    Update the accumulated information based on the response content from the AI assistant.
    """
    try:
        # Check if response_content is already a dictionary
        if isinstance(response_content, dict):
            response_dict = response_content
        else:
            # Parse the response content to a dictionary
            response_dict = json.loads(response_content)

        # Save a copy of the old accumulated_info for comparison
        old_accumulated_info = copy.deepcopy(accumulated_info)
        
        # Update the function_name
        if 'function_name' in response_dict:
            new_function_name = response_dict['function_name']
            # if new_function_name in all_service_functions:
            accumulated_info['function_name'] = new_function_name
            # else:
            #     logging.warning(f"Function {new_function_name} not in all_service_functions. Reverting to old function name.")
        
        # Update the arguments
        if 'arguments' in response_dict:
            for key, value in response_dict['arguments'].items():
                if key in accumulated_info['arguments']:
                    accumulated_info['arguments'][key] = value
        
        # Check if there was any update
        is_updated = old_accumulated_info != accumulated_info

        return accumulated_info, is_updated
    
    except json.JSONDecodeError:
        logging.error("Error: Unable to decode the response content.")
        return accumulated_info, False
    
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return accumulated_info, False

def update_serviceselector_router_last_system_prompt(messages, service_info):
    # Convert the information to a formatted string
    service_info_str = json.dumps(service_info, indent=4)
    
    # Create the updated prompt
    updated_prompt = (
        f"The current information in json format is:\n"
        f"{service_info_str}"
        f"Updated information in json format is:\n"
    )
    
    # Count the number of system messages in the list
    system_message_count = sum(1 for message in messages if message['role'] == 'system')
    
    # If there are at least 2 system messages, update the last system message
    if system_message_count >= 2:
        # Find the index of the last system message
        last_system_message_index = next(
            (index for index, message in reversed(list(enumerate(messages))) if message['role'] == 'system'), 
            None
        )
        if last_system_message_index is not None:
            messages[last_system_message_index]['content'] = updated_prompt
            
            # Remove the last system message from its current position
            last_system_message = messages.pop(last_system_message_index)
            # Append the updated system message to the end of the messages list
            messages.append(last_system_message)            
    else:
        # Create a new system message with the updated prompt
        new_system_message = {
            "role": "system",
            "content": updated_prompt
        }
        # Append the new system message to the end of the messages list
        messages.append(new_system_message)
    
    return messages
