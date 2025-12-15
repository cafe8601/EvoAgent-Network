#!/usr/bin/env python3
"""
Constitutional Compliance Validator

Validates that a plan.md file complies with Constitutional articles.
Checks all 9 articles and generates a compliance report.

Usage:
    python validate_constitution.py <path/to/plan.md> [--constitution <path/to/constitution.md>]
    
Example:
    python validate_constitution.py specs/001-feature/plan.md
    python validate_constitution.py specs/001-feature/plan.md --constitution memory/constitution.md
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ConstitutionValidator:
    """Validates plan compliance with Constitutional articles."""
    
    ARTICLES = {
        'I': 'Library-First Principle',
        'II': 'CLI Interface Mandate',
        'III': 'Test-First Imperative',
        'VII': 'Simplicity Gate',
        'VIII': 'Anti-Abstraction Gate',
        'IX': 'Integration-First Testing'
    }
    
    def __init__(self, plan_path: Path, constitution_path: Optional[Path] = None):
        self.plan_path = plan_path
        self.constitution_path = constitution_path or Path('memory/constitution.md')
        self.plan_content = ''
        self.constitution_content = ''
        self.violations: List[Dict] = []
        self.warnings: List[str] = []
        
    def load_files(self) -> bool:
        """Load plan and constitution files."""
        try:
            if not self.plan_path.exists():
                print(f"❌ Error: Plan file not found: {self.plan_path}")
                return False
            
            self.plan_content = self.plan_path.read_text()
            
            if self.constitution_path.exists():
                self.constitution_content = self.constitution_path.read_text()
            else:
                self.warnings.append(
                    f"⚠️  Constitution file not found: {self.constitution_path}"
                )
                
            return True
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            return False
    
    def validate(self) -> bool:
        """Run all constitutional validations."""
        print(f"📋 Validating: {self.plan_path}")
        print(f"📜 Constitution: {self.constitution_path}")
        print()
        
        if not self.load_files():
            return False
        
        # Check each article
        checks = [
            self._check_article_i,
            self._check_article_ii,
            self._check_article_iii,
            self._check_article_vii,
            self._check_article_viii,
            self._check_article_ix
        ]
        
        for check in checks:
            check()
        
        # Print results
        self._print_results()
        
        return len(self.violations) == 0
    
    def _check_article_i(self):
        """Article I: Library-First Principle"""
        article = 'I'
        
        # Look for "Library-First" compliance check
        if 'Article I' not in self.plan_content:
            self.warnings.append(
                f"Article {article}: No compliance check found in plan"
            )
            return
        
        # Check if library structure mentioned
        if 'src/lib/' not in self.plan_content and 'library' not in self.plan_content.lower():
            self.violations.append({
                'article': article,
                'title': self.ARTICLES[article],
                'issue': 'No library structure mentioned',
                'suggestion': 'Plan should include src/lib/ directory structure'
            })
        
        # Check for business logic in controllers/routes
        problematic_patterns = [
            'business logic in controller',
            'logic in routes',
            'controller contains logic'
        ]
        
        for pattern in problematic_patterns:
            if pattern in self.plan_content.lower():
                self.violations.append({
                    'article': article,
                    'title': self.ARTICLES[article],
                    'issue': f'Found mention of: "{pattern}"',
                    'suggestion': 'Business logic should be in library, not controllers'
                })
    
    def _check_article_ii(self):
        """Article II: CLI Interface Mandate"""
        article = 'II'
        
        if 'Article II' not in self.plan_content:
            self.warnings.append(
                f"Article {article}: No compliance check found in plan"
            )
            return
        
        # Check for CLI mention
        cli_patterns = ['cli', 'command line', 'command-line']
        has_cli = any(pattern in self.plan_content.lower() for pattern in cli_patterns)
        
        if not has_cli:
            self.violations.append({
                'article': article,
                'title': self.ARTICLES[article],
                'issue': 'No CLI interface mentioned',
                'suggestion': 'Every library should have a CLI interface'
            })
    
    def _check_article_iii(self):
        """Article III: Test-First Imperative (NON-NEGOTIABLE)"""
        article = 'III'
        
        if 'Article III' not in self.plan_content:
            self.violations.append({
                'article': article,
                'title': self.ARTICLES[article],
                'issue': 'Article III check MISSING - This is NON-NEGOTIABLE',
                'suggestion': 'Plan MUST include Article III compliance check'
            })
            return
        
        # Check for TDD workflow
        tdd_patterns = [
            'test-first',
            'test first',
            'tdd',
            'red-green-refactor',
            'write test',
            'user approval'
        ]
        
        has_tdd = any(pattern in self.plan_content.lower() for pattern in tdd_patterns)
        
        if not has_tdd:
            self.violations.append({
                'article': article,
                'title': self.ARTICLES[article],
                'issue': 'No TDD workflow mentioned - Article III is NON-NEGOTIABLE',
                'suggestion': 'Plan MUST include test-first workflow with user approval'
            })
        
        # Check for user approval mention
        if 'user approval' not in self.plan_content.lower():
            self.violations.append({
                'article': article,
                'title': self.ARTICLES[article],
                'issue': 'User approval not mentioned',
                'suggestion': 'Tests must be approved by user before implementation'
            })
    
    def _check_article_vii(self):
        """Article VII: Simplicity Gate"""
        article = 'VII'
        
        if 'Article VII' not in self.plan_content:
            self.warnings.append(
                f"Article {article}: No compliance check found in plan"
            )
            return
        
        # Count projects mentioned
        project_count = self._count_projects()
        
        if project_count > 3:
            self.violations.append({
                'article': article,
                'title': self.ARTICLES[article],
                'issue': f'Plan mentions {project_count} projects (max 3 allowed)',
                'suggestion': 'Simplify to ≤3 projects or justify in Complexity Register'
            })
        
        # Check for future-proofing keywords
        future_proof_patterns = [
            'future-proof',
            'just in case',
            'might need',
            'maybe later',
            'for scalability',
            'when we need to'
        ]
        
        for pattern in future_proof_patterns:
            if pattern in self.plan_content.lower():
                self.violations.append({
                    'article': article,
                    'title': self.ARTICLES[article],
                    'issue': f'Possible future-proofing detected: "{pattern}"',
                    'suggestion': 'Build only what is needed now (YAGNI principle)'
                })
    
    def _check_article_viii(self):
        """Article VIII: Anti-Abstraction Gate"""
        article = 'VIII'
        
        if 'Article VIII' not in self.plan_content:
            self.warnings.append(
                f"Article {article}: No compliance check found in plan"
            )
            return
        
        # Check for abstraction layers
        abstraction_patterns = [
            'wrapper',
            'abstraction layer',
            'interface for',
            'generic framework',
            'dto.*entity.*model',  # Multiple model representations
            'mapper',
            'adapter pattern'
        ]
        
        for pattern in abstraction_patterns:
            if re.search(pattern, self.plan_content.lower()):
                self.violations.append({
                    'article': article,
                    'title': self.ARTICLES[article],
                    'issue': f'Possible abstraction layer detected: "{pattern}"',
                    'suggestion': 'Use frameworks directly, avoid unnecessary abstractions'
                })
    
    def _check_article_ix(self):
        """Article IX: Integration-First Testing"""
        article = 'IX'
        
        if 'Article IX' not in self.plan_content:
            self.warnings.append(
                f"Article {article}: No compliance check found in plan"
            )
            return
        
        # Check for contract tests
        if 'contract test' not in self.plan_content.lower():
            self.violations.append({
                'article': article,
                'title': self.ARTICLES[article],
                'issue': 'No contract tests mentioned',
                'suggestion': 'Plan should include contract tests for APIs'
            })
        
        # Check for integration tests
        if 'integration test' not in self.plan_content.lower():
            self.violations.append({
                'article': article,
                'title': self.ARTICLES[article],
                'issue': 'No integration tests mentioned',
                'suggestion': 'Plan should include integration tests with real systems'
            })
        
        # Check if mocking is preferred over real systems
        mock_patterns = [
            'mock database',
            'mocked database',
            'in-memory database',
            'mock everything'
        ]
        
        for pattern in mock_patterns:
            if pattern in self.plan_content.lower():
                self.warnings.append(
                    f"Article {article}: Consider using real test database instead of: '{pattern}'"
                )
    
    def _count_projects(self) -> int:
        """Count number of projects mentioned in plan."""
        # Look for project structure section
        project_section_match = re.search(
            r'### Project Structure.*?```(.*?)```',
            self.plan_content,
            re.DOTALL
        )
        
        if not project_section_match:
            return 0
        
        structure = project_section_match.group(1)
        
        # Count top-level directories that look like projects
        # (e.g., src/lib/, src/api/, src/worker/)
        projects = re.findall(r'src/(\w+)/', structure)
        
        # Deduplicate
        unique_projects = set(projects)
        
        return len(unique_projects)
    
    def _print_results(self):
        """Print validation results."""
        print("=" * 70)
        print("📊 CONSTITUTIONAL COMPLIANCE REPORT")
        print("=" * 70)
        print()
        
        # Print warnings first
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()
        
        # Print violations
        if self.violations:
            print("❌ VIOLATIONS:")
            for violation in self.violations:
                print(f"\n  Article {violation['article']}: {violation['title']}")
                print(f"  Issue: {violation['issue']}")
                print(f"  Suggestion: {violation['suggestion']}")
            print()
            print("=" * 70)
            print(f"RESULT: ❌ FAILED - {len(self.violations)} violation(s) found")
            print("=" * 70)
            print()
            print("Next Steps:")
            print("1. Review violations above")
            print("2. Update plan.md to address issues")
            print("3. OR document justification in Complexity Register")
            print("4. Re-run validation")
        else:
            print("✅ PASSED - No violations found")
            print("=" * 70)
            print()
            print("Plan complies with all Constitutional articles!")
        
        print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_constitution.py <path/to/plan.md> [--constitution <path>]")
        print()
        print("Example:")
        print("  python validate_constitution.py specs/001-feature/plan.md")
        print("  python validate_constitution.py specs/001-feature/plan.md --constitution memory/constitution.md")
        sys.exit(1)
    
    plan_path = Path(sys.argv[1])
    constitution_path = None
    
    # Parse optional constitution path
    if '--constitution' in sys.argv:
        idx = sys.argv.index('--constitution')
        if idx + 1 < len(sys.argv):
            constitution_path = Path(sys.argv[idx + 1])
    
    # Run validation
    validator = ConstitutionValidator(plan_path, constitution_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
