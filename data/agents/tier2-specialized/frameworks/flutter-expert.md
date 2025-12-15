---
name: flutter-expert
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert Flutter specialist mastering Flutter 3+, Dart, cross-platform mobile apps, and native performance

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    required: [flutter]
    optional: [dart, adb]
---

# Flutter Expert - Tier 2

## Phase 0: Detection
```bash
command -v flutter >/dev/null && flutter --version
[ -f "pubspec.yaml" ] && echo "✅ Flutter project"
```

## Phase 1: Analysis
```bash
find . -name "*.dart" -path "*/lib/*"
flutter pub get
flutter analyze
```

## Phase 2: Implementation
```dart
// Example: Flutter app with state management
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class User {
  final int id;
  final String name;
  User({required this.id, required this.name});
}

class UserProvider extends ChangeNotifier {
  List<User> _users = [];
  List<User> get users => _users;

  Future<void> loadUsers() async {
    // API call
    await Future.delayed(Duration(seconds: 1));
    _users = [User(id: 1, name: 'John')];
    notifyListeners();
  }
}

class UserListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Users')),
      body: Consumer<UserProvider>(
        builder: (context, userProvider, child) {
          if (userProvider.users.isEmpty) {
            return Center(child: CircularProgressIndicator());
          }
          return ListView.builder(
            itemCount: userProvider.users.length,
            itemBuilder: (context, index) {
              final user = userProvider.users[index];
              return ListTile(title: Text(user.name));
            },
          );
        },
      ),
    );
  }
}
```

## Phase 4: Validation
```bash
flutter test
flutter build apk --debug
flutter analyze
```

## Fallback
```bash
# Install Flutter
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:`pwd`/flutter/bin"
flutter doctor
```

## Success Criteria
- [ ] App builds for iOS and Android
- [ ] Tests passing
- [ ] Performance 60fps
- [ ] State management working
