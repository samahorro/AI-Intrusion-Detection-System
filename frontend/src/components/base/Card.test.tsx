import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { Card } from "./Card";

afterEach(cleanup);

describe("Card", () => {
  it("renders a titled region with its description and contents", () => {
    render(
      <Card title="Connection health" description="Latest network status">
        <span>Connected</span>
      </Card>,
    );

    expect(screen.getByRole("heading", { name: "Connection health" })).toBeInTheDocument();
    expect(screen.getByText("Latest network status")).toBeInTheDocument();
    expect(screen.getByText("Connected")).toBeInTheDocument();
  });

  it("renders untitled content without an empty header", () => {
    render(<Card>Basic information</Card>);

    expect(screen.getByText("Basic information")).toBeInTheDocument();
    expect(screen.queryByRole("heading")).not.toBeInTheDocument();
  });

  it("forwards native section attributes and custom classes", () => {
    render(<Card aria-label="Activity" data-testid="activity" className="custom-card">Activity details</Card>);

    const card = screen.getByRole("region", { name: "Activity" });
    expect(card).toHaveClass("base-card", "custom-card");
    expect(card).toHaveAttribute("data-testid", "activity");
  });
});
