#!/usr/bin/env python3
"""
Generate comparison charts from tokenizer evaluation results.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def load_results(json_path="eval_results.json"):
    """Load evaluation results from JSON file."""
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run 'make eval' first.")
        sys.exit(1)
    
    with open(json_path, 'r') as f:
        return json.load(f)

def create_comparison_chart(results, output_path="tokenizer_comparison.png"):
    """Create a bar chart comparing tokenizers."""
    # Filter successful results
    successful = [r for r in results if r.get('success', False)]
    
    if not successful:
        print("No successful results to plot.")
        return
    
    # Extract data
    names = [r['name'] for r in successful]
    compression = [r['compression_ratio'] for r in successful]
    accuracy = [r['accuracy'] for r in successful]
    
    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Color scheme - highlight GBM tokenizer
    colors = ['#2ecc71' if 'GBM' in name else '#3498db' for name in names]
    
    # Plot 1: Compression Ratio
    bars1 = ax1.barh(names, compression, color=colors)
    ax1.set_xlabel('Compression Ratio (chars/token)', fontsize=11, fontweight='bold')
    ax1.set_title('Compression Ratio (Higher is Better)', fontsize=13, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars1, compression)):
        ax1.text(val + 0.1, i, f'{val:.2f}x', va='center', fontweight='bold')
    
    # Plot 2: Accuracy
    bars2 = ax2.barh(names, accuracy, color=colors)
    ax2.set_xlabel('Round-trip Accuracy (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Accuracy (Higher is Better)', fontsize=13, fontweight='bold')
    ax2.set_xlim(0, 115) # Make room for labels
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars2, accuracy)):
        ax2.text(val + 1, i, f'{val:.1f}%', va='center', fontweight='bold')

    # Plot 3: Fertility
    fertility = [r.get('fertility', 0) for r in successful]
    bars3 = ax3.barh(names, fertility, color=colors)
    ax3.set_xlabel('Fertility (tokens/word)', fontsize=11, fontweight='bold')
    ax3.set_title('Fertility (Lower is Better)', fontsize=13, fontweight='bold')
    ax3.grid(axis='x', alpha=0.3, linestyle='--')

    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars3, fertility)):
        ax3.text(val + 0.1, i, f'{val:.2f}', va='center', fontweight='bold')

    # Plot 4: Speed
    speed = [r.get('speed', 0) for r in successful]
    bars4 = ax4.barh(names, speed, color=colors)
    ax4.set_xlabel('Speed (tokens/sec)', fontsize=11, fontweight='bold')
    ax4.set_title('Encoding Speed (Higher is Better)', fontsize=13, fontweight='bold')
    ax4.grid(axis='x', alpha=0.3, linestyle='--')

    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars4, speed)):
        # Format speed with K/M suffixes
        if val >= 1_000_000:
            label = f'{val/1_000_000:.1f}M'
        elif val >= 1_000:
            label = f'{val/1_000:.1f}K'
        else:
            label = f'{val:.0f}'
        ax4.text(val * 1.05, i, label, va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Chart saved to {output_path}")
    
    return output_path

def main():
    results = load_results()
    create_comparison_chart(results)

if __name__ == '__main__':
    main()
