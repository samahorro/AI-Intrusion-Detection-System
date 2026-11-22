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

import { RegisterForm } from "./RegisterForm";

afterEach(() => {
  cleanup();
});

function getPasswordInput() {
  return screen.getByLabelText(
    /password/i,
    {
      selector: 'input[name="password"]',
    },
  );
}

function getConfirmPasswordInput() {
  return screen.getByLabelText(
    /confirm password/i,
  );
}

describe("RegisterForm", () => {
  it("shows required field errors", async () => {
    const onSubmit = vi.fn();

    render(
      <RegisterForm onSubmit={onSubmit} />,
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
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

    expect(
      screen.getByText(
        "Please confirm your password.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects a username with unsupported characters", async () => {
    const onSubmit = vi.fn();

    render(
      <RegisterForm onSubmit={onSubmit} />,
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
      getPasswordInput(),
      {
        target: {
          value: "StrongPassword1!",
        },
      },
    );

    fireEvent.change(
      getConfirmPasswordInput(),
      {
        target: {
          value: "StrongPassword1!",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
      }),
    );

    expect(
      await screen.findByText(
        "Username may contain only letters, numbers, underscores, and hyphens.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects a password shorter than 12 characters", async () => {
    const onSubmit = vi.fn();

    render(
      <RegisterForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/username/i),
      {
        target: {
          value: "demo_user",
        },
      },
    );

    fireEvent.change(
      getPasswordInput(),
      {
        target: {
          value: "Short1!",
        },
      },
    );

    fireEvent.change(
      getConfirmPasswordInput(),
      {
        target: {
          value: "Short1!",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
      }),
    );

    expect(
      await screen.findByText(
        "Password must be at least 12 characters.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects a password without an uppercase letter", async () => {
    const onSubmit = vi.fn();

    render(
      <RegisterForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/username/i),
      {
        target: {
          value: "demo_user",
        },
      },
    );

    fireEvent.change(
      getPasswordInput(),
      {
        target: {
          value: "strongpassword1!",
        },
      },
    );

    fireEvent.change(
      getConfirmPasswordInput(),
      {
        target: {
          value: "strongpassword1!",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
      }),
    );

    expect(
      await screen.findByText(
        "Password must contain an uppercase letter.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects a password without a lowercase letter", async () => {
    const onSubmit = vi.fn();

    render(
      <RegisterForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/username/i),
      {
        target: {
          value: "demo_user",
        },
      },
    );

    fireEvent.change(
      getPasswordInput(),
      {
        target: {
          value: "STRONGPASSWORD1!",
        },
      },
    );

    fireEvent.change(
      getConfirmPasswordInput(),
      {
        target: {
          value: "STRONGPASSWORD1!",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
      }),
    );

    expect(
      await screen.findByText(
        "Password must contain a lowercase letter.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects a password without a number", async () => {
    const onSubmit = vi.fn();

    render(
      <RegisterForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/username/i),
      {
        target: {
          value: "demo_user",
        },
      },
    );

    fireEvent.change(
      getPasswordInput(),
      {
        target: {
          value: "StrongPassword!",
        },
      },
    );

    fireEvent.change(
      getConfirmPasswordInput(),
      {
        target: {
          value: "StrongPassword!",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
      }),
    );

    expect(
      await screen.findByText(
        "Password must contain a number.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects a password without a special character", async () => {
    const onSubmit = vi.fn();

    render(
      <RegisterForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/username/i),
      {
        target: {
          value: "demo_user",
        },
      },
    );

    fireEvent.change(
      getPasswordInput(),
      {
        target: {
          value: "StrongPassword1",
        },
      },
    );

    fireEvent.change(
      getConfirmPasswordInput(),
      {
        target: {
          value: "StrongPassword1",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
      }),
    );

    expect(
      await screen.findByText(
        "Password must contain a special character.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects mismatched passwords", async () => {
    const onSubmit = vi.fn();

    render(
      <RegisterForm onSubmit={onSubmit} />,
    );

    fireEvent.change(
      screen.getByLabelText(/username/i),
      {
        target: {
          value: "demo_user",
        },
      },
    );

    fireEvent.change(
      getPasswordInput(),
      {
        target: {
          value: "StrongPassword1!",
        },
      },
    );

    fireEvent.change(
      getConfirmPasswordInput(),
      {
        target: {
          value: "DifferentPassword1!",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
      }),
    );

    expect(
      await screen.findByText(
        "Passwords do not match.",
      ),
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits valid normalized credentials", async () => {
    const onSubmit = vi.fn(
      async () => undefined,
    );

    render(
      <RegisterForm onSubmit={onSubmit} />,
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
      getPasswordInput(),
      {
        target: {
          value: "StrongPassword1!",
        },
      },
    );

    fireEvent.change(
      getConfirmPasswordInput(),
      {
        target: {
          value: "StrongPassword1!",
        },
      },
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Create Account",
      }),
    );

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        username: "demo_user",
        password: "StrongPassword1!",
      });
    });
  });

  it("disables controls while submitting", () => {
    render(
      <RegisterForm
        onSubmit={async () => undefined}
        isSubmitting
      />,
    );

    expect(
      screen.getByLabelText(/username/i),
    ).toBeDisabled();

    expect(
      getPasswordInput(),
    ).toBeDisabled();

    expect(
      getConfirmPasswordInput(),
    ).toBeDisabled();

    expect(
      screen.getByRole("button", {
        name: "Creating account...",
      }),
    ).toBeDisabled();
  });

  it("displays registration errors", () => {
    render(
      <RegisterForm
        onSubmit={async () => undefined}
        errorMessage="Username already exists."
      />,
    );

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent(
      "Username already exists.",
    );
  });
});