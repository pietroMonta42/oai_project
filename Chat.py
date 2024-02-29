import streamlit as st
import logging
from util_page.chat_page import create_page
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('web_app:Main')


with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    
if "center" not in st.session_state:
    layout = "wide"
else:
    layout = "centered" if st.session_state.center else "wide"

st.set_page_config(page_title="chatGPT", page_icon="📖", layout=layout)
    
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

if 'register' in st.session_state and st.session_state["register"]:
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(preauthorization=False)
        if email_of_registered_user:
            logger.info(f"User registered: {username_of_registered_user}+ {email_of_registered_user} + {name_of_registered_user}")
            st.success('User registered successfully')
            with open('./config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
                logger.info(f"config: {config}")
            st.session_state["register"] = False
            st.session_state["registering_success"] = True
            st.rerun()
    except Exception as e:
        st.error(e)
    if st.button('Annulla'):
        st.session_state["register"] = False
        st.rerun()
else:
    if 'registering_success' in st.session_state and st.session_state["registering_success"]:
        st.success('User registered successfully')
        st.session_state["registering_success"] = False
    authenticator.login(max_concurrent_users= 3)
    if st.button('Register new User'):
        logger.info(f"User registering:")
        st.session_state["register"] = True
        st.rerun()
if st.session_state["authentication_status"]:
    if not config['credentials']['usernames'].get(st.session_state["username"]) :
        st.error('Username/password is incorrect')
        st.stop()
    st.session_state["oai_key"] = config['credentials']['usernames'][st.session_state["username"]]['oai_key']
    create_page(authenticator)
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
    st.stop()
    
