plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.24"
    id("org.jetbrains.intellij.platform") version "2.0.0"
}

group = "com.doomscript"
version = "2026.1.0"

repositories {
    mavenCentral()
    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    intellijPlatform {
        // Target IntelliJ Community Platform (the exact open-source base of PyCharm & IntelliJ)
        intellijIdeaCommunity("2024.1.4")
        bundledPlugin("com.intellij.java")
        bundledPlugin("terminal")
        bundledPlugin("DatabaseTools") // PyCharm Professional-grade database tooling support
    }
    implementation("org.jetbrains.kotlin:kotlin-stdlib")
}

intellijPlatform {
    pluginConfiguration {
        id = "com.doomscript.studio"
        name = "DoomScript Studio"
        version = project.version.toString()
        vendor {
            name = "DoomScript Open Source Project"
            url = "https://github.com/doomscript/doomscript"
        }
        description = """
            Official Professional Language Support & Standalone IDE Distribution for DoomScript (.doom).
            Provides syntax highlighting, live AST transpilation, integrated database explorer, and standalone EXE building.
        """.trimIndent()
    }
    
    publishing {
        token = providers.environmentVariable("JETBRAINS_MARKETPLACE_TOKEN")
    }
}

tasks {
    buildSearchableOptions {
        enabled = false
    }
}
