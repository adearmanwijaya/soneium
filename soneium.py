import time
from web3 import Web3
from colorama import init, Fore, Style

# Initialize colorama (auto-reset colors after each print)
init(autoreset=True)

# --- Configuration ---
rpc_url = "https://rpc.soneium.org"
chain_id = 1868  # Soneium mainnet chain ID (adjust if needed)
contract_address = Web3.to_checksum_address("0xDEf357D505690F1b0032a74C3b581163c23d1535")
tx_value = int(0.00001 * 10**18)  # 0.00001 ETH in Wei
gas_limit = 500000  # Adjust if necessary

# Provided raw data containing a hard-coded address to be replaced.
# The substring "7f7b76f0473c8cc9d4db962847ec2a63ff9a708d" will be replaced with the sender address from the private key.
data_ghalibie = (
    "0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000124c04b8d59000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000007f7b76f0473c8cc9d4db962847ec2a63ff9a708d0000000000000000000000000000000000000000000000000000000067bf51cd000000000000000000000000000000000000000000000000000009184e72a0000000000000000000000000000000000000000000000000000828697649fc92cd000000000000000000000000000000000000000000000000000000000000002b4200000000000000000000000000000000000006000bb82cae934a1e84f693fbb78ca5ed3b0a689325944100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000412210e8a00000000000000000000000000000000000000000000000000000000"
)

# --- Connect to Soneium ---
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    print(Fore.RED + "❌ Could not connect to the Soneium node.")
    exit()
else:
    print(Fore.GREEN + "🚀 Connected to Soneium node.")

# --- Load Private Keys from file ---
try:
    with open("private_keys.txt", "r") as f:
        private_keys = [line.strip() for line in f if line.strip()]
    if not private_keys:
        print(Fore.RED + "❌ No private keys found in private_keys.txt.")
        exit()
except Exception as e:
    print(Fore.RED + f"❌ Failed to load private keys: {e}")
    exit()

# --- Process each private key ---
for pk in private_keys:
    account = web3.eth.account.from_key(pk)
    sender_addr = Web3.to_checksum_address(account.address)
    print(Style.BRIGHT + Fore.CYAN + f"\nProcessing account: {sender_addr}")

    # Check the total transaction count for the address
    tx_count = web3.eth.get_transaction_count(sender_addr)
    print(Fore.YELLOW + f"Total transactions so far: {tx_count}")
    if tx_count > 45:
        print(Fore.MAGENTA + "⚠️  Address has more than 45 transactions. Skipping to next key.")
        continue

    # Replace the hardcoded address in the raw data with the sender's address (without '0x' and in lowercase)
    replacement = sender_addr[2:].lower()  # remove 0x and lowercase
    raw_data = data_ghalibie.replace("7f7b76f0473c8cc9d4db962847ec2a63ff9a708d", replacement)

    # Get the starting nonce for this account
    nonce_start = tx_count

    # Send 50 transactions for this account
    for i in range(50):
        nonce = nonce_start + i
        tx = {
            "nonce": nonce,
            "to": contract_address,
            "value": tx_value,
            "gas": gas_limit,
            "gasPrice": web3.eth.gas_price,
            "data": raw_data,
            "chainId": chain_id
        }
        try:
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=pk)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(Fore.YELLOW + f"📤 Transaction {i+1}/50 sent. Hash: 0x{tx_hash.hex()}")

            # Wait for receipt
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            status = receipt.get("status", 0)
            if status == 1:
                print(Fore.GREEN + f"✅ Transaction {i+1}/50 succeeded")
            else:
                print(Fore.RED + f"❌ Transaction {i+1}/50 failed (status: {status}).")
            # Optionally, add a short delay between transactions
            time.sleep(1)
        except Exception as e:
            print(Fore.RED + f"❌ Error sending transaction {i+1}/50: {e}")
            continue

print(Style.BRIGHT + Fore.MAGENTA + "\nAll transactions processed!")
