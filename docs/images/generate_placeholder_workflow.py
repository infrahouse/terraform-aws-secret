#!/usr/bin/env python3
"""Generate placeholder workflow diagram for terraform-aws-secret module."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# Colors
tf_color = "#7B42BC"  # Terraform purple
aws_color = "#FF9900"  # AWS orange
admin_color = "#232F3E"  # AWS dark

# Participants
participants = [
    (2, 9, "Terraform", tf_color),
    (5, 9, "Secrets Manager", aws_color),
    (8, 9, "Admin", admin_color),
]

for x, y, label, color in participants:
    box = FancyBboxPatch(
        (x - 0.8, y - 0.3),
        1.6,
        0.6,
        boxstyle="round,pad=0.05",
        facecolor=color,
        edgecolor="black",
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=10, color="white", weight="bold")
    # Vertical lifeline
    ax.plot([x, x], [y - 0.3, 1], color="gray", linestyle="--", linewidth=1)

# Messages (y position, from_x, to_x, label, note_x, note_text)
messages = [
    (7.5, 2, 5, "1. First PR (plan/apply): Create secret", 5, 'Value = "NoValue"'),
    (6.0, 8, 5, "2. Set real value", 5, 'Value = "real-secret"'),
    (4.5, 2, 5, "3. Second PR (plan/apply): Use real value", None, None),
    (3.5, 5, 2, "4. Returns value", 2, "Pass secret to\nother resources"),
]

for y, x1, x2, label, note_x, note_text in messages:
    # Arrow
    ax.annotate(
        "",
        xy=(x2, y),
        xytext=(x1, y),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
    )
    # Label above arrow
    mid_x = (x1 + x2) / 2
    ax.text(mid_x, y + 0.2, label, ha="center", va="bottom", fontsize=9)
    # Note
    if note_x and note_text:
        ax.text(
            note_x + 1.5,
            y - 0.3,
            note_text,
            ha="left",
            va="top",
            fontsize=8,
            style="italic",
            bbox=dict(boxstyle="round", facecolor="lightyellow", edgecolor="gray"),
        )

# Title
ax.text(5, 9.7, "Placeholder Workflow", ha="center", va="bottom", fontsize=14, weight="bold")

plt.tight_layout()
plt.savefig("placeholder-workflow.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()

print("Generated placeholder-workflow.png")
