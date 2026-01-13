# BloomPath Implementation Summary - Jan 13, 2026

## Project State
We have successfully built the **"Logic Engine"** for BloomPath, a Digital Twin of Organization (DTO) that visualizes Jira projects as a growing garden.

## Current Capabilities (UE5 + Python Middleware)
- **Growth Trigger**: Moving a Jira issue to "Done" triggers a visual spawn in UE5.
- **Thorns (Blockers)**: Moving an issue to "Blocked" spawns a specific "Thorn" object.
- **Shrinking (Reopen)**: Reopening an issue finds the specific object (via ID Tag) and deletes it.
- **Priority Mapping**:
    - High Priority = Red Color / Large 2.0x Scale
    - Medium Priority = Green Color / Normal 1.0x Scale
- **Structure**: Epics can be used to group growth (though currently just passed as an ID).

## Context for Marble AI (Asset Generation)
We need a **Chinese Garden** aesthetic. The logic is ready to plug in these assets.
Here is what we need prompts for:

1.  **Growth Meshes (Leaf/Flower replacements)**:
    -   Needs to look good when scaled (1x to 2.0x).
    -   Needs to take **Vertex Color** or Material Parameters (so we can tint them Red/Green based on priority).
    -   *Concept*: Lotus flowers, Bamboo shoots, Cherry Blossoms.

2.  **Blocker/Thorn Meshes**:
    -   Visual metaphor for "Obstacles".
    -   *Concept*: Jagged rocks, weeds, withered branches, or dark stone lanterns.

3.  **Environment**:
    -   Walled Garden walls (modular).
    -   Ponds or paths (static background).

## Technical Implementation Details
- **Actors**: `BP_GrowerActor` is the central manager.
- **Spawning**: Uses `Add Static Mesh Component` in Blueprints.
- **Tagging**: Every spawned mesh has a Component Tag matching the Jira Issue Key (e.g., `KAN-32`).
- **Communication**: HTTP PUT requests to UE5 Remote Control API.
