import os
from pathlib import Path
from fastmcp import FastMCP

# 初始化 FastMCP
mcp = FastMCP("LennySkillsPlus",stateless_http=True)

# 定义技能根目录
SKILLS_DIR = Path(__file__).parent / "skills"


def get_skill_content(skill_path: Path) -> str:
    """聚合技能包的所有相关内容"""
    content = []

    # 1. 读取主技能文档
    main_skill = skill_path / "SKILL.md"
    if main_skill.exists():
        content.append(f"# {skill_path.name.upper()} SKILL DEFINITION\n")
        content.append(main_skill.read_text(encoding="utf-8"))

    # 2. 读取 references 目录下的所有文档
    ref_dir = skill_path / "references"
    if ref_dir.exists():
        content.append("\n\n---\n## SUPPORTING REFERENCES & TEMPLATES\n")
        for ref_file in ref_dir.glob("*.md"):
            content.append(f"\n### File: {ref_file.name}")
            content.append(ref_file.read_text(encoding="utf-8"))
            content.append("\n")

    return "\n".join(content)


# 自动注册所有技能为 MCP Resources
if SKILLS_DIR.exists():
    for skill_path in SKILLS_DIR.iterdir():
        if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
            slug = skill_path.name

            # 使用闭包或局部变量捕获当前路径
            def create_resource_func(path=skill_path):
                return lambda: get_skill_content(path)

            # 注册资源
            mcp.resource(f"skill://{slug}")(create_resource_func())

if __name__ == "__main__":
    # 从环境变量获取配置，方便部署
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", 8001))

    # 以 SSE 模式启动 MCP Server
    # SSE 模式允许通过 HTTP 协议访问，通常用于 Web 端或远程连接
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
    )
