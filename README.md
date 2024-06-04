# Email Notification for ETH Block Proposals

This Python script monitors the Ethereum blockchain for new finalized blocks and sends email notifications when a block is proposed by a validator index specified in the `validators.txt` file. I should mention that I run this instead of using beaconcha.in service as the app will send a notification even if it's at odd hours of the day (and I don't want to silence it as I want to be pinged when validators are down). This is therefore a homebrew solution to receive email when one of my validators proposes a block.

## Installation

1. Clone the repository or download the script files.

2. Install the required Python packages:
`pip install requests python-dotenv`

3. Create a `.env` file in the same directory as the script and provide the following information:
```
SENDER_EMAIL=myemail@changethis.com
RECEIVER_EMAIL=receiveremail@changethis.com
PASSWORD=smtppassword
SMTP_SERVER=smtp.changethis.com
SMTP_PORT=587
```

4. Replace the placeholders with your actual email credentials and SMTP server details.

5. Create a `validators.txt` file and list the validator indices you want to monitor, one per line. For example:
```
1
2
3
```


## Usage

To start monitoring the Ethereum blockchain and receive email notifications, run the script:
`python scan.py`

The script will continuously check for new finalized blocks. When a block is proposed by a validator index listed in the `validators.txt` file, an email notification will be sent to the specified receiver email address.

The email notification includes the following information:
- Proposer index
- Block number
- MEV reward (in ETH)
- Block reward (in ETH)

## Disclaimer

This script is provided as-is and may require modifications to suit your specific use case. Make sure to review and understand the code before running it in a production environment. The authors are not responsible for any damages or losses incurred while using this script.
