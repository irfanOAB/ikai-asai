import base64
import os
import requests
import streamlit as st
from openai import OpenAI
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables if available
try:
    load_dotenv()
except ImportError:
    pass

# Page configuration
st.set_page_config(
    page_title="Ikai Asai Enhanced Prompt Generator",
    page_icon="🏺",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-family: 'Serif';
        font-size: 36px;
        color: #5c4033;
        text-align: center;
    }
    .subtitle {
        font-size: 18px;
        color: #7d6b5d;
        text-align: center;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 22px;
        color: #5c4033;
        margin-top: 20px;
    }
    .stButton > button {
        background-color: #4a6741;
        color: white;
        border-radius: 4px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #3a5231;
    }
    .prompt-box {
        background-color: #f8f8f8;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 15px;
        margin-top: 20px;
        font-family: monospace;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .copy-button {
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='main-title'>Ikai Asai Enhanced Prompt Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Create detailed, customized prompts for generating beautiful product visualizations in the Ikai Asai style</p>", 
            unsafe_allow_html=True)

# Get API key from environment or session state
def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and 'api_key' in st.session_state:
        api_key = st.session_state.api_key
    return api_key

# Original enrich_prompt function preserved for compatibility
def original_enrich_prompt(user_prompt):
    """
    Enriches the user's prompt with Ikai Asai aesthetic context.
    """
    ikai_asai_context = (
        "handcrafted, minimalist design with an earthy aesthetic. The style draws inspiration "
        "from natural materials like ceramic, wood, and metal, emphasizing rustic, organic textures. "
        "Products are elegant, functional, and often presented in soft, natural lighting with a serene, "
        "contemporary feel, blending traditional Indian craftsmanship with modern sensibilities."
    )
    return f"Create an image of {user_prompt}. Style: {ikai_asai_context}"

# Enhanced prompt function with additional parameters
def enhanced_enrich_prompt(product_type, material, color, size, additional_details, lighting, background, composition, mood):
    """
    Enriches the user's prompt with detailed Ikai Asai aesthetic context and customizations.
    """
    # Use the original Ikai Asai context as the base
    ikai_asai_context = (
        "handcrafted, minimalist design with an earthy aesthetic. The style draws inspiration "
        "from natural materials like ceramic, wood, and metal, emphasizing rustic, organic textures. "
        "Products are elegant, functional, and often presented in soft, natural lighting with a serene, "
        "contemporary feel, blending traditional Indian craftsmanship with modern sensibilities."
    )
    
    # Build the base product description
    product_desc = f"a {color} {product_type} made of {material}"
    
    if size:
        product_desc += f", size {size}"
    
    if additional_details:
        product_desc += f". {additional_details}"
    
    # Add the new customization options to the style description
    style_desc = ikai_asai_context
    
    # Customize the photography style based on user selections
    if lighting:
        style_desc += f" Lighting: {lighting}."
    
    if background:
        style_desc += f" Background: {background}."
    
    if composition:
        style_desc += f" Composition: {composition}."
    
    if mood:
        style_desc += f" Mood: {mood}."
    
    # Combine in a way that follows the original format
    return f"Create an image of {product_desc}. Style: {style_desc}"

# Main content area with two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h3 class='section-header'>Product Details</h3>", unsafe_allow_html=True)
    
    # Product specifications form
    product_type = st.text_input("Product Type", 
                                placeholder="e.g., bowl, vase, plate, cup", 
                                help="Enter the type of product you want to visualize")
    
    material = st.selectbox("Material", 
                           ["ceramic", "wood", "metal", "stone", "glass", "terracotta", 
                            "bronze", "marble", "brass", "copper"],
                           help="Select the primary material for your product")
    
    color = st.text_input("Color/Finish", 
                         placeholder="e.g., earthen brown, matte black, ivory", 
                         help="Describe the color or finish of the product")
    
    size = st.text_input("Dimensions", 
                        placeholder="e.g., 10cm x 5cm, small/medium/large", 
                        help="Enter the approximate size or dimensions")
    
    additional_details = st.text_area("Additional Details", 
                                     placeholder="e.g., with geometric patterns, smooth texture, rough edges", 
                                     help="Add any additional styling or functional details")
    
    # New customization options
    st.markdown("<h3 class='section-header'>Photography Style Customization</h3>", unsafe_allow_html=True)
    
    lighting = st.selectbox("Lighting Style",
                           ["", "Natural sunlight through window", "Soft diffused studio light", 
                            "Warm golden hour glow", "Dramatic side lighting", "Minimalist even lighting"],
                           help="Select the type of lighting for the product photography")
    
    background = st.selectbox("Background",
                             ["", "Neutral beige", "Minimalist white", "Textured natural stone", 
                              "Warm wooden surface", "Soft gradient", "Muted earth tones"],
                             help="Choose the background style for the product")
    
    composition = st.selectbox("Composition",
                              ["", "Centered isolated product", "Styled with complementary props", 
                               "Overhead flat lay", "45-degree angle view", "Multiple angles in composition"],
                              help="Select how the product should be composed in the frame")
    
    mood = st.selectbox("Mood/Tone",
                       ["", "Serene and calm", "Warm and inviting", "Elegant and sophisticated", 
                        "Rustic and authentic", "Minimalist and clean"],
                       help="Choose the overall mood or feeling of the image")
    
    # Generate prompt button
    if st.button("Generate Enhanced Prompt", disabled=not product_type):
        if not product_type:
            st.error("Please enter at least the product type.")
        else:
            enriched_prompt = enhanced_enrich_prompt(product_type, material, color, size, additional_details, 
                                                   lighting, background, composition, mood)
            
            # Store the prompt in session state to display in the right column
            st.session_state.prompt = enriched_prompt
            st.success("Prompt generated successfully!")

# Right column to display the generated prompt
with col2:
    st.markdown("<h3 class='section-header'>Generated Prompt</h3>", unsafe_allow_html=True)
    
    # Display placeholder or generated prompt
    if 'prompt' in st.session_state and st.session_state.prompt:
        st.markdown("<div class='prompt-box'>" + st.session_state.prompt + "</div>", unsafe_allow_html=True)
        
        # Add copy button functionality with JavaScript
        st.markdown("""
        <button class="copy-button" onclick="copyToClipboard()">Copy to Clipboard</button>
        <script>
        function copyToClipboard() {
            const text = document.querySelector('.prompt-box').innerText;
            navigator.clipboard.writeText(text).then(function() {
                alert('Prompt copied to clipboard!');
            }, function(err) {
                alert('Could not copy text: ' + err);
            });
        }
        </script>
        """, unsafe_allow_html=True)
        
        # Option to generate image directly if API key is available
        api_key = get_api_key()
        if api_key:
            if st.button("Generate Image with this Prompt"):
                with st.spinner("Generating image..."):
                    try:
                        client = OpenAI(api_key=api_key)
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt=st.session_state.prompt,
                            n=1,
                            size="1024x1024"
                        )
                        
                        if response.data and hasattr(response.data[0], 'url') and response.data[0].url:
                            image_url = response.data[0].url
                            st.session_state.image_url = image_url
                            st.success("Image generated successfully!")
                        else:
                            st.error("No image URL received in the response.")
                    except Exception as e:
                        st.error(f"Error generating image: {e}")
        else:
            st.info("To generate images directly, please set your OpenAI API key in the sidebar.")
        
        # Explanation of the prompt
        st.markdown("### How to Use This Prompt")
        st.markdown("""
        This enhanced prompt can be used with:
        - OpenAI's DALL-E models
        - Midjourney
        - Stable Diffusion
        - Other AI image generation tools
        
        The prompt combines your product specifications with Ikai Asai's signature aesthetic and your selected photography style preferences.
        """)
        
        # Display generated image if available
        if 'image_url' in st.session_state and st.session_state.image_url:
            st.markdown("### Generated Image")
            try:
                response = requests.get(st.session_state.image_url)
                image = Image.open(BytesIO(response.content))
                st.image(image, use_column_width=True)
                st.markdown(f"[Download Image]({st.session_state.image_url})")
            except Exception as e:
                st.error(f"Error displaying image: {e}")
    else:
        # Display placeholder
        st.markdown(
            """
            <div style="
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 80px 20px;
                text-align: center;
                color: #888;
                border: 1px dashed #ccc;
                margin: 20px 0;
            ">
                <h3>Your enhanced prompt will appear here</h3>
                <p>Complete the form and click "Generate Enhanced Prompt"</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Sidebar for settings and API key
with st.sidebar:
    st.markdown("### Settings")
    
    # API key input
    api_key_input = st.text_input(
        "OpenAI API Key", 
        type="password",
        value=get_api_key() or "",
        help="Enter your OpenAI API key to generate images directly"
    )
    
    if api_key_input:
        st.session_state.api_key = api_key_input
        if st.button("Save API Key"):
            st.success("API key saved for this session!")
    
    st.markdown("### About")
    st.markdown("""
    This app helps you create detailed prompts for AI image generation tools to produce product images 
    in the style of Ikai Asai - a brand known for its handcrafted, 
    minimalist designs with an earthy aesthetic.
    
    The generated prompts can be used with:
    - OpenAI's DALL-E
    - Midjourney
    - Stable Diffusion
    - Other AI image generators
    """)
    
    st.markdown("### How It Works")
    st.markdown("""
    1. Fill in the product details
    2. Customize the photography style
    3. Click "Generate Enhanced Prompt"
    4. Copy the generated prompt or generate an image directly
    """)
    
    st.markdown("### Tips for Best Results")
    st.markdown("""
    - Be specific about materials and colors
    - Choose complementary lighting and background options
    - Consider the mood that best represents your product
    - Experiment with different compositions for varied results
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 12px;'> 2025 Ikai Asai Enhanced Prompt Generator</p>",
    unsafe_allow_html=True
)