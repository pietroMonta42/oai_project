from manage.clientOpenAIUtil import OpenAI_Client
import manage.localDb as localDb
import manage.litedb as litedb

class Operations:
    
    def __init__(self, key ):
        self.client = OpenAI_Client(key)
        self.db = litedb.LocalDB()
        
    def get_all_models(self):
        return self.client.get_models()
    
    def get_all_conversations(self):
        db = self.db
        return db.get_threads()
        
    def get_all_assistants(self):
        db = self.db
        return db.get_assistants()
    
    def create_assistant(self, name, model,description, instructions, image, tools = []):
        assistant = self.client.create_assistant(name=name, instructions= instructions, model = model, tools=tools)
        db = self.db
        db.new_assistant(assistant.id, name, model, image)
        return assistant
    
    def start_new_conversation(self, assistant_id, message, files = [], tools = None):
        response_message, thread_id, title = self.client.start_new_conversation(assistant_id=assistant_id, instructions=None, message=message, files=files, tools=tools)
        db = self.db
        print(thread_id, assistant_id, title)
        db.new_thread(thread_id, assistant_id, title)
        return response_message
    
    def continue_conversation(self, assistant_id, thread_id, message, files = [], tools = None):
        response_message, message_id = self.client.continue_conversation(assistant_id, thread_id, message, files=files, tools=tools)
        db = self.db
        db.put_thread(thread_id, assistant_id)
        return response_message
    
    def create_image(self, input):
        link_images = self.client.images_generation(prompt=input)
        return link_images
    
    def get_history_conversation(self, thread_id):
        messages = self.client.retrive_thread_messages(thread_id, order="asc")
        stamp_messages = []
        for message in messages:
            if message.role == "user":
                stamp_messages.append({"role": "user", "content": message.content[0].text.value})
            else:
                stamp_messages.append({"role": "assistant", "content": message.content[0].text.value})
        return stamp_messages
    
    def get_meta_conversation(self, thread_id):
        db = self.db
        return db.get_thread(thread_id)
    
    def upload_file(self, file):
        return self.client.upload_file(file)
    
#op = Operations()

#op.create_assistant("test", "gpt-4", "assistant di prova", "sei un assistente utile", "image")
#image = op.create_image("an avatar for my profile of discord that rappresent a futuristic boy with long mossy hair")
#print (image)
#message = op.start_new_conversation(assistant_id="asst_nRvVoYvzAuMUgPsIoizX88ur", message="Hello, you know python?")
#print(message)
#print(op.get_history_conversation("thread_3wjgjMAwX4G5czImKsSK5u2V"))