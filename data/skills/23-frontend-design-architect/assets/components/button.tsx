/**
 * Button Component - React with CSS Modules
 * Production-ready with accessibility, variants, sizes, and states
 */

import React, { forwardRef, ButtonHTMLAttributes, AnchorHTMLAttributes } from 'react';
import styles from './button.module.css';
import clsx from 'clsx';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonBaseProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  isFullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

type ButtonAsButton = ButtonBaseProps &
  Omit<ButtonHTMLAttributes<HTMLButtonElement>, keyof ButtonBaseProps> & {
    as?: 'button';
  };

type ButtonAsAnchor = ButtonBaseProps &
  Omit<AnchorHTMLAttributes<HTMLAnchorElement>, keyof ButtonBaseProps> & {
    as: 'a';
    href: string;
  };

type ButtonProps = ButtonAsButton | ButtonAsAnchor;

const Button = forwardRef<HTMLButtonElement | HTMLAnchorElement, ButtonProps>(
  (props, ref) => {
    const {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      isFullWidth = false,
      leftIcon,
      rightIcon,
      children,
      className,
      disabled,
      as = 'button',
      ...rest
    } = props;

    const isDisabled = disabled || isLoading;

    const buttonClasses = clsx(
      styles.button,
      styles[variant],
      styles[size],
      {
        [styles.fullWidth]: isFullWidth,
        [styles.loading]: isLoading,
        [styles.disabled]: isDisabled,
      },
      className
    );

    const content = (
      <>
        {isLoading && (
          <span className={styles.spinner} aria-hidden="true">
            <svg
              className={styles.spinnerIcon}
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                className={styles.spinnerTrack}
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="3"
              />
              <path
                className={styles.spinnerHead}
                d="M12 2C6.48 2 2 6.48 2 12"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
              />
            </svg>
          </span>
        )}
        {leftIcon && !isLoading && (
          <span className={styles.iconLeft} aria-hidden="true">
            {leftIcon}
          </span>
        )}
        <span className={clsx(styles.label, { [styles.labelHidden]: isLoading })}>
          {children}
        </span>
        {rightIcon && (
          <span className={styles.iconRight} aria-hidden="true">
            {rightIcon}
          </span>
        )}
      </>
    );

    if (as === 'a') {
      const { href, ...anchorProps } = rest as AnchorHTMLAttributes<HTMLAnchorElement> & {
        href: string;
      };
      return (
        <a
          ref={ref as React.Ref<HTMLAnchorElement>}
          href={href}
          className={buttonClasses}
          aria-disabled={isDisabled}
          {...anchorProps}
        >
          {content}
        </a>
      );
    }

    return (
      <button
        ref={ref as React.Ref<HTMLButtonElement>}
        type="button"
        className={buttonClasses}
        disabled={isDisabled}
        aria-busy={isLoading}
        {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}
      >
        {content}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
export type { ButtonProps, ButtonVariant, ButtonSize };

/**
 * Usage Examples:
 *
 * // Basic
 * <Button>Click me</Button>
 *
 * // Variants
 * <Button variant="secondary">Secondary</Button>
 * <Button variant="ghost">Ghost</Button>
 * <Button variant="danger">Delete</Button>
 *
 * // Sizes
 * <Button size="sm">Small</Button>
 * <Button size="lg">Large</Button>
 *
 * // With icons
 * <Button leftIcon={<PlusIcon />}>Add item</Button>
 * <Button rightIcon={<ArrowRightIcon />}>Continue</Button>
 *
 * // Loading state
 * <Button isLoading>Saving...</Button>
 *
 * // Full width
 * <Button isFullWidth>Submit</Button>
 *
 * // As link
 * <Button as="a" href="/page">Go to page</Button>
 */
