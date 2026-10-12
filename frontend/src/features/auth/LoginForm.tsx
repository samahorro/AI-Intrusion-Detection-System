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
  username: string;
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
  username?: string;
  password?: string;
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

export function LoginForm({
  onSubmit,
  isSubmitting = false,
  errorMessage,
  onClearError,
}: LoginFormProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [errors, setErrors] =
    useState<LoginFormErrors>({});

  function validate(): LoginFormErrors {
    const nextErrors: LoginFormErrors = {};
    const normalizedUsername = username.trim();

    nextErrors.username =
      validateUsername(normalizedUsername);

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
      nextErrors.username ||
      nextErrors.password
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
        id="login-username"
        label="Username"
        error={errors.username}
        required
      >
        <Input
          id="login-username"
          name="username"
          type="text"
          value={username}
          autoComplete="username"
          placeholder="your-username"
          disabled={isSubmitting}
          hasError={Boolean(errors.username)}
          aria-describedby={
            errors.username
              ? "login-username-error"
              : undefined
          }
          onChange={(event) => {
            setUsername(event.target.value);

            if (errors.username) {
              setErrors((current) => ({
                ...current,
                username: undefined,
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
