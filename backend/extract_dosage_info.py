#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extract dosage information from PDF"""

import re

# Try to read the PDF and extract dosage-related content
try:
    import PyPDF2
    
    pdf_path = r"c:\Users\mural\Farm_Vaidya_Internship\chatbot\farmvaidya-conversational-ai\Biofactor knowledge base 21112025.pdf"
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        print(f"Total pages: {len(pdf_reader.pages)}\n")
        
        dosage_info = []
        
        # Extract text from all pages
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            # Look for dosage-related content
            if any(keyword in text.lower() for keyword in ['dosage', 'dose', 'per acre', 'application', 'kg/', 'grams', 'litres', 'ml/']):
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in ['dosage', 'dose', 'per acre', 'application', 'kg', 'gram', 'litre', 'ml']):
                        # Get context (previous and next lines)
                        context_start = max(0, i-2)
                        context_end = min(len(lines), i+3)
                        context = '\n'.join(lines[context_start:context_end])
                        dosage_info.append(f"\n--- Page {page_num + 1} ---\n{context}\n")
        
        print("\n=== DOSAGE INFORMATION FOUND ===\n")
        for info in dosage_info[:20]:  # Limit to first 20 matches
            print(info)
            print("-" * 80)
            
except ImportError:
    print("PyPDF2 not installed. Trying pdfplumber...")
    try:
        import pdfplumber
        
        pdf_path = r"c:\Users\mural\Farm_Vaidya_Internship\chatbot\farmvaidya-conversational-ai\Biofactor knowledge base 21112025.pdf"
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}\n")
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and any(keyword in text.lower() for keyword in ['dosage', 'dose', 'per acre', 'application', 'kg/', 'grams', 'litres']):
                    print(f"\n--- Page {page_num + 1} ---")
                    print(text[:500])  # Print first 500 chars
                    print("...")
                    
    except ImportError:
        print("Neither PyPDF2 nor pdfplumber is installed.")
        print("Please install one: pip install PyPDF2 or pip install pdfplumber")
