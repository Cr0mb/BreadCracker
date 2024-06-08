![image](https://github.com/Cr0mb/BreadCracker/assets/137664526/50a58a13-0134-4516-b205-c9044cbd17b4)

[Video](https://www.youtube.com/watch?v=X346wqB37vw&t=736s)

```Direct Url: https://www.youtube.com/watch?v=X346wqB37vw&t=736s```

# Bread Cracker
Bread Cracker is a Python script designed to scan for cryptocurrency wallets derived from mnemonic seeds and check their balances. 
It supports both Bitcoin (BTC) and Ethereum (ETH) wallets. The script utilizes the BIP-39 standard for mnemonic generation and BIP-44 for wallet derivation.

## Features
- Mnemonic Generation: Generates BIP-39 compliant mnemonic seeds.
- Wallet Derivation: Derives BTC and ETH wallet addresses from mnemonic seeds.
- Balance Checking: Checks the balances of BTC and ETH wallets using blockchain APIs.
- Logging: Logs wallet information and balance checks.
- Command-Line Interface: Terminal-based interface for easy operation.
## Prerequisites
Before running the script, ensure you have the following dependencies installed:

- Python 3.x
- requests
- logging
- dotenv
- bip_utils
- pyfiglet
- curses
You can install the dependencies using pip:
```
pip install requests logging python-dotenv bip-utils pyfiglet
```
## Usage
1. Clone this repository to your local machine:
```
git clone https://github.com/Cr0mb/BreadCracker.git
```
2. Navigate to the directory where you cloned the repository:
```
cd BreadCracker
```
3. Set up your environment variables by creating a file named breadcracker.env with your Etherscan API key:
```
ETHERSCAN_API_KEY=your_etherscan_api_key
```
4. Run the script:
```
python BreadCracker.py
```
5. The script will continuously scan for wallets and display information about found wallets and their balances.

## Notes
- Ensure that you have a reliable internet connection for balance checking.
- Check the logs (breadcracker.log) for detailed information about scanned wallets and balance checks.

