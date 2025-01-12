import os
import json
import boto3
import logging
import urllib.parse
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize the SES client
ses_client = boto3.client('ses')

# Load environment variables
SES_RECIP_EMAIL = os.getenv('SES_RECIP_EMAIL')
SES_SOURCE_EMAIL = os.getenv('SES_SOURCE_EMAIL')

# Constants
ERROR_ENV_VARS = "SES_RECIP_EMAIL or SES_SOURCE_EMAIL environment variable not set"

# Utility Functions
def validate_environment_variables() -> None:
    """Ensure required environment variables are set."""
    if not SES_RECIP_EMAIL or not SES_SOURCE_EMAIL:
        logger.error('Missing required environment variables', 
                     extra={'SES_RECIP_EMAIL': bool(SES_RECIP_EMAIL), 'SES_SOURCE_EMAIL': bool(SES_SOURCE_EMAIL)})
        raise EnvironmentError(ERROR_ENV_VARS)

def parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse the JSON body from the event."""
    try:
        body = event['body']
        body_dict = urllib.parse.parse_qs(body)
        logger.info(f'Parsed event body successfully: {body_dict}', extra={'body': body_dict})
        return body_dict
    except (KeyError, json.JSONDecodeError) as e:
        logger.error('Error parsing event body', exc_info=True)
        raise ValueError("Invalid event body") from e

def construct_email_content(form_data: Dict[str, Any]) -> Dict[str, str]:
    """Construct the email content dynamically based on form data."""
    html_body = "<h1>Form Submission</h1>"
    text_body = "Form Submission\n"

    for key, value in form_data.items():
        if key not in ['recipient', 'sender_name', 'subject']:
            html_body += f"<p><strong>{key.capitalize()}:</strong> {value}</p>"
            text_body += f"{key.capitalize()}: {value}\n"

    return {
        "html_body": html_body,
        "text_body": text_body
    }

def create_email_template(template_name: str, subject: str, html_body: str, text_body: str) -> None:
    """Create an SES email template."""
    template = {
        "TemplateName": template_name,
        "SubjectPart": subject,
        "HtmlPart": html_body,
        "TextPart": text_body
    }
    ses_client.create_template(Template=template)
    logger.info('Created email template', extra={'template_name': template_name})

def send_email(template_name: str) -> None:
    """Send an email using the SES template."""
    ses_client.send_templated_email(
        Source=SES_SOURCE_EMAIL,
        Destination={'ToAddresses': [SES_RECIP_EMAIL]},
        Template=template_name,
        TemplateData="{}"
    )
    logger.info('Sent email successfully', extra={'template_name': template_name})

def delete_email_template(template_name: str) -> None:
    """Delete the SES email template."""
    ses_client.delete_template(TemplateName=template_name)
    logger.info('Deleted email template', extra={'template_name': template_name})

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler function."""
    logger.info('Starting Lambda execution', extra={'request_id': context.aws_request_id})
    logger.info(f'Received event: {event}', extra={'event': event})

    try:
        validate_environment_variables()

        # Parse and process form data
        form_data = parse_event_body(event)
        subject = form_data.get('subject', 'New Form Submission')
        content = construct_email_content(form_data)

        # Generate a unique template name
        template_name = f"DynamicFormTemplate-{context.aws_request_id[:8]}"

        # Create, send, and clean up the email template
        create_email_template(template_name, subject[0], content['html_body'], content['text_body'])
        send_email(template_name)
        delete_email_template(template_name)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email sent successfully!"}),
        }
    except Exception as e:
        logger.error('Error during Lambda execution', exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
