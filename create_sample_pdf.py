"""Script to create a sample PDF for testing."""

import fitz


def create_sample_pdf(output_path: str = "test_data/sample.pdf"):
    """Create a simple sample PDF for testing placeholders."""
    # Create document
    doc = fitz.open()
    
    # Add page
    page = doc.new_page(width=612, height=792)  # Letter size
    
    # Add some content
    page.insert_text(
        point=(72, 100),
        text="Certificate of Completion",
        fontsize=24,
        fontname="helv",
        color=(0.2, 0.3, 0.5)
    )
    
    page.insert_text(
        point=(72, 150),
        text="This certificate is awarded to:",
        fontsize=14,
        fontname="helv",
        color=(0, 0, 0)
    )
    
    # Space for name placeholder (around y=180)
    
    page.insert_text(
        point=(72, 220),
        text="For successfully completing the training program.",
        fontsize=12,
        fontname="helv",
        color=(0, 0, 0)
    )
    
    page.insert_text(
        point=(72, 260),
        text="Company:",
        fontsize=12,
        fontname="helv",
        color=(0, 0, 0)
    )
    
    # Space for company placeholder (around y=260, after "Company:")
    
    page.insert_text(
        point=(72, 300),
        text="Contact Email:",
        fontsize=12,
        fontname="helv",
        color=(0, 0, 0)
    )
    
    # Space for email placeholder (around y=300, after "Contact Email:")
    
    # Add a decorative line
    page.draw_line((72, 320), (540, 320), color=(0.7, 0.7, 0.7), width=1)
    
    page.insert_text(
        point=(72, 350),
        text="Date: February 2026",
        fontsize=10,
        fontname="helv",
        color=(0.5, 0.5, 0.5)
    )
    
    # Save
    doc.save(output_path)
    doc.close()
    print(f"Created sample PDF: {output_path}")


if __name__ == "__main__":
    create_sample_pdf()
