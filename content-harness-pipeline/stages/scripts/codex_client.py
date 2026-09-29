from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from stages.scripts import agent_audit
from stages.scripts import usage_log

def resolve_executable(name: str) -> str:
    """이름만 넘기지 않고 셸이 고르는 것과 같은 실행 파일을 찾아 준다.

    Windows에서 `subprocess`에 이름만 주면 `CreateProcess`가 PATH를 자체 탐색하는데,
    그 순서가 셸과 달라 **같은 이름의 다른 설치본**이 실행될 수 있다.
    실측: 셸에서는 npm 설치본(0.147.0)이 도는데 `["codex", ...]`로는 오래된
    standalone(0.133.0-alpha.1)이 돌아, 서버의 새 모델 목록을 못 읽고 400으로 거절됐다.
    어느 바이너리가 도는지가 산출물을 좌우하므로 여기서 한 번에 고정한다.
    """
    return shutil.which(name) or name


PROVIDER_CODEX = "codex"
PROVIDER_CLAUDE = "claude"


def create_prompt_client(
    *,
    provider: str,
    codex_bin: str,
    claude_bin: str,
    project_dir: Path,
    timeout_seconds: int,
    allowed_tools: tuple[str, ...] = (),
):
    """`allowed_tools` 는 claude 에만 쓴다 — 비대화형이라 허락할 사람이 없는 명령 중 **미리 허용할 것**.
    codex 는 이미 `--dangerously-bypass-approvals-and-sandbox` 로 돈다."""
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
            allowed_tools=tuple(allowed_tools),
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
        stage: str | None = None,
    ) -> dict | None:
        """부르고, **걸린 시간과 토큰을 run 에 적는다**(`usage_log`). 실패해도 걸린 시간은 남긴다."""
        started = time.monotonic()
        try:
            usage = self._run_prompt(prompt, output_schema, output_path, model, stage)
        except BaseException as exc:
            usage_log.record_call(stage, PROVIDER_CODEX, model, time.monotonic() - started, None, False,
                                  f"{type(exc).__name__}: {exc}")
            raise
        usage_log.record_call(stage, PROVIDER_CODEX, model or None, time.monotonic() - started, usage, True)
        return usage

    def _run_prompt(
        self,
        prompt: str,
        output_schema: Path,
        output_path: Path,
        model: str | None = None,
        stage: str | None = None,
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

        # 실패해도 남긴다 — 명령은 이미 실행됐고, 죽은 stage가 무엇을 열었는지가 더 중요하다.
        agent_audit.record_codex(stage, completed.stdout)

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
            resolve_executable(self.codex_bin),
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
    # `acceptEdits` 는 파일 수정만 허락한다. 명령은 여기 적은 것만 돈다(예: `Bash(python -B -m stages.scripts.self_check:*)`).
    allowed_tools: tuple[str, ...] = ()
    # 사용자 전역 설정(~/.claude/settings.json)의 허용 규칙을 **물려받지 않는다.** 실측(2026-09-29) — 전역에
    # `Bash(node -e ' *)` · 특정 경로 `rm -rf` 등이 있어 파이프라인의 claude 도 그 명령을 돌릴 수 있었다.
    # PC 마다 전역 설정이 다르므로 이렇게 해야 어디서나 같은 권한으로 돈다.
    setting_sources: str = "project"

    def run_prompt(
        self,
        prompt: str,
        output_schema: Path,
        output_path: Path,
        model: str | None = None,
        stage: str | None = None,
    ) -> dict | None:
        """부르고, **걸린 시간과 토큰을 run 에 적는다**(`usage_log`). 실패해도 걸린 시간은 남긴다."""
        started = time.monotonic()
        try:
            usage = self._run_prompt(prompt, output_schema, output_path, model, stage)
        except BaseException as exc:
            usage_log.record_call(stage, PROVIDER_CLAUDE, model, time.monotonic() - started, None, False,
                                  f"{type(exc).__name__}: {exc}")
            raise
        usage_log.record_call(stage, PROVIDER_CLAUDE, model or claude_model(usage), time.monotonic() - started, usage, True)
        return usage

    def _run_prompt(
        self,
        prompt: str,
        output_schema: Path,
        output_path: Path,
        model: str | None = None,
        stage: str | None = None,
    ) -> dict | None:
        command = self.build_command(output_schema=output_schema, model=model)
        # `--output-format json` 에는 도구 호출 기록이 없다. 감사되지 않았다는 사실만 남긴다.
        agent_audit.record_claude_unaudited(stage)

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
        # codex와 같은 이유로 셸이 고르는 것과 같은 실행 파일을 고정한다(resolve_executable 주석).
        command = [resolve_executable(self.claude_bin)]
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
                load_schema_for_claude(output_schema),
                "--permission-mode",
                self.permission_mode,
                "--setting-sources",
                self.setting_sources,
            ]
        )
        if self.allowed_tools:
            command.extend(["--allowedTools", *self.allowed_tools])
        return command


def load_schema_for_claude(output_schema: Path) -> str:
    """Claude Code CLI에 넘길 schema 문자열을 만든다.

    `$schema: https://json-schema.org/draft/2020-12/schema`를 그대로 넘기면 CLI가
    모델을 부르기 전에 `no schema with key or ref ...`로 거절한다(메타 schema를 해석하지 못한다).
    codex 쪽은 같은 파일을 그대로 받으므로 파일에서는 유지하고, 여기서만 떼어낸다.
    """
    schema = json.loads(output_schema.read_text(encoding="utf-8"))
    if isinstance(schema, dict):
        schema.pop("$schema", None)
    return json.dumps(schema, ensure_ascii=False)


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


def claude_model(usage: dict | None) -> str | None:
    """claude 는 `--model` 없이 부르면 어느 모델이 돌았는지 `modelUsage` 키로만 알 수 있다."""
    models = (usage or {}).get("model_usage") or {}
    return next(iter(models), None) if isinstance(models, dict) else None
