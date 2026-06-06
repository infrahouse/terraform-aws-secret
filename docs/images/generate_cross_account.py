#!/usr/bin/env python3
"""Generate cross-account secret access Excalidraw diagram for terraform-aws-secret module."""

import json
import os
from typing import Any, Dict, List, Optional, Tuple


def make_id(name: str) -> str:
    """Create a descriptive ID from a name."""
    return name


class ExcalidrawBuilder:
    """Builds an Excalidraw JSON document element by element."""

    def __init__(self) -> None:
        self.elements: List[Dict[str, Any]] = []
        self._seed = 1000
        self._index_counter = 0

    def _next_seed(self) -> int:
        """Return next seed value."""
        self._seed += 1
        return self._seed

    def _next_index(self) -> str:
        """Return next index value like a0, a1, ..."""
        idx = f"a{self._index_counter}"
        self._index_counter += 1
        return idx

    def _base_props(
        self,
        elem_id: str,
        elem_type: str,
        x: int,
        y: int,
        width: int,
        height: int,
        stroke_color: str = "#1e1e1e",
        bg_color: str = "transparent",
        fill_style: str = "solid",
        stroke_width: int = 2,
        stroke_style: str = "solid",
        roughness: int = 1,
        opacity: int = 100,
        group_ids: Optional[List[str]] = None,
        bound_elements: Optional[List[Dict[str, str]]] = None,
        roundness: Optional[Dict[str, int]] = None,
        locked: bool = False,
    ) -> Dict[str, Any]:
        """Return the base properties every element needs."""
        return {
            "id": elem_id,
            "type": elem_type,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "strokeColor": stroke_color,
            "backgroundColor": bg_color,
            "fillStyle": fill_style,
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "roughness": roughness,
            "opacity": opacity,
            "angle": 0,
            "seed": self._next_seed(),
            "version": 1,
            "isDeleted": False,
            "boundElements": bound_elements or [],
            "link": None,
            "locked": locked,
            "groupIds": group_ids or [],
            "frameId": None,
            "roundness": roundness,
            "index": self._next_index(),
        }

    def add_rectangle(
        self,
        elem_id: str,
        x: int,
        y: int,
        width: int,
        height: int,
        bg_color: str = "transparent",
        stroke_color: str = "#1e1e1e",
        stroke_width: int = 2,
        stroke_style: str = "solid",
        fill_style: str = "solid",
        roughness: int = 1,
        group_ids: Optional[List[str]] = None,
        bound_elements: Optional[List[Dict[str, str]]] = None,
        roundness_type: int = 3,
    ) -> Dict[str, Any]:
        """Add a rectangle element."""
        props = self._base_props(
            elem_id,
            "rectangle",
            x,
            y,
            width,
            height,
            stroke_color=stroke_color,
            bg_color=bg_color,
            fill_style=fill_style,
            stroke_width=stroke_width,
            stroke_style=stroke_style,
            roughness=roughness,
            group_ids=group_ids,
            bound_elements=bound_elements,
            roundness={"type": roundness_type},
        )
        self.elements.append(props)
        return props

    def add_text(
        self,
        elem_id: str,
        x: int,
        y: int,
        text: str,
        font_size: int = 16,
        font_family: int = 3,
        text_align: str = "center",
        vertical_align: str = "middle",
        width: Optional[int] = None,
        height: Optional[int] = None,
        container_id: Optional[str] = None,
        stroke_color: str = "#1e1e1e",
        group_ids: Optional[List[str]] = None,
        auto_resize: bool = True,
    ) -> Dict[str, Any]:
        """Add a text element."""
        line_height = 1.2
        line_count = text.count("\n") + 1
        calc_height = height or int(font_size * line_height * line_count)
        calc_width = width or int(len(max(text.split("\n"), key=len)) * font_size * 0.6)

        props = self._base_props(
            elem_id,
            "text",
            x,
            y,
            calc_width,
            calc_height,
            stroke_color=stroke_color,
            group_ids=group_ids,
        )
        props.update(
            {
                "text": text,
                "originalText": text,
                "fontSize": font_size,
                "fontFamily": font_family,
                "textAlign": text_align,
                "verticalAlign": vertical_align,
                "baseline": int(font_size * 0.8),
                "lineHeight": line_height,
                "containerId": container_id,
                "autoResize": auto_resize,
            }
        )
        self.elements.append(props)
        return props

    def add_arrow(
        self,
        elem_id: str,
        x: int,
        y: int,
        points: List[List[int]],
        stroke_color: str = "#1e1e1e",
        stroke_style: str = "solid",
        stroke_width: int = 2,
        start_binding: Optional[Dict[str, Any]] = None,
        end_binding: Optional[Dict[str, Any]] = None,
        start_arrowhead: Optional[str] = None,
        end_arrowhead: str = "arrow",
        group_ids: Optional[List[str]] = None,
        bound_elements: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Add an arrow element."""
        # Calculate bounding box from points
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        width = max_x - min_x
        height = max_y - min_y

        props = self._base_props(
            elem_id,
            "arrow",
            x,
            y,
            width,
            max(height, 1),
            stroke_color=stroke_color,
            stroke_style=stroke_style,
            stroke_width=stroke_width,
            group_ids=group_ids,
            bound_elements=bound_elements,
            roundness={"type": 2},
        )
        props.update(
            {
                "points": points,
                "startBinding": start_binding,
                "endBinding": end_binding,
                "startArrowhead": start_arrowhead,
                "endArrowhead": end_arrowhead,
                "elbowed": False,
            }
        )
        self.elements.append(props)
        return props

    def add_labeled_box(
        self,
        box_id: str,
        text_id: str,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        bg_color: str = "transparent",
        stroke_color: str = "#1e1e1e",
        font_size: int = 16,
        stroke_width: int = 2,
        group_ids: Optional[List[str]] = None,
        text_color: str = "#1e1e1e",
        roundness_type: int = 3,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Add a rectangle with bound text label inside."""
        rect = self.add_rectangle(
            box_id,
            x,
            y,
            width,
            height,
            bg_color=bg_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            group_ids=group_ids,
            bound_elements=[{"id": text_id, "type": "text"}],
            roundness_type=roundness_type,
        )

        line_height = 1.2
        line_count = label.count("\n") + 1
        text_height = int(font_size * line_height * line_count)
        text_y = y + (height - text_height) // 2
        text_width = width - 10

        txt = self.add_text(
            text_id,
            x + 5,
            text_y,
            label,
            font_size=font_size,
            container_id=box_id,
            width=text_width,
            height=text_height,
            stroke_color=text_color,
            group_ids=group_ids,
        )
        return rect, txt

    def build(self) -> Dict[str, Any]:
        """Build the final Excalidraw document."""
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://app.excalidraw.com",
            "elements": self.elements,
            "appState": {
                "gridSize": 20,
                "gridStep": 5,
                "gridModeEnabled": False,
                "viewBackgroundColor": "#ffffff",
            },
            "files": {},
        }


def generate_diagram() -> Dict[str, Any]:
    """Generate the cross-account secret access diagram."""
    b = ExcalidrawBuilder()

    # Layout constants
    acct_a_x = 20
    acct_b_x = 580
    acct_w = 520
    acct_h = 520
    acct_y = 60

    # ---- Diagram title ----
    b.add_text(
        "title",
        200,
        10,
        "Cross-Account Secret Access with Customer-Managed KMS Key (CMK)",
        font_size=20,
        text_align="center",
        vertical_align="top",
        width=720,
        height=28,
    )

    # ==================================================================
    # Account A (Owner) - light green frame
    # ==================================================================
    b.add_rectangle(
        "account_a_frame",
        acct_a_x,
        acct_y,
        acct_w,
        acct_h,
        bg_color="#ebfbee",
        stroke_color="#2b8a3e",
        stroke_width=2,
        fill_style="solid",
    )
    b.add_text(
        "account_a_title",
        acct_a_x + 10,
        acct_y + 10,
        "Account A (Owner)",
        font_size=20,
        text_align="left",
        vertical_align="top",
        width=250,
        height=24,
        stroke_color="#2b8a3e",
    )

    # Terraform box
    tf_x = acct_a_x + 30
    tf_y = acct_y + 60
    b.add_labeled_box(
        "terraform_box",
        "terraform_label",
        tf_x,
        tf_y,
        180,
        50,
        "terraform-aws-secret",
        bg_color="#e7f5ff",
        stroke_color="#1971c2",
        font_size=14,
        text_color="#1971c2",
    )

    # Secret box
    secret_x = acct_a_x + 30
    secret_y = acct_y + 170
    b.add_labeled_box(
        "secret_box",
        "secret_label",
        secret_x,
        secret_y,
        200,
        50,
        "Secrets Manager Secret",
        bg_color="#ffe3e3",
        stroke_color="#c92a2a",
        font_size=14,
        text_color="#c92a2a",
    )

    # Resource policy box (under secret)
    rp_x = secret_x
    rp_y = secret_y + 60
    b.add_labeled_box(
        "resource_policy_box",
        "resource_policy_label",
        rp_x,
        rp_y,
        200,
        40,
        "Resource Policy",
        bg_color="#f8f9fa",
        stroke_color="#868e96",
        font_size=12,
        text_color="#495057",
    )
    # Resource policy detail
    b.add_text(
        "rp_detail",
        rp_x,
        rp_y + 45,
        "Grants consumer-role:\nGetSecretValue\nPutSecretValue\nDescribeSecret",
        font_size=11,
        text_align="left",
        vertical_align="top",
        width=200,
        height=55,
        stroke_color="#495057",
    )

    # KMS CMK box
    kms_x = acct_a_x + 280
    kms_y = acct_y + 170
    b.add_labeled_box(
        "kms_box",
        "kms_label",
        kms_x,
        kms_y,
        200,
        50,
        "KMS CMK\n(auto-created by module)",
        bg_color="#e5dbff",
        stroke_color="#7048e8",
        font_size=14,
        text_color="#7048e8",
    )

    # Key policy box (under KMS)
    kp_x = kms_x
    kp_y = kms_y + 60
    b.add_labeled_box(
        "key_policy_box",
        "key_policy_label",
        kp_x,
        kp_y,
        200,
        40,
        "Key Policy",
        bg_color="#f8f9fa",
        stroke_color="#868e96",
        font_size=12,
        text_color="#495057",
    )
    # Key policy detail
    b.add_text(
        "kp_detail",
        kp_x,
        kp_y + 45,
        "Grants consumer-role:\nkms:Decrypt\nkms:GenerateDataKey*",
        font_size=11,
        text_align="left",
        vertical_align="top",
        width=200,
        height=45,
        stroke_color="#495057",
    )

    # ==================================================================
    # Account B (Consumer) - light blue frame
    # ==================================================================
    b.add_rectangle(
        "account_b_frame",
        acct_b_x,
        acct_y,
        acct_w,
        acct_h,
        bg_color="#e7f5ff",
        stroke_color="#1971c2",
        stroke_width=2,
        fill_style="solid",
    )
    b.add_text(
        "account_b_title",
        acct_b_x + 10,
        acct_y + 10,
        "Account B (Consumer)",
        font_size=20,
        text_align="left",
        vertical_align="top",
        width=270,
        height=24,
        stroke_color="#1971c2",
    )

    # Consumer IAM Role box
    role_x = acct_b_x + 40
    role_y = acct_y + 70
    b.add_labeled_box(
        "consumer_role_box",
        "consumer_role_label",
        role_x,
        role_y,
        180,
        50,
        "IAM Role: consumer-role",
        bg_color="#fff4e6",
        stroke_color="#e8590c",
        font_size=14,
        text_color="#e8590c",
    )

    # Trust policy box
    trust_x = role_x + 220
    trust_y = role_y
    b.add_labeled_box(
        "trust_policy_box",
        "trust_policy_label",
        trust_x,
        trust_y,
        220,
        50,
        "Trust Policy",
        bg_color="#f8f9fa",
        stroke_color="#868e96",
        font_size=12,
        text_color="#495057",
    )
    b.add_text(
        "trust_detail",
        trust_x,
        trust_y + 55,
        "Allows sts:AssumeRole\nfrom trusted principals",
        font_size=11,
        text_align="left",
        vertical_align="top",
        width=220,
        height=30,
        stroke_color="#495057",
    )

    # Identity policy - Secrets Manager permissions
    idp_sm_x = role_x
    idp_sm_y = role_y + 100
    b.add_labeled_box(
        "identity_policy_sm_box",
        "identity_policy_sm_title",
        idp_sm_x,
        idp_sm_y,
        440,
        40,
        "Identity Policy - Secrets Manager Permissions",
        bg_color="#f8f9fa",
        stroke_color="#868e96",
        font_size=13,
        text_color="#495057",
    )
    b.add_text(
        "idp_sm_detail",
        idp_sm_x + 10,
        idp_sm_y + 45,
        "Actions: secretsmanager:GetSecretValue,\n"
        "         PutSecretValue, DescribeSecret\n"
        "Resource: arn:aws:secretsmanager:<region>:<AcctA>:secret:<name>",
        font_size=11,
        text_align="left",
        vertical_align="top",
        width=430,
        height=45,
        stroke_color="#495057",
    )

    # Identity policy - KMS permissions
    idp_kms_x = role_x
    idp_kms_y = idp_sm_y + 105
    b.add_labeled_box(
        "identity_policy_kms_box",
        "identity_policy_kms_title",
        idp_kms_x,
        idp_kms_y,
        440,
        40,
        "Identity Policy - KMS Permissions",
        bg_color="#f8f9fa",
        stroke_color="#868e96",
        font_size=13,
        text_color="#495057",
    )
    b.add_text(
        "idp_kms_detail",
        idp_kms_x + 10,
        idp_kms_y + 45,
        "Actions: kms:Decrypt, kms:GenerateDataKey*\n"
        "Resource: arn:aws:kms:<region>:<AcctA>:key/<key-id>\n"
        "Condition: kms:ViaService =\n"
        "  secretsmanager.<region>.amazonaws.com",
        font_size=11,
        text_align="left",
        vertical_align="top",
        width=430,
        height=56,
        stroke_color="#495057",
    )

    # ==================================================================
    # Arrows
    # ==================================================================

    # Terraform -> Secret ("creates", solid)
    tf_bot_x = tf_x + 90
    tf_bot_y = tf_y + 50
    secret_top_x = secret_x + 100
    secret_top_y = secret_y
    b.add_arrow(
        "arrow_tf_to_secret",
        tf_bot_x,
        tf_bot_y,
        [[0, 0], [0, secret_top_y - tf_bot_y]],
        stroke_color="#1971c2",
        stroke_style="solid",
        stroke_width=2,
        start_binding={
            "elementId": "terraform_box",
            "focus": 0,
            "gap": 1,
            "fixedPoint": None,
        },
        end_binding={
            "elementId": "secret_box",
            "focus": 0,
            "gap": 1,
            "fixedPoint": None,
        },
        bound_elements=[{"id": "arrow_tf_to_secret_label", "type": "text"}],
    )
    b.add_text(
        "arrow_tf_to_secret_label",
        tf_bot_x + 5,
        tf_bot_y + (secret_top_y - tf_bot_y) // 2 - 8,
        "creates",
        font_size=12,
        text_align="left",
        vertical_align="middle",
        width=50,
        height=15,
        container_id="arrow_tf_to_secret",
        stroke_color="#1971c2",
    )

    # Terraform -> KMS CMK ("creates", solid — module auto-creates the CMK)
    tf_right_x = tf_x + 180
    tf_right_y = tf_y + 25
    kms_top_x = kms_x + 100
    kms_top_y = kms_y
    b.add_arrow(
        "arrow_tf_to_kms",
        tf_right_x,
        tf_right_y,
        [
            [0, 0],
            [kms_top_x - tf_right_x, 0],
            [kms_top_x - tf_right_x, kms_top_y - tf_right_y],
        ],
        stroke_color="#1971c2",
        stroke_style="solid",
        stroke_width=2,
        start_binding={
            "elementId": "terraform_box",
            "focus": 0,
            "gap": 1,
            "fixedPoint": None,
        },
        end_binding={
            "elementId": "kms_box",
            "focus": 0,
            "gap": 1,
            "fixedPoint": None,
        },
        bound_elements=[{"id": "arrow_tf_to_kms_label", "type": "text"}],
    )
    b.add_text(
        "arrow_tf_to_kms_label",
        tf_right_x + (kms_top_x - tf_right_x) // 2 - 40,
        tf_right_y - 18,
        "creates",
        font_size=12,
        text_align="center",
        vertical_align="middle",
        width=50,
        height=15,
        container_id="arrow_tf_to_kms",
        stroke_color="#1971c2",
    )

    # Consumer Role -> Secret ("GetSecretValue / PutSecretValue", dashed)
    cr_left_x = role_x
    cr_left_y = role_y + 25
    secret_right_x = secret_x + 200
    secret_right_y = secret_y + 25
    b.add_arrow(
        "arrow_role_to_secret",
        cr_left_x,
        cr_left_y,
        [
            [0, 0],
            [-(cr_left_x - secret_right_x), secret_right_y - cr_left_y],
        ],
        stroke_color="#c92a2a",
        stroke_style="dashed",
        stroke_width=2,
        start_binding={
            "elementId": "consumer_role_box",
            "focus": 0,
            "gap": 1,
            "fixedPoint": None,
        },
        end_binding={
            "elementId": "secret_box",
            "focus": 0,
            "gap": 1,
            "fixedPoint": None,
        },
        bound_elements=[
            {"id": "arrow_role_to_secret_label", "type": "text"}
        ],
    )
    b.add_text(
        "arrow_role_to_secret_label",
        (cr_left_x + secret_right_x) // 2 - 80,
        (cr_left_y + secret_right_y) // 2 - 22,
        "GetSecretValue / PutSecretValue",
        font_size=11,
        text_align="center",
        vertical_align="middle",
        width=200,
        height=14,
        container_id="arrow_role_to_secret",
        stroke_color="#c92a2a",
    )

    # Consumer Role -> KMS CMK ("Decrypt (via SecretsManager)", dashed)
    cr2_left_x = role_x
    cr2_left_y = role_y + 40
    kms_right_x = kms_x + 200
    kms_right_y = kms_y + 25
    b.add_arrow(
        "arrow_role_to_kms",
        cr2_left_x,
        cr2_left_y,
        [
            [0, 0],
            [-(cr2_left_x - kms_right_x), kms_right_y - cr2_left_y],
        ],
        stroke_color="#7048e8",
        stroke_style="dashed",
        stroke_width=2,
        start_binding={
            "elementId": "consumer_role_box",
            "focus": 0,
            "gap": 1,
            "fixedPoint": None,
        },
        end_binding={
            "elementId": "kms_box",
            "focus": 0,
            "gap": 1,
            "fixedPoint": None,
        },
        bound_elements=[
            {"id": "arrow_role_to_kms_label", "type": "text"}
        ],
    )
    b.add_text(
        "arrow_role_to_kms_label",
        (cr2_left_x + kms_right_x) // 2 - 80,
        (cr2_left_y + kms_right_y) // 2 + 5,
        "Decrypt (via SecretsManager)",
        font_size=11,
        text_align="center",
        vertical_align="middle",
        width=190,
        height=14,
        container_id="arrow_role_to_kms",
        stroke_color="#7048e8",
    )

    return b.build()


def main() -> None:
    """Generate and write the Excalidraw JSON file."""
    diagram = generate_diagram()
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "cross-account.excalidraw")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(diagram, f, indent=2)

    # Validate the output
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = []
    for elem in data["elements"]:
        if elem["type"] == "text":
            if "originalText" not in elem or elem["originalText"] is None:
                errors.append(
                    f"Text element '{elem['id']}' missing originalText"
                )
            if "height" not in elem or elem["height"] is None:
                errors.append(
                    f"Text element '{elem['id']}' has null height"
                )
        required = [
            "id",
            "type",
            "x",
            "y",
            "width",
            "height",
            "strokeColor",
            "backgroundColor",
            "fillStyle",
            "strokeWidth",
            "strokeStyle",
            "roughness",
            "opacity",
            "angle",
            "seed",
            "version",
            "isDeleted",
            "boundElements",
            "link",
            "locked",
            "groupIds",
            "frameId",
            "roundness",
            "index",
        ]
        for prop in required:
            if prop not in elem:
                errors.append(
                    f"Element '{elem['id']}' missing property '{prop}'"
                )

    if errors:
        print("VALIDATION ERRORS:")
        for err in errors:
            print(f"  - {err}")
    else:
        elem_count = len(data["elements"])
        text_count = sum(
            1 for e in data["elements"] if e["type"] == "text"
        )
        rect_count = sum(
            1 for e in data["elements"] if e["type"] == "rectangle"
        )
        arrow_count = sum(
            1 for e in data["elements"] if e["type"] == "arrow"
        )
        print(f"Generated {output_path}")
        print(
            f"  {elem_count} elements: "
            f"{rect_count} rectangles, "
            f"{text_count} texts, "
            f"{arrow_count} arrows"
        )
        print("  All validations passed.")


if __name__ == "__main__":
    main()
