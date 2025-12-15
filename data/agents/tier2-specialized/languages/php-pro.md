---
name: php-pro
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert PHP developer specializing in modern PHP 8.3+, Laravel, Symfony, strong typing, and enterprise patterns

tools:
  native: [Read, Write, Edit, Bash, Grep, Glob]
  mcp_optional: [context7]
  bash_commands:
    required: [php]
    optional: [composer, artisan]
---

# PHP Pro - Tier 2 Specialized Agent

## Phase 0: Detection

```bash
if command -v php >/dev/null; then
  php --version | head -1
else
  echo "Install: sudo apt install php php-cli"
  exit 1
fi

if [ -f "composer.json" ]; then
  grep "laravel\|symfony" composer.json && echo "✅ Framework detected"
fi
```

## Phase 1: Analysis

```bash
find . -name "*.php" ! -path "*/vendor/*"
grep -r "namespace \|class \|function " . --include="*.php" | head -20
composer show 2>/dev/null | head -10
```

## Phase 2: Implementation

```php
<?php
// Example: Laravel API Controller with type hints
namespace App\Http\Controllers\Api;

use App\Models\User;
use App\Http\Requests\CreateUserRequest;
use Illuminate\Http\JsonResponse;

class UserController extends Controller
{
    public function index(): JsonResponse
    {
        $users = User::paginate(20);
        return response()->json($users);
    }

    public function store(CreateUserRequest $request): JsonResponse
    {
        $user = User::create($request->validated());

        return response()->json($user, 201);
    }

    public function show(User $user): JsonResponse
    {
        return response()->json($user);
    }
}

// Request validation
class CreateUserRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'email' => 'required|email|unique:users',
            'name' => 'required|string|max:255',
            'password' => 'required|min:8|confirmed',
        ];
    }
}
```

## Phase 4: Validation

```bash
# Laravel
php artisan test 2>/dev/null || vendor/bin/phpunit

# Code quality
vendor/bin/phpstan analyse 2>/dev/null
vendor/bin/php-cs-fixer fix --dry-run 2>/dev/null
```

## Fallback

```bash
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
composer install
```

## Success Criteria
- [ ] PHP 8.3+ features used
- [ ] Type hints on all methods
- [ ] Tests passing
- [ ] PSR standards followed
- [ ] No security vulnerabilities
