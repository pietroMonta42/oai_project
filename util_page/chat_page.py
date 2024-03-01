import streamlit as st
import logging
from manage.operations import Operations


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('web_app:Chat')

def create_page(authenticator):
    
    if st.session_state['oai_key']:
        if st.session_state['oai_key'] == True:
            st.session_state['oai_key'] = st.secrets["OPENAI_API_KEY"]
        oai_key = st.session_state['oai_key']
    else:
        if key := st.text_input("OpenAI API Key"):
            st.session_state['oai_key'] = key
            st.rerun()
        st.stop()
    op = Operations(oai_key)

    tool_options = ["code Interpreter", "function", "retrieval"]

    def reload_history():
        
        logger.info(f"reload_history:")
        history = op.get_history_conversation(st.session_state['thread_id'])    
        logger.info(f"history reloaded, generating messages...")
        # Initialize chat history
        st.session_state.messages = []
        # Add message to chat history
        #st.session_state.messages.append({"role": "assistant", "content": "Hello 👋"})
        #load messages from thread
        for message in history:
            st.session_state.messages.append(message)
        if 'reload' in st.session_state:
            st.session_state['reload'] = False

    assistants_dict_meta = op.get_all_assistants()
    logger.info(f"assistants_dict_meta: loaded")
    logger.info(f"assistants_dict_meta: {assistants_dict_meta}")
    assistants_name = [ a['name'] for a in assistants_dict_meta ]
    assistants_id_name = { a['id'] : a['name'] for a in assistants_dict_meta }
    logger.info(f"assistants_id_name: {assistants_id_name}")


    threads_dict_meta = op.get_all_conversations()
    logger.info(f"thread_dict_meta: loaded")
    logger.info(f"thread_dict_meta: {threads_dict_meta}")
    threads_name = [ t['title'] for t in threads_dict_meta ]
    threads_id_name = { t['id'] : t['title'] for t in threads_dict_meta }
    logger.info(f"threads_id_name: {threads_id_name}")


    if False:
        st.title("Create New Conversation")
        with st.form("new_conversation"):
            assistant = st.selectbox("Choose Assistant", title_conv)
            message = st.text_input("Message")
            submit = st.form_submit_button("Start Conversation")
            if submit:
                print("start new conversation")
                #thread_id = op.start_new_conversation(assistant_id=assistant, message=message)
                print(thread_id)
                st.write(thread_id)

    with st.sidebar:
            
        st.write(f'Welcome *{st.session_state["name"]}*')
        authenticator.logout(location = "sidebar", key="chat")
        
        if name:= st.selectbox("Choose Assistant", assistants_name, index=1):
            logger.info(f"name: {name}")
            assistant_id = assistants_dict_meta[assistants_name.index(name)]['id']
            logger.info(f"assistant_id: {assistant_id}")
            st.session_state['assistant_id'] = assistant_id
        if st.button("Create New Assistant"):
            logger.info(f"Create New Assistant")
            st.session_state['new_assistant'] = True
            
        if title:= st.selectbox("Choose Conversation", threads_name):
            thread_id = threads_dict_meta[threads_name.index(title)]['id']
            logger.info(f"thread_id: {thread_id}")
            st.session_state['thread_id'] = thread_id
            st.session_state['reload'] = True
        if st.button("Start New Conversation"):
            logger.info(f"Sart New Conversation")
            st.session_state['new_conversation'] = True
            
        st.checkbox(
            "Mobile", key="center", value=st.session_state.get("center", False)
        )
            
    
    
    #pagine da mostrare
    if 'new_assistant' in st.session_state and st.session_state['new_assistant']:
        with st.form(key='my_form'):
                    name = st.text_input("Nome")
                    instructions = st.text_area("Istruzioni")
                    model_list = op.get_all_models()
                    model_ids = [ m['id'] for m in model_list ]
                    model = st.selectbox("Modello", model_ids)
                    st.write("Tools")
                    codeInterpreter = st.checkbox("Code Interpreter")
                    retrieval = st.checkbox("Retrieval")
                    function = st.checkbox("Function")
                    files = st.file_uploader("Upload File")
                    # Dividi il form in due colonne
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_button = st.form_submit_button(label='Invia')
                    with col2:
                        cancel_button = st.form_submit_button(label='Annulla')
                    # Gestisci l'invio del form
                    if submit_button:
                        logger.info(f"submit_button:data: {name}, {model}, {instructions}")
                        #create tools list
                        tools = []
                        if codeInterpreter:
                            tools.append({"type": "code_interpreter"})
                        if retrieval:
                            tools.append({"type": "retrieval"})
                        if function:
                            tools.append({"type": "function"})
                        id = op.create_assistant(name, model, "description", instructions, "image", tools)
                        if id:
                            st.session_state['new_assistant'] = False
                            st.session_state['assistant_id'] = id
                            st.rerun()
                        logger.info(f"submit_button:assistant_id: {id}")
                    if cancel_button:
                        st.session_state['new_assistant'] = False
                        st.rerun()
    elif 'new_conversation' in st.session_state and st.session_state['new_conversation']:
        st.header("🤖 "+assistants_id_name[st.session_state['assistant_id']])
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Add message to chat history
            #st.session_state.messages.append({"role": "assistant", "content": "Hello 👋"})

                
        # Upload file button
        files = st.file_uploader("Upload File", accept_multiple_files=True)

        # React to user input
        if prompt := st.chat_input("What is up?"):
            # Display user message in chat message container
            
            file_ids = []
            if files:
                with st.spinner("Uploading images..."):
                    for file in files:
                        id=op.upload_file(file)
                        file_ids.append(id)
                    logger.info(f"id: {file_ids}")
                    st.write(f"Files uploaded with id: {file_ids}")
                    
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Print assistant getting response
            
            with st.spinner("Genereting response..."):
                
                if file_ids == []:
                    file_ids = None
                    
                # Get assistant response
                response = op.start_new_conversation(assistant_id=st.session_state['assistant_id'], message=prompt, files=file_ids)
                logger.info(f"response: {response}")
            history = op.get_history_conversation(st.session_state['thread_id'])
            st.session_state['new_conversation'] = False
            st.rerun()
    else:            
        st.header("🤖 "+assistants_id_name[st.session_state['assistant_id']])
        st.title(threads_id_name[st.session_state['thread_id']])


        reload_history()
            
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


        # Upload file button
        files = st.file_uploader("Upload File", accept_multiple_files=True)
                
        # React to user input
        if prompt := st.chat_input("What is up?"):
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            file_ids = []
            if files:
                with st.spinner("Uploading images..."):
                    for file in files:
                        id=op.upload_file(file)
                        file_ids.append(id)
                    logger.info(f"id: {file_ids}")
                    st.write(f"Files uploaded with id: {file_ids}")
                    
                
            # Print assistant getting response
            with st.spinner("Genereting response..."):
                
                if file_ids == []:
                    file_ids = None
                    
                # Get assistant response
                response = op.continue_conversation(assistant_id=st.session_state['assistant_id'], thread_id=st.session_state['thread_id'], message=prompt, files=file_ids)
                logger.info(f"response: {response}")
            history = op.get_history_conversation(st.session_state['thread_id'])
            st.rerun()
                