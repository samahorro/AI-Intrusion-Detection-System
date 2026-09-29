import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";

import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import { LoginForm } from "./LoginForm";

afterEach(() => {
  cleanup();
});

describe("LoginForm", () => {
  it("shows required field errors", async () => {
    const onSubmit = vi.fn();

    render(
      <LoginForm onSubmit={onSubmit} />,
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign in",
      }),
    );

    expect(
      await screen.findByText(
        "Email is required.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Password is required.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects an invalid email address", async () => {
    const onSubmit = vi.fn();

    render(
      <LoginForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/email/i),
      {
        target: {
          value: "invalid-email",
        },
      },
    );

    fireEvent.change(
      screen.getByLabelText(/password/i),
      {
        target: {
          value: "password123",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign in",
      }),
    );

    expect(
      await screen.findByText(
        "Enter a valid email address.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits normalized credentials", async () => {
    const onSubmit = vi.fn(
      async () => undefined,
    );

    render(
      <LoginForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/email/i),
      {
        target: {
          value: "  demo@example.com  ",
        },
      },
    );

    fireEvent.change(
      screen.getByLabelText(/password/i),
      {
        target: {
          value: "demo-password",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign in",
      }),
    );

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: "demo@example.com",
        password: "demo-password",
      });
    });
  });

  it("disables controls while submitting", () => {
    render(
      <LoginForm
        onSubmit={async () => undefined}
        isSubmitting
      />,
    );

    expect(
      screen.getByLabelText(/email/i),
    ).toBeDisabled();

    expect(
      screen.getByLabelText(/password/i),
    ).toBeDisabled();

    expect(
      screen.getByRole("button", {
        name: "Signing in...",
      }),
    ).toBeDisabled();
  });

  it("displays authentication errors", () => {
    render(
      <LoginForm
        onSubmit={async () => undefined}
        errorMessage="The email or password is incorrect."
      />,
    );

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent(
      "The email or password is incorrect.",
    );
  });
});
