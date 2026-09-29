import {
  useState,
  type FormEvent,
} from "react";

import {
  Button,
  FormField,
  Input,
} from "../../components/base";

export type LoginFormValues = {
  email: string;
  password: string;
};

export type LoginFormProps = {
  onSubmit(
    values: LoginFormValues,
  ): Promise<void>;
  isSubmitting?: boolean;
  errorMessage?: string;
  onClearError?(): void;
};

type LoginFormErrors = {
  email?: string;
  password?: string;
};

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export function LoginForm({
  onSubmit,
  isSubmitting = false,
  errorMessage,
  onClearError,
}: LoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [errors, setErrors] =
    useState<LoginFormErrors>({});

  function validate(): LoginFormErrors {
    const nextErrors: LoginFormErrors = {};
    const normalizedEmail = email.trim();

    if (!normalizedEmail) {
      nextErrors.email = "Email is required.";
    } else if (!isValidEmail(normalizedEmail)) {
      nextErrors.email =
        "Enter a valid email address.";
    }

    if (!password) {
      nextErrors.password =
        "Password is required.";
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
      nextErrors.email ||
      nextErrors.password
    ) {
      return;
    }

    await onSubmit({
      email: email.trim(),
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
        id="login-email"
        label="Email"
        error={errors.email}
        required
      >
        <Input
          id="login-email"
          name="email"
          type="email"
          value={email}
          autoComplete="email"
          placeholder="you@example.com"
          disabled={isSubmitting}
          hasError={Boolean(errors.email)}
          aria-describedby={
            errors.email
              ? "login-email-error"
              : undefined
          }
          onChange={(event) => {
            setEmail(event.target.value);

            if (errors.email) {
              setErrors((current) => ({
                ...current,
                email: undefined,
              }));
            }

            onClearError?.();
          }}
        />
      </FormField>

      <FormField
        id="login-password"
        label="Password"
        error={errors.password}
        required
      >
        <Input
          id="login-password"
          name="password"
          type="password"
          value={password}
          autoComplete="current-password"
          disabled={isSubmitting}
          hasError={Boolean(errors.password)}
          aria-describedby={
            errors.password
              ? "login-password-error"
              : undefined
          }
          onChange={(event) => {
            setPassword(event.target.value);

            if (errors.password) {
              setErrors((current) => ({
                ...current,
                password: undefined,
              }));
            }

            onClearError?.();
          }}
        />
      </FormField>

      <Button
        type="submit"
        isLoading={isSubmitting}
        loadingLabel="Signing in..."
        className="auth-login-form__submit"
      >
        Sign in
      </Button>
    </form>
  );
}
