# DoomScript Studio — IntelliJ Platform Project

This folder contains the complete Gradle and IntelliJ Platform SDK project to build the **DoomScript Studio IDE** (either as a standalone branded IDE distribution or as a native plugin for PyCharm / IntelliJ IDEA).

---

## 🛠️ Requirements
- **JDK 17 or 21** (e.g. Temurin, Corretto, or JetBrains Runtime)
- **Gradle 8.5+** (or use `./gradlew`)

---

## 🚀 Building & Running

### 1. Test Run Inside a Sandbox IDE
To launch an isolated instance of the IDE with DoomScript Studio active:
```bash
./gradlew runIde
```

### 2. Package Plugin (`.zip`)
To package the plugin archive ready to install into any PyCharm Professional or Community edition:
```bash
./gradlew buildPlugin
```
The resulting `.zip` will be generated in `build/distributions/doomscript-studio-2026.1.0.zip`. You can drag-and-drop this zip directly into PyCharm:
**Settings** → **Plugins** → **⚙ (Gear icon)** → **Install Plugin from Disk...**

### 3. Build Standalone Custom IDE Distribution
Using the IntelliJ Platform Gradle Plugin, you can build a standalone distributable IDE:
```bash
./gradlew prepareSandbox
```
