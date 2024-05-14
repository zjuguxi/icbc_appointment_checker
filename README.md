# ICBC Appointment Checker

This script checks for available appointments at various ICBC locations and sends email notifications if there are any changes.

## Features

- Checks for available appointments at specified ICBC locations.
- Sends email notifications if there are any changes in the available appointments.
- Saves the latest appointments to a text file.

## Requirements

- Python 3.x
- `requests` library
- `pyyaml` library
- `loguru` library
- `faker` library

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/icbc-appointment-checker.git
    cd icbc-appointment-checker
    ```

2. Install the required Python libraries:

    ```bash
    pip install requests pyyaml loguru faker
    ```

## Configuration

1. Create a `config.yml` file in the project directory. You can use the provided `config.yml.example` as a template:

    ```bash
    cp config.yml.example config.yml
    ```

2. Edit the `config.yml` file with your own details:

    ```yaml
    icbc:
      drvrLastName: "YourLastName"
      licenceNumber: "YourLicenceNumber"
      keyword: "YourKeyword"
      expactAfterDate: "2024-05-01"
      expactBeforeDate: "2024-06-01"
      expactAfterTime: "08:00"
      expactBeforeTime: "17:00"
      examClass: "5"
      posID: 273
      prfDaysOfWeek: "[0,1,2,3,4,5,6]"
      prfPartsOfDay: "[0,1]"

    email:
      smtp_server: "smtp.your-email-provider.com"
      smtp_port: 587
      sender_address: "your_email@provider.com"
      sender_pass: "your_application_specific_password"
      receiver_addresses:
        - "receiver1_email@provider.com"
        - "receiver2_email@provider.com"
    ```

## Usage

Run the script with the specified config file:

    ```bash
    python icbc_appointment_checker.py config.yml
    ```

The script will check for available appointments and send email notifications to the specified recipients if there are any changes.

## Location Parameters

    ```markdown
    | Location                                        | posID |
    |-------------------------------------------------|-------|
    | Richmond claim centre (Elmbridge Way)            | 273   |
    | Richmond driver licensing (Lansdowne Centre mall)| 93    |
    | Vancouver driver licensing (Point Grey)          | 9     |
    | Vancouver claim centre (Kingsway)                | 275   |
    | Burnaby claim centre (Wayburne Drive)            | 274   |
    | Surrey driver licensing                          | 11    |
    | Newton claim centre (68 Avenue)                  | 271   |
    | Surrey claim centre (152A St.)                   | 269   |
    | North Vancouver driver licensing                 | 8     |
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
