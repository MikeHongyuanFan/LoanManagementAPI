"""
PDF Generation utilities for document management system
"""
import os
import tempfile
from datetime import datetime
from django.template.loader import render_to_string
from django.conf import settings

# Try to import WeasyPrint, but don't fail if it's not available
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    pass

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFGenerator:
    """Base class for PDF generation"""
    
    def __init__(self, output_path=None):
        """Initialize the PDF generator
        
        Args:
            output_path: Path where the PDF will be saved. If None, a temporary file will be created.
        """
        self.output_path = output_path
        if not output_path:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            self.output_path = temp_file.name
            temp_file.close()
    
    def add_watermark(self, input_pdf_path, watermark_text="DRAFT", output_path=None):
        """Add a watermark to a PDF
        
        Args:
            input_pdf_path: Path to the input PDF
            watermark_text: Text to use as watermark
            output_path: Path where the watermarked PDF will be saved
        
        Returns:
            Path to the watermarked PDF
        """
        try:
            from PyPDF2 import PdfReader, PdfWriter
            
            if not output_path:
                output_path = self.output_path
            
            # Create watermark
            watermark_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            c = canvas.Canvas(watermark_file.name, pagesize=letter)
            c.setFont("Helvetica", 70)
            c.setFillColor(colors.lightgrey)
            c.setFillAlpha(0.5)
            c.saveState()
            c.translate(letter[0]/2, letter[1]/2)
            c.rotate(45)
            c.drawCentredString(0, 0, watermark_text)
            c.restoreState()
            c.save()
            watermark_file.close()
            
            # Apply watermark
            watermark = PdfReader(watermark_file.name)
            watermark_page = watermark.pages[0]
            
            pdf_reader = PdfReader(input_pdf_path)
            pdf_writer = PdfWriter()
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page.merge_page(watermark_page)
                pdf_writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # Clean up
            os.unlink(watermark_file.name)
            
            return output_path
        except ImportError:
            # If PyPDF2 is not available, just return the original PDF
            print("PyPDF2 not available, skipping watermark")
            if not output_path:
                import shutil
                shutil.copy(input_pdf_path, self.output_path)
                return self.output_path
            else:
                import shutil
                shutil.copy(input_pdf_path, output_path)
                return output_path


class HTMLToPDFGenerator(PDFGenerator):
    """Generate PDF from HTML template"""
    
    def generate_from_template(self, template_name, context, output_path=None, css_files=None):
        """Generate a PDF from an HTML template
        
        Args:
            template_name: Name of the HTML template
            context: Context data for the template
            output_path: Path where the PDF will be saved
            css_files: List of CSS files to apply
        
        Returns:
            Path to the generated PDF
        """
        if not output_path:
            output_path = self.output_path
        
        if not WEASYPRINT_AVAILABLE:
            # Fall back to ReportLab if WeasyPrint is not available
            generator = ReportLabPDFGenerator()
            if isinstance(context.get('application'), dict):
                return generator.generate_application_summary(context, output_path)
            else:
                return generator.generate_application_summary(context, output_path)
        
        # Render HTML template
        html_string = render_to_string(template_name, context)
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Prepare CSS
        css = []
        if css_files:
            for css_file in css_files:
                css_path = os.path.join(settings.STATIC_ROOT, 'css', css_file)
                if os.path.exists(css_path):
                    css.append(CSS(css_path, font_config=font_config))
        
        # Generate PDF
        HTML(string=html_string).write_pdf(
            output_path,
            stylesheets=css,
            font_config=font_config
        )
        
        return output_path


class ReportLabPDFGenerator(PDFGenerator):
    """Generate PDF using ReportLab"""
    
    def __init__(self, output_path=None, page_size=letter, title="Document", author="Loan Management System"):
        """Initialize the ReportLab PDF generator
        
        Args:
            output_path: Path where the PDF will be saved
            page_size: Page size for the PDF
            title: Title of the PDF document
            author: Author of the PDF document
        """
        super().__init__(output_path)
        self.page_size = page_size
        self.title = title
        self.author = author
        self.styles = getSampleStyleSheet()
        
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='Heading1Center',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='Normal-Right',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))
        
        self.styles.add(ParagraphStyle(
            name='Normal-Center',
            parent=self.styles['Normal'],
            alignment=TA_CENTER
        ))
    
    def generate_loan_agreement(self, loan_data, output_path=None):
        """Generate a loan agreement PDF
        
        Args:
            loan_data: Dictionary containing loan data
            output_path: Path where the PDF will be saved
        
        Returns:
            Path to the generated PDF
        """
        if not output_path:
            output_path = self.output_path
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            title=f"Loan Agreement - {loan_data.get('borrower_name', 'Unknown')}",
            author=self.author
        )
        
        # Build content
        content = []
        
        # Add logo if available
        # if hasattr(settings, 'COMPANY_LOGO') and os.path.exists(settings.COMPANY_LOGO):
        #     logo = Image(settings.COMPANY_LOGO)
        #     logo.drawHeight = 0.5*inch
        #     logo.drawWidth = 1.5*inch
        #     content.append(logo)
        
        # Title
        content.append(Paragraph(f"LOAN AGREEMENT", self.styles['Heading1Center']))
        content.append(Spacer(1, 0.25*inch))
        
        # Date
        content.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal-Right']))
        content.append(Spacer(1, 0.25*inch))
        
        # Parties
        content.append(Paragraph("THIS LOAN AGREEMENT is made between:", self.styles['Normal']))
        content.append(Spacer(1, 0.1*inch))
        content.append(Paragraph(f"<b>Lender:</b> {loan_data.get('lender_name', 'Company Name')}", self.styles['Normal']))
        content.append(Paragraph(f"<b>Borrower:</b> {loan_data.get('borrower_name', 'Borrower Name')}", self.styles['Normal']))
        content.append(Spacer(1, 0.25*inch))
        
        # Loan details
        content.append(Paragraph("<b>LOAN DETAILS</b>", self.styles['Heading2']))
        
        # Create a table for loan details
        loan_details = [
            ["Loan Amount:", f"${loan_data.get('loan_amount', 0):,.2f}"],
            ["Interest Rate:", f"{loan_data.get('interest_rate', 0):.2f}%"],
            ["Loan Term:", f"{loan_data.get('loan_term', 0)} months"],
            ["Start Date:", loan_data.get('start_date', 'N/A')],
            ["End Date:", loan_data.get('end_date', 'N/A')],
            ["Payment Frequency:", loan_data.get('payment_frequency', 'Monthly')],
            ["Payment Amount:", f"${loan_data.get('payment_amount', 0):,.2f}"]
        ]
        
        table = Table(loan_details, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 0.25*inch))
        
        # Terms and conditions
        content.append(Paragraph("<b>TERMS AND CONDITIONS</b>", self.styles['Heading2']))
        
        terms = [
            "1. <b>Loan Amount:</b> The Lender agrees to lend the Borrower the principal sum as specified above.",
            "2. <b>Interest Rate:</b> The loan shall bear interest at the rate specified above.",
            "3. <b>Repayment:</b> The Borrower shall repay the loan in installments as specified above.",
            "4. <b>Late Payment:</b> If any payment is late, the Borrower shall pay a late fee of 5% of the payment amount.",
            "5. <b>Prepayment:</b> The Borrower may prepay the loan in whole or in part at any time without penalty.",
            "6. <b>Default:</b> If the Borrower defaults on any payment, the entire loan balance shall become immediately due."
        ]
        
        for term in terms:
            content.append(Paragraph(term, self.styles['Normal']))
            content.append(Spacer(1, 0.1*inch))
        
        content.append(Spacer(1, 0.25*inch))
        
        # Signatures
        content.append(Paragraph("<b>SIGNATURES</b>", self.styles['Heading2']))
        content.append(Spacer(1, 0.5*inch))
        
        signature_data = [
            ["________________________", "________________________"],
            ["Lender Signature", "Borrower Signature"],
            ["", ""],
            ["________________________", "________________________"],
            ["Date", "Date"]
        ]
        
        signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        content.append(signature_table)
        
        # Build the PDF
        doc.build(content)
        
        return output_path
    
    def generate_application_summary(self, application_data, output_path=None):
        """Generate an application summary PDF
        
        Args:
            application_data: Dictionary containing application data
            output_path: Path where the PDF will be saved
        
        Returns:
            Path to the generated PDF
        """
        if not output_path:
            output_path = self.output_path
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            title=f"Loan Application Summary - {application_data.get('application_id', 'Unknown')}",
            author=self.author
        )
        
        # Build content
        content = []
        
        # Title
        content.append(Paragraph(f"LOAN APPLICATION SUMMARY", self.styles['Heading1Center']))
        content.append(Spacer(1, 0.25*inch))
        
        # Application ID and Date
        content.append(Paragraph(f"Application ID: {application_data.get('application_id', 'Unknown')}", self.styles['Normal']))
        content.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        content.append(Spacer(1, 0.25*inch))
        
        # Borrower Information
        content.append(Paragraph("<b>BORROWER INFORMATION</b>", self.styles['Heading2']))
        
        borrower_details = [
            ["Name:", application_data.get('borrower_name', 'N/A')],
            ["Email:", application_data.get('borrower_email', 'N/A')],
            ["Phone:", application_data.get('borrower_phone', 'N/A')],
            ["Address:", application_data.get('borrower_address', 'N/A')]
        ]
        
        table = Table(borrower_details, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 0.25*inch))
        
        # Loan Information
        content.append(Paragraph("<b>LOAN INFORMATION</b>", self.styles['Heading2']))
        
        loan_details = [
            ["Loan Type:", application_data.get('loan_type', 'N/A')],
            ["Loan Amount:", f"${application_data.get('loan_amount', 0):,.2f}"],
            ["Interest Rate:", f"{application_data.get('interest_rate', 0):.2f}%"],
            ["Loan Term:", f"{application_data.get('loan_term', 0)} months"],
            ["Purpose:", application_data.get('loan_purpose', 'N/A')]
        ]
        
        table = Table(loan_details, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 0.25*inch))
        
        # Application Status
        content.append(Paragraph("<b>APPLICATION STATUS</b>", self.styles['Heading2']))
        
        status_details = [
            ["Status:", application_data.get('status', 'N/A')],
            ["Submitted Date:", application_data.get('submitted_date', 'N/A')],
            ["Last Updated:", application_data.get('last_updated', 'N/A')],
            ["Assigned To:", application_data.get('assigned_to', 'N/A')]
        ]
        
        table = Table(status_details, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 0.25*inch))
        
        # Notes
        if application_data.get('notes'):
            content.append(Paragraph("<b>NOTES</b>", self.styles['Heading2']))
            content.append(Paragraph(application_data.get('notes', ''), self.styles['Normal']))
            content.append(Spacer(1, 0.25*inch))
        
        # Disclaimer
        content.append(Paragraph("<i>This is a summary of the loan application and does not constitute a loan agreement. The final loan terms may differ based on underwriting and approval processes.</i>", self.styles['Normal-Center']))
        
        # Build the PDF
        doc.build(content)
        
        return output_path
