from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


KST = timezone(timedelta(hours=9))
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 960},
    "tablet": {"width": 834, "height": 1112},
    "mobile": {"width": 390, "height": 844},
}
TOUCH_TARGET_MIN_SIZE = 44
MAX_SCENE_SCREENSHOTS = 10
HIGH_FINDING_TYPES = {
    "console_error",
    "page_error",
    "request_failure",
    "broken_image",
    "horizontal_overflow",
    "overlap",
    "fixed_overlay",
    "asset_integration",
    "composition",
}


def run_visual_qa(
    *,
    html_path: Path,
    run_dir: Path,
    iteration: str,
    output_path: Path,
    timeout_seconds: int = 600,
    artifact_dir_name: str = "visual_qa",
    viewport_names: tuple[str, ...] | None = None,
) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Playwright is required for visual QA. Install it with "
            "`python -m pip install -r ./requirement.txt` and then run "
            "`python -m playwright install chromium`."
        ) from exc

    screenshots_dir = run_dir / f"iter_{iteration}" / artifact_dir_name
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    render_checks = empty_render_checks()
    design_evidence: list[dict[str, Any]] = []
    priority_findings: list[dict[str, Any]] = []
    refine_suggestions: list[str] = []
    screenshots: list[dict[str, Any]] = []
    selected_viewports = viewport_names or tuple(VIEWPORTS.keys())

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            for viewport in selected_viewports:
                size = VIEWPORTS[viewport]
                viewport_result = inspect_viewport(
                    browser=browser,
                    html_path=html_path,
                    run_dir=run_dir,
                    screenshots_dir=screenshots_dir,
                    viewport=viewport,
                    width=size["width"],
                    height=size["height"],
                    timeout_seconds=timeout_seconds,
                )
                screenshots.extend(viewport_result["screenshots"])
                merge_render_checks(render_checks, viewport_result["render_checks"])
                design_evidence.extend(viewport_result["design_evidence"])
        finally:
            browser.close()

    dedupe_render_checks(render_checks)
    design_evidence = dedupe_dicts(design_evidence)
    priority_findings.extend(priority_from_render_checks(render_checks))
    priority_findings.extend(priority_from_design_evidence(design_evidence))
    refine_suggestions.extend(build_refine_suggestions(priority_findings))
    design_review = build_design_review(design_evidence)
    status = get_status(priority_findings, design_review)

    output = {
        "status": status,
        "checked_at": datetime.now(KST).isoformat(timespec="seconds"),
        "html_path": "output/index.html",
        "viewports": list(selected_viewports),
        "screenshots": screenshots,
        "render_checks": render_checks,
        "design_review": design_review,
        "priority_findings": priority_findings,
        "refine_suggestions": refine_suggestions,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def empty_render_checks() -> dict[str, list[dict[str, Any]]]:
    return {
        "console_errors": [],
        "page_errors": [],
        "request_failures": [],
        "broken_images": [],
        "horizontal_overflow": [],
        "text_clipping": [],
        "small_touch_targets": [],
        "overlaps": [],
        "fixed_overlay_risks": [],
    }


def launch_browser(playwright: Any) -> Any:
    try:
        return playwright.chromium.launch()
    except Exception as bundled_error:
        executable_path = find_system_chromium()
        if executable_path:
            return playwright.chromium.launch(executable_path=str(executable_path))
        raise RuntimeError(
            "Playwright Chromium is not installed and no system Chrome/Edge executable was found. "
            "Run `python -m playwright install chromium`, or install Chrome/Edge locally."
        ) from bundled_error


def find_system_chromium() -> Path | None:
    roots = [
        os.environ.get("PROGRAMFILES"),
        os.environ.get("PROGRAMFILES(X86)"),
        os.environ.get("LOCALAPPDATA"),
    ]
    relative_paths = [
        Path("Google") / "Chrome" / "Application" / "chrome.exe",
        Path("Microsoft") / "Edge" / "Application" / "msedge.exe",
        Path("Chromium") / "Application" / "chrome.exe",
    ]
    for root in roots:
        if not root:
            continue
        for relative_path in relative_paths:
            candidate = Path(root) / relative_path
            if candidate.exists():
                return candidate
    return None


def inspect_viewport(
    *,
    browser: Any,
    html_path: Path,
    run_dir: Path,
    screenshots_dir: Path,
    viewport: str,
    width: int,
    height: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
    page = context.new_page()
    render_checks = empty_render_checks()
    design_evidence: list[dict[str, Any]] = []
    screenshots: list[dict[str, Any]] = []

    page.on(
        "console",
        lambda message: collect_console_error(render_checks, viewport, message),
    )
    page.on(
        "pageerror",
        lambda error: render_checks["page_errors"].append(
            {
                "viewport": viewport,
                "severity": "high",
                "message": str(error),
            }
        ),
    )
    page.on(
        "requestfailed",
        lambda request: render_checks["request_failures"].append(
            {
                "viewport": viewport,
                "severity": "high",
                "message": request.url,
            }
        ),
    )

    try:
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle", timeout=timeout_seconds * 1000)
        page.wait_for_timeout(300)
        capture_inspected_state(
            page=page,
            screenshots=screenshots,
            render_checks=render_checks,
            design_evidence=design_evidence,
            screenshots_dir=screenshots_dir,
            run_dir=run_dir,
            viewport=viewport,
            width=width,
            height=height,
            label="initial",
        )
        capture_scene_states(
            page=page,
            screenshots=screenshots,
            render_checks=render_checks,
            design_evidence=design_evidence,
            screenshots_dir=screenshots_dir,
            run_dir=run_dir,
            viewport=viewport,
            width=width,
            height=height,
        )
    finally:
        context.close()

    return {
        "screenshots": screenshots,
        "render_checks": render_checks,
        "design_evidence": design_evidence,
    }


def capture_inspected_state(
    *,
    page: Any,
    screenshots: list[dict[str, Any]],
    render_checks: dict[str, list[dict[str, Any]]],
    design_evidence: list[dict[str, Any]],
    screenshots_dir: Path,
    run_dir: Path,
    viewport: str,
    width: int,
    height: int,
    label: str,
) -> None:
    filename = f"{viewport}.png" if label == "initial" else f"{viewport}__{sanitize_capture_label(label)}.png"
    screenshot_path = screenshots_dir / filename
    page.screenshot(path=str(screenshot_path), full_page=True)
    metrics = page.evaluate(build_inspection_script())

    render_checks["broken_images"].extend(build_selector_findings(viewport, metrics["brokenImages"], "high"))
    render_checks["horizontal_overflow"].extend(
        build_selector_findings(viewport, metrics["horizontalOverflow"], "high")
    )
    render_checks["text_clipping"].extend(build_selector_findings(viewport, metrics["textClipping"], "medium"))
    render_checks["small_touch_targets"].extend(
        build_selector_findings(viewport, metrics["smallTouchTargets"], "medium")
    )
    render_checks["overlaps"].extend(build_selector_findings(viewport, metrics["overlaps"], "high"))
    render_checks["fixed_overlay_risks"].extend(
        build_selector_findings(viewport, metrics["fixedOverlayRisks"], "high")
    )

    screenshots.append(
        {
            "viewport": viewport,
            "capture_label": label,
            "path": relative_to_run(screenshot_path, run_dir),
            "width": width,
            "height": height,
        }
    )
    design_evidence.extend(build_design_evidence(viewport, metrics["designSignals"]))


def capture_scene_states(
    *,
    page: Any,
    screenshots: list[dict[str, Any]],
    render_checks: dict[str, list[dict[str, Any]]],
    design_evidence: list[dict[str, Any]],
    screenshots_dir: Path,
    run_dir: Path,
    viewport: str,
    width: int,
    height: int,
) -> None:
    targets = page.evaluate(build_scene_targets_script())
    seen_labels = {"initial"}
    for index, target in enumerate(targets[:MAX_SCENE_SCREENSHOTS], start=1):
        raw_label = target.get("sceneId") or target.get("label") or target.get("action")
        label = unique_capture_label(f"{index:02d}_{raw_label}", seen_labels)
        try:
            action = target.get("action")
            if action == "show_scene":
                page.evaluate(build_show_scene_script(), target.get("sceneId"))
            elif action == "click":
                locator = page.locator(target["selector"]).first
                locator.click(timeout=1200)
            else:
                locator = page.locator(target["selector"]).first
                locator.evaluate("element => element.scrollIntoView({ block: 'start', inline: 'nearest' })")
            page.wait_for_timeout(300)
            capture_inspected_state(
                page=page,
                screenshots=screenshots,
                render_checks=render_checks,
                design_evidence=design_evidence,
                screenshots_dir=screenshots_dir,
                run_dir=run_dir,
                viewport=viewport,
                width=width,
                height=height,
                label=label,
            )
        except Exception:
            continue


def collect_console_error(render_checks: dict[str, list[dict[str, Any]]], viewport: str, message: Any) -> None:
    if message.type != "error":
        return
    render_checks["console_errors"].append(
        {
            "viewport": viewport,
            "severity": "high",
            "message": message.text,
        }
    )


def build_selector_findings(
    viewport: str,
    items: list[dict[str, Any]],
    severity: str,
) -> list[dict[str, Any]]:
    return [
        {
            "viewport": viewport,
            "severity": severity,
            "selector": item["selector"],
            "evidence": item["evidence"],
            "suggested_fix": item["suggestedFix"],
        }
        for item in items
    ]


def build_design_evidence(viewport: str, signals: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = []
    card_count = signals["cardLikeCount"]
    large_white_panel_count = signals["largeWhitePanelCount"]
    generic_button_ratio = signals["genericButtonRatio"]
    image_count = signals["imageCount"]
    fixed_area_ratio = signals["fixedAreaRatio"]

    if card_count >= 6 or large_white_panel_count >= 3:
        evidence.append(
            design_item(
                viewport,
                "high",
                "card_template",
                f"{card_count} card-like white panels and {large_white_panel_count} large white panels detected.",
                "Collapse repeated white panels into scene-specific frames, boards, machines, or inline status areas.",
            )
        )
    elif card_count >= 3:
        evidence.append(
            design_item(
                viewport,
                "medium",
                "card_template",
                f"{card_count} card-like white panels detected.",
                "Reduce repeated card surfaces and give each section a more specific visual structure.",
            )
        )

    if image_count > 0 and large_white_panel_count >= 2:
        evidence.append(
            design_item(
                viewport,
                "high",
                "asset_integration",
                f"{image_count} images are present, but {large_white_panel_count} large white panels still dominate the viewport.",
                "Place text, controls, and feedback inside asset safe zones instead of covering assets with generic panels.",
            )
        )
    elif image_count == 0:
        evidence.append(
            design_item(
                viewport,
                "medium",
                "asset_integration",
                "No bitmap image elements are visible in the inspected viewport.",
                "Use planned assets as visible scene material when the section depends on generated images.",
            )
        )

    if generic_button_ratio >= 0.7 and signals["buttonCount"] >= 3:
        evidence.append(
            design_item(
                viewport,
                "medium",
                "interface_affordance",
                f"{signals['buttonCount']} buttons are present and {generic_button_ratio:.0%} look like generic rounded web buttons.",
                "Restyle primary controls as story objects such as tickets, machine keys, panels, or reward controls.",
            )
        )

    if fixed_area_ratio >= 0.18:
        evidence.append(
            design_item(
                viewport,
                "high",
                "composition",
                f"Fixed or sticky UI covers about {fixed_area_ratio:.0%} of the viewport area.",
                "Shrink fixed UI and move persistent status into the scene so it does not compete with the main activity.",
            )
        )

    return evidence


def design_item(
    viewport: str,
    severity: str,
    finding_type: str,
    evidence: str,
    suggested_fix: str,
) -> dict[str, Any]:
    return {
        "viewport": viewport,
        "severity": severity,
        "type": finding_type,
        "evidence": evidence,
        "suggested_fix": suggested_fix,
    }


def build_design_review(design_evidence: list[dict[str, Any]]) -> dict[str, Any]:
    risks = {
        "card_template": risk_for(design_evidence, "card_template"),
        "asset_integration": risk_for(design_evidence, "asset_integration"),
        "interface_affordance": risk_for(design_evidence, "interface_affordance"),
        "composition": risk_for(design_evidence, "composition"),
    }
    status = "REJECT" if any(risk == "high" for risk in risks.values()) else "PASS"
    summary = (
        "Visual QA found high-priority design risks."
        if status == "REJECT"
        else "Visual QA did not find high-priority design risks."
    )
    return {
        "status": status,
        "summary": summary,
        "card_template_risk": risks["card_template"],
        "asset_integration_risk": risks["asset_integration"],
        "interface_affordance_risk": risks["interface_affordance"],
        "composition_risk": risks["composition"],
        "evidence": design_evidence,
    }


def risk_for(evidence: list[dict[str, Any]], finding_type: str) -> str:
    severities = [item["severity"] for item in evidence if item["type"] == finding_type]
    if "high" in severities:
        return "high"
    if "medium" in severities:
        return "medium"
    return "low"


def priority_from_render_checks(render_checks: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    priorities = []
    message_mappings = {
        "console_errors": ("console_error", "Fix the JavaScript error before refining visual details."),
        "page_errors": ("page_error", "Fix the runtime page error before refining visual details."),
        "request_failures": ("request_failure", "Remove or replace failed local or remote resource references."),
    }
    selector_mappings = {
        "broken_images": ("broken_image", "Fix the asset path or remove the broken image reference."),
        "horizontal_overflow": ("horizontal_overflow", "Constrain widths and remove viewport-breaking fixed sizes."),
        "text_clipping": ("text_clipping", "Let text wrap or reduce the fixed height of this component."),
        "small_touch_targets": ("small_touch_target", f"Make the target at least {TOUCH_TARGET_MIN_SIZE}px by {TOUCH_TARGET_MIN_SIZE}px."),
        "overlaps": ("overlap", "Separate the overlapping elements with a responsive grid or safe-zone layout."),
        "fixed_overlay_risks": ("fixed_overlay", "Reduce fixed or sticky UI so it does not cover the main content."),
    }

    for key, (finding_type, suggested_fix) in message_mappings.items():
        for item in render_checks[key]:
            priorities.append(
                {
                    "viewport": item["viewport"],
                    "severity": item["severity"],
                    "type": finding_type,
                    "evidence": item["message"],
                    "suggested_fix": suggested_fix,
                }
            )

    for key, (finding_type, default_fix) in selector_mappings.items():
        for item in render_checks[key]:
            priorities.append(
                {
                    "viewport": item["viewport"],
                    "severity": item["severity"],
                    "type": finding_type,
                    "evidence": f"{item['selector']}: {item['evidence']}",
                    "suggested_fix": item.get("suggested_fix", default_fix),
                }
            )

    return sorted(priorities, key=finding_sort_key)


def priority_from_design_evidence(design_evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "viewport": item["viewport"],
                "severity": item["severity"],
                "type": item["type"],
                "evidence": item["evidence"],
                "suggested_fix": item["suggested_fix"],
            }
            for item in design_evidence
            if item["severity"] in {"medium", "high"}
        ],
        key=finding_sort_key,
    )


def finding_sort_key(finding: dict[str, Any]) -> tuple[int, str]:
    severity_rank = {"high": 0, "medium": 1, "low": 2}
    return severity_rank.get(finding["severity"], 3), finding["type"]


def build_refine_suggestions(priority_findings: list[dict[str, Any]]) -> list[str]:
    suggestions = []
    seen = set()
    for finding in priority_findings:
        suggestion = f"[{finding['viewport']}] {finding['suggested_fix']}"
        if suggestion in seen:
            continue
        seen.add(suggestion)
        suggestions.append(suggestion)
    return suggestions


def get_status(priority_findings: list[dict[str, Any]], design_review: dict[str, Any]) -> str:
    has_high_finding = any(
        finding["severity"] == "high" and finding["type"] in HIGH_FINDING_TYPES
        for finding in priority_findings
    )
    if has_high_finding or design_review["status"] == "REJECT":
        return "REJECT"
    return "PASS"


def merge_render_checks(target: dict[str, list[dict[str, Any]]], incoming: dict[str, list[dict[str, Any]]]) -> None:
    for key, items in incoming.items():
        target[key].extend(items)


def dedupe_render_checks(render_checks: dict[str, list[dict[str, Any]]]) -> None:
    for key, items in render_checks.items():
        render_checks[key] = dedupe_dicts(items)


def dedupe_dicts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped = []
    seen = set()
    for item in items:
        marker = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(item)
    return deduped


def relative_to_run(path: Path, run_dir: Path) -> str:
    return path.relative_to(run_dir).as_posix()


def unique_capture_label(label: str, seen: set[str]) -> str:
    sanitized = sanitize_capture_label(label)
    if sanitized not in seen:
        seen.add(sanitized)
        return sanitized
    suffix = 2
    while f"{sanitized}_{suffix}" in seen:
        suffix += 1
    unique = f"{sanitized}_{suffix}"
    seen.add(unique)
    return unique


def sanitize_capture_label(label: str) -> str:
    cleaned = []
    previous_was_separator = False
    for character in label.lower():
        if "a" <= character <= "z" or "0" <= character <= "9":
            cleaned.append(character)
            previous_was_separator = False
        elif not previous_was_separator:
            cleaned.append("_")
            previous_was_separator = True
    sanitized = "".join(cleaned).strip("_")
    return sanitized[:64] or "state"


def build_scene_targets_script() -> str:
    return f"""
() => {{
  const MAX_SCENE_SCREENSHOTS = {MAX_SCENE_SCREENSHOTS};

  function isVisible(element) {{
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.visibility !== 'hidden'
      && style.display !== 'none'
      && Number(style.opacity || 1) > 0.01
      && rect.width > 2
      && rect.height > 2;
  }}

  function selectorFor(element) {{
    const tag = element.tagName.toLowerCase();
    if (element.id) {{
      const escapedId = window.CSS && CSS.escape ? CSS.escape(element.id) : element.id;
      return `${{tag}}#${{escapedId}}`;
    }}
    const classes = [...element.classList].slice(0, 3).map((className) => {{
      return window.CSS && CSS.escape ? CSS.escape(className) : className;
    }}).join('.');
    if (classes) {{
      return `${{tag}}.${{classes}}`;
    }}
    const parent = element.parentElement;
    if (!parent) {{
      return tag;
    }}
    const index = [...parent.children].indexOf(element) + 1;
    return `${{tag}}:nth-child(${{index}})`;
  }}

  function labelFor(element, fallback) {{
    const values = [
      element.getAttribute('data-qa-label'),
      element.getAttribute('data-qa-scene'),
      element.getAttribute('aria-label'),
      element.getAttribute('data-scene'),
      element.getAttribute('data-section'),
      element.getAttribute('data-screen'),
      element.getAttribute('data-step'),
      element.id,
      (element.innerText || '').trim(),
      fallback
    ];
    const value = values.find((candidate) => candidate && String(candidate).trim().length > 0);
    return String(value || fallback).slice(0, 80);
  }}

  const targets = [];
  const selectors = new Set();
  const activeScene = document.querySelector('.scene.active[id], .section.active[id], section.active[id]');
  const qaScenes = [...document.querySelectorAll('[data-qa-scene]')]
    .map((element, index) => {{
      const value = element.getAttribute('data-qa-scene');
      const order = Number(element.getAttribute('data-qa-order'));
      return {{
        element,
        index,
        value,
        order: Number.isFinite(order) ? order : index + 1
      }};
    }})
    .filter((item) => item.value && String(item.value).trim().length > 0)
    .sort((first, second) => first.order - second.order || first.index - second.index);

  if (qaScenes.length > 0) {{
    const activeQaScene = qaScenes.find((item) => isVisible(item.element));
    qaScenes.forEach((item) => {{
      if (activeQaScene && item.element === activeQaScene.element) {{
        return;
      }}
      targets.push({{
        action: 'show_scene',
        selector: `[data-qa-scene="${{item.value}}"]`,
        sceneId: item.value,
        label: labelFor(item.element, item.value)
      }});
    }});
    return targets.slice(0, MAX_SCENE_SCREENSHOTS);
  }}

  document.querySelectorAll('section[id], .scene[id], .section[id], [data-scene][id], [data-screen][id]').forEach((element) => {{
    if (element === activeScene) {{
      return;
    }}
    const className = String(element.className || '').toLowerCase();
    const looksLikeScene = element.matches('section[id], [data-scene][id], [data-screen][id]')
      || className.includes('scene')
      || className.includes('section')
      || className.includes('screen')
      || className.includes('step');
    if (!looksLikeScene) {{
      return;
    }}
    const selector = selectorFor(element);
    const marker = `show_scene:${{selector}}`;
    if (selectors.has(marker)) {{
      return;
    }}
    selectors.add(marker);
    targets.push({{
      action: 'show_scene',
      selector,
      sceneId: element.id,
      label: labelFor(element, 'scene')
    }});
  }});

  function pushTarget(element, action, fallback) {{
    if (!isVisible(element)) {{
      return;
    }}
    if (action === 'scroll' && activeScene && element === activeScene) {{
      return;
    }}
    const selector = selectorFor(element);
    if (selectors.has(`${{action}}:${{selector}}`)) {{
      return;
    }}
    selectors.add(`${{action}}:${{selector}}`);
    targets.push({{
      action,
      selector,
      label: labelFor(element, fallback)
    }});
  }}

  const clickSelectors = [
    '[role="tab"]',
    '[aria-controls]',
    '[data-scene]',
    '[data-section]',
    '[data-screen]',
    '[data-step]',
    '.step-tabs button',
    '.step-tabs a[href^="#"]',
    '.tabs button',
    '.tabs a[href^="#"]',
    '.slide-controls button',
    'nav button',
    'nav a[href^="#"]'
  ];

  clickSelectors.forEach((selector) => {{
    document.querySelectorAll(selector).forEach((element) => {{
      const tag = element.tagName.toLowerCase();
      if (!['button', 'a'].includes(tag) && element.getAttribute('role') !== 'tab') {{
        return;
      }}
      pushTarget(element, 'click', selector);
    }});
  }});

  const scrollSelectors = [
    'main section[id]',
    'section[id]',
    '.section',
    '[data-scene]:not(button):not(a)',
    '[data-section]:not(button):not(a)',
    '[data-screen]:not(button):not(a)',
    '[data-step]:not(button):not(a)',
    '.scene',
    '.screen',
    '.slide'
  ];

  scrollSelectors.forEach((selector) => {{
    document.querySelectorAll(selector).forEach((element) => {{
      pushTarget(element, 'scroll', selector);
    }});
  }});

  return targets.slice(0, MAX_SCENE_SCREENSHOTS);
}}
"""


def build_show_scene_script() -> str:
    return """
(sceneId) => {
  if (!sceneId) {
    return;
  }
  if (typeof window.__contentHarnessShowScene === 'function') {
    window.__contentHarnessShowScene(sceneId);
    return;
  }
  if (typeof window.showScene === 'function') {
    window.showScene(sceneId);
    return;
  }
  if (typeof window.showSection === 'function') {
    window.showSection(sceneId);
    return;
  }
  const escapedSceneId = window.CSS && CSS.escape ? CSS.escape(sceneId) : sceneId;
  const target = document.querySelector(`[data-qa-scene="${escapedSceneId}"]`) || document.getElementById(sceneId);
  if (!target) {
    return;
  }
  if (target.hasAttribute('data-qa-scene')) {
    document.querySelectorAll('[data-qa-scene]').forEach((section) => {
      section.classList.toggle('active', section.getAttribute('data-qa-scene') === sceneId);
      section.hidden = section.getAttribute('data-qa-scene') !== sceneId;
    });
  } else {
    document.querySelectorAll('.scene, .section, section[id]').forEach((section) => {
      section.classList.toggle('active', section.id === sceneId);
    });
  }
  const stepLabel = document.getElementById('stepLabel');
  if (stepLabel && target.dataset) {
    stepLabel.textContent = target.dataset.qaLabel || target.dataset.step || stepLabel.textContent;
  }
  target.scrollIntoView({ block: 'start', inline: 'nearest' });
}
"""


def build_inspection_script() -> str:
    return f"""
() => {{
  const TOUCH_TARGET_MIN_SIZE = {TOUCH_TARGET_MIN_SIZE};
  const viewportArea = Math.max(1, window.innerWidth * window.innerHeight);

  function isVisible(element) {{
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.visibility !== 'hidden'
      && style.display !== 'none'
      && Number(style.opacity || 1) > 0.01
      && rect.width > 1
      && rect.height > 1;
  }}

  function selectorFor(element) {{
    if (element.id) {{
      return `${{element.tagName.toLowerCase()}}#${{element.id}}`;
    }}
    const classes = [...element.classList].slice(0, 3).join('.');
    if (classes) {{
      return `${{element.tagName.toLowerCase()}}.${{classes}}`;
    }}
    const parent = element.parentElement;
    if (!parent) {{
      return element.tagName.toLowerCase();
    }}
    const index = [...parent.children].indexOf(element) + 1;
    return `${{element.tagName.toLowerCase()}}:nth-child(${{index}})`;
  }}

  function rectOf(element) {{
    const rect = element.getBoundingClientRect();
    return {{
      left: rect.left,
      top: rect.top,
      right: rect.right,
      bottom: rect.bottom,
      width: rect.width,
      height: rect.height,
      area: rect.width * rect.height
    }};
  }}

  function nearWhite(color) {{
    const match = color.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([0-9.]+))?\\)/);
    if (!match) {{
      return false;
    }}
    const alpha = match[4] === undefined ? 1 : Number(match[4]);
    return alpha >= 0.75 && Number(match[1]) >= 238 && Number(match[2]) >= 238 && Number(match[3]) >= 238;
  }}

  const allElements = [...document.querySelectorAll('body *')].filter(isVisible);
  const interactiveElements = [...document.querySelectorAll('button, a[href], input, select, textarea, [role="button"], [tabindex]')]
    .filter(isVisible);
  const images = [...document.images].filter(isVisible);

  const brokenImages = images
    .filter((image) => !image.complete || image.naturalWidth === 0)
    .slice(0, 20)
    .map((image) => ({{
      selector: selectorFor(image),
      evidence: `Image source did not load: ${{image.getAttribute('src') || ''}}`,
      suggestedFix: 'Fix the image source path and keep it under output/assets/.'
    }}));

  const horizontalOverflow = [];
  const documentOverflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  if (documentOverflow > 2) {{
    horizontalOverflow.push({{
      selector: 'document',
      evidence: `Document scrollWidth exceeds viewport by ${{Math.round(documentOverflow)}}px.`,
      suggestedFix: 'Remove fixed widths wider than the viewport and add responsive max-width constraints.'
    }});
  }}
  allElements
    .filter((element) => {{
      const rect = element.getBoundingClientRect();
      return rect.right > window.innerWidth + 2 || rect.left < -2;
    }})
    .slice(0, 20)
    .forEach((element) => {{
      const rect = rectOf(element);
      horizontalOverflow.push({{
        selector: selectorFor(element),
        evidence: `Element extends outside viewport: left=${{Math.round(rect.left)}} right=${{Math.round(rect.right)}} width=${{Math.round(rect.width)}}.`,
        suggestedFix: 'Constrain this element with max-width, wrapping, or responsive grid tracks.'
      }});
    }});

  const textClipping = allElements
    .filter((element) => {{
      const text = (element.innerText || '').trim();
      if (text.length < 8) {{
        return false;
      }}
      const hasVisibleChildren = [...element.children].some(isVisible);
      if (hasVisibleChildren && !interactiveElements.includes(element)) {{
        return false;
      }}
      return element.scrollWidth > element.clientWidth + 2 || element.scrollHeight > element.clientHeight + 2;
    }})
    .slice(0, 20)
    .map((element) => ({{
      selector: selectorFor(element),
      evidence: 'Text content is larger than the visible box.',
      suggestedFix: 'Allow wrapping, reduce fixed height, or move long copy to a larger responsive area.'
    }}));

  const smallTouchTargets = interactiveElements
    .filter((element) => {{
      const rect = element.getBoundingClientRect();
      return rect.width < TOUCH_TARGET_MIN_SIZE || rect.height < TOUCH_TARGET_MIN_SIZE;
    }})
    .slice(0, 20)
    .map((element) => {{
      const rect = rectOf(element);
      return {{
        selector: selectorFor(element),
        evidence: `Touch target is ${{Math.round(rect.width)}}x${{Math.round(rect.height)}}px.`,
        suggestedFix: 'Increase padding or min-size so the target is easy to tap.'
      }};
    }});

  const interactiveSet = new Set(interactiveElements);
  const overlapCandidates = allElements
    .filter((element) => {{
      const text = (element.innerText || '').trim();
      const rect = rectOf(element);
      const isInteractive = interactiveSet.has(element);
      const hasVisibleChildren = [...element.children].some(isVisible);
      const isLeafText = text.length > 0 && !hasVisibleChildren;
      return (isInteractive || isLeafText) && rect.area / viewportArea < 0.25;
    }})
    .slice(0, 120);
  const overlaps = [];
  for (let i = 0; i < overlapCandidates.length; i += 1) {{
    for (let j = i + 1; j < overlapCandidates.length; j += 1) {{
      const first = overlapCandidates[i];
      const second = overlapCandidates[j];
      if (first.contains(second) || second.contains(first)) {{
        continue;
      }}
      const a = rectOf(first);
      const b = rectOf(second);
      const overlapWidth = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
      const overlapHeight = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
      const overlapArea = overlapWidth * overlapHeight;
      const smallerArea = Math.max(1, Math.min(a.area, b.area));
      if (overlapArea / smallerArea > 0.18 && overlapArea > 160) {{
        overlaps.push({{
          selector: `${{selectorFor(first)}} overlaps ${{selectorFor(second)}}`,
          evidence: `Elements overlap by ${{Math.round(overlapArea)}}px2.`,
          suggestedFix: 'Move these elements into separate grid rows or a declared safe zone.'
        }});
      }}
      if (overlaps.length >= 20) {{
        break;
      }}
    }}
    if (overlaps.length >= 20) {{
      break;
    }}
  }}

  const fixedOverlayRisks = allElements
    .filter((element) => {{
      const style = window.getComputedStyle(element);
      if (!['fixed', 'sticky'].includes(style.position)) {{
        return false;
      }}
      const rect = rectOf(element);
      return rect.area / viewportArea > 0.12;
    }})
    .slice(0, 20)
    .map((element) => {{
      const rect = rectOf(element);
      return {{
        selector: selectorFor(element),
        evidence: `Fixed or sticky element covers about ${{Math.round((rect.area / viewportArea) * 100)}}% of the viewport.`,
        suggestedFix: 'Reduce this persistent UI or make it part of the scrollable scene.'
      }};
    }});

  let cardLikeCount = 0;
  let largeWhitePanelCount = 0;
  let fixedArea = 0;
  let genericButtonCount = 0;
  for (const element of allElements) {{
    const style = window.getComputedStyle(element);
    const rect = rectOf(element);
    const bgIsWhite = nearWhite(style.backgroundColor);
    const radius = parseFloat(style.borderRadius || '0');
    const shadow = style.boxShadow && style.boxShadow !== 'none';
    const className = String(element.className || '').toLowerCase();
    if (bgIsWhite && (radius >= 8 || shadow || /card|panel|box|wrap/.test(className))) {{
      cardLikeCount += 1;
      if (rect.area / viewportArea > 0.08) {{
        largeWhitePanelCount += 1;
      }}
    }}
    if (['fixed', 'sticky'].includes(style.position)) {{
      fixedArea += Math.min(rect.area, viewportArea);
    }}
    if (element.matches('button, [role="button"], a[href]')) {{
      const looksGeneric = radius >= 8 && bgIsWhite;
      if (looksGeneric || /btn|button/.test(className)) {{
        genericButtonCount += 1;
      }}
    }}
  }}

  return {{
    brokenImages,
    horizontalOverflow,
    textClipping,
    smallTouchTargets,
    overlaps,
    fixedOverlayRisks,
    designSignals: {{
      cardLikeCount,
      largeWhitePanelCount,
      imageCount: images.length,
      buttonCount: interactiveElements.length,
      genericButtonRatio: interactiveElements.length === 0 ? 0 : genericButtonCount / interactiveElements.length,
      fixedAreaRatio: fixedArea / viewportArea
    }}
  }};
}}
"""
