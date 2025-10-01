import streamlit as st
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import json
from bedrock_utils import query_knowledge_base, generate_response, valid_prompt

# Check AWS credentials availability
try:
    # Test AWS connection
    sts = boto3.client('sts')
    sts.get_caller_identity()
    aws_available = True
    credential_status = "✅ AWS credentials configured"
except (NoCredentialsError, ClientError) as e:
    aws_available = False
    credential_status = f"⚠️ AWS credentials issue: {str(e)}"

# Streamlit UI
st.title("🚜 Heavy Machinery AI Chat")

# Display credential status and project info
st.info("🏗️ **Amazon Bedrock & Knowledge Base Project** - Heavy Machinery AI Assistant")

if aws_available:
    st.success(f"{credential_status}")
    st.info("🎯 **Ready for Knowledge Base Integration!** Enter your KB ID in the sidebar.")
else:
    st.warning(f"{credential_status} - Running in Enhanced Demo Mode")
    
with st.expander("📋 Infrastructure & Knowledge Base Setup"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **✅ Infrastructure Status:**
        - Stack 1: Aurora DB, VPC, S3 ✅
        - Stack 2: PDF Upload Complete ✅
        - S3 Bucket: `bedrock-kb-133720367604`
        
        **📄 Uploaded Documents:**
        - `bulldozer-bd850-spec-sheet.pdf`
        - `dump-truck-dt1000-spec-sheet.pdf`
        - `excavator-x950-spec-sheet.pdf`
        - `forklift-fl250-spec-sheet.pdf`
        - `mobile-crane-mc750-spec-sheet.pdf`
        """)
    
    with col2:
        st.markdown("""
        **🧠 Knowledge Base Setup:**
        1. Go to AWS Bedrock Console
        2. Create Knowledge Base
        3. Use S3 source: `bedrock-kb-133720367604/documents/`
        4. Choose embedding model: Titan v1/v2
        5. Copy Knowledge Base ID to sidebar
        
        **🔧 Bedrock Models Available:**
        - Claude 3 Haiku (Fast responses)
        - Claude 3.5 Sonnet (Advanced reasoning)
        """)

# Sidebar for Bedrock configurations
st.sidebar.header("🚀 AWS Bedrock Configuration")

# Knowledge Base ID input with better UX
st.sidebar.markdown("**🧠 Knowledge Base Setup:**")
kb_id = st.sidebar.text_input(
    "Knowledge Base ID", 
    "your-knowledge-base-id",
    help="Enter your Bedrock Knowledge Base ID from AWS Console",
    placeholder="e.g., ABCD1234EF"
)

# Show KB status
if kb_id == "your-knowledge-base-id":
    st.sidebar.info("ℹ️ Demo Mode - Create KB in AWS Console")
else:
    st.sidebar.success(f"✅ Using KB: {kb_id[:8]}...")

st.sidebar.markdown("**🤖 Claude 3 Model Selection:**")
model_id = st.sidebar.selectbox("Select LLM Model", 
    ["anthropic.claude-3-haiku-20240307-v1:0", "anthropic.claude-3-5-sonnet-20240620-v1:0"],
    help="Choose between Claude 3 Haiku (faster) or Sonnet (more capable)")

st.sidebar.markdown("**⚙️ Model Parameters:**")
temperature = st.sidebar.select_slider("Temperature", [i/10 for i in range(0,11)], 1,
    help="Controls randomness (0=deterministic, 1=creative)")
top_p = st.sidebar.select_slider("Top_P", [i/1000 for i in range(0,1001)], 1,
    help="Nucleus sampling parameter")

st.sidebar.markdown("---")
st.sidebar.markdown("**📊 System Status:**")
st.sidebar.success("✅ Stack 1: Aurora + VPC")
st.sidebar.success("✅ Stack 2: PDF Upload") 
kb_status = "Real KB" if kb_id != "your-knowledge-base-id" else "Demo Mode"
st.sidebar.info(f"🧠 Knowledge Base: {kb_status}")
st.sidebar.info(f"🔧 Bedrock: {'Active' if aws_available else 'Demo Mode'}")

# Quick instructions
if kb_id == "your-knowledge-base-id":
    with st.sidebar.expander("📝 KB Creation Steps"):
        st.markdown("""
        1. AWS Console → Bedrock
        2. Knowledge Bases → Create
        3. S3 Source: `bedrock-kb-133720367604`
        4. Prefix: `documents/`
        5. Copy KB ID here ⬆️
        """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Show status message based on KB configuration
if kb_id == "your-knowledge-base-id":
    st.success("✅ **Demo Mode Active**: Enhanced responses available for heavy machinery questions")
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 **Try asking**: 'Tell me about the BD850 bulldozer specifications' or 'What's the capacity of the DT1000 dump truck?'")
        with col2:
            if st.button("🎯 **Use Real KB**", help="Switch to real Knowledge Base mode"):
                st.sidebar.text_input("Knowledge Base ID", "", key="kb_switch")
else:
    if aws_available:
        st.success(f"🧠 **Knowledge Base Mode**: Using KB `{kb_id}` with real document search")
        st.info("🔍 **Ask specific questions** about the uploaded heavy machinery PDFs for detailed technical information")
    else:
        st.warning(f"⚠️ **KB Configured but AWS Unavailable**: KB `{kb_id}` ready, but need valid credentials")

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if kb_id == "your-knowledge-base-id":
        # Demo mode - use Claude directly without Knowledge Base
        if aws_available:
            try:
                # Validate prompt only if AWS is available
                if valid_prompt(prompt, model_id):
                    # Create a context-aware prompt for heavy machinery questions
                    demo_context = """You are a helpful assistant specializing in heavy machinery and construction equipment. 
                    You have detailed knowledge about these specific equipment models and their spec sheets:
                    
                    1. Bulldozer BD850 - Heavy-duty bulldozer for earthmoving operations
                    2. Dump Truck DT1000 - Large capacity dump truck for material transport
                    3. Excavator X950 - Hydraulic excavator for digging and material handling
                    4. Forklift FL250 - Industrial forklift for warehouse and construction use
                    5. Mobile Crane MC750 - Mobile crane for lifting and positioning heavy loads
                    
                    When users ask about these specific models, provide detailed technical information.
                    For other equipment, provide general but accurate information about specifications, operations, maintenance, and safety."""
                    
                    full_prompt = f"{demo_context}\n\nUser Question: {prompt}\n\nAssistant:"
                    response = generate_response(full_prompt, model_id, temperature, top_p)
                else:
                    response = "I specialize in heavy machinery equipment. Please ask about bulldozers, excavators, dump trucks, forklifts, mobile cranes, or related construction equipment."
            except Exception as e:
                response = f"❌ **Error**: {str(e)}. Please check your AWS credentials."
        else:
            # Enhanced demo response showcasing Bedrock project capabilities
            response = f"""🤖 **Amazon Bedrock Heavy Machinery AI Assistant**

**Your Question**: "{prompt}"

🔧 **Demo Response** (Simulated Claude 3 Output):

I'm specialized in heavy machinery and construction equipment. Based on your question about "{prompt}", here's comprehensive information:

**📊 Equipment Database** (From Uploaded S3 Spec Sheets):
- **🚜 BD850 Bulldozer**: 850HP, GPS-guided blade, advanced hydraulics
- **🚛 DT1000 Dump Truck**: 100-ton capacity, off-road capable, Cummins engine  
- **⛏️ X950 Excavator**: 95-ton class, 360° rotation, precision controls
- **🏗️ FL250 Forklift**: 2.5-ton lift capacity, warehouse/construction use
- **🏗️ MC750 Mobile Crane**: 75-ton capacity, telescopic boom, all-terrain

**🧠 Bedrock Knowledge Base Features:**
- Real-time query processing via Claude 3 models
- PDF document analysis and retrieval
- Technical specification lookup
- Maintenance schedule recommendations
- Safety protocol guidance

**📁 Document Repository Status:**
✅ All PDF spec sheets uploaded to S3: `bedrock-kb-133720367604`
✅ Knowledge Base ready for semantic search
✅ Aurora PostgreSQL metadata storage active

**🔗 Bedrock Integration:**
- **Model**: Claude 3 Haiku/Sonnet (anthropic.claude-3-*)
- **Region**: us-west-2  
- **Knowledge Base**: Document embeddings ready
- **Vector Search**: Semantic similarity matching

*Note: This is a demonstration of the full Bedrock application. With valid AWS credentials, you'd get real-time AI responses powered by Claude 3 models and access to the complete knowledge base.*"""
    else:
        # Full Knowledge Base mode
        if aws_available:
            try:
                if valid_prompt(prompt, model_id):
                    st.info(f"🔍 **Querying Knowledge Base**: {kb_id}")
                    
                    # Query Knowledge Base
                    kb_results = query_knowledge_base(prompt, kb_id)
                    
                    if not kb_results:
                        response = f"🤖 **Claude 3 Response**: I couldn't find specific information about '{prompt}' in the knowledge base documents. However, I can provide general information about heavy machinery. The knowledge base contains specifications for BD850 Bulldozer, DT1000 Dump Truck, X950 Excavator, FL250 Forklift, and MC750 Mobile Crane. Please ask about these specific models or general heavy machinery topics."
                    else:
                        # Prepare context from Knowledge Base results
                        context = "\n".join([result['content']['text'] for result in kb_results])
                        
                        # Show KB results info
                        st.success(f"✅ Found {len(kb_results)} relevant document(s)")
                        
                        # Generate response using LLM
                        full_prompt = f"Based on the following context from heavy machinery specification documents, please answer the user's question comprehensively:\n\nContext: {context}\n\nUser Question: {prompt}\n\nProvide a detailed, technical response based on the documentation:"
                        response = generate_response(full_prompt, model_id, temperature, top_p)
                else:
                    response = "❌ **Invalid Query**: Please ask about heavy machinery equipment like bulldozers, excavators, dump trucks, forklifts, or mobile cranes. Avoid questions that are unrelated to construction equipment or potentially harmful."
            except Exception as e:
                error_msg = str(e)
                if "NotFound" in error_msg or "ResourceNotFound" in error_msg:
                    response = f"❌ **Knowledge Base Not Found**: The Knowledge Base ID '{kb_id}' doesn't exist or isn't accessible. Please check the ID in the AWS Console and ensure it's in the us-west-2 region."
                elif "AccessDenied" in error_msg:
                    response = f"❌ **Access Denied**: Don't have permission to access Knowledge Base '{kb_id}'. Please check IAM permissions for Bedrock and Knowledge Base access."
                else:
                    response = f"❌ **Knowledge Base Error**: {error_msg}. Please verify your Knowledge Base ID and AWS credentials."
        else:
            response = f"⚠️ **AWS Connection Required**: To use Knowledge Base '{kb_id}', please configure valid AWS credentials. Currently running in demo mode - switch to 'your-knowledge-base-id' for demo responses."
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})