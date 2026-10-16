import { createRef } from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Input } from "./Input";

afterEach(cleanup);

describe("Input", () => {
  it("forwards standard input attributes and changes", () => {
    const onChange = vi.fn();
    render(
      <Input aria-label="Username" name="username" placeholder="Enter username" onChange={onChange} />,
    );

    const input = screen.getByRole("textbox", { name: "Username" });
    expect(input).toHaveAttribute("name", "username");
    expect(input).toHaveAttribute("placeholder", "Enter username");
    fireEvent.change(input, { target: { value: "test-user" } });
    expect(input).toHaveValue("test-user");
    expect(onChange).toHaveBeenCalledOnce();
  });

  it("marks invalid input accessibly and applies error styling", () => {
    render(<Input aria-label="Username" hasError className="custom-input" />);

    const input = screen.getByRole("textbox", { name: "Username" });
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input).toHaveClass("base-input", "base-input--error", "custom-input");
  });

  it("does not mark a valid input invalid", () => {
    render(<Input aria-label="Username" />);

    const input = screen.getByRole("textbox", { name: "Username" });
    expect(input).not.toHaveAttribute("aria-invalid");
    expect(input).not.toHaveClass("base-input--error");
  });

  it("forwards React refs and native disabled state", () => {
    const ref = createRef<HTMLInputElement>();
    render(<Input ref={ref} aria-label="Readonly identifier" disabled />);

    const input = screen.getByRole("textbox", { name: "Readonly identifier" });
    expect(ref.current).toBe(input);
    expect(input).toBeDisabled();
  });
});
