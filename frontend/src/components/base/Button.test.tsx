import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Button } from "./Button";

afterEach(cleanup);

describe("Button", () => {
  it("renders children with safe default button type", () => {
    render(<Button>Save settings</Button>);

    const button = screen.getByRole("button", { name: "Save settings" });
    expect(button).toHaveAttribute("type", "button");
    expect(button).toHaveClass("base-button", "base-button--primary");
  });

  it("forwards click events and native button attributes", () => {
    const onClick = vi.fn();
    render(
      <Button type="submit" variant="secondary" title="Save" onClick={onClick}>
        Save
      </Button>,
    );

    const button = screen.getByRole("button", { name: "Save" });
    expect(button).toHaveAttribute("type", "submit");
    expect(button).toHaveAttribute("title", "Save");
    expect(button).toHaveClass("base-button--secondary");
    fireEvent.click(button);
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("does not fire clicks while disabled", () => {
    const onClick = vi.fn();
    render(<Button disabled onClick={onClick}>Delete</Button>);

    const button = screen.getByRole("button", { name: "Delete" });
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it("disables interaction and announces its loading state", () => {
    const onClick = vi.fn();
    render(
      <Button isLoading loadingLabel="Saving..." onClick={onClick}>
        Save
      </Button>,
    );

    const button = screen.getByRole("button", { name: "Saving..." });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");
    expect(screen.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
    fireEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });
});
