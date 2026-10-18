"""
VSIX Packager for DoomScript VS Code Extension
Creates a standard .vsix archive without requiring Node.js or vsce.
"""

import zipfile
from pathlib import Path

def create_vsix():
    src_dir = Path(__file__).parent.parent / "extensions" / "doomscript-vscode"
    dist_dir = Path(__file__).parent.parent / "dist"
    dist_dir.mkdir(exist_ok=True)
    vsix_path = dist_dir / "doomscript-0.2.0.vsix"

    content_types = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="vsixmanifest" ContentType="text/xml" />
</Types>
'''

    vsix_manifest = '''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Id="doomscript-vscode" Version="0.2.0" Publisher="doomscript" Language="en-US" DisplayName="DoomScript Language Support" />
    <Description>Official syntax highlighting and language support for DoomScript (.doom)</Description>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
'''

    with zipfile.ZipFile(vsix_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("extension.vsixmanifest", vsix_manifest)
        
        for file in src_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(src_dir)
                archive_name = f"extension/{rel_path}".replace("\\", "/")
                zf.write(file, archive_name)

    print(f"Created VSIX: {vsix_path}")

if __name__ == "__main__":
    create_vsix()
