"""
mcp — MCP(Model Context Protocol) 학습용 인프라
================================================

모듈 1(연결) 노트북에서 반복되던 MCP 골격 구현을 한곳에 모았습니다.
실제 MCP SDK(JSON-RPC, stdio/SSE 전송)를 쓰지 않고, 프로토콜의 **구조**
(Host ↔ Client ↔ Server, list_tools / call_tool)를 순수 파이썬으로 단순화해
'개념'에 집중할 수 있게 한 교육용 시뮬레이션입니다.

구성:
    MCPServer            서버 추상 기반 클래스 (name / list_tools / call_tool)
    CalculatorMCPServer  계산기 도구 서버 (calculate / factorial)
    FileSystemMCPServer  파일 시스템 도구 서버 (read/write/list, 메모리 시뮬레이션)
    MCPClient            서버 하나와의 연결을 유지하며 도구를 호출하는 클라이언트
    MCPHost              여러 MCPClient 를 관리하는 호스트(= AI 애플리케이션)

설계 의도:
    - 서버는 도구의 '스키마(list_tools)'와 '실행(call_tool)'만 제공한다.
    - 클라이언트는 서버 연결을 캡슐화한다(끊김 처리 등).
    - 호스트는 여러 서버를 묶어 단일 진입점(call_tool)을 제공한다.
"""

import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List

# 계산기 서버의 eval 에 노출할 안전 심볼. __builtins__ 를 비워 임의 코드 실행을 막고
# math 모듈만 화이트리스트로 제공한다(예: math.sqrt(144)).
_SAFE_GLOBALS = {"__builtins__": {}}
_SAFE_LOCALS = {"math": math}


class MCPServer(ABC):
    """MCP 서버 추상 기반 클래스.

    모든 MCP 서버는 자신의 이름(name)과, 제공 도구의 스키마 목록(list_tools),
    그리고 도구 실행 진입점(call_tool)을 구현해야 한다.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """서버 식별 이름(예: 'calculator-server')."""
        raise NotImplementedError

    @abstractmethod
    def list_tools(self) -> List[Dict]:
        """이 서버가 제공하는 도구들의 스키마 목록을 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """이름으로 도구를 실행하고 결과를 반환한다."""
        raise NotImplementedError


class CalculatorMCPServer(MCPServer):
    """계산기 MCP 서버 — 수식 계산(calculate)과 팩토리얼(factorial)을 제공한다."""

    @property
    def name(self) -> str:
        return "calculator-server"

    def list_tools(self) -> List[Dict]:
        """계산기 도구 2종의 입력 스키마(JSON Schema 형식)를 반환한다."""
        return [
            {
                "name": "calculate",
                "description": "수학 계산 수행",
                "inputSchema": {
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                },
            },
            {
                "name": "factorial",
                "description": "팩토리얼 계산",
                "inputSchema": {
                    "type": "object",
                    "properties": {"n": {"type": "integer"}},
                    "required": ["n"],
                },
            },
        ]

    def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """calculate / factorial 도구를 실행한다(미지원 이름이면 예외)."""
        if tool_name == "calculate":
            expr = arguments["expression"]
            result = eval(expr, _SAFE_GLOBALS, _SAFE_LOCALS)  # noqa: S307 (화이트리스트로 안전)
            return {"result": result, "expression": expr}
        if tool_name == "factorial":
            n = arguments["n"]
            return {"result": math.factorial(n), "n": n}
        raise ValueError(f"알 수 없는 도구: {tool_name}")


class FileSystemMCPServer(MCPServer):
    """파일 시스템 MCP 서버 (메모리 시뮬레이션).

    실제 디스크에 쓰지 않고 내부 dict 에 경로→내용을 저장한다. 교육용으로
    파일 IO 도구(read/write/list)의 형태만 보여 주기 위한 단순 구현이다.
    """

    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self._files: Dict[str, str] = {}  # 경로(str) → 내용(str)

    @property
    def name(self) -> str:
        return "filesystem-server"

    def list_tools(self) -> List[Dict]:
        """파일 도구 3종(read_file / write_file / list_files)의 스키마를 반환한다."""
        return [
            {"name": "read_file", "description": "파일 읽기",
             "inputSchema": {"type": "object",
                             "properties": {"path": {"type": "string"}},
                             "required": ["path"]}},
            {"name": "write_file", "description": "파일 쓰기",
             "inputSchema": {"type": "object",
                             "properties": {"path": {"type": "string"},
                                            "content": {"type": "string"}},
                             "required": ["path", "content"]}},
            {"name": "list_files", "description": "파일 목록 조회",
             "inputSchema": {"type": "object", "properties": {}}},
        ]

    def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """read_file / write_file / list_files 도구를 실행한다."""
        if tool_name == "read_file":
            path = arguments["path"]
            return self._files.get(path, f"파일 없음: {path}")
        if tool_name == "write_file":
            self._files[arguments["path"]] = arguments["content"]
            return {"success": True, "path": arguments["path"]}
        if tool_name == "list_files":
            return list(self._files.keys())
        raise ValueError(f"알 수 없는 도구: {tool_name}")


class MCPClient:
    """MCP 클라이언트 — 서버 하나와의 연결을 유지하며 도구를 호출한다."""

    def __init__(self, server: MCPServer):
        self.server = server
        self._connected = True
        print(f"[MCP Client] '{server.name}' 서버에 연결됨")

    def get_tools(self) -> List[Dict]:
        """연결된 서버의 도구 스키마 목록을 가져온다."""
        return self.server.list_tools()

    def call(self, tool_name: str, **kwargs) -> Any:
        """연결 상태를 확인한 뒤 서버의 도구를 호출한다."""
        if not self._connected:
            raise ConnectionError("서버와 연결이 끊겼습니다")
        print(f"  [MCP] {self.server.name}.{tool_name}({kwargs})")
        return self.server.call_tool(tool_name, kwargs)


class MCPHost:
    """MCP 호스트 — 여러 MCPClient 를 관리하는 AI 애플리케이션 측 진입점."""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}  # 서버 이름 → 클라이언트

    def connect(self, server: MCPServer) -> MCPClient:
        """서버에 대한 클라이언트를 만들어 등록하고 반환한다."""
        client = MCPClient(server)
        self.clients[server.name] = client
        return client

    def list_all_tools(self) -> Dict[str, List[Dict]]:
        """연결된 모든 서버의 도구 목록을 {서버이름: [도구...]} 로 모은다."""
        return {name: client.get_tools() for name, client in self.clients.items()}

    def call_tool(self, server_name: str, tool_name: str, **kwargs) -> Any:
        """특정 서버의 도구를 이름으로 호출한다(미등록 서버면 예외)."""
        if server_name not in self.clients:
            raise ValueError(f"서버 없음: {server_name}")
        return self.clients[server_name].call(tool_name, **kwargs)
