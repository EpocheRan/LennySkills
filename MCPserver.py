import os
from pathlib import Path
from fastmcp import FastMCP

# 1. 解决 404 和 3.1.0 兼容性问题：通过环境变量启用无状态 HTTP 模式
os.environ["FASTMCP_STATELESS_HTTP"] = "true"

# 初始化 FastMCP (移除了会导致报错的 stateless_http 参数)
mcp = FastMCP("LennySkillsPlus")

# 定义技能根目录
SKILLS_DIR = Path(__file__).parent / "skills"

def get_skill_content(skill_path: Path) -> str:
    """聚合技能包的所有相关内容"""
    if not skill_path.exists():
        return f"Error: Skill path {skill_path} not found."
        
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

# --- 2. 核心改进：注册为【工具】，这样 LobeHub 就能看到工具了 ---
@mcp.tool()
def get_lenny_skill(skill_name: str) -> str:
    """
    Retrieve a specific Lenny Skill by name to improve task performance.
    Example skill_name: 'ai-evals', 'writing-prds', 'growth-strategy'
    """
    skill_path = SKILLS_DIR / skill_name
    if not (skill_path.exists() and (skill_path / "SKILL.md").exists()):
        available_skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
        return f"Skill '{skill_name}' not found. Available skills: {', '.join(available_skills)}"
    
    return get_skill_content(skill_path)

@mcp.tool()
def list_lenny_skills() -> list[str]:
    """List all available Lenny Skills in the workspace."""
    if not SKILLS_DIR.exists():
        return []
    return [d.name for d in SKILLS_DIR.iterdir() if (d / "SKILL.md").exists()]

# --- 3. 自动注册为【资源】 (保留原有逻辑) ---
if SKILLS_DIR.exists():
    for skill_path in SKILLS_DIR.iterdir():
        if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
            slug = skill_path.name

            # 使用 lambda 捕获当前路径
            def make_handler(p):
                return lambda: get_skill_content(p)

            # 注册资源 (Resource)
            mcp.resource(f"skill://{slug}")(make_handler(skill_path))

if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", 8001))

    print(f"🚀 Starting LennySkillsPlus on {host}:{port}")
    # 以 SSE 模式启动
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
    )
