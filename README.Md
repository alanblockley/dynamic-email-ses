# Dynamic Email SES Lambda Function

## Overview
This project implements an AWS Lambda function to dynamically process form submissions and send emails using Amazon SES (Simple Email Service). The function dynamically constructs email content based on form data, uses SES templates to format the email, and ensures cleanup of resources after execution.

---

## :warning: :warning: :warning: WARNING
Review this code before you deploy it into your environment. 

You are responsible for implementing your own security and spam prevention methods. 

---

## Features
- **Dynamic Email Content**: Processes form submissions with varying fields to generate custom emails.
- **SES Integration**: Uses SES templates for structured email delivery.
- **Robust Logging**: Logs all operations for debugging and tracing.
- **Error Handling**: Ensures graceful handling of exceptions and informative error messages.

---

## Prerequisites
### Environment Variables
Set the following environment variables in your Lambda configuration:
- **`SES_RECIP_EMAIL`**: The recipient email address.
- **`SES_SOURCE_EMAIL`**: The verified SES source email address.

### IAM Permissions
The Lambda function requires the following permissions:
- `ses:CreateTemplate`
- `ses:SendTemplatedEmail`
- `ses:DeleteTemplate`

---

## Installation
### Using AWS SAM
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/dynamic-email-ses.git
   cd dynamic-email-ses
   ```

2. Build and deploy the Lambda function:
   ```bash
   sam build
   sam deploy --guided
   ```

3. Provide the required parameter values during the guided deployment:
   - **`SES_RECIP_EMAIL`**: Your recipient email.
   - **`SES_SOURCE_EMAIL`**: Your verified source email.

---

## Usage
### HTML Form Integration
You can point an HTML form to the API Gateway endpoint for this Lambda function. For example:

```html
<form action="https://your-api-endpoint.amazonaws.com/send" method="POST">
  <input type="text" name="name" placeholder="Your Name" required>
  <input type="email" name="email" placeholder="Your Email" required>
  <input type="text" name="message" placeholder="Your Message" required>
  <button type="submit">Send</button>
</form>
```

### Example Forms
Sample HTML forms can be found in the `example` folder of the repository. These forms include various configurations for testing and integration.

### Event Payload Example
Submit a URL-encoded payload through API Gateway to trigger the Lambda function:
```plaintext
name=John+Doe&business=Example+Corp&phone=1234567890&email=john.doe%40example.com&subject=Feedback+Form+Submission&message=Hello+World
```

### Response Example
Upon success, the Lambda function returns:
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Email sent successfully!\"}"
}
```

On error:
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Error details\"}"
}
```

---

## Key Functions
### `validate_environment_variables()`
Ensures required environment variables are set. Raises an error if not.

### `parse_event_body(event)`
Parses the URL-encoded body of the event and converts it into a dictionary.

### `construct_email_content(form_data)`
Generates HTML and plain-text email content dynamically based on the form data.

### `create_email_template(template_name, subject, html_body, text_body)`
Creates an SES email template with the specified parameters.

### `send_email(template_name)`
Sends an email using the SES template.

### `delete_email_template(template_name)`
Deletes the SES email template to clean up resources.

---

## Testing
### Locally
1. Install dependencies:
   ```bash
   pip install boto3
   ```

2. Simulate an event by passing a test JSON payload to the `lambda_handler` function.

### In AWS
1. Deploy the Lambda function.
2. Send a POST request to the API Gateway endpoint with URL-encoded form data.

---

## Logs
Logs are automatically captured by AWS CloudWatch. Ensure your Lambda function has appropriate permissions to write to CloudWatch Logs.

---

## Known Issues
- Ensure SES source email and recipient email are verified if using in the sandbox environment.
- Lambda timeout should be sufficient to handle SES retries.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

