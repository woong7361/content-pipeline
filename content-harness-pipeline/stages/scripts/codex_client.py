from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

PROVIDER_CODEX = "codex"
PROVIDER_CLAUDE = "claude"


def create_prompt_client(
    *,
    provider: str,
    codex_bin: str,
    claude_bin: str,
    project_dir: Path,
    timeout_seconds: int,
):
    if provider == PROVIDER_CODEX:
        return CodexClient(
            codex_bin=codex_bin,
            project_dir=project_dir,
            timeout_seconds=timeout_seconds,
        )
    if provider == PROVIDER_CLAUDE:
        return ClaudeClient(
            claude_bin=claude_bin,
            project_dir=project_dir,
            timeout_seconds=timeout_seconds,
        )
    raise ValueError(f"unsupported LLM provider: {provider}")


@dataclass(frozen=True)
class CodexClient:
    codex_bin: str
    project_dir: Path
    timeout_seconds: int = 600
    bypass_approvals_and_sandbox: bool = True

    def run_prompt(
        self,
        prompt: str,
        output_schema: Path,
        output_path: Path,
        model: str | None = None,
    ) -> dict | None:
        command = self.build_command(
            output_schema=output_schema,
            output_path=output_path,
            model=model,
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                encoding="utf-8",
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(
                "Codex CLI timed out in non-interactive mode.\n"
                f"command: {command}\n"
                f"timeout_seconds: {self.timeout_seconds}"
            ) from exc

        if completed.returncode != 0:
            raise RuntimeError(
                "Codex CLI failed\n"
                f"command: {command}\n"
                f"stdout: {completed.stdout}\n"
                f"stderr: {completed.stderr}"
            )

        return extract_token_usage(completed.stdout)

    def build_command(
        self,
        output_schema: Path,
        output_path: Path,
        model: str | None = None,
    ) -> list[str]:
        command = [
            self.codex_bin,
            "exec",
        ]
        if model:
            command.extend(["--model", model])

        command.extend(
            [
                "--ephemeral",
                "--json",
            ]
        )
        if self.bypass_approvals_and_sandbox:
            command.append("--dangerously-bypass-approvals-and-sandbox")

        command.extend(
            [
                "-C",
                str(self.project_dir),
                "--output-schema",
                str(output_schema),
                "--output-last-message",
                str(output_path),
                "-",
            ]
        )
        return command


@dataclass(frozen=True)
class ClaudeClient:
    claude_bin: str
    project_dir: Path
    timeout_seconds: int = 600
    permission_mode: str = "acceptEdits"
    bare: bool = False

    def run_prompt(
        self,
        prompt: str,
        output_schema: Path,
        output_path: Path,
        model: str | None = None,
    ) -> dict | None:
        command = self.build_command(output_schema=output_schema, model=model)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                encoding="utf-8",
                cwd=self.project_dir,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(
                "Claude Code CLI timed out in non-interactive mode.\n"
                f"command: {command}\n"
                f"timeout_seconds: {self.timeout_seconds}"
            ) from exc

        if completed.returncode != 0:
            raise RuntimeError(
                "Claude Code CLI failed\n"
                f"command: {command}\n"
                f"stdout: {completed.stdout}\n"
                f"stderr: {completed.stderr}"
            )

        result = parse_claude_json_output(completed.stdout, command)
        structured_output = extract_claude_structured_output(
            result=result,
            command=command,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

        output_path.write_text(
            json.dumps(structured_output, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return extract_claude_usage(result)

    def build_command(self, output_schema: Path, model: str | None = None) -> list[str]:
        command = [self.claude_bin]
        if self.bare:
            command.append("--bare")
        if model:
            command.extend(["--model", model])
        command.extend(
            [
                "-p",
                "Execute the complete task described in stdin and return only the requested structured output.",
                "--output-format",
                "json",
                "--json-schema",
                output_schema.read_text(encoding="utf-8"),
                "--permission-mode",
                self.permission_mode,
            ]
        )
        return command


def extract_token_usage(stdout: str) -> dict | None:
    usage = None
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    return usage


def parse_claude_json_output(stdout: str, command: list[str]) -> dict:
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Claude Code CLI did not return JSON output\n"
            f"command: {command}\n"
            f"stdout: {stdout}"
        ) from exc
    if not isinstance(result, dict):
        raise RuntimeError(
            "Claude Code CLI returned non-object JSON output\n"
            f"command: {command}\n"
            f"stdout: {stdout}"
        )
    return result


def extract_claude_structured_output(
    *,
    result: dict,
    command: list[str],
    stdout: str,
    stderr: str,
) -> dict:
    if result.get("is_error") is True:
        raise RuntimeError(
            "Claude Code CLI returned an error result\n"
            f"command: {command}\n"
            f"result: {result.get('result')}\n"
            f"stdout: {stdout}\n"
            f"stderr: {stderr}"
        )

    structured_output = result.get("structured_output")
    if isinstance(structured_output, dict):
        return structured_output

    structured_output = parse_json_object_from_text(result.get("result"))
    if structured_output is not None:
        return structured_output

    raise RuntimeError(
        "Claude Code CLI did not return structured output as an object\n"
        f"command: {command}\n"
        f"stdout: {stdout}\n"
        f"stderr: {stderr}"
    )


def parse_json_object_from_text(value: object) -> dict | None:
    if not isinstance(value, str):
        return None

    text = value.strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        return parsed

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def extract_claude_usage(result: dict) -> dict | None:
    usage: dict = {}
    if isinstance(result.get("usage"), dict):
        usage["usage"] = result["usage"]
    if isinstance(result.get("modelUsage"), dict):
        usage["model_usage"] = result["modelUsage"]
    if result.get("total_cost_usd") is not None:
        usage["total_cost_usd"] = result["total_cost_usd"]
    return usage or None
