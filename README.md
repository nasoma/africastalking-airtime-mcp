[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/nasoma-africastalking-airtime-mcp-badge.png)](https://mseep.ai/app/nasoma-africastalking-airtime-mcp)

# Africa's Talking Airtime MCP
[![smithery badge](https://smithery.ai/badge/@nasoma/africastalking-airtime-mcp)](https://smithery.ai/server/@nasoma/africastalking-airtime-mcp)

This project implements a **Model Context Protocol (MCP) server** for managing airtime transactions using the **Africa's Talking API**. It provides a set of tools to check account balance, send airtime, view recent top-up transactions, sum the amounts of recent top-ups, and count top-ups for a specific phone number. The application uses SQLite to store transaction data and supports African countries supported by Africa's Talking Airtime Service with proper phone number formatting.

<a href="https://glama.ai/mcp/servers/@nasoma/africastalking-airtime-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@nasoma/africastalking-airtime-mcp/badge" />

  [![Verified on MseeP](https://mseep.ai/badge.svg)](https://mseep.ai/app/f5bd5826-abe0-421e-ac2b-6a5daeaa384a)

## Description

The **Africa's Talking Airtime MCP Server** integrates with the Africa's Talking Airtime API to facilitate airtime transfers. Key features include:

- Sending airtime to specified phone numbers.
- Storing transaction details in a SQLite database.
- Retrieving and summarizing transaction history.
- Checking the account balance on Africa's Talking.

The application supports the countries where Africa's Talking Airtime service is supported.

## Installation

### Installing via Smithery

To install Africa's Talking Airtime Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@nasoma/africastalking-airtime-mcp):

```bash
npx -y @smithery/cli install @nasoma/africastalking-airtime-mcp --client claude
```

### Prerequisites

1. Python 3.10 or higher

2. [Install uv](https://docs.astral.sh/uv/#highlights)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Follow these steps to set up and run the project locally:

1. Clone the repository:
```bash
git clone https://github.com/nasoma/africastalking-airtime-mcp.git
cd africastalking-airtime-mcp
```

2. Set up the virtual environment and install dependencies by running:
```bash
uv sync 
```
3. You are good to go!

## Using with AI Tools

### With Claude Desktop

Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "Airtime Server": {
      "command": "{{PATH_TO_UV}}", // Run `which uv` and place the output here
      "args": [
        "--directory",
        "{{PATH_TO_PROJECT}}", // cd into the repo, run `pwd` and enter the output here
        "run",
        "main.py"
      ],
      "env": {
        "username": "your_africastalking_username",
        "api_key": "your_africastalking_api_key",
        "country":"your_country", # e.g kenya, uganda, dr congo, rwanda, south africa
        "currency_code":"currency-code"  # e.g. KES, UGX, NGN
      }
    }
  }
}
```
### With Goose

[Goose](https://block.github.io/goose/) is a good option if you want to use your preferred LLM and supply an API key.

- Install Goose.
- Open the settings panel and add a custom extension (MCP Server).
- Give your extension a name. Type is STDIO.
- Add the command. Save changes.
![Goose Demo](goose-demo1.png)
- Add your environment variables: `username`, `api_key`, `currency_code` and `country`.
- Save changes.

![Goose Demo2](goose-demo2.png)

## Tools Descriptions

The MCP provides the following tools for managing airtime transactions:

1. **check_balance**:
   - **Description**: Retrieves the current airtime balance for your Africa's Talking account.
   - **Usage**: `check_balance()`
   - **Output**: Returns the account balance (e.g., "Account Balance: KES 1234.00") or an error message if the balance cannot be fetched.

2. **load_airtime**:
   - **Description**: Sends airtime to a specified phone number and saves the transaction in the database.
   - **Parameters**:
     - `phone_number`: The recipient's phone number (e.g., "0712345678" or "+254712345678").
     - `amount`: The amount of airtime to send (e.g., 100).
     - `currency_code`: The currency code (e.g., "KES").
   - **Usage**: `load_airtime("0712345678", 100.00, "KES")`
   - **Output**: Confirms success (e.g., "Successfully sent KES 100.00 airtime to +254712345678") or reports an error.

3. **get_last_topups**:
   - **Description**: Retrieves the last `N` airtime top-up transactions from the database.
   - **Parameters**:
     - `limit`: Number of transactions to retrieve (default: 3).
   - **Usage**: `get_last_topups(3)`
   - **Output**: Lists recent transactions (e.g., "Last 3 top-up transactions: ...") or indicates no transactions found.

4. **sum_last_n_topups**:
   - **Description**: Calculates the total amount of the last `N` successful top-ups, ensuring they use the same currency.
   - **Parameters**:
     - `n`: Number of transactions to sum (default: 3).
   - **Usage**: `sum_last_n_topups(3)`
   - **Output**: Returns the sum (e.g., "Sum of last 3 successful top-ups: KES 300.00") or an error if currencies differ.

5. **count_topups_by_number**:
   - **Description**: Counts the number of successful top-ups to a specific phone number.
   - **Parameters**:
     - `phone_number`: The phone number to query (e.g., "0712345678").
   - **Usage**: `count_topups_by_number("0712345678")`
   - **Output**: Returns the count (e.g., "Number of successful top-ups to +254712345678: 5") or an error.

## Example prompts

The following are example questions or commands users can ask the AI to interact with the Africa's Talking Airtime MCP, based on the available tools:

#### Check Account Balance
- What is my Africa's Talking account balance?
- Can you show me the current balance?
- Check my airtime balance.

#### Send Airtime
- Send 100 KES airtime to 0712345678.
- Topup my 0712345678 with 60.
- Load 50 NGN to +2348012345678.
- Can you top up 200 UGX to 0755123456?

#### View Recent Top-Ups
- Show me the last 3 airtime transactions.
- What are my most recent top-ups?
- List the last 5 airtime top-ups.

#### Sum Recent Top-Ups
- What is the total of my last 3 top-ups?
- Sum the amounts of my last 4 airtime transactions.
- How much have I sent in my last 5 top-ups?

#### Count Top-Ups by Phone Number
- How many times have I topped up 0712345678?
- Count the top-ups to +254712345678.
- Tell me how many successful top-ups were made to 0755123456.

## Notes

- Ensure your Africa's Talking account is funded to send airtime.
- Phone numbers are automatically formatted based on the `country` variable set in the client or on `claude_desktop_config.json`.
- The SQLite database (`airtime_transactions.db`) is created in the project directory upon initialization.
- Works best with models that support tool calling, e.g `Claude 3.7 Sonnet`. If you are price conscious `GPT-4.1 Nano` is a good, cheaper option when used with clients like Goose.

## 🙏 Credits

*   Africa's Talking API [Africa's Talking Documentation](https://developers.africastalking.com/).
