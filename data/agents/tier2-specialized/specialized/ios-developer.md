---
name: ios-developer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert iOS developer mastering Swift, SwiftUI, UIKit, Core Data, and Apple platform development

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [xcodebuild, swift, swiftlint]
---

# iOS Developer - Tier 2

## Phase 0: Detection
```bash
find . -name "*.xcodeproj" -o -name "*.xcworkspace"
find . -name "*.swift" | head -10
```

## Phase 1: Analysis
```bash
find . -name "*.swift" -path "*/Sources/*"
grep -r "import UIKit\|import SwiftUI" . --include="*.swift"
xcodebuild -list 2>/dev/null
```

## Phase 2: Implementation
```swift
// Example: SwiftUI app with MVVM
import SwiftUI

struct User: Identifiable, Codable {
    let id: Int
    let name: String
    let email: String
}

@MainActor
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var error: Error?

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }

        do {
            let url = URL(string: "https://api.example.com/users")!
            let (data, _) = try await URLSession.shared.data(from: url)
            users = try JSONDecoder().decode([User].self, from: data)
        } catch {
            self.error = error
        }
    }
}

struct UserListView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users) { user in
            VStack(alignment: .leading) {
                Text(user.name).font(.headline)
                Text(user.email).font(.caption)
            }
        }
        .task {
            await viewModel.loadUsers()
        }
        .overlay {
            if viewModel.isLoading {
                ProgressView()
            }
        }
    }
}
```

## Phase 4: Validation
```bash
xcodebuild -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15' test
swiftlint 2>/dev/null
```

## Success Criteria
- [ ] App builds successfully
- [ ] Tests passing
- [ ] SwiftUI best practices
- [ ] Async/await correctly used
- [ ] Memory management proper
