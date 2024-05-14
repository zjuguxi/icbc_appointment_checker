import argparse
import requests
import json
import yaml
from datetime import datetime
from loguru import logger
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from faker import Faker

# Load configuration from YAML file
def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Generate fake headers using Faker
def generate_headers():
    fake = Faker()
    headers = {
        'Content-type': 'application/json',
        'User-Agent': fake.user_agent(),
        'Sec-Ch-Ua-Platform': fake.random_element(elements=["Windows", "macOS", "Linux"]),
        'Sec-Ch-Ua': f'"Chromium";v="{fake.random_int(min=70, max=100)}", "Google Chrome";v="{fake.random_int(min=70, max=100)}", "Not;A=Brand";v="99"',
        'Dnt': '1'
    }
    return headers

# Get the authorization token
def get_token(config):
    login_url = "https://onlinebusiness.icbc.com/deas-api/v1/webLogin/webLogin"
    headers = generate_headers()
    payload = {
        "drvrLastName": config['icbc']['drvrLastName'],
        "licenceNumber": config['icbc']['licenceNumber'],
        "keyword": config['icbc']['keyword']
    }

    # Log request details
    logger.debug(f"Request URL: {login_url}")
    logger.debug(f"Request Headers: {headers}")
    logger.debug(f"Request Payload: {payload}")

    response = requests.put(login_url, data=json.dumps(payload), headers=headers)

    # Log response details
    logger.debug(f"Response Status Code: {response.status_code}")
    logger.debug(f"Response Text: {response.text}")

    if response.status_code == 200:
        logger.debug(response.headers)
        logger.debug(response.headers["Authorization"])
        return response.headers["Authorization"]
    else:
        logger.error("Failed to get token")
        return ""

# Get available appointments
def get_appointments(config, token):
    appointment_url = "https://onlinebusiness.icbc.com/deas-api/v1/web/getAvailableAppointments"
    headers = generate_headers()
    headers['Authorization'] = token
    
    payload = {
        "aPosID": config['icbc']['posID'],
        "examType": str(config['icbc']['examClass']) + "-R-1",
        "examDate": config['icbc']['expactAfterDate'],
        "ignoreReserveTime": "false",
        "prfDaysOfWeek": config['icbc']['prfDaysOfWeek'],
        "prfPartsOfDay": config['icbc']['prfPartsOfDay'],
        "lastName": config['icbc']['drvrLastName'],
        "licenseNumber": config['icbc']['licenceNumber']
    }

    response = requests.post(appointment_url, data=json.dumps(payload), headers=headers)

    # Log response details
    logger.debug(f"Response Status Code: {response.status_code}")
    # logger.debug(f"Response Text: {response.text}")

    if response.status_code == 200:
        appointments = response.json()[:10]
        for appointment in appointments:
            date = appointment["appointmentDt"]["date"]
            day_of_week = appointment["appointmentDt"]["dayOfWeek"]
            time = appointment["startTm"]
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y-%m-%d %A")
            logger.debug(f"{formatted_date} {time}")
        return appointments
    logger.error("Authorization error or failed to get appointments")
    return []

# Save the appointments to a text file
def save_appointments_to_txt(appointments, file_path):
    with open(file_path, 'w') as file:
        for appointment in appointments:
            date = appointment["appointmentDt"]["date"]
            day_of_week = appointment["appointmentDt"]["dayOfWeek"]
            time = appointment["startTm"]
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y-%m-%d %A")
            file.write(f"{formatted_date} {time}\n")

# Load the appointments from a text file
def load_appointments_from_txt(file_path):
    appointments = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                date_str, time = line.strip().rsplit(' ', 1)
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %A")
                date = date_obj.strftime("%Y-%m-%d")
                day_of_week = date_obj.strftime("%A")
                appointments.append({
                    "appointmentDt": {"date": date, "dayOfWeek": day_of_week},
                    "startTm": time
                })
    return appointments

# Compare two lists of appointments and return if there are differences
def compare_appointments(old_appointments, new_appointments):
    old_set = set((appt["appointmentDt"]["date"], appt["startTm"]) for appt in old_appointments)
    new_set = set((appt["appointmentDt"]["date"], appt["startTm"]) for appt in new_appointments)
    return old_set != new_set

# Send email with the latest 10 appointments
def send_email(subject, body, config):
    smtp_server = config['email']['smtp_server']
    smtp_port = config['email']['smtp_port']
    sender_address = config['email']['sender_address']
    sender_pass = config['email']['sender_pass']
    receiver_addresses = config['email']['receiver_addresses']

    # Send the email to each recipient
    try:
        session = smtplib.SMTP(smtp_server, smtp_port)
        session.starttls() # Enable security
        session.login(sender_address, sender_pass) # Login with sender's email and password

        for receiver_address in receiver_addresses:
            # Setup the MIME for each recipient
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            text = message.as_string()
            session.sendmail(sender_address, receiver_address, text)
        
        session.quit()
        logger.info("Emails sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

# Format appointments for email content
def format_appointments(appointments):
    formatted = "Latest 10 Appointments:\n"
    for appointment in appointments:
        date = appointment["appointmentDt"]["date"]
        day_of_week = appointment["appointmentDt"]["dayOfWeek"]
        time = appointment["startTm"]
        formatted += f"{date} ({day_of_week}) at {time}\n"
    return formatted

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="ICBC Appointment Checker")
    parser.add_argument('config', type=str, help='Path to the config file')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    token = get_token(config)
    if not token:
        logger.error("No token received. Exiting.")
        return

    new_appointments = get_appointments(config, token)
    old_appointments = load_appointments_from_txt('appointments.txt')

    if compare_appointments(old_appointments, new_appointments):
        subject = "ICBC Appointment Changes"
        body = format_appointments(new_appointments)
        send_email(subject, body, config)

    # Save the latest appointments to a text file
    save_appointments_to_txt(new_appointments, 'appointments.txt')

if __name__ == "__main__":
    main()
