from openai import OpenAI, APIConnectionError, BadRequestError, InternalServerError
import time
import logging

logging.basicConfig(level=logging.INFO)
        
class OpenAI_Client:

    global LOG_NAME
    LOG_NAME = "OpenAI_Client."
    
    
    def __init__(self, key):
        self.client = OpenAI(api_key = key)
        self.logger = logging.getLogger(__name__)
        
    def get_models(self):
        self.logger.info(LOG_NAME+"get_models: ...")
        models = self.client.models.list()
        self.logger.info(LOG_NAME+f"get_models: (models): {models}")
        return [ x.__dict__ for x in models.data ]
        
    def response_awaiting(self, run):
        self.logger.info(LOG_NAME+f"response_awaiting: ... : (run): {run}")
        while True:
            if run.status == 'in_progress':
                self.logger.info(LOG_NAME+f"response_awaiting: (run.status): {run.status}")
            if run.status == 'completed':
                self.logger.info(LOG_NAME+f"response_awaiting: (run.status): {run.status}")
                break
            if run.status == "requires_action":
                self.logger.info(LOG_NAME+f"response_awaiting: (run.status): {run.status}")
                self.logger.info(LOG_NAME+f"response_awaiting: run: {run}")
                raise Exception("requires_action")            
            if run.status == "failed" or run.status == "expired":
                self.logger.info(LOG_NAME+f"response_awaiting: (run.status): {run.status}")
                self.logger.info(LOG_NAME+f"response_awaiting: run: {run}")
                raise Exception("failed")
            time.sleep(0.5)
            run = self.client.beta.threads.runs.retrieve(thread_id = run.thread_id, run_id = run.id)
        
        #message = self.client.beta.threads.messages.list(thread_id=run.thread_id, order = "desc").data[0]#.content[0].text.value
        run_steps = self.client.beta.threads.runs.steps.list(
                thread_id=run.thread_id,
                run_id=run.id,
                )
        messages = []
        for step in run_steps.data:
            if step.step_details.type == 'message_creation':
                message_id = step.step_details.message_creation.message_id
                messages.append(self.client.beta.threads.messages.retrieve(thread_id=run.thread_id, message_id=message_id))
        self.logger.info(LOG_NAME+"response_awaiting: returning openai_response")  
        return messages
     
    def response_not_awaiting(self, run):
        self.logger.info(LOG_NAME+f"response_not_awaiting: ... : (run): {run}")
        
        return []
    
    def start_new_conversation(self, assistant_id, message, instructions = None, files = [], model = None, tools = None):
        self.logger.info(LOG_NAME+f"start_new_conversation: (inputs): \n {assistant_id}, {message}, {instructions}, {files}, {tools}, {model}")
        run = self.client.beta.threads.create_and_run(
                assistant_id=assistant_id,
                thread={
                    "messages": [
                    {"role": "user", "content": message, "file_ids": files}
                    ]
                },
                model = model,
                instructions = instructions,
                tools=tools
        )
        response_message = self.response_awaiting(run)   
        #user_message_id = self.retrive_thread_messages(run.thread_id, limit = 1, order = "asc")['first_id']
        self.logger.info(LOG_NAME+f"start_new_conversation: (openai_response): \n message: {response_message}")
        # chat name
        run_title = self.client.beta.threads.create_and_run(
                            assistant_id='asst_bGRwzril69DJY40KP4efenqc',#os.getenv("NAME_ASSISTANT_ID"),
                            thread={
                                "messages": [
                                {"role": "user", "content": message}
                                ]
                            }
                            )
        title = self.response_awaiting(run_title)
        title = title[0].content[0].text.value
        self.logger.info(LOG_NAME+f"Assing title to the new conversation: \n Title: {title}")
        #deleting title thread
        self.client.beta.threads.delete(thread_id=run_title.thread_id)
        return response_message, run.thread_id, title
    
    def continue_conversation(self, assistant_id, thread_id , message, instructions = None, files = [], tools = None, model = None):
        self.logger.info(LOG_NAME+f"continue_conversation: (inputs): \n {assistant_id}, {thread_id}, {message}, {instructions}, {files}, {tools}, {model}")
        user_message = self.client.beta.threads.messages.create(
                        thread_id = thread_id,
                        role="user",
                        content=message,
                        file_ids=files
                        )
        self.logger.info(LOG_NAME+f"continue_conversation: (user_message): \n {user_message}")
        run = self.client.beta.threads.runs.create(
                model = model,
                thread_id=thread_id,
                assistant_id=assistant_id,
                instructions=instructions,
                tools=tools
                )
        steps = self.client.beta.threads.runs.steps.list(
                thread_id=thread_id,
                run_id=run.id,
                order="desc"
                )

        response_message = self.response_awaiting(run)
        
        self.logger.info(LOG_NAME+f"continue_conversation: (new_steps): \n {steps}")
            
        self.logger.info(LOG_NAME+f"continue_conversation: (openai_response): \n message: {response_message}, \nmessage_id: {user_message.id}")
        return response_message, user_message.id
    
    def retrive_thread_messages(self, thread_id, limit = 50, order = "desc"):
        self.logger.info(LOG_NAME+f"retrive_thread_messages: (inputs): \n {thread_id}, {limit}, {order}")
        messages = self.client.beta.threads.messages.list(thread_id=thread_id, limit = limit, order = order)
        self.logger.info(LOG_NAME+f"retrive_thread_messages: (outputs): \n {messages}")
        return messages
    
    def create_assistant(self, name, instructions, model, files = [], tools = []):
        self.logger.info(LOG_NAME+f"create_assistant: (inputs): \n {name}, {instructions}, {model}, {files}, {tools}")
        assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=model,
                file_ids=files,
                tools=tools
                )
        self.logger.info(LOG_NAME+f"create_assistant: (outputs): \n {assistant}")
        return assistant
        
    def retrive_assistant(self, assistant_id):
        self.logger.info(LOG_NAME+f"retrive_assistant: (inputs): {assistant_id}")
        assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)
        self.logger.info(LOG_NAME+f"retrive_assistant: (outputs): {assistant}")
        return assistant
    
    def delete_assistant(self, assistant_id):
        self.logger.info(LOG_NAME+f"delete_assistant: (inputs): {assistant_id}")
        self.client.beta.assistants.delete(assistant_id=assistant_id)
        self.logger.info(LOG_NAME+f"delete_assistant: (outputs): {assistant_id}")
        return True
    
    def upload_file(self, file):
        self.logger.info(LOG_NAME+f"upload_file: (inputs): {file}")
        file_obj= self.client.files.create(file=file, purpose="assistants")
        self.logger.info(LOG_NAME+f"upload_file: (outputs): {file_obj}")
        return file_obj.id
    
    def delete_file(self, file_id):
        self.logger.info(LOG_NAME+f"delete_file: (inputs): {file_id}")
        self.client.files.delete(file_id=file_id)
        self.logger.info(LOG_NAME+f"delete_file: (outputs): {file_id}")
        return True
    
    def delete_thread(self, thread_id):
        self.logger.info(LOG_NAME+f"delete_thread: (inputs): {thread_id}")
        self.client.beta.threads.delete(thread_id=thread_id)
        self.logger.info(LOG_NAME+f"delete_thread: (outputs): {thread_id}")
        return True
    
    def images_generation(self, prompt, model= "dall-e-3", size="1024x1024", quality="standard", n=1 ):
        if model == "dall-e-3" and n != 1:
            self.logger.error(LOG_NAME+f"image_generation: dall-e-3 model only supports n=1")
            self.logger.warning(LOG_NAME+f"image_generation: generating only one image")
            n = 1
        if model =="dall-e-2" and quality != "standard":
            self.logger.error(LOG_NAME+f"image_generation: dall-e-2 model only supports quality=standard")
            self.logger.warning(LOG_NAME+f"image_generation: setting quality=standard")
            quality = "standard"
        self.logger.info(LOG_NAME+f"image_generation: (inputs): \n {prompt}, {model}, {size}, {quality}, {n}")
        try:
            reponse = self.client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=n
                    )
        except APIConnectionError as e:
            self.logger.error(LOG_NAME+f"image_generation: APIConnectionError: {e}")
            raise InternalServerError("Failed to connect to OpenAI")
        except BadRequestError as e:
            self.logger.error(LOG_NAME+f"image_generation: BadRequestError: {e}")
            raise InternalServerError("Failed to generate images, Bad request")
        except InternalServerError as e:
            self.logger.error(LOG_NAME+f"image_generation: InternalServerError: {e}")
            raise InternalServerError("Failed to generate images")
        except Exception as e:
            self.logger.error(LOG_NAME+f"image_generation: Exception: {e}")
            raise InternalServerError("Failed to generate images")
        images_url = []
        for image in reponse.data:
            images_url.append(image.url)
        return images_url