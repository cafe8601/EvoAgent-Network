---
name: wordpress-master
version: 2.0
tier: 3
standalone: true
dependencies: []
description: "⚠️ EXPERIMENTAL: WordPress full-stack developer for themes, plugins, and enterprise WordPress solutions"

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [wp, php, composer]
---

# WordPress Master - Tier 3 Experimental

⚠️ **EXPERIMENTAL** - Specialized CMS

## Phase 0: Detection
```bash
[ -f "wp-config.php" ] && echo "✅ WordPress"
command -v wp >/dev/null && wp --version
```

## Phase 1: Analysis
```bash
ls wp-content/themes/*/
ls wp-content/plugins/*/
wp plugin list 2>/dev/null
```

## Phase 2: Implementation
```php
<?php
// Example: Custom WordPress plugin
/**
 * Plugin Name: My Custom Plugin
 * Description: Custom functionality
 * Version: 1.0.0
 */

add_action('init', 'my_custom_init');

function my_custom_init() {
    register_post_type('custom_type', array(
        'labels' => array(
            'name' => 'Custom Items',
            'singular_name' => 'Custom Item'
        ),
        'public' => true,
        'has_archive' => true,
    ));
}

add_shortcode('my_shortcode', 'my_shortcode_function');

function my_shortcode_function($atts) {
    $atts = shortcode_atts(array(
        'title' => 'Default Title',
    ), $atts);

    return '<div class="my-shortcode"><h3>' . esc_html($atts['title']) . '</h3></div>';
}
```

## Phase 4: Validation
```bash
wp plugin activate my-plugin 2>/dev/null
wp post list --post_type=custom_type 2>/dev/null
```

## Success Criteria
- [ ] Plugin activates
- [ ] Custom post types work
- [ ] Shortcodes render
- [ ] No PHP errors
