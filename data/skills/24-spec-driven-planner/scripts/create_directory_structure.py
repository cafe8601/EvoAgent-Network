#!/usr/bin/env python3
"""
Spec Directory Structure Creator

Creates complete directory structure for a new feature specification.

Usage:
    python create_directory_structure.py <feature-name> [--specs-dir <path>]
    
Example:
    python create_directory_structure.py "Real-time Chat"
    python create_directory_structure.py "User Authentication" --specs-dir ./specs
    
Creates:
    specs/###-feature-name/
    ├── spec.md
    ├── plan.md
    ├── tasks.md
    └── contracts/
        ├── openapi.json
        └── README.md
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


class SpecDirectoryCreator:
    """Creates directory structure for new feature spec."""
    
    def __init__(self, feature_name: str, specs_dir: Path = Path('specs')):
        self.feature_name = feature_name
        self.specs_dir = specs_dir
        self.feature_dir: Optional[Path] = None
        
    def create_structure(self) -> bool:
        """Create complete directory structure."""
        try:
            # Generate feature number and directory name
            from generate_feature_number import FeatureNumberGenerator
            
            generator = FeatureNumberGenerator(self.specs_dir)
            dir_name = generator.generate_directory_name(self.feature_name)
            
            self.feature_dir = self.specs_dir / dir_name
            
            # Check if already exists
            if self.feature_dir.exists():
                print(f"❌ Error: Feature directory already exists: {self.feature_dir}")
                return False
            
            print(f"📁 Creating feature directory: {dir_name}")
            print()
            
            # Create main directory
            self.feature_dir.mkdir(parents=True, exist_ok=False)
            print(f"✅ Created: {self.feature_dir}/")
            
            # Create subdirectories
            self._create_contracts_dir()
            
            # Create template files
            self._create_spec_template()
            self._create_plan_template()
            self._create_tasks_template()
            
            # Print summary
            self._print_summary()
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating directory structure: {e}")
            return False
    
    def _create_contracts_dir(self):
        """Create contracts directory."""
        contracts_dir = self.feature_dir / 'contracts'
        contracts_dir.mkdir(exist_ok=True)
        print(f"✅ Created: {contracts_dir}/")
        
        # Create README
        readme_path = contracts_dir / 'README.md'
        readme_content = """# API Contracts

This directory contains API contracts and specifications.

## Files

- `openapi.json` - REST API specification (OpenAPI 3.0)
- `websocket-spec.md` - WebSocket/SignalR event specifications
- `graphql-schema.graphql` - GraphQL schema (if applicable)

## Usage

Contract files are used for:
1. **Contract Testing**: Validate API responses match specifications
2. **Documentation**: Auto-generate API documentation
3. **Client Generation**: Generate API clients automatically
4. **Validation**: Ensure backward compatibility

## Contract Testing

Contract tests should verify:
- Request schema validation
- Response schema validation
- Error response formats
- Status codes
- Headers

See `tests/contracts/` for contract test examples.
"""
        readme_path.write_text(readme_content)
        print(f"✅ Created: {readme_path}")
        
        # Create empty OpenAPI template
        openapi_path = contracts_dir / 'openapi.json'
        openapi_content = """{
  "openapi": "3.0.0",
  "info": {
    "title": "%s API",
    "version": "1.0.0",
    "description": "API specification for %s"
  },
  "paths": {},
  "components": {
    "schemas": {}
  }
}
""" % (self.feature_name, self.feature_name)
        openapi_path.write_text(openapi_content)
        print(f"✅ Created: {openapi_path}")
    
    def _create_spec_template(self):
        """Create spec.md from template."""
        # Load template from assets
        template_path = Path(__file__).parent.parent / 'assets' / 'spec-template.md'
        
        if not template_path.exists():
            print(f"⚠️  Template not found: {template_path}")
            print(f"   Creating basic spec.md...")
            spec_content = self._get_basic_spec_template()
        else:
            spec_content = template_path.read_text()
        
        # Replace placeholders
        spec_content = spec_content.replace('[FEATURE NAME]', self.feature_name)
        spec_content = spec_content.replace('YYYY-MM-DD', datetime.now().strftime('%Y-%m-%d'))
        
        spec_path = self.feature_dir / 'spec.md'
        spec_path.write_text(spec_content)
        print(f"✅ Created: {spec_path}")
    
    def _create_plan_template(self):
        """Create plan.md from template."""
        template_path = Path(__file__).parent.parent / 'assets' / 'plan-template.md'
        
        if not template_path.exists():
            print(f"⚠️  Template not found: {template_path}")
            print(f"   Creating basic plan.md...")
            plan_content = self._get_basic_plan_template()
        else:
            plan_content = template_path.read_text()
        
        # Replace placeholders
        plan_content = plan_content.replace('[FEATURE NAME]', self.feature_name)
        plan_content = plan_content.replace('YYYY-MM-DD', datetime.now().strftime('%Y-%m-%d'))
        
        # Extract feature number from directory name
        import re
        match = re.match(r'^(\d{3})-', self.feature_dir.name)
        feature_number = match.group(1) if match else '###'
        plan_content = plan_content.replace('[###]', feature_number)
        
        plan_path = self.feature_dir / 'plan.md'
        plan_path.write_text(plan_content)
        print(f"✅ Created: {plan_path}")
    
    def _create_tasks_template(self):
        """Create tasks.md from template."""
        template_path = Path(__file__).parent.parent / 'assets' / 'tasks-template.md'
        
        if not template_path.exists():
            print(f"⚠️  Template not found: {template_path}")
            print(f"   Creating basic tasks.md...")
            tasks_content = self._get_basic_tasks_template()
        else:
            tasks_content = template_path.read_text()
        
        # Replace placeholders
        tasks_content = tasks_content.replace('[FEATURE NAME]', self.feature_name)
        tasks_content = tasks_content.replace('YYYY-MM-DD', datetime.now().strftime('%Y-%m-%d'))
        
        # Extract feature number
        import re
        match = re.match(r'^(\d{3})-', self.feature_dir.name)
        feature_number = match.group(1) if match else '###'
        tasks_content = tasks_content.replace('[###]', feature_number)
        
        tasks_path = self.feature_dir / 'tasks.md'
        tasks_path.write_text(tasks_content)
        print(f"✅ Created: {tasks_path}")
    
    def _get_basic_spec_template(self) -> str:
        """Get basic spec template if file not found."""
        return f"""# Feature Specification: {self.feature_name}

> **Status**: Draft  
> **Priority**: P1 (Critical)  
> **Created**: {datetime.now().strftime('%Y-%m-%d')}

---

## User Scenarios & Testing (REQUIRED)

### P1: Critical Path (Must-Have)

#### Scenario 1: [Primary User Goal]
**As a** [user type]  
**I want to** [action]  
**So that** [business value]

**Acceptance Criteria**:
```gherkin
Given [context]
When [action]
Then [expected outcome]
```

---

## Requirements (REQUIRED)

### Functional Requirements

**FR-001**: [Requirement Description]
- **Priority**: P1
- **Rationale**: [Why this is needed]

---

## Success Criteria (REQUIRED)

### Business Metrics
- [Measurable outcome 1]

### Technical Metrics
- [Measurable metric 1]
"""
    
    def _get_basic_plan_template(self) -> str:
        """Get basic plan template if file not found."""
        return f"""# Implementation Plan: {self.feature_name}

> **Status**: Planning  
> **Created**: {datetime.now().strftime('%Y-%m-%d')}

---

## Phase -1: Pre-Implementation Gates

### Constitutional Compliance Check

[To be completed]

---

## Phase 0: Technical Foundation

### Technology Stack Selection

[To be completed]

---

## Phase 1: Data Model Design

[To be completed]

---

## Phase 2: API Contracts

[To be completed]

---

## Phase 3: Implementation Sequence

[To be completed]
"""
    
    def _get_basic_tasks_template(self) -> str:
        """Get basic tasks template if file not found."""
        return f"""# Tasks: {self.feature_name}

> **Status**: Not Started  
> **Created**: {datetime.now().strftime('%Y-%m-%d')}

---

## Task Execution Rules

**EVERY implementation task MUST follow**:
1. Write Test → User reviews and approves
2. Run Test → Confirm it FAILS (RED)
3. Implement → Write minimum code to pass
4. Run Test → Confirm it PASSES (GREEN)
5. Refactor → Improve without breaking tests

---

## User Story 1: [Story Name]

[To be completed]
"""
    
    def _print_summary(self):
        """Print creation summary."""
        print()
        print("=" * 60)
        print("✅ SUCCESS! Feature structure created")
        print("=" * 60)
        print()
        print(f"📁 Location: {self.feature_dir.absolute()}")
        print()
        print("📋 Files created:")
        print(f"  • spec.md         - Feature specification")
        print(f"  • plan.md         - Implementation plan")
        print(f"  • tasks.md        - Task breakdown")
        print(f"  • contracts/      - API contracts")
        print()
        print("🎯 Next steps:")
        print(f"  1. Edit {self.feature_dir.name}/spec.md")
        print(f"     - Complete user scenarios")
        print(f"     - Define requirements")
        print(f"     - Mark [NEEDS CLARIFICATION] items")
        print()
        print(f"  2. Generate plan:")
        print(f"     - Review spec with user")
        print(f"     - Create implementation plan")
        print(f"     - Check constitutional compliance")
        print()
        print(f"  3. Break down tasks:")
        print(f"     - Convert plan to tasks.md")
        print(f"     - Define TDD workflow")
        print(f"     - Identify parallel work tracks")
        print()
        print("=" * 60)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python create_directory_structure.py <feature-name> [--specs-dir <path>]")
        print()
        print("Example:")
        print('  python create_directory_structure.py "Real-time Chat"')
        print('  python create_directory_structure.py "User Auth" --specs-dir ./specs')
        sys.exit(1)
    
    feature_name = sys.argv[1]
    specs_dir = Path('specs')
    
    # Parse optional specs directory
    if '--specs-dir' in sys.argv:
        idx = sys.argv.index('--specs-dir')
        if idx + 1 < len(sys.argv):
            specs_dir = Path(sys.argv[idx + 1])
    
    # Create structure
    creator = SpecDirectoryCreator(feature_name, specs_dir)
    success = creator.create_structure()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
