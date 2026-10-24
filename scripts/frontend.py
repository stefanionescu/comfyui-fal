"""Check that the shipped browser bundle equals a fresh build of web/scripts."""

import sys
import asyncio

from scripts.paths import WEB_DIR, REPO_ROOT, FRONTEND_CHECK_DIR

# The files esbuild writes: the bundle, and the stylesheet its imports pull in.
BUILT_FILES = ('extension.js', 'extension.css')


async def _build_bundle() -> bool:
    """Run the build script of package.json with its output in the scratch folder, and return whether it passed."""
    FRONTEND_CHECK_DIR.mkdir(parents=True, exist_ok=True)
    process = await asyncio.create_subprocess_exec(
        'bun', 'run', '--no-install', 'build', f'--outfile={FRONTEND_CHECK_DIR / BUILT_FILES[0]}', cwd=REPO_ROOT
    )
    return await process.wait() == 0


def main() -> int:
    """Build the bundle into the scratch folder, and report each shipped file that differs."""
    if not asyncio.run(_build_bundle()):
        problems = ['esbuild failed.']
    else:
        problems = [
            f'Rebuild web/{name} with bun run build.'
            for name in BUILT_FILES
            if not (shipped := WEB_DIR / name).is_file()
            or shipped.read_bytes() != (FRONTEND_CHECK_DIR / name).read_bytes()
        ]
    for problem in problems:
        sys.stderr.write(problem + '\n')
    return int(bool(problems))


if __name__ == '__main__':
    raise SystemExit(main())
