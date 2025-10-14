def parse_email(email_input):
    # Extrae los valores del diccionario email_input
    author = email_input.get("author", "")
    to = email_input.get("to", "")
    subject = email_input.get("subject", "")
    email_thread = email_input.get("email_thread", "")
    return author, to, subject, email_thread

def format_email_markdown(subject, author, to, email_thread):
    # Formatea el correo electrónico en Markdown
    markdown = f"### Subject: {subject}\n"
    markdown += f"**From:** {author}\n"
    markdown += f"**To:** {to}\n"
    markdown += f"**Email Thread:**\n{email_thread}\n"
    return markdown