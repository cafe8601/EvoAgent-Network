<!--
  Button Component - Svelte 5
  Production-ready with accessibility, variants, sizes, and states
-->

<script lang="ts">
  import { type Snippet } from 'svelte';

  type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
  type ButtonSize = 'sm' | 'md' | 'lg';

  interface Props {
    variant?: ButtonVariant;
    size?: ButtonSize;
    isLoading?: boolean;
    isFullWidth?: boolean;
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
    href?: string;
    leftIcon?: Snippet;
    rightIcon?: Snippet;
    children: Snippet;
    onclick?: (event: MouseEvent) => void;
  }

  let {
    variant = 'primary',
    size = 'md',
    isLoading = false,
    isFullWidth = false,
    disabled = false,
    type = 'button',
    href,
    leftIcon,
    rightIcon,
    children,
    onclick,
    ...restProps
  }: Props = $props();

  const isDisabled = $derived(disabled || isLoading);

  const classes = $derived([
    'button',
    `button--${variant}`,
    `button--${size}`,
    isFullWidth && 'button--full-width',
    isLoading && 'button--loading',
    isDisabled && 'button--disabled',
  ].filter(Boolean).join(' '));

  function handleClick(event: MouseEvent) {
    if (isDisabled) {
      event.preventDefault();
      return;
    }
    onclick?.(event);
  }
</script>

{#if href}
  <a
    {href}
    class={classes}
    aria-disabled={isDisabled}
    aria-busy={isLoading}
    onclick={handleClick}
    {...restProps}
  >
    {#if isLoading}
      <span class="button__spinner" aria-hidden="true">
        <svg
          class="button__spinner-icon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            class="button__spinner-track"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="3"
          />
          <path
            class="button__spinner-head"
            d="M12 2C6.48 2 2 6.48 2 12"
            stroke="currentColor"
            stroke-width="3"
            stroke-linecap="round"
          />
        </svg>
      </span>
    {/if}

    {#if leftIcon && !isLoading}
      <span class="button__icon button__icon--left" aria-hidden="true">
        {@render leftIcon()}
      </span>
    {/if}

    <span class="button__label" class:button__label--hidden={isLoading}>
      {@render children()}
    </span>

    {#if rightIcon}
      <span class="button__icon button__icon--right" aria-hidden="true">
        {@render rightIcon()}
      </span>
    {/if}
  </a>
{:else}
  <button
    {type}
    class={classes}
    disabled={isDisabled}
    aria-busy={isLoading}
    onclick={handleClick}
    {...restProps}
  >
    {#if isLoading}
      <span class="button__spinner" aria-hidden="true">
        <svg
          class="button__spinner-icon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            class="button__spinner-track"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="3"
          />
          <path
            class="button__spinner-head"
            d="M12 2C6.48 2 2 6.48 2 12"
            stroke="currentColor"
            stroke-width="3"
            stroke-linecap="round"
          />
        </svg>
      </span>
    {/if}

    {#if leftIcon && !isLoading}
      <span class="button__icon button__icon--left" aria-hidden="true">
        {@render leftIcon()}
      </span>
    {/if}

    <span class="button__label" class:button__label--hidden={isLoading}>
      {@render children()}
    </span>

    {#if rightIcon}
      <span class="button__icon button__icon--right" aria-hidden="true">
        {@render rightIcon()}
      </span>
    {/if}
  </button>
{/if}

<style>
  .button {
    /* Base */
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 0.5rem);

    /* Typography */
    font-family: var(--font-sans, system-ui, sans-serif);
    font-weight: 500;
    text-decoration: none;
    white-space: nowrap;

    /* Interaction */
    cursor: pointer;
    user-select: none;

    /* Transitions */
    transition-property: background-color, border-color, color, box-shadow, transform;
    transition-duration: 150ms;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);

    /* Reset */
    border: 1px solid transparent;
    outline: none;
  }

  .button:focus-visible {
    outline: 2px solid var(--color-primary-500, #3b82f6);
    outline-offset: 2px;
  }

  /* Variants */
  .button--primary {
    background-color: var(--color-primary-500, #3b82f6);
    color: white;
    border-color: var(--color-primary-500, #3b82f6);
  }

  .button--primary:hover:not(.button--disabled) {
    background-color: var(--color-primary-600, #2563eb);
    border-color: var(--color-primary-600, #2563eb);
  }

  .button--secondary {
    background-color: transparent;
    color: var(--color-gray-900, #111827);
    border-color: var(--color-gray-300, #d1d5db);
  }

  .button--secondary:hover:not(.button--disabled) {
    background-color: var(--color-gray-50, #f9fafb);
    border-color: var(--color-gray-400, #9ca3af);
  }

  .button--ghost {
    background-color: transparent;
    color: var(--color-gray-700, #374151);
    border-color: transparent;
  }

  .button--ghost:hover:not(.button--disabled) {
    background-color: var(--color-gray-100, #f3f4f6);
  }

  .button--danger {
    background-color: var(--color-red-500, #ef4444);
    color: white;
    border-color: var(--color-red-500, #ef4444);
  }

  .button--danger:hover:not(.button--disabled) {
    background-color: var(--color-red-600, #dc2626);
    border-color: var(--color-red-600, #dc2626);
  }

  /* Sizes */
  .button--sm {
    height: 32px;
    padding: 0 0.75rem;
    font-size: 0.8125rem;
    border-radius: var(--radius-md, 0.375rem);
  }

  .button--md {
    height: 40px;
    padding: 0 1rem;
    font-size: 0.875rem;
    border-radius: var(--radius-md, 0.375rem);
  }

  .button--lg {
    height: 48px;
    padding: 0 1.5rem;
    font-size: 1rem;
    border-radius: var(--radius-lg, 0.5rem);
  }

  /* States */
  .button--disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }

  .button--full-width {
    width: 100%;
  }

  .button--loading {
    position: relative;
    cursor: wait;
  }

  .button__label--hidden {
    visibility: hidden;
  }

  /* Icons */
  .button__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 1em;
    height: 1em;
  }

  /* Spinner */
  .button__spinner {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .button__spinner-icon {
    width: 1em;
    height: 1em;
    animation: spin 1s linear infinite;
  }

  .button__spinner-track {
    opacity: 0.25;
  }

  .button__spinner-head {
    opacity: 1;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .button {
      transition-duration: 0.01ms;
    }
    .button__spinner-icon {
      animation-duration: 1.5s;
    }
  }
</style>

<!--
Usage Examples:

<Button>Click me</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="danger">Delete</Button>

<Button size="sm">Small</Button>
<Button size="lg">Large</Button>

<Button isLoading>Saving...</Button>
<Button isFullWidth>Submit</Button>

<Button href="/page">Go to page</Button>

<Button>
  {#snippet leftIcon()}<PlusIcon />{/snippet}
  Add item
</Button>

<Button>
  Continue
  {#snippet rightIcon()}<ArrowRightIcon />{/snippet}
</Button>
-->
