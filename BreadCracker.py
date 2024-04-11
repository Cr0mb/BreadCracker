import subprocess
import sys
import os
import platform
import requests
import logging
import time
from dotenv import load_dotenv
from bip_utils import (
    Bip39MnemonicGenerator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
    Bip39WordsNum,
)
import pyfiglet
import curses

LOG_FILE_NAME = "breadcracker.log"
ENV_FILE_NAME = "breadcracker.env"
WALLETS_FILE_NAME = "wallets_with_balance.txt"
wallets_scanned = 0

directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(directory, LOG_FILE_NAME)
env_file_path = os.path.join(directory, ENV_FILE_NAME)
wallets_file_path = os.path.join(directory, WALLETS_FILE_NAME)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),  # Log to a file
        logging.StreamHandler(sys.stdout),  # Log to standard output
    ],
)

if not os.path.exists(env_file_path):
    print("The breadcracker.env file does not exist. Let's create it.")
    etherscan_api_key = input("Enter your Etherscan API key: ").strip()

    with open(env_file_path, "w") as env_file:
        env_file.write(f"ETHERSCAN_API_KEY={etherscan_api_key}\n")

load_dotenv(env_file_path)
required_env_vars = ["ETHERSCAN_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

if os.environ.get("RUNNING_IN_NEW_CMD") != "TRUE":
    os.environ["RUNNING_IN_NEW_CMD"] = "TRUE"
    os_type = platform.system()
    if os_type == "Windows":
        subprocess.run(["cmd", "/k", f"python {__file__}"], shell=True)
    elif os_type == "Linux":
        subprocess.run(["python3", __file__])
    sys.exit()

def update_cmd_title():
    if platform.system() == "Windows":
        os.system(f"title Bread Cracker - Wallets Scanned: {wallets_scanned}")

def bip():
    return Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)

def bip44_ETH_wallet_from_seed(seed):
    seed_bytes = Bip39SeedGenerator(seed).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc_ctx = (
        bip44_mst_ctx.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )
    eth_address = bip44_acc_ctx.PublicKey().ToAddress()
    return eth_address

def bip44_BTC_seed_to_address(seed):
    seed_bytes = Bip39SeedGenerator(seed).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
    bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
    return bip44_addr_ctx.PublicKey().ToAddress()

def check_ETH_balance(address, etherscan_api_key, retries=3, delay=5):
    api_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={etherscan_api_key}"
    for attempt in range(retries):
        try:
            response = requests.get(api_url)
            data = response.json()
            if data["status"] == "1":
                balance = int(data["result"]) / 1e18
                return balance
            else:
                logging.error("Error getting balance: %s", data["message"])
                return 0
        except Exception as e:
            if attempt < retries - 1:
                logging.error(
                    f"Error checking balance, retrying in {delay} seconds: {str(e)}"
                )
                time.sleep(delay)
            else:
                logging.error("Error checking balance: %s", str(e))
                return 0

def check_BTC_balance(address, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(f"https://blockchain.info/balance?active={address}")
            data = response.json()
            balance = data[address]["final_balance"]
            return balance / 100000000
        except Exception as e:
            if attempt < retries - 1:
                logging.error(
                    f"Error checking balance, retrying in {delay} seconds: {str(e)}"
                )
                time.sleep(delay)
            else:
                logging.error("Error checking balance: %s", str(e))
                return 0

def write_to_file(seed, BTC_address, BTC_balance, ETH_address, ETH_balance):
    with open(wallets_file_path, "a") as f:
        log_message = f"Seed: {seed}\nAddress: {BTC_address}\nBalance: {BTC_balance} BTC\n\nEthereum Address: {ETH_address}\nBalance: {ETH_balance} ETH\n\n"
        f.write(log_message)
        logging.info(f"Written to file: {log_message}")

def main(stdscr):
    global wallets_scanned
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Set black on white
    stdscr.clear()
    stdscr.bkgd(' ', curses.color_pair(1))  # Set background color

    while True:
        seed = bip()
        BTC_address = bip44_BTC_seed_to_address(seed)
        BTC_balance = check_BTC_balance(BTC_address)
        ETH_address = bip44_ETH_wallet_from_seed(seed)
        etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
        if not etherscan_api_key:
            raise ValueError(
                "The Etherscan API key must be set in the environment variables."
            )
        ETH_balance = check_ETH_balance(ETH_address, etherscan_api_key)

        bread_cracker = pyfiglet.figlet_format("Bread Cracker", font="doom")
        stdscr.addstr(0, 0, bread_cracker, curses.color_pair(1))

        wallet_info = f"Seed: {seed}\nBTC address: {BTC_address}\nBTC balance: {BTC_balance} BTC\nETH address: {ETH_address}\nETH balance: {ETH_balance} ETH\n"
        stdscr.addstr(6, 0, wallet_info, curses.color_pair(1))

        update_cmd_title()
        wallets_scanned += 1
        if BTC_balance > 0 or ETH_balance > 0:
            logging.info("(!) Wallet with balance found!")
            write_to_file(seed, BTC_address, BTC_balance, ETH_address, ETH_balance)
        stdscr.refresh()
        time.sleep(0.01)

if __name__ == "__main__":
    curses.wrapper(main)





