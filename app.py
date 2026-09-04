import streamlit as st
import streamlit.components.v1 as components
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ==========================================
# 1. PAGE CONFIGURATION & UI THEME
# ==========================================
st.set_page_config(
    page_title="NEURAL_CODE_NEXUS //",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sci-Fi CSS Styling
SCIFI_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Share Tech Mono', monospace;
        background-color: #0a0a0f !important;
        color: #00ffcc !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #ff00ff !important;
        text-transform: uppercase;
        text-shadow: 0 0 5px #ff00ff;
    }
    
    /* Buttons */
    .stButton>button {
        background: transparent !important;
        color: #00ffcc !important;
        border: 1px solid #00ffcc !important;
        box-shadow: 0 0 10px rgba(0, 255, 204, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #00ffcc !important;
        color: #0a0a0f !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.6);
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 1px dashed #ff00ff;
        background: rgba(255, 0, 255, 0.05);
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Chat bubbles */
    .stChatMessage {
        background-color: rgba(0, 255, 204, 0.05) !important;
        border-left: 2px solid #00ffcc;
        border-radius: 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Orbitron', sans-serif;
        color: #00ffcc !important;
    }
</style>
"""
st.markdown(SCIFI_CSS, unsafe_allow_html=True)

# ==========================================
# 2. CONSTANTS & HELPER FUNCTIONS
# ==========================================
MAX_FILE_SIZE_MB = 5
SUPPORTED_EXTENSIONS = ['.py', '.js', '.java', '.cpp', '.c', '.ts', '.go', '.rs']

def render_mermaid(code: str):
    """Renders a Mermaid.js diagram using HTML/JS injection."""
    html_code = f"""
    <div class="mermaid" style="background-color: #f0f0f0; padding: 20px; border-radius: 10px;">
        {code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    </script>
    """
    components.html(html_code, height=600, scrolling=True)

@st.cache_data(ttl=3600, show_spinner=False)
def analyze_code_cached(_llm, code_content: str, language: str):
    """Caches the heavy analysis to prevent redundant API calls."""
    desc_prompt = PromptTemplate.from_template("""Analyze the following {language} code. Provide structural descriptions at three difficulty levels.
        FORMAT EXACTLY LIKE THIS:
        ### [BEGINNER]
        (Simple explanation for non-technical users)
        ### [INTERMEDIATE]
        (Explanation for developers, focusing on logic and functions)
        ### [EXPERT]
        (Deep dive into time complexity, memory management, and architectural patterns)
        
        CODE:
        {code}""")
    
    mermaid_prompt = PromptTemplate.from_template("""Create a Mermaid.js flowchart mapping out the logic and dependencies of this {language} code.
        Respond ONLY with the valid Mermaid code blocks (start with 'graph TD'). Do not include markdown code ticks (`).
        
        CODE:
        {code}""")
    
    # Modern LCEL (LangChain Expression Language) chaining
    desc_chain = desc_prompt | _llm | StrOutputParser()
    mermaid_chain = mermaid_prompt | _llm | StrOutputParser()
    
    descriptions = desc_chain.invoke({"code": code_content, "language": language})
    mermaid_code = mermaid_chain.invoke({"code": code_content, "language": language})
    
    return descriptions, mermaid_code

# ==========================================
# 3. MAIN APPLICATION LOGIC
# ==========================================
def main():
    st.title("NEURAL_CODE_NEXUS //")
    st.markdown("`[SYSTEM ACTIVE] AI-POWERED CODE TOPOGRAPHY AND ANALYSIS ENGINE`")

    # Sidebar: Config & Keys
    with st.sidebar:
        st.header("TERMINAL_CONFIG")
        api_key = st.text_input("ENTER OPENAI API KEY:", type="password")
        if not api_key:
            st.warning("SYSTEM REQUIRES API KEY TO INITIALIZE.")
            st.stop()
            
        st.markdown("---")
        st.markdown(f"**Max Upload Size:** {MAX_FILE_SIZE_MB}MB")
        st.markdown(f"**Supported:** {', '.join(SUPPORTED_EXTENSIONS)}")

    # Initialize LLM
    try:
        llm = ChatOpenAI(temperature=0.2, openai_api_key=api_key, model_name="gpt-3.5-turbo")
    except Exception as e:
        st.error(f"INITIALIZATION_ERROR: {str(e)}")
        st.stop()

    # Session State for Chat Memory
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # File Upload
    uploaded_file = st.file_uploader("DRAG & DROP SOURCE CODE", type=[x.strip('.') for x in SUPPORTED_EXTENSIONS])
    
    if uploaded_file:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        file_size = uploaded_file.size / (1024 * 1024) # Convert to MB
        
        # Validation
        if file_ext not in SUPPORTED_EXTENSIONS:
            st.error("UNSUPPORTED_FILE_TYPE_DETECTED.")
            st.stop()
        if file_size > MAX_FILE_SIZE_MB:
            st.error(f"FILE_SIZE_EXCEEDS_LIMIT ({file_size:.2f}MB > {MAX_FILE_SIZE_MB}MB).")
            st.stop()
            
        code_content = uploaded_file.getvalue().decode("utf-8")
        
        # UI Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["DATA_STREAM (Code)", "ANALYSIS_CORE", "HOLOGRAM_MAP (Diagram)", "COMMLINK (Q&A)"])
        
        with tab1:
            st.subheader(f"FILE: {uploaded_file.name}")
            st.code(code_content, language=file_ext.strip('.'))
            
        # Run Analysis
        with st.spinner("PROCESSING NEURAL PATHWAYS... (Max 30s)"):
            try:
                descriptions, mermaid_code = analyze_code_cached(llm, code_content, file_ext)
            except Exception as e:
                st.error(f"PROCESSING_FAILED: {str(e)}")
                st.stop()

        with tab2:
            st.subheader("STRUCTURAL DECRYPTION")
            st.markdown(descriptions)
            
            # Downloadable Report
            report = f"File: {uploaded_file.name}\n\n{descriptions}\n\nMermaid Diagram Code:\n{mermaid_code}"
            st.download_button(
                label="DOWNLOAD_REPORT.TXT",
                data=report,
                file_name=f"analysis_{uploaded_file.name}.txt",
                mime="text/plain"
            )

        with tab3:
            st.subheader("SYSTEM ARCHITECTURE GRAPH")
            render_mermaid(mermaid_code)
            with st.expander("VIEW RAW MERMAID CODE"):
                st.code(mermaid_code, language="markdown")

        with tab4:
            st.subheader("INTERACTIVE CODE QUERY")
            
            # Render chat history
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            # Chat Input
            if prompt := st.chat_input("QUERY SYSTEM ABOUT CODE..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                with st.chat_message("assistant"):
                    with st.spinner("CALCULATING RESPONSE..."):
                        
                        # Format chat history directly from session state natively
                        chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[:-1]])
                        
                        chat_prompt = PromptTemplate.from_template("""You are an expert AI code assistant. Use the provided source code to answer the question.
                        
                        Code:
                        {code}
                        
                        Chat History:
                        {chat_history}
                        
                        Question: {question}""")
                        
                        # Modern LCEL chain replacing deprecated LLMChain & ConversationBufferMemory
                        chat_chain = chat_prompt | llm | StrOutputParser()
                        
                        response = chat_chain.invoke({
                            "code": code_content,
                            "chat_history": chat_history_str,
                            "question": prompt
                        })
                        
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
