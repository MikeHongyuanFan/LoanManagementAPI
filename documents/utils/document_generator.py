"""
Document generation service for the document management system
"""
import os
import tempfile
from django.conf import settings
from django.core.files import File
from django.utils import timezone
from django.template import Template, Context
from django.template.loader import get_template
from applications.models import Application
from documents.models import Document, DocumentTemplate
from documents.utils.pdf_generator import HTMLToPDFGenerator, ReportLabPDFGenerator


class DocumentGenerator:
    """Service for generating documents from templates"""
    
    def __init__(self, user=None):
        """Initialize the document generator
        
        Args:
            user: The user generating the document
        """
        self.user = user
        self.html_generator = HTMLToPDFGenerator()
        self.reportlab_generator = ReportLabPDFGenerator()
    
    def _get_application_context(self, application):
        """Get context data for an application
        
        Args:
            application: Application object
        
        Returns:
            Dictionary with application context data
        """
        borrower = application.borrower
        
        # Format currency values
        loan_amount = f"${application.loan_amount:,.2f}" if application.loan_amount else "N/A"
        
        context = {
            'application': application,
            'application_id': application.id,
            'borrower': borrower,
            'borrower_name': f"{borrower.first_name} {borrower.last_name}" if borrower else "N/A",
            'borrower_email': borrower.email if borrower else "N/A",
            'borrower_phone': borrower.phone_number if borrower else "N/A",
            'loan_amount': loan_amount,
            'loan_type': application.get_loan_type_display() if hasattr(application, 'get_loan_type_display') else "N/A",
            'status': application.get_status_display() if hasattr(application, 'get_status_display') else "N/A",
            'submitted_date': application.created_at.strftime('%B %d, %Y') if application.created_at else "N/A",
            'last_updated': application.updated_at.strftime('%B %d, %Y') if application.updated_at else "N/A",
            'current_date': timezone.now().strftime('%B %d, %Y'),
            'company_name': getattr(settings, 'COMPANY_NAME', 'Loan Management System'),
            'company_address': getattr(settings, 'COMPANY_ADDRESS', '123 Finance Street'),
            'company_phone': getattr(settings, 'COMPANY_PHONE', '(555) 123-4567'),
            'company_email': getattr(settings, 'COMPANY_EMAIL', 'contact@loanmanagementsystem.com'),
        }
        
        # Add broker information if available
        if hasattr(application, 'broker') and application.broker:
            broker = application.broker
            context.update({
                'broker': broker,
                'broker_name': f"{broker.first_name} {broker.last_name}" if hasattr(broker, 'first_name') else broker.name,
                'broker_email': broker.email if hasattr(broker, 'email') else "N/A",
                'broker_phone': broker.phone_number if hasattr(broker, 'phone_number') else "N/A",
            })
        
        # Add loan calculation details if available
        if hasattr(application, 'repayments') and application.repayments.exists():
            repayment = application.repayments.first()
            context.update({
                'interest_rate': f"{repayment.interest_rate:.2f}%" if repayment.interest_rate else "N/A",
                'loan_term': f"{repayment.term} months" if repayment.term else "N/A",
                'payment_amount': f"${repayment.monthly_payment:,.2f}" if repayment.monthly_payment else "N/A",
                'payment_frequency': repayment.get_frequency_display() if hasattr(repayment, 'get_frequency_display') else "Monthly",
                'start_date': repayment.start_date.strftime('%B %d, %Y') if repayment.start_date else "N/A",
                'end_date': repayment.end_date.strftime('%B %d, %Y') if repayment.end_date else "N/A",
            })
        
        return context
    
    def generate_from_template(self, template_id, application_id, document_type, title=None, description=None):
        """Generate a document from a template
        
        Args:
            template_id: ID of the template to use
            application_id: ID of the application
            document_type: Type of document to create
            title: Title for the document
            description: Description for the document
        
        Returns:
            Generated Document object
        """
        try:
            template = DocumentTemplate.objects.get(id=template_id)
            application = Application.objects.get(id=application_id)
        except (DocumentTemplate.DoesNotExist, Application.DoesNotExist):
            return None
        
        # Get context data
        context = self._get_application_context(application)
        
        # Generate document based on template type
        if template.file.name.endswith('.html'):
            # HTML template
            output_path = self._generate_from_html_template(template, context)
        else:
            # Use ReportLab for other template types
            output_path = self._generate_from_reportlab(application, document_type, context)
        
        # Create document record
        with open(output_path, 'rb') as f:
            document = Document.objects.create(
                application=application,
                document_type=document_type,
                title=title or f"{application.borrower.last_name} - {template.name}",
                description=description or f"Generated from template: {template.name}",
                uploaded_by=self.user,
                last_modified_by=self.user,
                status='draft'
            )
            document.file.save(os.path.basename(output_path), File(f))
        
        # Clean up temporary file
        os.unlink(output_path)
        
        return document
    
    def _generate_from_html_template(self, template, context):
        """Generate a document from an HTML template
        
        Args:
            template: DocumentTemplate object
            context: Context data for the template
        
        Returns:
            Path to the generated PDF
        """
        # Create a temporary file for the rendered template
        temp_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        temp_html_path = temp_html.name
        temp_html.close()
        
        # Read the template content
        with open(template.file.path, 'r') as f:
            template_content = f.read()
        
        # Render the template
        template_obj = Template(template_content)
        rendered_html = template_obj.render(Context(context))
        
        # Write the rendered HTML to the temporary file
        with open(temp_html_path, 'w') as f:
            f.write(rendered_html)
        
        # Generate PDF from the HTML
        output_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        output_pdf_path = output_pdf.name
        output_pdf.close()
        
        try:
            # Try to use WeasyPrint to convert HTML to PDF
            html_generator = HTMLToPDFGenerator()
            html_generator.generate_from_template(temp_html_path, context, output_pdf_path)
        except Exception as e:
            # If WeasyPrint fails, fall back to ReportLab
            print(f"HTML to PDF conversion failed: {e}. Falling back to ReportLab.")
            generator = ReportLabPDFGenerator()
            if context.get('document_type') == 'agreement':
                generator.generate_loan_agreement(context, output_pdf_path)
            else:
                generator.generate_application_summary(context, output_pdf_path)
        
        # Clean up temporary HTML file
        os.unlink(temp_html_path)
        
        return output_pdf_path
    
    def _generate_from_reportlab(self, application, document_type, context):
        """Generate a document using ReportLab
        
        Args:
            application: Application object
            document_type: Type of document to create
            context: Context data for the document
        
        Returns:
            Path to the generated PDF
        """
        generator = ReportLabPDFGenerator()
        
        # Create a temporary file for the PDF
        output_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        output_pdf_path = output_pdf.name
        output_pdf.close()
        
        if document_type == 'agreement':
            # Generate loan agreement
            generator.generate_loan_agreement(context, output_pdf_path)
        else:
            # Generate application summary by default
            generator.generate_application_summary(context, output_pdf_path)
        
        return output_pdf_path
    
    def generate_loan_agreement(self, application_id, title=None, description=None):
        """Generate a loan agreement document
        
        Args:
            application_id: ID of the application
            title: Title for the document
            description: Description for the document
        
        Returns:
            Generated Document object
        """
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None
        
        # Get context data
        context = self._get_application_context(application)
        
        # Generate loan agreement
        generator = ReportLabPDFGenerator()
        output_path = generator.generate_loan_agreement(context)
        
        # Create document record
        with open(output_path, 'rb') as f:
            document = Document.objects.create(
                application=application,
                document_type='agreement',
                title=title or f"Loan Agreement - {application.borrower.last_name}",
                description=description or "Generated loan agreement document",
                uploaded_by=self.user,
                last_modified_by=self.user,
                status='draft'
            )
            document.file.save(f"loan_agreement_{application.id}.pdf", File(f))
        
        # Clean up temporary file
        os.unlink(output_path)
        
        return document
    
    def generate_application_summary(self, application_id, title=None, description=None):
        """Generate an application summary document
        
        Args:
            application_id: ID of the application
            title: Title for the document
            description: Description for the document
        
        Returns:
            Generated Document object
        """
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None
        
        # Get context data
        context = self._get_application_context(application)
        
        # Generate application summary
        generator = ReportLabPDFGenerator()
        output_path = generator.generate_application_summary(context)
        
        # Create document record
        with open(output_path, 'rb') as f:
            document = Document.objects.create(
                application=application,
                document_type='application',
                title=title or f"Application Summary - {application.borrower.last_name}",
                description=description or "Generated application summary document",
                uploaded_by=self.user,
                last_modified_by=self.user,
                status='draft'
            )
            document.file.save(f"application_summary_{application.id}.pdf", File(f))
        
        # Clean up temporary file
        os.unlink(output_path)
        
        return document
