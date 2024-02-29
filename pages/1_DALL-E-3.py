import streamlit as st
from manage.operations import Operations
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('web_app:DALL-E-3')

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False

if not st.session_state["authentication_status"]:
    st.error('Please login to use this feature')
    st.stop()
    
if "last_image" in st.session_state:
    st.write("Last image generated: " + st.session_state["last_image"])
    

if st.session_state['oai_key']:
    op = Operations(st.secrets["OPENAI_API_KEY"])
else:
    if key := st.text_input("OpenAI API Key"):
        st.session_state['oai_key'] = key
    st.stop()

with st.sidebar:
    st.markdown("# Settings")
    st.checkbox(
        "Mobile", key="center", value=st.session_state.get("center", False)
    )
    
st.title("DALL-E 3")
st.caption("Generative Image Model")

if "generating" not in st.session_state:
    st.session_state["generating"] = False

if (prompt := st.text_input("Prompt for image generation", disabled=st.session_state['generating'])) and not st.session_state['generating']:
    logger.info(f"prompt: {prompt}")
    st.session_state["generating"] = True
    with st.spinner("Generating image..."):
        image=op.create_image(prompt)
        st.image(image[0], use_column_width=True)
        logger.info(f"image: {image[0]}")
        st.write("Image generated at:" + image[0])
        st.session_state["last_image"] = image[0]
        image_name = image[0][117:149]
        logger.info(f"image_name: {image_name}")
        if False:
            save_path = os.path.join("images", image_name)
            with open(save_path, 'wb') as image_file:
                image_file.write(requests.get(image[0]).content)
                logger.info(f"image_file saved at: {save_path}")
        else:
            if st.download_button("Save Image", requests.get(image[0]).content, f"{image_name}.jpg", "Save image to your computer"):
                logger.info(f"image_file saved at: {image_name}")
    st.session_state["generating"] = False
            
        
    if st.button("Generate another image"):
        st.session_state["generating"] = False
        st.rerun()