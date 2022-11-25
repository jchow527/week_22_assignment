import os
import json
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from hexbytes import HexBytes

load_dotenv('ttf.env')

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Set the contract address (this is the address of the deployed contract)
tokentimefund_contract_address = os.getenv("TOKENTIMEFUND_ADDRESS")
tokentimefundcrowdsale_contract_address = os.getenv("TOKENTIMEFUNDCROWDSALE_ADDRESS")

################################################################################
# Contract Helper function:
# 1. Loads the contract once using cache
# 2. Connects to the contract using the contract address and ABI
################################################################################


@st.cache(allow_output_mutation=True)
def load_contract():

    # Load the TokenTimeFund contract ABI
    with open(Path('./contracts/compiled/TokenTimeFund_abi.json')) as f:
        tokentimefund_contract_abi = json.load(f)

    # Load the TokenTimeFundCrowdsale contract ABI
    with open(Path('./contracts/compiled/TokenTimeFundCrowdsale_abi.json')) as f:
        tokentimefundcrowdsale_contract_abi = json.load(f)       

    # Get the tokentimefund contract
    tokentimefund_contract = w3.eth.contract(
        address=tokentimefund_contract_address,
        abi=tokentimefund_contract_abi
    )

    # Get the tokentimefundcrowdsale contract
    tokentimefundcrowdsale_contract = w3.eth.contract(
        address=tokentimefundcrowdsale_contract_address,
        abi=tokentimefundcrowdsale_contract_abi
    )   

    return tokentimefund_contract, tokentimefundcrowdsale_contract

# Load the contracts
tokentimefund_contract, tokentimefundcrowdsale_contract = load_contract()


# Use of accounts from Ganache:
# Account 0,1 - not used
# Account 2 - for deploying contracts using Remix and Metamask
# Account 3 - for Wei raised
# Account 4 - for TTF tokens bought back from investors, to be burnt
# Account 5 to 9 - Investors accounts
accounts = w3.eth.accounts
investors_accounts = accounts[5:10]

# Load AUM Wallet (acccounts[3]) address and private key
aum_wallet_address = accounts[3]
aum_wallet_private_key = os.getenv('AUMWALLET_PRIVATE_KEY')

# Set burn wallet address
burn_wallet_address = accounts[4]

# Show title of webpage
st.sidebar.title("Token Time Fund")

# Show fund information on sidebar
st.sidebar.markdown("## Token Time Fund Information")

# Show total TTF token supply
st.sidebar.write('Total TTF token supply:')
total_supply_placeholder = st.sidebar.empty()
total_supply = tokentimefund_contract.functions.totalSupply().call()
total_supply_placeholder.markdown('{:,}'.format(total_supply))
st.sidebar.write(tokentimefund_contract_address)
st.sidebar.write('')
st.sidebar.write('')

# Show total wei raised in sidebar
st.sidebar.write('Asset Under Management (in Wei):')
aum_placeholder = st.sidebar.empty()
# aum = tokentimefundcrowdsale_contract.functions.weiRaised().call()
aum = int(w3.eth.getBalance(aum_wallet_address)) - 100000000000000000000
aum_placeholder.markdown('{:,}'.format(aum))
st.sidebar.write(aum_wallet_address)

# Show amount of tokens in burn wallet
st.sidebar.write('')
st.sidebar.write('')
tokens_burn_wallet = tokentimefund_contract.functions.balanceOf(burn_wallet_address).call()
st.sidebar.write('Number of tokens in burn wallet:')
burn_balance_placeholder = st.sidebar.empty()
burn_balance_placeholder.markdown('{}'.format(tokens_burn_wallet))
st.sidebar.write(burn_wallet_address)

st.sidebar.markdown("---")

tokens_burn_placeholder = st.sidebar.empty()
tokens_amount_to_burn = tokens_burn_placeholder.text_input("Enter number of tokens to burn:", value="0")
if st.sidebar.button("Burn"):
    tx_hash = tokentimefund_contract.functions.burn(int(tokens_amount_to_burn)).transact({'from': burn_wallet_address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.sidebar.write('Blockchain transaction receipt:', tx_receipt)

    # Update displayed information
    total_supply = tokentimefund_contract.functions.totalSupply().call()
    total_supply_placeholder.markdown('{:,}'.format(total_supply))
    tokens_burn_wallet = tokentimefund_contract.functions.balanceOf(burn_wallet_address).call()
    burn_balance_placeholder.markdown('{}'.format(tokens_burn_wallet))


# Investors panel

st.write('Rate:  1 ETH = 1000000000000000000 wei,  1 token = 1 wei')
st.write('')
st.write('')

address = st.selectbox("Select Investor Account:", options=investors_accounts)
account_balance = w3.eth.getBalance(address)
account_number = w3.eth.accounts.index(address)

# wei balance streamlit placeholder
wei_balance_placeholder = st.empty() 

# ttf balance streamlit placeholder
ttf_balance_placeholder = st.empty()

wei_balance_placeholder.markdown('Wei balance: {}'.format(account_balance))
token_balance = tokentimefund_contract.functions.balanceOf(address).call()
ttf_balance_placeholder.markdown('TTF token balance: {}'.format(token_balance))

if st.button("Update Page"):
    x = 1

st.markdown("---")


# Buy tokens

buy_input_placeholder = st.empty()  # placeholder for text input
tokens_amount_to_buy = buy_input_placeholder.text_input("Enter number of tokens to buy:", value="0")
if st.button("Buy"):

    tx_hash = tokentimefundcrowdsale_contract.functions.buyTokens(address).transact({'from': address, 'value':int(tokens_amount_to_buy)})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write('Blockchain transaction receipt:', tx_receipt)

    ## Update information on webpage
    total_supply = tokentimefund_contract.functions.totalSupply().call()
    total_supply_placeholder.markdown('{:,}'.format(total_supply))
    # total_wei_raised = tokentimefundcrowdsale_contract.functions.weiRaised().call()
    aum = int(w3.eth.getBalance(aum_wallet_address)) - 100000000000000000000
    aum_placeholder.markdown('{:,}'.format(aum))
    account_balance = w3.eth.getBalance(address)
    wei_balance_placeholder.markdown('Wei balance: {}'.format(account_balance))
    token_balance = tokentimefund_contract.functions.balanceOf(address).call()
    ttf_balance_placeholder.markdown('TTF token balance: {}'.format(token_balance))

st.markdown("---")

# Sell tokens

sell_input_placeholder = st.empty() # placeholder for text input
tokens_amount_to_sell = sell_input_placeholder.text_input("Enter number of tokens to sell:", value="0")
if st.button("Sell"):

    ## transfer tokens from investor wallet to AUM wallet
    tx_hash = tokentimefund_contract.functions.transfer(accounts[4], int(tokens_amount_to_sell)).transact({'from': address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write('Blockchain transaction receipt:', tx_receipt)

    ## transfer wei from AUM wallet to investor wallet

    # Set gas price strategy
    w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

    # build a transaction in a dictionary
    raw_tx = {
        'to': address,
        'from': aum_wallet_address,
        'value': int(tokens_amount_to_sell),
        'gas': w3.eth.estimateGas({"to": address, "from": aum_wallet_address, "value": int(tokens_amount_to_sell)}),
        'gasPrice': 0,
        'nonce': w3.eth.getTransactionCount(aum_wallet_address)
    }


    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(raw_tx, aum_wallet_private_key)

    # send transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # display transaction hash
    st.write(tx_hash)


    ## Update information on webpage
    aum = int(w3.eth.getBalance(aum_wallet_address)) - 100000000000000000000
    aum_placeholder.markdown('{:,}'.format(aum))
    tokens_burn_wallet = tokentimefund_contract.functions.balanceOf(accounts[4]).call()
    burn_balance_placeholder.markdown('{}'.format(tokens_burn_wallet))
    account_balance = w3.eth.getBalance(address)
    wei_balance_placeholder.markdown('Wei balance: {}'.format(account_balance))
    token_balance = tokentimefund_contract.functions.balanceOf(address).call()
    ttf_balance_placeholder.markdown('TTF token balance: {}'.format(token_balance))



### TO DO
# 1. simulate increase or decrease of AUM wallet due to portforlio performance by moving wei in or out of AUM wallet
# 2. change the value of tokens by changing the wei-token rate
