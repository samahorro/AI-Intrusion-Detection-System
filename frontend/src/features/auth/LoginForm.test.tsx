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
        "Username is required.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Password is required.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects a username with unsupported characters", async () => {
    const onSubmit = vi.fn();

    render(
      <LoginForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/username/i),
      {
        target: {
          value: "invalid@example.com",
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
        "Username may contain only letters, numbers, underscores, and hyphens.",
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
      screen.getByLabelText(/username/i),
      {
        target: {
          value: "  demo_user  ",
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
        username: "demo_user",
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
      screen.getByLabelText(/username/i),
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
        errorMessage="The username or password is incorrect."
      />,
    );

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent(
      "The username or password is incorrect.",
    );
  });
});
