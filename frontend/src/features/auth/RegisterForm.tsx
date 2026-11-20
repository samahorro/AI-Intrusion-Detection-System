import {
  useMemo,
  useState,
  type FormEvent,
} from "react";

import {
  Button,
  FormField,
  Input,
} from "../../components/base";

export type RegisterFormValues = {
  username: string;
  password: string;
};

export type RegisterFormProps = {
  onSubmit(
    values: RegisterFormValues,
  ): Promise<void>;
  isSubmitting?: boolean;
  errorMessage?: string;
  onClearError?(): void;
};

type RegisterFormErrors = {
  username?: string;
  password?: string;
  confirmPassword?: string;
};

function validateUsername(
  value: string,
): string | undefined {
  if (!value) {
    return "Username is required.";
  }

  if (value.length < 3) {
    return "Username must be at least 3 characters.";
  }

  if (value.length > 50) {
    return "Username must be 50 characters or fewer.";
  }

  if (!/^[A-Za-z0-9_-]+$/.test(value)) {
    return "Username may contain only letters, numbers, underscores, and hyphens.";
  }

  return undefined;
}

function getPasswordChecks(password: string) {
  return {
    length: password.length >= 12,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };
}

function validatePassword(
  password: string,
): string | undefined {
  if (!password) {
    return "Password is required.";
  }

  const checks =
    getPasswordChecks(password);

  if (!checks.length) {
    return "Password must be at least 12 characters.";
  }

  if (!checks.uppercase) {
    return "Password must contain an uppercase letter.";
  }

  if (!checks.lowercase) {
    return "Password must contain a lowercase letter.";
  }

  if (!checks.number) {
    return "Password must contain a number.";
  }

  if (!checks.special) {
    return "Password must contain a special character.";
  }

  return undefined;
}

export function RegisterForm({
  onSubmit,
  isSubmitting = false,
  errorMessage,
  onClearError,
}: RegisterFormProps) {
  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [errors, setErrors] =
    useState<RegisterFormErrors>({});

  const passwordChecks = useMemo(
    () => getPasswordChecks(password),
    [password],
  );

  function validate():
    RegisterFormErrors {
    const nextErrors:
      RegisterFormErrors = {};

    const normalizedUsername =
      username.trim();

    nextErrors.username =
      validateUsername(
        normalizedUsername,
      );

    nextErrors.password =
      validatePassword(password);

    if (!confirmPassword) {
      nextErrors.confirmPassword =
        "Please confirm your password.";
    } else if (
      password !== confirmPassword
    ) {
      nextErrors.confirmPassword =
        "Passwords do not match.";
    }

    return nextErrors;
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const nextErrors = validate();

    setErrors(nextErrors);

    if (
      nextErrors.username ||
      nextErrors.password ||
      nextErrors.confirmPassword
    ) {
      return;
    }

    await onSubmit({
      username: username.trim(),
      password,
    });
  }

  return (
    <form
      className="auth-login-form"
      onSubmit={handleSubmit}
      noValidate
    >
      {errorMessage ? (
        <div
          className="auth-login-form__error"
          role="alert"
        >
          {errorMessage}
        </div>
      ) : null}

      <FormField
        id="register-username"
        label="Username"
        error={errors.username}
        required
      >
        <Input
          id="register-username"
          name="username"
          type="text"
          value={username}
          autoComplete="username"
          placeholder="your-username"
          disabled={isSubmitting}
          hasError={Boolean(
            errors.username,
          )}
          onChange={(event) => {
            setUsername(
              event.target.value,
            );

            if (errors.username) {
              setErrors(
                (current) => ({
                  ...current,
                  username: undefined,
                }),
              );
            }

            onClearError?.();
          }}
        />
      </FormField>

      <FormField
        id="register-password"
        label="Password"
        error={errors.password}
        required
      >
        <Input
          id="register-password"
          name="password"
          type="password"
          value={password}
          autoComplete="new-password"
          disabled={isSubmitting}
          hasError={Boolean(
            errors.password,
          )}
          onChange={(event) => {
            setPassword(
              event.target.value,
            );

            if (errors.password) {
              setErrors(
                (current) => ({
                  ...current,
                  password: undefined,
                }),
              );
            }

            onClearError?.();
          }}
        />
      </FormField>

      <div className="auth-password-rules">
        <strong>
          Password requirements
        </strong>

        <ul>
          <li
            className={
              passwordChecks.length
                ? "is-valid"
                : ""
            }
          >
            At least 12 characters
          </li>

          <li
            className={
              passwordChecks.uppercase
                ? "is-valid"
                : ""
            }
          >
            One uppercase letter
          </li>

          <li
            className={
              passwordChecks.lowercase
                ? "is-valid"
                : ""
            }
          >
            One lowercase letter
          </li>

          <li
            className={
              passwordChecks.number
                ? "is-valid"
                : ""
            }
          >
            One number
          </li>

          <li
            className={
              passwordChecks.special
                ? "is-valid"
                : ""
            }
          >
            One special character
          </li>
        </ul>
      </div>

      <FormField
        id="register-confirm-password"
        label="Confirm Password"
        error={
          errors.confirmPassword
        }
        required
      >
        <Input
          id="register-confirm-password"
          name="confirmPassword"
          type="password"
          value={confirmPassword}
          autoComplete="new-password"
          disabled={isSubmitting}
          hasError={Boolean(
            errors.confirmPassword,
          )}
          onChange={(event) => {
            setConfirmPassword(
              event.target.value,
            );

            if (
              errors.confirmPassword
            ) {
              setErrors(
                (current) => ({
                  ...current,
                  confirmPassword:
                    undefined,
                }),
              );
            }

            onClearError?.();
          }}
        />
      </FormField>

      <Button
        type="submit"
        isLoading={isSubmitting}
        loadingLabel="Creating account..."
        className="auth-login-form__submit"
      >
        Create Account
      </Button>
    </form>
  );
}