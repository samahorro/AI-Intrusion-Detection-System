import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { FormField } from "./FormField";
import { Input } from "./Input";

afterEach(cleanup);

describe("FormField", () => {
  it("associates its label with the matching input", () => {
    render(
      <FormField id="username" label="Username">
        <Input id="username" />
      </FormField>,
    );

    expect(screen.getByRole("textbox", { name: "Username" })).toHaveAttribute("id", "username");
  });

  it("shows a required marker without adding it to the accessible label", () => {
    render(
      <FormField id="username" label="Username" required>
        <Input id="username" />
      </FormField>,
    );

    const label = screen.getByText("Username", { exact: false });
    expect(label.querySelector('[aria-hidden="true"]')).toHaveTextContent("*");
    expect(screen.getByRole("textbox", { name: "Username" })).toBeInTheDocument();
  });

  it("renders optional guidance when there is no error", () => {
    render(
      <FormField id="username" label="Username" hint="Use letters and numbers">
        <Input id="username" />
      </FormField>,
    );

    expect(screen.getByText("Use letters and numbers")).toHaveAttribute("id", "username-hint");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("replaces guidance with an announced validation error", () => {
    render(
      <FormField id="username" label="Username" hint="Use letters and numbers" error="Username is required">
        <Input id="username" hasError />
      </FormField>,
    );

    expect(screen.getByRole("alert")).toHaveAttribute("id", "username-error");
    expect(screen.getByRole("alert")).toHaveTextContent("Username is required");
    expect(screen.queryByText("Use letters and numbers")).not.toBeInTheDocument();
  });
});
