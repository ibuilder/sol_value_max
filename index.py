import os
import json
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import argparse


class SolanaStakingAnalyzer:
    """A tool to analyze and optimize value from Solana staking."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer with API key if provided."""
        self.api_key = api_key or os.environ.get("SOLANA_API_KEY")
        self.base_url = "https://api.solscan.io/v1"
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def get_current_sol_price(self) -> float:
        """Get the current price of SOL in USD."""
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "solana",
            "vs_currencies": "usd"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data["solana"]["usd"]
        except Exception as e:
            print(f"Error fetching SOL price: {e}")
            return 0.0
    
    def get_network_stats(self) -> Dict:
        """Fetch current Solana network statistics."""
        url = f"{self.base_url}/network/stats"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching network stats: {e}")
            return {}
    
    def get_validators(self, limit: int = 100) -> List[Dict]:
        """Fetch information about Solana validators."""
        url = f"{self.base_url}/validators"
        params = {"limit": limit, "offset": 0}
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            print(f"Error fetching validators: {e}")
            return []
    
    def calculate_apy(self, inflation_rate: float, validator_commission: float = 0.0) -> float:
        """Calculate the APY for Solana staking based on inflation rate and validator commission."""
        # Most validator commissions range from 0% to 10%
        net_inflation = inflation_rate * (1 - validator_commission)
        # Solana's target stake participation is around 80%
        stake_participation_rate = 0.8
        # If the actual participation is less, APY is higher
        estimated_apy = net_inflation / stake_participation_rate
        return estimated_apy * 100  # Convert to percentage
    
    def calculate_staking_returns(self, sol_amount: float, apy: float, time_period_days: int) -> Dict:
        """Calculate potential returns from staking SOL over a period of time."""
        current_sol_price = self.get_current_sol_price()
        
        # Calculate returns
        apy_decimal = apy / 100
        time_period_years = time_period_days / 365
        
        # Compound daily interest formula
        # A = P(1 + r/n)^(nt)
        compounds_per_year = 365  # Daily compounding
        final_sol = sol_amount * (1 + (apy_decimal / compounds_per_year)) ** (compounds_per_year * time_period_years)
        
        sol_earned = final_sol - sol_amount
        current_value_usd = sol_amount * current_sol_price
        projected_value_usd = final_sol * current_sol_price  # Using current price as estimate
        
        return {
            "initial_sol": sol_amount,
            "final_sol": final_sol,
            "sol_earned": sol_earned,
            "current_value_usd": current_value_usd,
            "projected_value_usd": projected_value_usd,
            "roi_percentage": (sol_earned / sol_amount) * 100
        }
    
    def find_optimal_validators(self, top_n: int = 5) -> List[Dict]:
        """Find the optimal validators for staking based on performance and commission."""
        validators = self.get_validators(limit=200)
        
        # Create DataFrame for analysis
        df = pd.DataFrame(validators)
        if df.empty:
            return []
        
        # Clean and prepare data
        try:
            # Convert relevant fields to numeric
            for col in ['commission', 'apy', 'totalActiveStake', 'creditScore']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate a score for each validator
            # Lower commission, higher APY, and higher credit score are better
            if 'commission' in df.columns and 'apy' in df.columns and 'creditScore' in df.columns:
                df['score'] = (
                    df['apy'] * 0.4 +  # 40% weight to APY
                    (100 - df['commission']) * 0.3 +  # 30% weight to low commission
                    df['creditScore'] * 0.3  # 30% weight to credit score
                )
                
                # Sort by score and get top N validators
                top_validators = df.sort_values('score', ascending=False).head(top_n).to_dict('records')
                return top_validators
            else:
                print("Required columns not found in validator data")
                return []
        except Exception as e:
            print(f"Error analyzing validators: {e}")
            return []
    
    def plot_staking_projection(self, sol_amount: float, apy: float, days: int = 365) -> str:
        """Generate a plot showing projected staking returns over time."""
        # Generate data points for every 30 days
        intervals = range(0, days + 1, 30)
        if intervals[-1] != days:
            intervals = list(intervals) + [days]
        
        sol_values = []
        usd_values = []
        current_sol_price = self.get_current_sol_price()
        
        for day in intervals:
            returns = self.calculate_staking_returns(sol_amount, apy, day)
            sol_values.append(returns["final_sol"])
            usd_values.append(returns["projected_value_usd"])
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Plot SOL growth
        ax1.plot(intervals, sol_values, marker='o', linestyle='-', color='#00FFA3')
        ax1.set_title('Projected SOL Growth Over Time', fontsize=14)
        ax1.set_xlabel('Days', fontsize=12)
        ax1.set_ylabel('SOL Amount', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.fill_between(intervals, sol_values, sol_amount, alpha=0.3, color='#00FFA3')
        
        # Plot USD value
        ax2.plot(intervals, usd_values, marker='o', linestyle='-', color='#2563EB')
        ax2.set_title('Projected USD Value Over Time', fontsize=14)
        ax2.set_xlabel('Days', fontsize=12)
        ax2.set_ylabel('USD Value', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.fill_between(intervals, usd_values, sol_amount * current_sol_price, alpha=0.3, color='#2563EB')
        
        plt.tight_layout()
        
        # Save plot to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"solana_staking_projection_{timestamp}.png"
        plt.savefig(filename)
        plt.close()
        
        return filename
    
    def compare_validators(self, validators: List[Dict]) -> pd.DataFrame:
        """Compare different validators and their performance metrics."""
        if not validators:
            return pd.DataFrame()
        
        df = pd.DataFrame(validators)
        
        # Select relevant columns for comparison
        columns_to_show = [
            'name', 'votePubkey', 'commission', 'apy', 
            'totalActiveStake', 'creditScore', 'score'
        ]
        
        # Filter columns that exist in the dataframe
        existing_columns = [col for col in columns_to_show if col in df.columns]
        
        # Format numbers for better readability
        if 'totalActiveStake' in df.columns:
            df['totalActiveStake'] = df['totalActiveStake'] / 1_000_000_000  # Convert to billions
            df['totalActiveStake'] = df['totalActiveStake'].round(2).astype(str) + " B SOL"
        
        if 'commission' in df.columns:
            df['commission'] = df['commission'].round(1).astype(str) + "%"
            
        if 'apy' in df.columns:
            df['apy'] = df['apy'].round(2).astype(str) + "%"
        
        return df[existing_columns]
    
    def generate_staking_report(self, sol_amount: float, time_period_days: int = 365) -> str:
        """Generate a comprehensive staking report with recommendations."""
        # Get network inflation rate
        network_stats = self.get_network_stats()
        inflation_rate = network_stats.get("inflation", 0.08)  # Default to 8% if not available
        
        # Find optimal validators
        top_validators = self.find_optimal_validators(5)
        
        # Calculate returns for different scenarios
        low_commission = 0.0
        avg_commission = 0.05
        high_commission = 0.10
        
        low_apy = self.calculate_apy(inflation_rate, high_commission)
        avg_apy = self.calculate_apy(inflation_rate, avg_commission)
        high_apy = self.calculate_apy(inflation_rate, low_commission)
        
        low_returns = self.calculate_staking_returns(sol_amount, low_apy, time_period_days)
        avg_returns = self.calculate_staking_returns(sol_amount, avg_apy, time_period_days)
        high_returns = self.calculate_staking_returns(sol_amount, high_apy, time_period_days)
        
        # Generate plots
        plot_filename = self.plot_staking_projection(sol_amount, avg_apy, time_period_days)
        
        # Create report content
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""
        # Solana Staking Analysis Report
        Generated on: {current_time}
        
        ## Initial Investment
        - Amount: {sol_amount} SOL
        - Current Value: ${low_returns['current_value_usd']:.2f} USD
        - Time Period: {time_period_days} days
        
        ## Network Statistics
        - Current Inflation Rate: {inflation_rate * 100:.2f}%
        - Current SOL Price: ${self.get_current_sol_price():.2f} USD
        
        ## Projected Returns
        
        ### Low Estimate (High Commission of 10%)
        - APY: {low_apy:.2f}%
        - SOL after {time_period_days} days: {low_returns['final_sol']:.4f}
        - SOL earned: {low_returns['sol_earned']:.4f}
        - Projected Value: ${low_returns['projected_value_usd']:.2f} USD
        - ROI: {low_returns['roi_percentage']:.2f}%
        
        ### Average Estimate (Average Commission of 5%)
        - APY: {avg_apy:.2f}%
        - SOL after {time_period_days} days: {avg_returns['final_sol']:.4f}
        - SOL earned: {avg_returns['sol_earned']:.4f}
        - Projected Value: ${avg_returns['projected_value_usd']:.2f} USD
        - ROI: {avg_returns['roi_percentage']:.2f}%
        
        ### High Estimate (Low Commission of 0%)
        - APY: {high_apy:.2f}%
        - SOL after {time_period_days} days: {high_returns['final_sol']:.4f}
        - SOL earned: {high_returns['sol_earned']:.4f}
        - Projected Value: ${high_returns['projected_value_usd']:.2f} USD
        - ROI: {high_returns['roi_percentage']:.2f}%
        
        ## Top Recommended Validators
        
        {self.compare_validators(top_validators).to_markdown(index=False) if top_validators else "No validator data available"}
        
        ## Recommendations
        
        1. Consider spreading your stake across 2-3 validators to reduce risk.
        2. Re-evaluate your staking strategy every 3 months.
        3. Monitor validator performance and commission changes.
        4. Check for any upcoming network upgrades that might affect staking.
        
        ## Visualization
        
        See the attached file: {plot_filename}
        """
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"solana_staking_report_{timestamp}.md"
        
        with open(report_filename, "w") as f:
            f.write(report)
        
        return report_filename


def main():
    """Main function to run the Solana Staking Value Analyzer."""
    parser = argparse.ArgumentParser(description="Analyze Solana staking value and opportunities")
    parser.add_argument("--amount", type=float, default=10.0, help="Amount of SOL to stake")
    parser.add_argument("--days", type=int, default=365, help="Time period in days")
    parser.add_argument("--api-key", type=str, help="API key for Solana API (optional)")
    
    args = parser.parse_args()
    
    print(f"📊 Solana Staking Value Analyzer 📊")
    print(f"Analyzing staking returns for {args.amount} SOL over {args.days} days...\n")
    
    analyzer = SolanaStakingAnalyzer(api_key=args.api_key)
    
    # Get current SOL price
    sol_price = analyzer.get_current_sol_price()
    print(f"Current SOL Price: ${sol_price:.2f} USD")
    
    # Generate report
    report_file = analyzer.generate_staking_report(args.amount, args.days)
    print(f"\n✅ Analysis complete! Report saved to: {report_file}")
    print(f"📈 Projection chart saved as well.")


if __name__ == "__main__":
    main()