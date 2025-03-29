# Solana Staking Value Analyzer

A comprehensive Python tool for analyzing, optimizing, and visualizing Solana staking returns.

![Solana](https://solana.com/src/img/branding/solanaLogoMark.svg)

## Overview

This application helps Solana holders maximize value from their staking activities by providing data-driven insights, validator recommendations, and visual projections of potential returns.

## Features

- 💰 **Real-time SOL price data** via CoinGecko API integration
- 📊 **Detailed staking return calculations** with compound interest modeling
- 🔍 **Validator analysis and scoring** based on commission, APY, and performance metrics
- 📈 **Visual projections** of SOL growth and USD value over time
- 📑 **Comprehensive staking reports** with actionable recommendations
- 🔄 **Multi-scenario analysis** with low, average, and high return projections

## Installation

```bash
# Clone this repository
git clone https://github.com/ibuilder/sol-value-max.git
cd sol-value-max

# Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

## Requirements

Create a `requirements.txt` file with the following dependencies:

```
requests>=2.28.1
pandas>=1.5.0
matplotlib>=3.6.0
```

## Usage

### Basic Usage

```bash
python solana_staking_analyzer.py --amount 100 --days 365
```

### Command-line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--amount` | Amount of SOL to analyze | 10.0 |
| `--days` | Time period in days | 365 |
| `--api-key` | Optional Solana API key for enhanced data access | None |

### Example

```bash
python solana_staking_analyzer.py --amount 500 --days 730
```

This command will analyze potential returns for staking 500 SOL over a 2-year period.

## Output

The analyzer generates two main outputs:

1. **Markdown Report** (`solana_staking_report_YYYYMMDD_HHMMSS.md`):
   - Initial investment details
   - Current network statistics
   - Projected returns across multiple scenarios
   - Top validator recommendations
   - Strategic staking recommendations

2. **Visualization Chart** (`solana_staking_projection_YYYYMMDD_HHMMSS.png`):
   - SOL growth projection over time
   - USD value projection over time

## API Keys

While the tool works without API keys, you can enhance its capabilities by:

1. Getting a free API key from [Solscan](https://public-api.solscan.io/)
2. Setting it as an environment variable:
   ```bash
   export SOLANA_API_KEY=your_api_key_here
   ```
   
   Or passing it directly:
   ```bash
   python solana_staking_analyzer.py --amount 100 --api-key your_api_key_here
   ```

## Example Report

```markdown
# Solana Staking Analysis Report
Generated on: 2025-03-29 12:34:56

## Initial Investment
- Amount: 100 SOL
- Current Value: $3,250.00 USD
- Time Period: 365 days

## Network Statistics
- Current Inflation Rate: 7.50%
- Current SOL Price: $32.50 USD

## Projected Returns

### Low Estimate (High Commission of 10%)
- APY: 6.75%
- SOL after 365 days: 106.97
- SOL earned: 6.97
- Projected Value: $3,476.52 USD
- ROI: 6.97%

### Average Estimate (Average Commission of 5%)
- APY: 7.13%
- SOL after 365 days: 107.37
- SOL earned: 7.37
- Projected Value: $3,489.52 USD
- ROI: 7.37%

### High Estimate (Low Commission of 0%)
- APY: 7.50%
- SOL after 365 days: 107.79
- SOL earned: 7.79
- Projected Value: $3,503.17 USD
- ROI: 7.79%

## Top Recommended Validators
...
```

## Advanced Usage

### Integration with Other Systems

The `SolanaStakingAnalyzer` class can be imported and used in other Python applications:

```python
from solana_staking_analyzer import SolanaStakingAnalyzer

# Initialize the analyzer
analyzer = SolanaStakingAnalyzer()

# Get current SOL price
sol_price = analyzer.get_current_sol_price()

# Find optimal validators
top_validators = analyzer.find_optimal_validators(top_n=3)

# Calculate potential returns
returns = analyzer.calculate_staking_returns(
    sol_amount=100, 
    apy=7.5, 
    time_period_days=365
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool provides projections based on current data and historical performance. Actual staking returns may vary due to market conditions, validator performance, and Solana network changes. This is not financial advice.
