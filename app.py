import streamlit as st
import openai
import os
from PIL import Image
import requests
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Ikai Asai Product Image Generator",
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
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='main-title'>Ikai Asai Product Image Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Create beautiful product visualizations with natural aesthetics inspired by Ikai Asai</p>", 
            unsafe_allow_html=True)

# Function to enrich user prompts with Ikai Asai aesthetics
def enrich_prompt(product_type, material, color, size, additional_details):
    # Create a more neutral style description that avoids safety triggers
    ikai_asai_style = (
       "Artisanal luxury product embodying Ikai Asai's signature style: handcrafted with meticulous attention to detail, "
        "featuring a minimalist design with an earthy, organic aesthetic. The piece showcases the natural beauty and "
        "tactile qualities of the material with subtle, rustic textures and organic forms. "
        "The product exudes understated sophistication and timeless beauty while remaining functional for modern living. "
        "Photographed in soft, natural lighting against a neutral background to highlight its authentic character, "
        "subtle color variations, and artisanal craftsmanship. The composition should evoke a sense of tranquility "
        "and connection to nature, characteristic of Ikai Asai's design philosophy.")
    # Build the base product description
    product_desc = f"A {color} {product_type} made of {material}"
    
    if size:
        product_desc += f", size {size}"
    
    if additional_details:
        # Filter out any potentially problematic words from additional details
        product_desc += f". {additional_details}"
    
    # Combine in a way that separates the product from the style guidance
    return f"Product: {product_desc}. Photography style: {ikai_asai_style}"

# Function to generate an image with the enriched prompt
def generate_image(enriched_prompt):
    import traceback
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None, "OpenAI API key not found in environment variables"
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.images.generate(
            prompt=enriched_prompt,
            n=1,
            size="1024x1024",
            model="dall-e-3"
        )
        image_url = response.data[0].url
        return image_url, None
    except openai.OpenAIError as oe:
        # OpenAI specific error
        error_str = str(oe)
        if 'moderation_blocked' in error_str or 'safety system' in error_str:
            return None, ("Your prompt was blocked by OpenAI's safety system. "
                         "Please rephrase your product description and try again. ")
        return None, f"OpenAI API error: {oe}"
    except Exception as e:
        # Log traceback for debugging in Streamlit
        import streamlit as st
        st.error(f"Unexpected error: {e}")
        st.text(traceback.format_exc())
        return None, f"Unexpected error: {e}"

# Sidebar for settings
with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    This app uses OpenAI's latest image model (gpt-image-1) to generate product images 
    in the style of Ikai Asai - a brand known for its handcrafted, 
    minimalist designs with an earthy aesthetic.
    """)

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
    
    # Generate image button
    if st.button("Generate Image", disabled=not product_type):
        if not product_type:
            st.error("Please enter at least the product type.")
        else:
            enriched_prompt = enrich_prompt(product_type, material, color, size, additional_details)
            
            with st.spinner("Generating your product image..."):
                image_url, error = generate_image(enriched_prompt)
                
                if image_url:
                    # Store the image URL in session state to display in the right column
                    st.session_state.image_url = image_url
                    st.session_state.prompt = enriched_prompt
                    st.success("Image generated successfully!")
                else:
                    st.error(f"Failed to generate image: {error}")

# Right column to display the generated image
with col2:
    st.markdown("<h3 class='section-header'>Generated Image</h3>", unsafe_allow_html=True)
    
    # Display placeholder or generated image
    if 'image_url' in st.session_state and st.session_state.image_url:
        try:
            # Download and display the image
            response = requests.get(st.session_state.image_url)
            image = Image.open(BytesIO(response.content))
            st.image(image, use_column_width=True)
            
            # Display download link
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
                <h3>Your generated image will appear here</h3>
                <p>Complete the form and click "Generate Image"</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 12px;">
        Powered by OpenAI GPT-4o Image | Inspired by Ikai Asai aesthetics
    </div>
    """, 
    unsafe_allow_html=True
)