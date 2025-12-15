#!/usr/bin/env python3
"""
Feature Number Generator

Automatically generates the next available feature number based on existing spec directories.

Usage:
    python generate_feature_number.py [--specs-dir <path>]
    
Example:
    python generate_feature_number.py
    python generate_feature_number.py --specs-dir ./specs
    
Output:
    Returns next feature number (e.g., 001, 002, 003)
"""

import re
import sys
from pathlib import Path
from typing import List, Optional


class FeatureNumberGenerator:
    """Generates next available feature number."""
    
    def __init__(self, specs_dir: Path = Path('specs')):
        self.specs_dir = specs_dir
        self.existing_numbers: List[int] = []
        
    def scan_existing_features(self) -> List[int]:
        """Scan specs directory for existing feature numbers."""
        if not self.specs_dir.exists():
            print(f"📁 Specs directory does not exist: {self.specs_dir}")
            print(f"   This is OK for first feature. Creating directory...")
            self.specs_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        numbers = []
        
        for item in self.specs_dir.iterdir():
            if not item.is_dir():
                continue
            
            # Match pattern: ###-feature-name
            match = re.match(r'^(\d{3})-', item.name)
            if match:
                number = int(match.group(1))
                numbers.append(number)
        
        return sorted(numbers)
    
    def get_next_number(self) -> str:
        """Get next available feature number."""
        self.existing_numbers = self.scan_existing_features()
        
        if not self.existing_numbers:
            # First feature
            return '001'
        
        # Find next sequential number
        next_num = max(self.existing_numbers) + 1
        
        # Format as 3-digit with leading zeros
        return f'{next_num:03d}'
    
    def generate_directory_name(self, feature_name: str) -> str:
        """Generate full directory name: ###-feature-name."""
        number = self.get_next_number()
        
        # Sanitize feature name for directory
        sanitized = feature_name.lower()
        sanitized = re.sub(r'[^a-z0-9]+', '-', sanitized)
        sanitized = sanitized.strip('-')
        
        return f'{number}-{sanitized}'
    
    def print_report(self):
        """Print feature number report."""
        self.existing_numbers = self.scan_existing_features()
        
        print("📊 FEATURE NUMBER REPORT")
        print("=" * 50)
        print(f"Specs Directory: {self.specs_dir.absolute()}")
        print()
        
        if not self.existing_numbers:
            print("📋 Existing Features: None")
            print("✨ Next Available: 001")
        else:
            print(f"📋 Existing Features: {len(self.existing_numbers)}")
            print()
            
            # Show last 5 features
            recent = self.existing_numbers[-5:]
            for num in recent:
                # Find directory with this number
                pattern = f'{num:03d}-*'
                matches = list(self.specs_dir.glob(pattern))
                if matches:
                    dir_name = matches[0].name
                    print(f"  • {dir_name}")
            
            if len(self.existing_numbers) > 5:
                print(f"  ... and {len(self.existing_numbers) - 5} more")
            
            print()
            next_num = self.get_next_number()
            print(f"✨ Next Available: {next_num}")
        
        print("=" * 50)


def main():
    """Main entry point."""
    specs_dir = Path('specs')
    
    # Parse command line arguments
    if '--specs-dir' in sys.argv:
        idx = sys.argv.index('--specs-dir')
        if idx + 1 < len(sys.argv):
            specs_dir = Path(sys.argv[idx + 1])
    
    generator = FeatureNumberGenerator(specs_dir)
    
    # Check if feature name provided
    if len(sys.argv) >= 2 and not sys.argv[1].startswith('--'):
        feature_name = sys.argv[1]
        dir_name = generator.generate_directory_name(feature_name)
        print(dir_name)
    else:
        # Just show report
        generator.print_report()


if __name__ == '__main__':
    main()
