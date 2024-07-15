import time
import requests
from web3 import Web3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
import os

load_dotenv()

def get_latest_finalized_block():
    url = 'https://beaconcha.in/api/v1/epoch/finalized/slots'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for unsuccessful status codes
        data = response.json()
        
        if data['status'] == 'OK':
            latest_block = max(data['data'], key=lambda block: block['exec_block_number'] if block['exec_block_number'] else 0)
            return latest_block['exec_block_number']
        else:
            print(f"Error: {data['status']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching data: {e}")
        return None

start_block = get_latest_finalized_block()

# Define the throttling intervals (in seconds)
WEB3_THROTTLE_INTERVAL = 1
BEACONCHAIN_THROTTLE_INTERVAL = 1

# Initialize the last request timestamps
beaconchain_last_request_time = 0

def get_beaconchain_block_info(block_number):
    global beaconchain_last_request_time
    current_time = time.time()
    if current_time - beaconchain_last_request_time < BEACONCHAIN_THROTTLE_INTERVAL:
        time.sleep(BEACONCHAIN_THROTTLE_INTERVAL - (current_time - beaconchain_last_request_time))
    url = f"https://beaconcha.in/api/v1/execution/block/{block_number}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    beaconchain_last_request_time = time.time()
    return response.json()

def send_email(proposer_index, block_number, block_mev_reward, block_reward):
    # Email configuration
    sender_email = os.environ["SENDER_EMAIL"]
    receiver_email = os.environ["RECEIVER_EMAIL"]
    password = os.environ["PASSWORD"]
    smtp_server = os.environ["SMTP_SERVER"]
    smtp_port = os.environ["SMTP_PORT"]

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"Block Proposal Notification - Block #{block_number}"

    # Add body to the email
    body = f"Proposer index: {proposer_index}\n"
    body += f"Block number: {block_number}\n"
    body += f"MEV reward: {block_mev_reward:.18f} ETH\n"
    body += f"Block reward: {block_reward:.18f} ETH"
    message.attach(MIMEText(body, "plain"))

    # Create a secure SSL/TLS connection
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, password)

    # Send the email
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)

    # Close the SMTP connection
    server.quit()

# Read validator indices from a text file
with open('validators.txt', 'r') as file:
    validator_indices = set(map(int, file.read().splitlines()))
    print(f'Loaded {len(validator_indices)} validator indices.')

while True:
    try:
        # Wait for a certain interval before checking for new finalized blocks again
        time.sleep(30)  # Wait for 30 seconds, adjust as needed

        # Get the latest finalized block number
        latest_finalized_block = get_latest_finalized_block()

        # Check if there are new finalized blocks
        if latest_finalized_block > start_block:
            # Retrieve and process the new finalized blocks
            last_block_checked = start_block
            for block_number in range(start_block + 1, latest_finalized_block + 1):
                # Process the block data as needed
                print(f"New finalized block: {block_number}")

                # Get additional block info from beaconcha.in
                beaconchain_block_info = get_beaconchain_block_info(block_number)
                print(f"Beaconcha.in block info: {beaconchain_block_info}")
                
                # Check if the proposer index is in the validator_indices set
                try:
                  proposer_index = beaconchain_block_info['data'][0]['posConsensus']['proposerIndex']
                except:
                  break
                last_block_checked = block_number
                if proposer_index in validator_indices:
                    print(f"Proposer index {proposer_index} is in the validator indices.")
                    
                    # Extract MEV and block reward from beaconcha.in block info
                    block_mev_reward = beaconchain_block_info['data'][0]['blockMevReward'] / 10**18  # Convert to ETH
                    block_reward = beaconchain_block_info['data'][0]['blockReward'] / 10**18  # Convert to ETH
                    
                    send_email(proposer_index, block_number, block_mev_reward, block_reward)  # Send email notification
                else:
                    print(f"Proposer index {proposer_index} is not in the validator indices.")

            # Update the starting block number
            start_block = last_block_checked
    except Exception as e:
        print(f"Error encountered: {e}")
        print("Retrying in 30 seconds...")
        continue
