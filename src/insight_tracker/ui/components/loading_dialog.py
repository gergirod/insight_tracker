import streamlit as st

def show_loading_dialog(title: str, description: str, loading_message: str = "Just a moment..."):
    """
    Display a loading dialog with customizable content.
    
    Args:
        title (str): The main title of the loading dialog
        description (str): The detailed description/message
        loading_message (str, optional): The message shown below the spinner. Defaults to "Just a moment..."
    
    Returns:
        st.empty: The container element that can be used to clear the dialog
    """
    loading_container = st.empty()
    loading_container.markdown(f"""
        <div style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            z-index: 9999;
            backdrop-filter: blur(8px);
        ">
            <div style="margin-bottom: 1.5rem;">
                <div class="spinner" style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #1E88E5;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 1rem auto;
                "></div>
            </div>
            <h3 style="color: #2C3E50; margin-bottom: 1rem; font-size: 1.2rem;">
                {title}
            </h3>
            <p style="color: #666; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1rem;">
                {description}
            </p>
            <div style="color: #1E88E5; font-size: 0.9rem;">
                {loading_message}
            </div>
        </div>
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .stApp {{
                position: relative;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    return loading_container 