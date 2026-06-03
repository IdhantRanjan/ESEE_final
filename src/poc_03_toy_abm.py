#!/usr/bin/env python3
"""
ESEE 2026 POC - Step 3: Toy Agent-Based Model

Minimal ABM using Mesa framework to simulate work-time reduction policy.
10,000 agents, 50 timesteps, tracks employment, inequality, and emissions proxy.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Try to import Mesa, create simple fallback if not available
try:
    from mesa import Model, Agent
    from mesa.time import RandomActivation
    from mesa.datacollection import DataCollector
    MESA_AVAILABLE = True
except ImportError:
    print("⚠ Mesa not available, using simplified implementation")
    MESA_AVAILABLE = False

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class WorkTimeAgent:
    """Simple agent class for work-time reduction simulation."""
    
    def __init__(self, unique_id, income_quintile, country, adoption_probability):
        self.unique_id = unique_id
        self.income_quintile = income_quintile
        self.country = country
        self.adoption_probability = adoption_probability
        self.employed = True
        self.working_hours = 40 if self.employed else 0
        self.income = self._initial_income()
        self.adopted_policy = False
    
    def _initial_income(self):
        """Set initial income based on quintile."""
        # Quintile 1: 10-20k, 2: 20-30k, 3: 30-50k, 4: 50-80k, 5: 80k+
        base_income = [15, 25, 40, 65, 100][self.income_quintile - 1] * 1000
        return base_income + np.random.normal(0, base_income * 0.2)
    
    def decide_adoption(self, timestep):
        """Decide whether to adopt work-time reduction policy."""
        if timestep == 0 and self.employed and not self.adopted_policy:
            # Random decision based on adoption probability
            if np.random.random() < self.adoption_probability:
                self.adopted_policy = True
                self.working_hours = 30  # Reduced from 40
                self.income *= 0.75  # Proportional reduction
    
    def become_unemployed(self):
        """Agent becomes unemployed."""
        self.employed = False
        self.working_hours = 0
        self.income *= 0.3  # Unemployment benefits


class WorkTimeModel:
    """Simple model for work-time reduction policy simulation."""
    
    def __init__(self, n_agents=10000, adoption_probs_df=None):
        self.n_agents = n_agents
        self.schedule = []  # Simple list-based scheduler
        self.agents = []
        self.timestep = 0
        self.adoption_probs_df = adoption_probs_df
        
        # Create agents
        self._create_agents()
    
    def _create_agents(self):
        """Create agents with initial attributes."""
        print("Creating agents...")
        
        # Load adoption probabilities if available
        if self.adoption_probs_df is not None:
            # Create lookup dict
            prob_lookup = {}
            for _, row in self.adoption_probs_df.iterrows():
                key = (row['income_quintile'], row['country'])
                prob_lookup[key] = row['adoption_prob_mean']
        else:
            prob_lookup = {}
            print("  ⚠ No adoption probabilities provided, using random")
        
        # Get countries from adoption probs or use defaults
        if self.adoption_probs_df is not None:
            countries = self.adoption_probs_df['country'].unique().tolist()
        else:
            countries = ['DE', 'FR', 'IT', 'ES', 'PL', 'NL', 'BE', 'SE', 'AT', 'CZ']
        
        # Create agents
        for i in range(self.n_agents):
            # Income quintile: 20% in each quintile
            income_quintile = (i % 5) + 1
            
            # Country: proportional distribution
            country_idx = int((i / self.n_agents) * len(countries))
            country = countries[min(country_idx, len(countries) - 1)]
            
            # Adoption probability
            key = (income_quintile, country)
            adoption_prob = prob_lookup.get(key, 0.4)  # Default 40%
            
            agent = WorkTimeAgent(i, income_quintile, country, adoption_prob)
            self.agents.append(agent)
        
        print(f"  ✓ Created {len(self.agents):,} agents")
        print(f"  Countries: {len(countries)}")
    
    def step(self):
        """Run one step of the model."""
        # Policy introduction at timestep 0
        if self.timestep == 0:
            print(f"\nTimestep {self.timestep}: Introducing work-time reduction policy...")
            
            # Agents decide to adopt
            adoptions = 0
            for agent in self.agents:
                agent.decide_adoption(self.timestep)
                if agent.adopted_policy:
                    adoptions += 1
            
            print(f"  {adoptions:,} agents ({adoptions/len(self.agents)*100:.1f}%) adopted policy")
            
            # Calculate employment effect
            # Total hours reduction
            total_hours_before = sum(a.working_hours for a in self.agents if a.employed)
            total_hours_after = sum(a.working_hours for a in self.agents if a.employed)
            hours_reduced = total_hours_before - total_hours_after
            
            # Employment impact: simplified
            # Some jobs may not be needed if total hours decrease
            unemployment_increase = max(0, hours_reduced / total_hours_before * 0.1)  # 10% of reduction becomes unemployment
            
            n_to_unemploy = int(len(self.agents) * unemployment_increase)
            if n_to_unemploy > 0:
                # Select agents to unemploy (inversely proportional to income)
                employed_agents = [a for a in self.agents if a.employed]
                if len(employed_agents) > 0:
                    # Probability inversely proportional to income quintile
                    weights = [6 - a.income_quintile for a in employed_agents]
                    weights = np.array(weights)
                    weights = weights / weights.sum()
                    
                    to_unemploy = np.random.choice(
                        len(employed_agents),
                        size=min(n_to_unemploy, len(employed_agents)),
                        replace=False,
                        p=weights
                    )
                    
                    for idx in to_unemploy:
                        employed_agents[idx].become_unemployed()
                    
                    print(f"  {len(to_unemploy):,} agents became unemployed due to policy")
        
        self.timestep += 1
    
    def collect_data(self):
        """Collect data from current state."""
        employed = sum(1 for a in self.agents if a.employed)
        employment_rate = employed / len(self.agents)
        
        # Gini coefficient (simplified)
        incomes = [a.income for a in self.agents]
        incomes_sorted = sorted(incomes)
        n = len(incomes_sorted)
        cumsum = np.cumsum(incomes_sorted)
        gini = (2 * np.sum((np.arange(1, n + 1)) * incomes_sorted)) / (n * np.sum(incomes_sorted)) - (n + 1) / n
        
        # Total hours worked (proxy for emissions)
        total_hours = sum(a.working_hours for a in self.agents)
        
        # Policy adoption rate
        adoption_rate = sum(1 for a in self.agents if a.adopted_policy) / len(self.agents)
        
        return {
            'timestep': self.timestep,
            'employment_rate': employment_rate,
            'gini_coefficient': gini,
            'total_hours': total_hours,
            'adoption_rate': adoption_rate
        }


def main():
    """Main ABM function."""
    print("=" * 70)
    print("ESEE 2026 POC - Step 3: Toy Agent-Based Model")
    print("=" * 70)
    print()
    
    # Paths
    input_table = PROJECT_ROOT / "results" / "tables" / "poc_adoption_probabilities.csv"
    output_results = PROJECT_ROOT / "results" / "model_outputs" / "poc_abm_results.csv"
    output_figure = PROJECT_ROOT / "results" / "figures" / "poc_abm_trajectories.png"
    
    # Create output directories
    output_results.parent.mkdir(parents=True, exist_ok=True)
    output_figure.parent.mkdir(parents=True, exist_ok=True)
    
    # Load adoption probabilities
    adoption_probs_df = None
    if input_table.exists():
        print(f"Loading adoption probabilities from: {input_table}")
        try:
            adoption_probs_df = pd.read_csv(input_table)
            print(f"  ✓ Loaded {len(adoption_probs_df):,} probability estimates")
        except Exception as e:
            print(f"  ⚠ Could not load: {e}, using defaults")
    else:
        print(f"  ⚠ File not found: {input_table}, using defaults")
    
    # Create model
    print("\nInitializing model...")
    model = WorkTimeModel(n_agents=10000, adoption_probs_df=adoption_probs_df)
    
    # Initial state
    initial_data = model.collect_data()
    print(f"\nInitial state (timestep 0):")
    print(f"  Employment rate: {initial_data['employment_rate']*100:.1f}%")
    print(f"  Gini coefficient: {initial_data['gini_coefficient']:.3f}")
    print(f"  Total hours: {initial_data['total_hours']:,.0f}")
    print(f"  Policy adoption: {initial_data['adoption_rate']*100:.1f}%")
    
    # Run simulation
    print(f"\nRunning simulation for 50 timesteps...")
    results = [initial_data]
    
    for t in range(1, 51):
        model.step()
        data = model.collect_data()
        results.append(data)
        
        if t % 10 == 0:
            print(f"  Timestep {t}: Employment={data['employment_rate']*100:.1f}%, Gini={data['gini_coefficient']:.3f}")
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Final state
    final_data = results[-1]
    print(f"\nFinal state (timestep 50):")
    print(f"  Employment rate: {final_data['employment_rate']*100:.1f}% (change: {(final_data['employment_rate']-initial_data['employment_rate'])*100:+.1f}%)")
    print(f"  Gini coefficient: {final_data['gini_coefficient']:.3f} (change: {final_data['gini_coefficient']-initial_data['gini_coefficient']:+.3f})")
    print(f"  Total hours: {final_data['total_hours']:,.0f} (change: {final_data['total_hours']-initial_data['total_hours']:+,.0f}, {(final_data['total_hours']/initial_data['total_hours']-1)*100:+.1f}%)")
    print(f"  Policy adoption: {final_data['adoption_rate']*100:.1f}%")
    
    # Save results
    print(f"\nSaving results...")
    results_df.to_csv(output_results, index=False)
    print(f"  ✓ Saved: {output_results}")
    
    # Generate figure
    print(f"\nGenerating trajectories figure...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Employment rate
    axes[0, 0].plot(results_df['timestep'], results_df['employment_rate'] * 100, linewidth=2, color='#2ecc71')
    axes[0, 0].set_title('Employment Rate', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Timestep')
    axes[0, 0].set_ylabel('Employment Rate (%)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Gini coefficient
    axes[0, 1].plot(results_df['timestep'], results_df['gini_coefficient'], linewidth=2, color='#e74c3c')
    axes[0, 1].set_title('Gini Coefficient (Inequality)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Timestep')
    axes[0, 1].set_ylabel('Gini Coefficient')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Total hours (emissions proxy)
    axes[1, 0].plot(results_df['timestep'], results_df['total_hours'] / 1000, linewidth=2, color='#3498db')
    axes[1, 0].set_title('Total Hours Worked (Emissions Proxy)', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Timestep')
    axes[1, 0].set_ylabel('Total Hours (thousands)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Policy adoption
    axes[1, 1].plot(results_df['timestep'], results_df['adoption_rate'] * 100, linewidth=2, color='#9b59b6')
    axes[1, 1].set_title('Policy Adoption Rate', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Timestep')
    axes[1, 1].set_ylabel('Adoption Rate (%)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Work-Time Reduction Policy: Macro Outcomes Over Time', 
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_figure, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_figure}")
    plt.close()
    
    print("\n" + "=" * 70)
    print("STEP 3 COMPLETE")
    print("=" * 70)
    print(f"Results: {output_results}")
    print(f"Figure: {output_figure}")
    print("=" * 70)
    
    return results_df


if __name__ == "__main__":
    try:
        result = main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


