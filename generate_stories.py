import os
import re

yaml_path = "_bmad-output/implementation-artifacts/sprint-status.yaml"
epics_path = "_bmad-output/planning-artifacts/epics.md"
out_dir = "_bmad-output/implementation-artifacts"

# Read files
with open(yaml_path, "r") as f:
    yaml_content = f.read()

with open(epics_path, "r") as f:
    epics_content = f.read()

# Parse epics.md to extract stories
story_blocks = epics_content.split("### Story ")

stories_info = {}
for block in story_blocks[1:]:
    lines = block.strip().split("\n")
    header = lines[0].strip()
    match = re.match(r"(\d+\.\d+):\s*(.*)", header)
    if not match:
        continue

    story_num = match.group(1)
    story_title = match.group(2)

    us_match = re.search(r"(As a .*?)(?=\*\*Acceptance Criteria:\*\*)", block, re.DOTALL)
    ac_match = re.search(r"(\*\*Acceptance Criteria:\*\*.*?)$", block, re.DOTALL)

    user_story = us_match.group(1).strip() if us_match else ""
    acc_criteria = ac_match.group(1).strip() if ac_match else ""

    stories_info[story_num] = {
        "title": story_title,
        "user_story": user_story,
        "acceptance_criteria": acc_criteria,
    }

# Find backlog stories in the yaml
# look for lines like "  1-1-project-initialization-infrastructure-scaffold: backlog"
keys = re.findall(r"  (\d+-\d+-.*?):\s*backlog", yaml_content)

modified_yaml = yaml_content

for key in keys:
    num_match = re.match(r"^(\d+)-(\d+)-", key)
    if not num_match:
        continue

    story_num = f"{num_match.group(1)}.{num_match.group(2)}"
    epic_key = f"epic-{num_match.group(1)}"

    info = stories_info.get(story_num)
    if not info:
        print(f"Could not find info for {key}")
        continue

    md_content = f"""# Story {key}: {info["title"]}

## User Story
{info["user_story"]}

## Acceptance Criteria
{info["acceptance_criteria"]}

## Developer Context
### Technical Requirements
- Follow guidelines in architecture.md and epics.md.
- Ensure proper use of async/await for I/O bounds and multi-agent loops.
- Use structured Pydantic v2.10+ models.
- Required to test with pytest, isolate/mock Vertex AI calls.

### Architecture Compliance
- Ensure separation of concerns (src/core vs src/ui vs src/agents).
- Follow the specific naming conventions and structural patterns (`snake_case` modules, `PascalCase` classes).
- Use `google-genai` and adhere strictly to ADK 2.0 orchestration paradigms.
- No global state. Utilize deterministic hashing.
"""
    # write the markdown file
    md_path = os.path.join(out_dir, f"{key}.md")
    with open(md_path, "w") as f:
        f.write(md_content)

    # update yaml contents
    modified_yaml = re.sub(rf"  {key}: backlog", f"  {key}: ready-for-dev", modified_yaml)
    modified_yaml = re.sub(rf"  {epic_key}: backlog", f"  {epic_key}: in-progress", modified_yaml)

with open(yaml_path, "w") as f:
    f.write(modified_yaml)

print("Created markdown files and updated sprint-status.yaml")
